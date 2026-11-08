# Author: Nicola Antonello
"""A scripted attack for the harness's tests: each run returns, or raises,
whatever it is given."""

from attacks.harness.attack import Attack, Result

NAMES = (
    "id",
    "title",
    "threats",
    "control",
    "control_page",
    "stopped_as",
    "expected_reason",
)


class Scripted(Attack):
    id = "bola"
    title = "Broken object-level authorization"
    threats = ("T-API-1",)
    control = "Ownership check"
    control_page = "docs/controls/ownership-check.md"
    stopped_as = Result.BLOCKED
    expected_reason = "404 bookmark_not_found"

    def __init__(self, attack=None, variant=None, legitimate=None):
        self.script = {"attack": attack, "variant": variant, "legitimate": legitimate}

    def play(self, run: str):
        value = self.script[run]
        if isinstance(value, BaseException):
            raise value
        return value

    def attack(self, api):
        return self.play("attack")

    def variant(self, api):
        return self.play("variant")

    def legitimate(self, api):
        self.play("legitimate")


def declare(**changes) -> type[Attack]:
    """Declare a new Attack with Scripted's attributes and these changes. A
    change to None leaves that attribute out."""
    attributes = {name: getattr(Scripted, name) for name in NAMES} | changes
    body = {name: value for name, value in attributes.items() if value is not None}
    body |= {"attack": Scripted.attack, "variant": Scripted.variant}
    body["legitimate"] = Scripted.legitimate
    return type("Declared", (Attack,), body)
