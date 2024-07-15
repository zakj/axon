from textual import on
import textual
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.suggester import SuggestFromList
from textual.widget import Widget
from textual.widgets import Input, Label, Switch, Pretty, Header, Rule, Static
from textual.containers import VerticalScroll
from textual.events import Compose, Load, Mount, Ready, Show


class Content(Widget):
    pages = reactive([])

    def compose(self) -> ComposeResult:
        self.border_title = "my border title"
        # self.is_scrollable = True
        yield VerticalScroll(*(Static(p) for p in self.pages))

    @on(Compose)  # TODO why doesn't Ready/Mount/App/etc work?
    def load_stuff(self) -> None:
        con = db.connect("tutorial.db")
        db.page_content(con, 1)
        self.pages = [db.page_content(con, 1)]


class Query(Widget):
    DEFAULT_CSS = """
    """

    def compose(self) -> ComposeResult:
        input = Input(
            suggester=SuggestFromList(
                ["apple", "orange", "peach"],
            ),
        )
        input.cursor_blink = False
        # yield Pretty([])
        yield Label("> ")
        yield input

    @on(Input.Changed)
    def show_results(self, event: Input.Changed) -> None:
        # self.query_one(Pretty).update(event.value)
        pass


from axon import db


class AxonApp(App):
    CSS_PATH = "ui.tcss"
    AUTO_FOCUS = "Query Input"

    def compose(self) -> ComposeResult:
        yield Content()
        yield Query()

    @on(Input.Changed)
    def show_results(self, event: Input.Changed) -> None:
        # self.query_one(Pretty).update(event.value)
        # self.query_one("Content Label", Label).update(event.value)
        pass  # TODOk


app = AxonApp()
