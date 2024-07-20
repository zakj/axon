import re
from dataclasses import dataclass, field
from itertools import dropwhile
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


# Logseq's markdown isn't quite conforming; the case I've noticed so far is
# when a document starts with a header.
# TODO: throwing away properties now; should I do something with them?
def preprocess_logseq(s: str) -> str:
    property = re.compile(r"[^\s].+:: .+")
    if s.startswith("#"):
        lines = s.splitlines()
        s = f"- {lines[0]}\n" + "\n".join(
            dropwhile(lambda l: property.match(l), lines[1:])
        )
    return s
