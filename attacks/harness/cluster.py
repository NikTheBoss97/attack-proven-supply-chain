# Author: Nicola Antonello
"""A throwaway kind cluster for one run of the suite, with its own name and its
own kubeconfig file, so it cannot touch any other cluster (ADR-0007, ADR-0010)."""

import os
import secrets
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from attacks.harness.commands import Runner, subprocess_runner
from attacks.harness.errors import SetupError

CONFIG = Path(__file__).resolve().parents[1] / "kind-cluster.yaml"


@dataclass
class Cluster:
    name: str
    kubeconfig: Path
    run: Runner = field(default=subprocess_runner, repr=False)

    @property
    def node(self) -> str:
        """The node's container name, which kind's Docker network resolves."""
        return f"{self.name}-control-plane"

    def kubectl(self, *args: str, stdin: str | None = None) -> str:
        return self.run(["kubectl", "--kubeconfig", str(self.kubeconfig), *args], stdin)

    def load(self, image: str) -> None:
        """Copy a local image into the node, so nothing is pushed anywhere."""
        self.run(["kind", "load", "docker-image", image, "--name", self.name])


def create_cluster(workdir: Path, run: Runner = subprocess_runner) -> Cluster:
    """Create the cluster and join the toolbox to kind's network, where the
    internal kubeconfig and the node's NodePorts are reachable (ADR-0010)."""
    cluster = Cluster(f"apsc-{secrets.token_hex(4)}", workdir / "kubeconfig", run)
    try:
        run(
            ["kind", "create", "cluster", "--name", cluster.name]
            + ["--config", str(CONFIG), "--kubeconfig", str(workdir / "external")]
            + ["--wait", "180s"]
        )
        internal = run(
            ["kind", "get", "kubeconfig", "--name", cluster.name, "--internal"]
        )
        cluster.kubeconfig.write_text(internal)
        container = os.environ.get("TOOLBOX_CONTAINER")
        if not container:
            raise SetupError("TOOLBOX_CONTAINER is not set: run tools/run.sh attacks")
        run(["docker", "network", "connect", "kind", container])
    except BaseException:
        delete_cluster(cluster, run)
        raise
    return cluster


def delete_cluster(cluster: Cluster, run: Runner = subprocess_runner) -> None:
    """Delete the cluster. It never raises, so a failed cleanup cannot hide the
    run's own result."""
    try:
        run(["kind", "delete", "cluster", "--name", cluster.name])
    except (SetupError, OSError) as error:
        print(f"could not delete cluster {cluster.name}: {error}", file=sys.stderr)


@contextmanager
def cluster_session(
    workdir: Path, run: Runner = subprocess_runner
) -> Iterator[Cluster]:
    """A cluster that is deleted however the block ends."""
    cluster = create_cluster(workdir, run)
    try:
        yield cluster
    finally:
        delete_cluster(cluster, run)
