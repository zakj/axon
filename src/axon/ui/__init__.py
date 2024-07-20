from itertools import islice
from typing import Iterable, cast

from axon import db
from axon.models import Page
from axon.ui.widgets import Query
from axon.util import partition

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Footer, Input, Label, Markdown, Placeholder, Rule


class QueryScreen(ModalScreen):
    BINDINGS = [("escape", "close", "Close")]
    pages = []

    def __init__(self, pages: list[Page]) -> None:
        self.pages = pages
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Query(self.pages)
        yield Footer()

    # TODO named screen https://textual.textualize.io/guide/screens/#named-screens
    @on(Input.Submitted)
    def action_close(self, event: Input.Submitted | None = None) -> None:
        self.dismiss()


class AxonApp(App):
    journals: list[Page] = []
    pages: list[Page] = []
    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("/", "search", "Search"),
        ("j", "journal", "Journal"),
        ("t", "toggle_sidebar", "Toggle sidebar"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, pages: Iterable[Page]):
        journals, pages = partition(lambda p: p.date is None, pages)
        self.journals, self.pages = list(journals), list(pages)
        super().__init__()

    def compose(self) -> ComposeResult:
        with Center():
            with Horizontal(id="container"):
                with VerticalScroll(id="main"):
                    for journal in islice(self.journals, 5):
                        md = Markdown(journal.render(con))
                        md.border_title = journal.name
                        yield md
                with Horizontal(id="sidebar"):
                    yield Rule(orientation="vertical")
                    yield Label("sidebar")
        yield Footer()

    @on(Query.Selected)
    def on_query_selected(self, message: Query.Selected) -> None:
        page = cast(Page, message.value)  # TODO typing
        main = self.query_one("#main")
        main.remove_children()
        main.scroll_y = 0
        md = Markdown(page.render(con))
        md.border_title = page.name
        main.mount(md)

    def action_search(self) -> None:
        self.push_screen(QueryScreen(self.pages))

    def action_journal(self) -> None:
        main = self.query_one("#main")
        main.remove_children()
        main.scroll_y = 0
        for journal in islice(self.journals, 5):
            md = Markdown(journal.render(con))
            md.border_title = journal.name
            main.mount(md)

    def action_toggle_sidebar(self) -> None:
        self.query_one("#sidebar").toggle_class("open")


con = db.connect("logseq/axon-cache.db")  # TODO how to get this filename. argparse?
app = AxonApp(Page.fetch_all(con))
