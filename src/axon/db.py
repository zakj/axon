import sqlite3

from axon.models import Block, Page


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
            foreign key (block_id) references blocks (id)
            foreign key (page_id) references pages (id)
        )
    """)


# we can avoid complexity by changing materialized path data from id.id.id to order.order.order
def page_content(con: sqlite3.Connection, id: int) -> str:
    cur = con.cursor()

    cur.execute("SELECT * from pages")
    cur.row_factory = Page.row_factory
    page = cur.fetchone()

    return "\n".join(
        [
            page.name or page.date,
            *(f"| {b.indent + b.content:75} {(b.path)}" for b in page.blocks(con)),
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
        for block in (b for b in blocks if b.root_id == id):
            ret.append(block.content)

    return "\n".join(ret)


if __name__ == "__main__":
    con = connect("tutorial.db")
    create(con)
    print(page_content(con, 1))
    print(show_refs(con, 1))
