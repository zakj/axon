import pprint
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import chain

from axon.markdown import Item, Token
from axon.util import partition


@dataclass
class TransformerContext:
    list_ordered: list[bool] = field(default_factory=list)
    list_num: list[int] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)

    def pop_refs(self) -> list[str]:
        refs = self.refs
        self.refs = []
        return refs


class AstTransformer:
    """Transform mistune's AST into `Item`s.

    Effectively a compressed version of the full AST, each top-level element
    in a markdown document is an item, as is each list item. Other child
    elements are folded into their enclosing item.
    """

    templates = {
        "blank_line": "\n\n",
        "block_text": "{children}",
        "codespan": "`{raw}`",
        "emphasis": "*{children}*",
        "softbreak": "\n",
        "strong": "**{children}**",
        "text": "{raw}",
        "thematic_break": "***",
    }

    def __init__(self):
        self.ctx = TransformerContext()

    def __call__(self, tokens: Iterable[Token]) -> list[Item]:
        return list(chain(*(self.visit(t) for t in tokens)))

    def visit(self, token: Token) -> list[Item]:
        # A defined method on this class takes precedence.
        method = "visit_" + token["type"]
        visitor = getattr(self, method, None)
        if visitor:
            return visitor(token)

        # Otherwise, fall back to `AstTransformer.templates`.
        template = self.templates.get(token["type"])
        if template:
            kwargs = {k: v for k, v in token.items() if k != "children"}
            kwargs["children"] = self.render(*token.get("children", []))
            return [Item(template.format(**kwargs))]

        # Unknown type; fall back to showing the AST.
        # TODO: better error handling once I implement all known types
        return [Item(f"UNKNOWN: {pprint.pformat(token)}")]

    def render(self, *tokens: Token) -> str:
        return "".join(c.content for c in self(tokens))

    def visit_reference(self, token: Token) -> list[Item]:
        assert "attrs" in token
        text = self.render(*token.get("children", []))
        to = token["attrs"].get("to", text)
        if token["attrs"].get("style") == "tag":
            content = f"#{text}"
        else:
            content = f"[[{text}]]"
        self.ctx.refs.append(to)
        return [Item(content)]

    def visit_heading(self, token: Token) -> list[Item]:
        prefix = "#" * token.get("attrs", {}).get("level", 1)
        return [Item(f"{prefix} {self.render(*token.get('children', []))}")]

    def visit_paragraph(self, token: Token) -> list[Item]:
        return [Item(self.render(*token.get("children", [])), refs=self.ctx.pop_refs())]

    def visit_list(self, token: Token) -> list[Item]:
        ordered = token.get("attrs", {}).get("ordered", False)
        self.ctx.list_ordered.append(ordered)
        self.ctx.list_num.append(0)
        items = self(token.get("children", []))
        self.ctx.list_ordered.pop()
        self.ctx.list_num.pop()
        return items

    def visit_list_item(self, token: Token) -> list[Item]:
        content, lists = partition(
            lambda t: t["type"] == "list", token.get("children", [])
        )
        marker = "-"
        self.ctx.list_num[-1] += 1
        if self.ctx.list_ordered[-1]:
            marker = f"{self.ctx.list_num[-1]}."
        item = Item(
            f"{marker} {self.render(*content)}",
            refs=self.ctx.pop_refs(),
        )
        # Render the children only after popping the references for the parent.
        item.children = self(lists)
        return [item]

    def visit_link(self, token: Token) -> list[Item]:
        assert "attrs" in token
        assert "children" in token
        title = token["attrs"].get("title")
        label = token.get("label")
        url = token["attrs"].get("url")
        text = self.render(*token["children"])
        if label:
            # TODO: mistune's ast does not include link ref mapping; it lives only in
            # the state that's passed to renderers.
            return [Item(f"[{text}][]")]
        else:
            if title:
                url = f'{url} "{title}"'
            return [Item(f"[{text}]({url})")]

    def visit_block_code(self, token: Token) -> list[Item]:
        assert "raw" in token
        assert "style" in token
        if token["style"] == "indent":
            return [Item(f"    {token['raw']}")]
        else:
            marker = token.get("marker", "```")
            return [Item(f"{marker}\n{token['raw']}{marker}")]

    def visit_block_quote(self, token: Token) -> list[Item]:
        content = self.render(*token.get("children", []))
        content = content.replace("\n", "\n> ")
        return [Item(f"> {content}")]

    def visit_image(self, token: Token) -> list[Item]:
        assert "attrs" in token
        assert "children" in token
        text = self.render(*token["children"])
        url = token["attrs"].get("url", "")
        title = token["attrs"].get("title")
        if title:
            url = f'{url} "{title}"'
        return [Item(f"![{text}]({url})")]
