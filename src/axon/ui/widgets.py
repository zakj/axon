from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label, ListView, ListItem


class Query[T](Widget):
    items: reactive[list[T]] = reactive([])
    filter: reactive[str] = reactive("")
    filtered_items: reactive[list[T]] = reactive([])

    BINDINGS = [
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
    ]

    class Selected(Message):
        def __init__(self, value: T) -> None:
            self.value = value
            super().__init__()

    def __init__(
        self,
        items: list[T],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.items = items

    def compose(self) -> ComposeResult:
        input = Input()
        input.cursor_blink = False
        yield input
        yield ListView()

    def watch_filter(self):
        list_view = self.query_one(ListView)
        if self.filter:
            self.filtered_items = [
                x for x in self.items if self.filter in str(x).lower()
            ]
            list_view.add_class("open")
        else:
            self.filtered_items = self.items
            list_view.remove_class("open")
        list_view.clear()
        list_view.extend(
            [ListItem(Label(str(p))) for p in self.filtered_items],
        )
        list_view.index = 0  # TODO doesn't highlight sometimes

    @on(Input.Changed)
    def update_filter(self, event: Input.Changed):
        self.filter = event.value.lower()

    @on(Input.Submitted)
    def submit(self, event: Input.Submitted):
        list_view = self.query_one(ListView)
        if list_view.index is not None:
            self.post_message(self.Selected(self.filtered_items[list_view.index]))

    @on(ListView.Selected)
    def select(self, event: ListView.Selected):
        list_view = event.list_view
        if list_view.index is not None:
            self.post_message(self.Selected(self.filtered_items[list_view.index]))

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()
