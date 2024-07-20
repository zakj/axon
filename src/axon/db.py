import sqlite3

from axon.models import Block, Page

DEFAULT_FILENAME = "axon-cache.db"


def connect(filename: str) -> sqlite3.Connection:
    con = sqlite3.connect(filename)
    con.execute("pragma foreign_keys = on")
    return con


def create(con: sqlite3.Connection) -> None:
    cur = con.cursor()

    # TODO: Remove after testing
    cur.execute("drop table if exists refs")
    cur.execute("drop table if exists blocks")
    cur.execute("drop table if exists pages")
    cur.execute(Page.SCHEMA)
    cur.execute(Block.SCHEMA)
    cur.execute("""
        create table if not exists refs (
            block_id integer not null,
            page_id integer not null,
            unique(block_id, page_id)
            foreign key (block_id) references blocks(id) on delete cascade
            foreign key (page_id) references pages(id) on delete cascade
        )
    """)
    # TODO: if we on delete cascade here, what happens to refs TO a page once we delete it?
    # is it better to use a non-integer FK for page?
    # that also doesn't work. maybe page_id -> page_name, and not a foreign key;
    # ok to track refs to things that don't exist, those are trackable
    # in fact might even be nice, we could display refs to a page that doesn't exist when querying
    # that page


# we can avoid complexity by changing materialized path data from id.id.id to order.order.order
def page_content(con: sqlite3.Connection, id: int) -> tuple[str, str]:
    cur = con.cursor()

    cur.execute("SELECT * from pages")
    cur.row_factory = Page.row_factory
    page = cur.fetchone()

    return page.name, "\n".join(
        [
            *(f"{b.indent + b.content}" for b in page.blocks(con)),
        ]
    )


def show_refs(con: sqlite3.Connection, id: int) -> str:
    cur = con.cursor()

    cur.execute("SELECT * from pages")
    cur.row_factory = Page.row_factory
    page = cur.fetchone()

    pages, blocks = page.refs(con)
    ret = []
    for id, name in pages.items():
        ret.append(f"== {name} ==")
        # TODO: should also show children of this block
        for block in (b for b in blocks if b.page_id == id):
            ret.append(block.content)

    return "\n".join(ret)
