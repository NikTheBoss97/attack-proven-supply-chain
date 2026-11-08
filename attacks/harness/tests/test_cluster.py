# Author: Nicola Antonello
"""The suite's cluster is unique, and deleted whatever happens."""

import re

import pytest

from attacks.harness.cluster import cluster_session, create_cluster, delete_cluster
from attacks.harness.errors import SetupError


def deleted(fake, name: str) -> bool:
    return ["kind", "delete", "cluster", "--name", name] in fake.commands


def test_cluster_is_deleted_when_the_body_raises(tmp_path, fake):
    with pytest.raises(RuntimeError), cluster_session(tmp_path, run=fake):
        raise RuntimeError
    assert deleted(fake, fake.cluster_name)


def test_cluster_names_are_unique(tmp_path, fake):
    names = [create_cluster(tmp_path, run=fake).name for _ in range(2)]
    assert names[0] != names[1]
    assert all(re.fullmatch(r"apsc-[0-9a-f]{8}", name) for name in names)


def test_missing_toolbox_container_is_a_setup_error(tmp_path, fake, monkeypatch):
    monkeypatch.delenv("TOOLBOX_CONTAINER")
    with pytest.raises(SetupError, match="TOOLBOX_CONTAINER"):
        create_cluster(tmp_path, run=fake)
    assert deleted(fake, fake.cluster_name)


def test_delete_cluster_never_raises(tmp_path, fake):
    cluster = create_cluster(tmp_path, run=fake)
    fake.fail("kind", "delete")
    delete_cluster(cluster, run=fake)
    assert deleted(fake, cluster.name)
