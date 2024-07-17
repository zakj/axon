import pathlib
import re

import pytest
from axon.markdown import AstTransformer, Item, Token
from axon.md_reference import parse_reference, reference, REFERENCE_PATTERN
import mistune


@pytest.fixture
def parse():
    return mistune.create_markdown(renderer="ast", plugins=[reference])


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


@pytest.fixture
def mock_state(mocker):
    class MockBlockState:
        append_token = mocker.stub()

    return MockBlockState()


def test_parse_reference_tag(mock_state):
    x = re.compile(REFERENCE_PATTERN)
    m = x.search("here is a #tagged reference")
    assert m
    parse_reference(None, m, mock_state)
    mock_state.append_token.assert_called_once_with(
        {
            "type": "reference",
            "children": [{"type": "text", "raw": "tagged"}],
            "attrs": {"style": "tag", "to": "tagged"},
        }
    )


def test_parse_reference_bracket(mock_state):
    x = re.compile(REFERENCE_PATTERN)
    m = x.search("here is a [[Bracketed reference]]")
    assert m
    parse_reference(None, m, mock_state)
    mock_state.append_token.assert_called_once_with(
        {
            "type": "reference",
            "children": [{"type": "text", "raw": "Bracketed reference"}],
            "attrs": {"style": "bracket", "to": "Bracketed reference"},
        }
    )


def test_transform_reference(ast):
    assert AstTransformer()(ast("reference.md")) == [
        Item("Paragraph with #a-tag and [[A Bracket]].", refs=["a-tag", "A Bracket"])
    ]


def test_transform_list_reference(ast):
    assert AstTransformer()(ast("list-reference.md")) == [
        Item(
            "- top level #a",
            refs=["a"],
            children=[
                Item(
                    "- second level #b",
                    refs=["b"],
                    children=[Item("- third level #c", refs=["c"])],
                ),
                Item("- second level again #d", refs=["d"]),
            ],
        )
    ]
