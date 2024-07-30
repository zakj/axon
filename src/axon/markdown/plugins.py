import re

from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline

# TODO compile this
REFERENCE_PATTERN = r"#(?P<tagged>[-0-9A-Za-z]+)|\[\[(?P<bracketed>[-_ 0-9A-Za-z]+)\]\]"


def reference_plugin(md: MarkdownIt) -> None:
    """
    Parse wiki-style links and tags:

    .. code-block:: md
        Example [[Wiki link]] or #tag.
    """
    md.inline.ruler.before("link", "reference", _reference_rule)


def is_escaped(src: str, pos: int) -> bool:
    """Determine whether there are odd number of backslashes before the given position."""
    count = 0
    while pos > 0:
        pos -= 1
        if src[pos] == "\\":
            count += 1
        else:
            break
    return bool(count and count % 2 == 1)


def _reference_rule(state: StateInline, start_line: int) -> bool:
    if state.src[state.pos] not in {"[", "#"} or is_escaped(state.src, state.pos):
        return False
    m = re.match(REFERENCE_PATTERN, state.src[state.pos :])
    if not m:
        return False
    tagged, bracketed = m.group("tagged"), m.group("bracketed")
    text = tagged or bracketed
    token = state.push("reference", "a", 0)
    token.content = tagged or bracketed
    token.markup = "#" if tagged else "[["
    state.pos = state.pos + m.end() + 1
    return True
