# Author: Nicola Antonello
"""Normal use of the service, which must work with every control on (ADR-0007)."""

from attacks.harness.api import BookmarksApi


def exercise(api: BookmarksApi) -> None:
    """Create a user, save two bookmarks, list them and find one by its title.
    Any deviation raises AssertionError with what went wrong."""
    token = api.create_user()
    recipe = api.add_bookmark(token, "https://example.com/1", "A recipe")
    reading = api.add_bookmark(token, "https://example.com/2", "A reading list")

    listed = api.list_bookmarks(token)
    assert listed.status_code == 200, f"listing returned {listed.status_code}"
    ids = [bookmark["id"] for bookmark in listed.json()]
    assert ids == [reading["id"], recipe["id"]], f"not newest first: {ids}"

    found = api.list_bookmarks(token, q="recipe")
    assert found.status_code == 200, f"searching returned {found.status_code}"
    ids = [bookmark["id"] for bookmark in found.json()]
    assert ids == [recipe["id"]], f"searching by title found {ids}"
