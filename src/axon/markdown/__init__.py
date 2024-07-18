from dataclasses import dataclass, field
from typing import Any, Required, TypedDict


class Token(TypedDict, total=False):
    """A item in mistune's AST."""

    type: Required[str]
    children: list["Token"]
    attrs: dict[str, Any]


# TODO: there has got to be a better name
@dataclass
class Item:
    content: str
    children: list["Item"] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)
