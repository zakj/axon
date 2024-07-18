from collections.abc import Iterable
from pathlib import Path
from typing import cast
import sqlite3

import mistune

from axon.db import connect, create
from axon.markdown import Item, Token
from axon.markdown.plugins import reference
from axon.markdown.transform import AstTransformer
from axon.models import Page, Block


def parse(filename: str) -> list[Item]:
    parse = mistune.create_markdown(renderer="ast", plugins=[reference])
    transform = AstTransformer()
    with open(filename, "r") as f:
        return transform(cast(list[Token], parse(f.read())))


def path_str(path: list[int]) -> str:
    return ".".join(f"{i:04}" for i in path)


def walk(
    items: list[Item],
    parent_path: list[int],
) -> Iterable[tuple[str, str]]:
    for i, item in enumerate(items, start=1):
        # TODO refs. maybe walk just builds paths and attaches items
        path = parent_path + [i]
        yield path_str(path), item.content
        yield from walk(item.children, path)


# TODO: walk could build a list of executemany-able values
def walk_old(
    cur: sqlite3.Cursor,
    page_id: int,
    items: list[Item],
    parent_path: list[int],
) -> None:
    if parent_path is None:
        parent_path = []
    for i, item in enumerate(items, start=1):
        path = parent_path + [i]
        # TODO: factor inserts out into model helpers?
        cur.execute(
            "insert into blocks (root_id, path, content) values (?, ?, ?)",
            (page_id, path_str(path), item.content),
        )
        walk_old(cur, page_id, item.children, path)


def sync(notes_dir: Path, cache_file: Path) -> None:
    con = connect(cache_file.as_posix())
    create(con)  # TODO create only if not exists
    # for md_file in notes_dir.rglob("*.md"):
    for path in notes_dir.rglob("PKM.md"):  # XXX
        relpath = path.relative_to(notes_dir)
        page_name = str(relpath.parent / relpath.stem)
        cur = con.cursor()
        # TODO should filename also be relative to notes_dir, so we don't lose our db if we move the notes?
        # TODO if page exists, check that last modified is greater than last sync
        # if not, nothing to do
        # if so, remove the page and its descendant blocks (does sqlite handle cascade?)
        cur.execute(
            "insert into pages (name, filename) values (?, ?)",
            (page_name, path.as_posix()),
        )
        page_id = cur.lastrowid
        assert page_id
        items = parse(path.as_posix())
        # TODO: factor inserts out into model helpers?
        cur.executemany(
            "insert into blocks (root_id, path, content) values (?, ?, ?)",
            [(page_id,) + row for row in walk(items, [])],
        )
        con.commit()
