from axon.ui.widgets import Query
from textual.binding import Binding
from axon import db
from axon.models import Page
from textual import on
import textual
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.suggester import SuggestFromList
from textual.widget import Widget
from textual.widgets import (
    Input,
    Label,
    ListItem,
    ListView,
    Placeholder,
    Switch,
    Pretty,
    Header,
    Rule,
    Static,
)
from textual.containers import VerticalScroll
from textual.events import Compose, Load, Mount, Ready, Show
from textual.widgets import MarkdownViewer, Markdown, Select


class Content(Widget):
    pages: reactive[list[tuple[str, str]]] = reactive([])

    def compose(self) -> ComposeResult:
        title, content = self.pages[0]
        self.border_title = title
        # self.is_scrollable = True
        # yield VerticalScroll(*(Static(p) for p in self.pages))

        yield VerticalScroll(Markdown(content))

    @on(Compose)  # TODO why doesn't Ready/Mount/App/etc work?
    def load_stuff(self) -> None:
        con = db.connect("logseq/cache.db")  # XXX
        db.page_content(con, 1)
        self.pages = [db.page_content(con, 1)]


class AxonApp(App):
    CSS_PATH = "ui.tcss"
    AUTO_FOCUS = "Query Input"
    pages: reactive[list[Page]] = reactive([])

    def __init__(self, pages: list[Page]):
        super().__init__()
        self.pages = pages

    def compose(self) -> ComposeResult:
        # yield Input()
        # sel = Select(options=((p.name, p.id) for p in self.pages))
        # yield sel
        # yield Query(items=self.pages)
        journals = [p for p in self.pages if p.name.startswith("journal")]
        journals.sort(key=lambda p: p.name, reverse=True)
        self.notify(str(len(journals)))
        mds = []
        for journal in journals[:5]:
            md = Markdown(journal.render(con))
            md.border_title = journal.name
            mds.append(md)

        # Query starts underneath content, and floats to a modal
        yield Query(items=self.pages)
        yield VerticalScroll(*mds)
        # yield Placeholder(variant="size")
        # yield Input()
        # yield ListView(
        #     ListItem(Label("apple")),
        #     ListItem(Label("orange")),
        #     ListItem(Label("peach")),
        #     initial_index=2,
        # )

        # from textual_autocomplete import AutoComplete
        # yield AutoComplete(
        #     Input(placeholder="Type to search..."),
        #     candidates=[
        #         DropdownItem("Glasgow"),
        #         DropdownItem("Edinburgh"),
        #         DropdownItem("Aberdeen"),
        #         DropdownItem("Dundee"),
        #     ],
        # )
        # yield Content()
        # yield Query(suggestions=[p.name for p in self.pages])

    def on_query_selected(self, message: Query.Selected) -> None:
        # TODO
        self.notify("selected: " + str(message.value))


from axon.db import connect

con = connect("logseq/cache.db")
app = AxonApp(Page.fetch_all(con))
