import pathlib
import re

import mistune
import pytest
from axon.markdown import Item, preprocess_logseq
from axon.markdown.plugins import REFERENCE_PATTERN, parse_reference, reference
from axon.markdown.transform import AstTransformer


@pytest.fixture
def contents():
    dir = pathlib.Path(__file__).parent

    def _contents(filename):
        with open(dir / filename) as f:
            return f.read()

    return _contents


@pytest.fixture
def parse():
    return mistune.create_markdown(renderer="ast", plugins=[reference])


@pytest.fixture
def ast(parse, contents):
    dir = pathlib.Path(__file__).parent

    def _ast(filename):
        return parse(contents(filename))

    return _ast


def test_transform_simple(ast):
    assert AstTransformer()(ast("simple.md")) == [
        Item("# Hello world"),
        Item("\n\n"),
        Item("This is some markdown."),
    ]


def test_transform_list(ast):
    assert AstTransformer()(ast("list.md")) == [
        Item(
            "- a",
            children=[Item("- b", children=[Item("- c")])],
        ),
        Item("- d"),
    ]


def test_transform_complex(ast):
    assert AstTransformer()(ast("complex.md")) == [
        Item("## second level heading"),
        Item("\n\n"),
        Item("Paragraph with *italic*, **bold**, `inline code`."),
        Item("\n\n"),
        Item('![alt text](# "title text")'),
        Item("\n\n"),
        Item("> blockquote\n> on multiple lines"),
        Item("\n\n"),
        Item("***"),
        Item("\n\n"),
        Item("- [link](#)"),
        Item('- [link](# "with a title")'),
        Item("- [ref-style][]"),
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


def test_preprocess_logseq(parse, contents):
    assert AstTransformer()(parse(preprocess_logseq(contents("logseq.md")))) == [
        Item("- # title", children=[Item("- content")])
    ]
