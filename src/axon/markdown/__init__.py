import re
from dataclasses import dataclass, field
from itertools import takewhile

from markdown_it import MarkdownIt

from axon.markdown.plugins import reference_plugin


# TODO: there has got to be a better name
@dataclass
class Item:
    content: str
    children: list["Item"] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)


def create_md():
    return MarkdownIt().enable("table").use(reference_plugin)


# Logseq's markdown isn't quite conforming.
# TODO cleanup
# TODO: should the property parser be a markdown plugin instead?
# see example on PKM where we accidentally parse properties in a fenced code block
def preprocess_logseq(s: str) -> str:
    property = re.compile(r"(?P<indent>\s*)(?P<k>[^\s]+)\s*::\s*(?P<v>.+)")
    ignored_properties = ("id", "collapsed", "icon")

    # If the first item in a page is a heading, logseq doesn't emit a bullet for it.
    # If that item has properties, they are not indented.
    if s.startswith("#"):
        first, *lines = s.splitlines()
        out = [f"- {first}"]
        properties = list(takewhile(lambda l: property.match(l), lines))
        out.extend(f"  {l}" for l in properties)
        out.extend(lines[len(properties) :])
        s = "\n".join(out)

    # Convert logseq properties to a table.
    lines = s.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        property_lines = list(takewhile(lambda l: property.search(l), lines[i:]))
        if property_lines:
            matches = [
                m.groupdict() for l in property_lines if (m := property.search(l))
            ]
            properties = []
            indent = matches[0]["indent"]
            for m in matches:
                if m["k"] in ignored_properties:
                    continue
                properties.append((m["k"], m["v"]))
            if properties:
                out.append(indent + "|||")
                out.append(indent + "|-:|-|")
                for k, v in properties:
                    out.append(f"{indent}|{k}|{v}|")
            i += len(property_lines)
        else:
            out.append(line)
            i += 1
    return "\n".join(out)
