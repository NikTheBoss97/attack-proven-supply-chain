# Author: Nicola Antonello
"""A stack: the service and its database, deployed into one namespace of the
suite's cluster, with passwords made for it (ADR-0010)."""

import json
import os
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from attacks.harness.api import BookmarksApi
from attacks.harness.cluster import Cluster
from attacks.harness.errors import SetupError

BASE = Path(__file__).resolve().parents[2] / "deploy"


@dataclass
class Stack:
    namespace: str
    base_url: str
    api: BookmarksApi


def deploy(
    cluster: Cluster, namespace: str, api_image: str, db_image: str, workdir: Path
) -> Stack:
    """Deploy the manifests in deploy/ and wait until the service answers. Any
    failure raises SetupError."""
    overlay = workdir / f"overlay-{namespace}"
    overlay.mkdir()
    write_overlay(overlay, namespace, api_image, db_image)
    # create, not apply: apply would copy the passwords into an annotation.
    cluster.kubectl("create", "-f", "-", stdin=json.dumps(credentials(namespace)))
    cluster.kubectl("apply", "-k", str(overlay))
    for deployment in ("db", "api"):
        cluster.kubectl(
            *(
                "--namespace",
                namespace,
                "rollout",
                "status",
                f"deployment/{deployment}",
            ),
            "--timeout=180s",
        )
    wait_until_connected(cluster, namespace)
    port = cluster.kubectl(
        *("--namespace", namespace, "get", "service", "api"),
        *("--output", "jsonpath={.spec.ports[0].nodePort}"),
    )
    base_url = f"http://{cluster.node}:{port}"
    wait_until_healthy(base_url)
    return Stack(namespace, base_url, BookmarksApi(base_url))


def write_overlay(overlay: Path, namespace: str, api_image: str, db_image: str) -> None:
    """The namespace, the run's image tags, and the Service exposed on a NodePort,
    which only this test overlay does. Written as JSON, which is also YAML."""
    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": namespace,
        "resources": [os.path.relpath(BASE, overlay)],
        "images": [image("apsc-api", api_image), image("apsc-db", db_image)],
        "patches": [
            {
                "target": {"kind": "Service", "name": "api"},
                "patch": json.dumps(
                    [{"op": "replace", "path": "/spec/type", "value": "NodePort"}]
                ),
            }
        ],
    }
    (overlay / "kustomization.yaml").write_text(json.dumps(kustomization, indent=2))


def image(name: str, reference: str) -> dict[str, str]:
    new_name, _, tag = reference.rpartition(":")
    return {"name": name, "newName": new_name, "newTag": tag}


def credentials(namespace: str) -> dict:
    """The namespace and its database passwords, made for this deployment and
    sent to kubectl on stdin, never as an argument."""
    return {
        "apiVersion": "v1",
        "kind": "List",
        "items": [
            {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": namespace}},
            {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {"name": "db-credentials", "namespace": namespace},
                "type": "Opaque",
                "stringData": {
                    "postgres-password": secrets.token_urlsafe(24),
                    "api-password": secrets.token_urlsafe(24),
                },
            },
        ],
    }


def wait_until_connected(cluster: Cluster, namespace: str, timeout: float = 60) -> None:
    """Wait until the service can open a database connection, with its own
    settings. Its readiness probe, /healthz, never touches the database, and the
    db Service starts routing a moment after its pod is ready."""
    probe = "import psycopg; psycopg.connect(connect_timeout=2).close()"
    deadline = time.monotonic() + timeout
    while True:
        try:
            cluster.kubectl(
                *("--namespace", namespace, "exec", "deployment/api"),
                *("--", "python", "-c", probe),
            )
            return
        except SetupError:
            if time.monotonic() > deadline:
                raise
            time.sleep(1)


def wait_until_healthy(base_url: str, timeout: float = 60) -> None:
    """Poll /healthz: a NodePort answers a moment after its Service exists."""
    deadline = time.monotonic() + timeout
    while not healthy(f"{base_url}/healthz"):
        if time.monotonic() > deadline:
            raise SetupError(
                f"{base_url}/healthz did not answer 200 in {timeout:.0f} s"
            )
        time.sleep(1)


def healthy(url: str) -> bool:
    try:
        return httpx.get(url, timeout=2).status_code == 200
    except httpx.HTTPError:
        return False
