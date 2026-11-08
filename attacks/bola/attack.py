# Author: Nicola Antonello
"""Broken object-level authorization, first in OWASP's API Security Top 10: Bob,
with an account of his own, reads or deletes Alice's bookmark by its ID
(T-API-1). The control is the ownership check: every query on a bookmark is
limited to the caller (ADR-0006). The payloads are example.com URLs, which the
service stores and never fetches."""

from attacks.harness.api import BookmarksApi, error_code
from attacks.harness.attack import Attack, Outcome, Result
from attacks.harness.errors import SetupError


def alice_and_bob(api: BookmarksApi) -> tuple[dict, str, str]:
    """Alice saves a bookmark and reads it back, which proves that it exists.
    If she cannot, the setup is broken and the run reports error."""
    alice = api.create_user()
    bob = api.create_user()
    bookmark = api.add_bookmark(alice, "https://example.com/alice/private", "Private")
    own = api.get_bookmark(alice, bookmark["id"])
    if own.status_code != 200:
        raise SetupError(f"Alice could not read her own bookmark: {own.status_code}")
    return bookmark, alice, bob


class BrokenObjectLevelAuthorization(Attack):
    id = "bola"
    title = "Broken object-level authorization"
    threats = ("T-API-1",)
    control = "Ownership check"
    control_page = "docs/controls/ownership-check.md"
    stopped_as = Result.BLOCKED
    expected_reason = "404 bookmark_not_found"

    def attack(self, api: BookmarksApi) -> Outcome:
        """Bob reads Alice's bookmark by its ID."""
        bookmark, _, bob = alice_and_bob(api)
        response = api.get_bookmark(bob, bookmark["id"])
        if response.status_code == 200 and response.json()["url"] == bookmark["url"]:
            return Outcome.succeeded(f"Bob read Alice's bookmark, {bookmark['url']}")
        return Outcome.stopped_by(f"{response.status_code} {error_code(response)}")

    def variant(self, api: BookmarksApi) -> Outcome:
        """Bob deletes Alice's bookmark, which a check written only for reads
        would let through. The effect decides, not Bob's response: whether
        Alice can still read her bookmark."""
        bookmark, alice, bob = alice_and_bob(api)
        deleted = api.delete_bookmark(bob, bookmark["id"])
        after = api.get_bookmark(alice, bookmark["id"])
        if after.status_code == 404:
            return Outcome.succeeded(
                f"Bob deleted Alice's bookmark; his DELETE got {deleted.status_code}"
            )
        if after.status_code == 200:
            return Outcome.stopped_by(f"{deleted.status_code} {error_code(deleted)}")
        raise SetupError(f"Alice's read after Bob's DELETE got {after.status_code}")

    def legitimate(self, api: BookmarksApi) -> None:
        """Alice reads her own bookmark, deletes it, and then finds it gone."""
        alice = api.create_user()
        bookmark = api.add_bookmark(alice, "https://example.com/alice/own", "Own")
        read = api.get_bookmark(alice, bookmark["id"])
        assert read.status_code == 200, f"Alice's read got {read.status_code}"
        assert read.json()["url"] == bookmark["url"], "Alice read another URL"
        deleted = api.delete_bookmark(alice, bookmark["id"])
        assert deleted.status_code == 204, f"Alice's delete got {deleted.status_code}"
        gone = api.get_bookmark(alice, bookmark["id"])
        assert (gone.status_code, error_code(gone)) == (404, "bookmark_not_found"), (
            f"after deleting, Alice's read got {gone.status_code} {error_code(gone)}"
        )
