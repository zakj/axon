from dataclasses import dataclass
import datetime
import sqlite3


@dataclass
class Block:
    id: int
    root_id: int
    path: str
    ordering: int
    content: str

    SCHEMA = """create table if not exists blocks (
        id integer primary key,
        root_id integer not null,
        path not null,
        ordering integer not null default 0,
        content not null default "",
        foreign key (root_id) references pages (id)
    )"""

    @classmethod
    def row_factory(cls, cursor: sqlite3.Cursor, row: sqlite3.Row) -> "Block":
        return cls(*row)

    @property
    def depth(self) -> int:
        # return len(self.path) // PATH_STEP_LEN
        return self.path.count(".")

    @property
    def indent(self) -> str:
        return "  " * self.depth


@dataclass
class Page:
    id: int
    date: datetime.date
    name: str
    filename: str
    last_sync: datetime.datetime

    SCHEMA = """create table if not exists pages (
        id integer primary key,
        date date,
        name unique,
        filename,
        last_sync_at timestamp default CURRENT_TIMESTAMP
    )"""

    @classmethod
    def row_factory(cls, cursor: sqlite3.Cursor, row: sqlite3.Row) -> "Page":
        return cls(*row)

    def blocks(self, con: sqlite3.Connection) -> list[Block]:
        cur = con.cursor()
        cur.row_factory = Block.row_factory
        cur.execute(
            "SELECT * from blocks where root_id = ? order by path",
            (self.id,),
        )
        return cur.fetchall()

    def refs(self, con: sqlite3.Connection) -> tuple[dict[int, str], list[Block]]:
        cur = con.cursor()
        cur.row_factory = Block.row_factory
        # TODO: how to order refs?
        cur.execute(
            "SELECT blocks.* from blocks, refs where page_id = ? and id = block_id",
            (self.id,),
        )
        blocks = cur.fetchall()

        cur = con.cursor()
        placeholders = ",".join("?" * len(blocks))
        cur.execute(
            f"select id, coalesce(date, name) from pages where id in ({placeholders})",
            [b.root_id for b in blocks],
        )
        pages = dict(cur.fetchall())
        return pages, blocks
