import markdown_it
import pytest

from axon.markdown import Item, create_md
from axon.markdown.plugins import reference_plugin
from axon.markdown.transform import Transformer


@pytest.fixture
def transform(contents):
    transformer = Transformer()
    md = create_md()

    def _transform(filename):
        return list(transformer(md.parse(contents(filename))))

    return _transform


def test_transform_simple(transform):
    assert transform("md/simple.md") == [
        Item("# Hello world"),
        Item("This is some markdown."),
    ]


def test_transform_list(transform):
    assert transform("md/list.md") == [
        Item(
            "- a",
            children=[Item("- b", children=[Item("- c")])],
        ),
        Item("- d"),
    ]


def test_transform_complex(transform):
    assert transform("md/complex.md") == [
        Item("## second level heading"),
        Item("Paragraph with *italic*, **bold**, `inline code`."),
        Item('![alt text](# "title text")'),
        Item("> blockquote\n> on multiple lines"),
        Item("***"),
        Item("- [link](#)"),
        Item('- [link](# "with a title")'),
        Item("- [ref-style][]"),
        Item("```\nfence\n```"),
        Item("    code block\n"),
    ]


def test_transform_reference(transform):
    assert transform("md/reference.md") == [
        Item("Paragraph with #a-tag and [[A Bracket]].", refs=["a-tag", "A Bracket"])
    ]


def test_transform_list_reference(transform):
    assert transform("md/list-reference.md") == [
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
