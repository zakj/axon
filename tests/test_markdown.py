import pathlib

import pytest
from axon.markdown import AstTransformer, Item, Token
import mistune


@pytest.fixture
def parse():
    return mistune.create_markdown(renderer="ast")


@pytest.fixture
def ast(parse):
    dir = pathlib.Path(__file__).parent

    def _ast(filename):
        with open(dir / filename) as f:
            return parse(f.read())

    return _ast


def test_transform_simple(ast):
    assert AstTransformer()(ast("simple.md")) == [
        Item(content="# Hello world"),
        Item(content="\n\n"),
        Item(content="This is some markdown."),
    ]


def test_transform_list(ast):
    assert AstTransformer()(ast("list.md")) == [
        Item(
            content="- a",
            children=[Item(content="- b", children=[Item(content="- c")])],
        ),
        Item(content="- d"),
    ]


def test_transform_complex(ast):
    assert AstTransformer()(ast("complex.md")) == [
        Item(content="## second level heading"),
        Item(content="\n\n"),
        Item(content="Paragraph with *italic* and **bold**."),
        Item(content="\n\n"),
        Item(content="***"),
        Item(content="\n\n"),
        Item(content="- [link](#)"),
        Item(content='- [link](# "with a title")'),
        Item(content="- [ref-style][]"),
    ]
