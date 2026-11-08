# Author: Nicola Antonello
"""Control-off copies are patched outside the working tree, and images are
always removed."""

import subprocess

import pytest

from attacks.harness.errors import SetupError
from attacks.harness.images import patched_copy, remove


def make_patch(tmp_path, before: str, after: str):
    """A patch like an attack's control-off.patch: diff -u, then an author line."""
    source = tmp_path / "source" / "app"
    source.mkdir(parents=True)
    (source / "store.py").write_text(before)
    changed = tmp_path / "changed.py"
    changed.write_text(after)
    diff = subprocess.run(
        ["diff", "-u", "--label", "a/app/store.py", "--label", "b/app/store.py"]
        + [str(source / "store.py"), str(changed)],
        capture_output=True,
        text=True,
        check=False,
    )
    patch = tmp_path / "control-off.patch"
    patch.write_text("# Author: Nicola Antonello\n" + diff.stdout)
    return source, patch


def test_patched_copy_applies_a_patch(tmp_path):
    source, patch = make_patch(tmp_path, "check = True\n", "check = False\n")
    workdir = tmp_path / "work"
    workdir.mkdir()
    copy = patched_copy(source, patch, workdir)
    assert (copy / "store.py").read_text() == "check = False\n"
    assert (source / "store.py").read_text() == "check = True\n"


def test_patch_that_does_not_apply_is_a_setup_error(tmp_path):
    source, patch = make_patch(tmp_path, "check = True\n", "check = False\n")
    (source / "store.py").write_text("check = 'moved'\n")
    workdir = tmp_path / "work"
    workdir.mkdir()
    with pytest.raises(SetupError, match="patch"):
        patched_copy(source, patch, workdir)


def test_remove_never_raises(fake):
    fake.fail("docker")
    remove(["apsc-api:test-on"], run=fake)
    assert fake.commands == [["docker", "image", "rm", "--force", "apsc-api:test-on"]]
