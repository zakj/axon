import re

from mistune.core import BlockState
from mistune.markdown import Markdown

REFERENCE_PATTERN = r"#(?P<tagged>[-0-9A-Za-z]+)|\[\[(?P<bracketed>[-_ 0-9A-Za-z]+)\]\]"


def parse_reference(_, m: re.Match, state: BlockState) -> int:
    tagged, bracketed = m.group("tagged"), m.group("bracketed")
    text = tagged or bracketed
    state.append_token(
        {
            "type": "reference",
            "children": [{"type": "text", "raw": text}],
            "attrs": {"to": text, "style": "tag" if tagged else "bracket"},
        }
    )
    return m.end()


# TODO: handle comma in brackets. ignore backslash-escaped tags
def reference(md: Markdown) -> None:
    """A mistune plugin to handle tags and wiki-style links.

    Tags can contain letters, numbers, and dashes. #my-reference
    Brackets can also contain spaces and underscores. [[My Reference]]
    """
    md.inline.register("reference", REFERENCE_PATTERN, parse_reference, before="link")
