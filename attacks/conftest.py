# Author: Nicola Antonello
"""The suite's fixtures: one cluster per run, the images built for it, and the
stacks deployed into it. All of it is removed however the run ends (ADR-0007)."""

import secrets
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from attacks.harness import images as image_tools
from attacks.harness.cluster import Cluster, cluster_session
from attacks.harness.stack import Stack, deploy

REPO = Path(__file__).resolve().parents[1]
RUN = secrets.token_hex(4)


@dataclass
class Images:
    db: str = ""
    api: str = ""
    built: list[str] = field(default_factory=list)


class Stacks:
    """One stack with every control on, and one per attack with its control off,
    each deployed the first time it is asked for."""

    def __init__(self, cluster: Cluster, images: Images, workdir: Path):
        self.cluster = cluster
        self.images = images
        self.workdir = workdir
        self._on: Stack | None = None
        self._off: dict[str, Stack] = {}

    @property
    def on(self) -> Stack:
        if self._on is None:
            self._on = deploy(
                self.cluster, "on", self.images.api, self.images.db, self.workdir
            )
        return self._on

    def off(self, attack_id: str, patch: Path) -> Stack:
        """The service built from a copy of app/ with patch applied: never the
        working tree, and never pushed (ADR-0007)."""
        if attack_id not in self._off:
            name = f"off-{attack_id.replace('_', '-')}"
            copy_dir = self.workdir / name
            copy_dir.mkdir()
            source = image_tools.patched_copy(REPO / "app", patch, copy_dir)
            tag = f"apsc-api:{RUN}-{name}"
            self.images.built.append(tag)
            image_tools.build(source, tag)
            self.cluster.load(tag)
            self._off[attack_id] = deploy(
                self.cluster, name, tag, self.images.db, self.workdir
            )
        return self._off[attack_id]


@pytest.fixture(scope="session")
def workdir(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("suite")


@pytest.fixture(scope="session")
def cluster(workdir):
    with cluster_session(workdir) as cluster:
        yield cluster


@pytest.fixture(scope="session")
def images(cluster):
    images = Images()
    try:
        images.built.append(f"apsc-db:{RUN}")
        images.db = image_tools.build(REPO / "db", f"apsc-db:{RUN}")
        images.built.append(f"apsc-api:{RUN}-on")
        images.api = image_tools.build(REPO / "app", f"apsc-api:{RUN}-on")
        cluster.load(images.db)
        cluster.load(images.api)
        yield images
    finally:
        image_tools.remove(images.built)


@pytest.fixture(scope="session")
def stacks(cluster, images, workdir) -> Stacks:
    return Stacks(cluster, images, workdir)
