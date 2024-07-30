from collections.abc import Generator, Iterable, Sequence
from itertools import chain

from markdown_it.tree import SyntaxTreeNode
from markdown_it.token import Token

from axon.markdown import Item
from axon.util import partition


# TODO: does this need to be a class anymore? it doesn't maintain any state
class Transformer:
    """Transform markdown-it's token stream into `Item`s.

    Effectively a compressed version of the full AST, each top-level element
    in a markdown document is an item, as is each list item. Other child
    elements are folded into their enclosing item.
    """

    LIST_TYPES = {"bullet_list", "ordered_list"}

    def __call__(self, tokens: Sequence[Token]) -> Generator[Item]:
        yield from self.to_items(SyntaxTreeNode(tokens).children)

    def to_items(self, nodes: Iterable[SyntaxTreeNode]) -> Generator[Item]:
        for node in nodes:
            if node.type in self.LIST_TYPES:
                yield from self.handle_list(node.children)
            else:
                item = self.visit(node)
                item.refs = self.references(node)
                yield item

    def content(self, node: SyntaxTreeNode) -> str:
        return node.content or "XXX".join(self.content(n) for n in node.children)

    def references(self, node: SyntaxTreeNode) -> list[str]:
        return [n.content for n in node.walk() if n.type == "reference"]

    def handle_list(self, nodes: list[SyntaxTreeNode]) -> Generator[Item]:
        for node in nodes:
            inline, blocks = partition(
                lambda t: t.type in self.LIST_TYPES, node.children
            )
            inline = list(inline)
            pad = "  " * (node.level // 2 + 1)
            content = f"\n".join(
                item.content for n in inline if (item := self.visit(n))
            ).replace("\n", f"\n{pad}")
            yield Item(
                f"{node.info}{node.markup} {content}",
                children=list(self.to_items(blocks)),
                refs=list(chain(*(self.references(n) for n in inline))),
            )

    def visit(self, node: SyntaxTreeNode) -> Item:
        method = f"visit_{node.type}"
        visitor = getattr(self, method, None)
        if not visitor:
            raise Exception(f"Unknown node: {node.pretty(show_text=True)}")
        return visitor(node)

    def visit_blockquote(self, node: SyntaxTreeNode) -> Item:
        content = self.content(node).replace("\n", f"\n{node.markup} ")
        return Item(f"{node.markup} {content}")

    def visit_code_block(self, node: SyntaxTreeNode) -> Item:
        return Item(f"    {node.content}")

    def visit_fence(self, node: SyntaxTreeNode) -> Item:
        return Item(f"{node.markup}\n{node.content}{node.markup}")

    def visit_heading(self, node: SyntaxTreeNode) -> Item:
        return Item(f"{node.markup} {self.content(node)}")

    def visit_hr(self, node: SyntaxTreeNode) -> Item:
        return Item("***")

    def visit_paragraph(self, node: SyntaxTreeNode) -> Item:
        return Item(self.content(node))

    def visit_table(self, node: SyntaxTreeNode) -> Item:
        def align_markup(s: str) -> str:
            align_to_markup = [
                ("left", ":-"),
                ("center", ":-:"),
                ("right", "-:"),
            ]
            return next(
                (markup for align, markup in align_to_markup if align in s), "-"
            )

        def row(cells: Iterable[str]) -> str:
            return f"|{"|".join(cells)}|"

        out = []
        thead = next(n for n in node.children if n.type == "thead")
        th_nodes = thead.children[0].children
        out.append(row(self.content(n) for n in th_nodes))
        aligns = [align_markup(str(n.attrs.get("style", ""))) for n in th_nodes]
        out.append(row(aligns))

        tbody = next(n for n in node.children if n.type == "tbody")
        row_nodes = tbody.children
        for row_node in row_nodes:
            out.append(row(self.content(n) for n in row_node.children))
        return Item("\n".join(out))
