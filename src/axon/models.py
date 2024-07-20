from dataclasses import dataclass
import datetime
import sqlite3
from typing import Optional


@dataclass
class Block:
    id: int
    page_id: int
    path: str
    content: str

    SCHEMA = """create table if not exists blocks (
        id integer primary key,
        page_id integer not null,
        path not null,
        content not null default "",
        foreign key (page_id) references pages(id) on delete cascade
    )"""

    @classmethod
    def row_factory(cls, cursor: sqlite3.Cursor, row: sqlite3.Row) -> "Block":
        return cls(*row)

    @property
    def depth(self) -> int:
        return self.path.count(".")

    @property
    def indent(self) -> str:
        return "  " * self.depth


@dataclass
class Page:
    id: int
    date: datetime.date  # only for journal entries
    name: str
    filename: str
    last_sync: datetime.datetime

    SCHEMA = """create table if not exists pages (
        id integer primary key,
        date date,
        name unique not null,
        filename unique not null,
        last_sync_at timestamp not null default CURRENT_TIMESTAMP
    )"""

    def __str__(self) -> str:
        return self.name

    def render(self, con: sqlite3.Connection) -> str:
        return "\n".join(
            [
                *(f"{b.indent + b.content}" for b in self.blocks(con)),
            ]
        )

    @classmethod
    def row_factory(cls, cursor: sqlite3.Cursor, row: sqlite3.Row) -> "Page":
        return cls(*row)

    @classmethod
    def fetch(
        cls,
        con: sqlite3.Connection,
        *,
        id: Optional[int] = None,
        name: Optional[str] = None,
    ):
        if id is None != name is None:
            raise TypeError("one of 'id' or 'name' is required")
        cur = con.cursor()
        cur.row_factory = cls.row_factory
        if id is not None:
            cur.execute("select * from pages where id = ?", (id,))
        else:
            cur.execute("select * from pages where name = ?", (name,))
        return cur.fetchone()

    @classmethod
    def fetch_all(cls, con: sqlite3.Connection):
        cur = con.cursor()
        cur.row_factory = cls.row_factory
        cur.execute("select * from pages")
        return cur.fetchall()

    def blocks(self, con: sqlite3.Connection) -> list[Block]:
        cur = con.cursor()
        cur.row_factory = Block.row_factory
        cur.execute(
            "select * from blocks where page_id = ? order by path",
            (self.id,),
        )
        return cur.fetchall()

    def refs(self, con: sqlite3.Connection) -> tuple[dict[int, str], list[Block]]:
        cur = con.cursor()
        cur.row_factory = Block.row_factory
        # TODO: how to order refs?
        cur.execute(
            "select blocks.* from blocks, refs where page_id = ? and id = block_id",
            (self.id,),
        )
        blocks = cur.fetchall()

        cur = con.cursor()
        placeholders = ",".join("?" * len(blocks))
        cur.execute(
            f"select id, coalesce(date, name) from pages where id in ({placeholders})",
            [b.page_id for b in blocks],
        )
        pages = dict(cur.fetchall())
        return pages, blocks
