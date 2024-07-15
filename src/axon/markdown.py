import re
from typing import Iterable

from mistletoe import Document
from mistletoe.base_renderer import BaseRenderer
from mistletoe.ast_renderer import AstRenderer
from mistletoe import block_token, span_token
from mistletoe.token import Token
from mistletoe.markdown_renderer import MarkdownRenderer, Fragment

from pprint import pprint as pp


class Ref(span_token.SpanToken):
    parse_inner = False
    parse_group = 0
    repr_attributes = ("name",)

    def __init__(self, match: re.Match):
        self.content = match.group(self.parse_group)
        self.name = match.group(1)


class TagRef(Ref):
    pattern = re.compile(r"#([-0-9A-Za-z]+)")


class BracketRef(Ref):
    pattern = re.compile(r"\[\[([-0-9A-Za-z ]+)\]\]")


class BlockRenderer(MarkdownRenderer):
    def __init__(self):
        self._refs = []
        super().__init__(TagRef, BracketRef)

    def _handle_block(self):
        pass
        self._refs = []

    @staticmethod
    def _parent_block(token: Token) -> Token:
        cur = token
        while not isinstance(cur, block_token.BlockToken):
            if not cur.parent:
                raise ValueError
            cur = cur.parent
        return cur

    def render_tag_ref(self, token: Ref) -> Iterable[Fragment]:
        self._refs.append(token.name)
        print("got ref", token.parent)
        yield Fragment(token.content)

    render_bracket_ref = render_tag_ref

    # def render_paragraph(
    #     self, token: block_token.Paragraph, max_line_length: int
    # ) -> Iterable[str]:
    #     return super().render_paragraph(token, max_line_length)


def test(filename: str):
    with open(filename) as f:
        if True:
            with BlockRenderer() as renderer:
                out = renderer.render(Document(f))
        else:
            with AstRenderer(TagRef, BracketRef) as renderer:
                out = renderer.render(Document(f))

    print(out)


if __name__ == "__main__":
    test("README.md")

"""
What is the actual output I want?
Something like the AST output, but with only block tokens, and each block token should
have a content attribute that is the MarkdownRendered version of all of its Span children
"""
