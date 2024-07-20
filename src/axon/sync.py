from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path
from typing import cast

import mistune

from axon.db import connect, create
from axon.markdown import Item, Token, preprocess_logseq
from axon.markdown.plugins import reference
from axon.markdown.transform import AstTransformer

DATE_FORMATS = [
    "%Y_%m_%d",  # Logseq
]


def parse(filename: str) -> list[Item]:
    parse = mistune.create_markdown(renderer="ast", plugins=[reference])
    transform = AstTransformer()
    with open(filename) as f:
        return transform(cast(list[Token], parse(preprocess_logseq(f.read()))))


def path_str(path: list[int]) -> str:
    return ".".join(f"{i:04}" for i in path)


def parse_date(s: str) -> date | None:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def walk(
    items: list[Item],
    parent_path: list[int],
) -> Iterable[tuple[str, str]]:
    for i, item in enumerate(items, start=1):
        # TODO refs. maybe walk just builds paths and attaches items
        path = parent_path + [i]
        yield path_str(path), item.content
        yield from walk(item.children, path)


def sync(notes_dir: Path, cache_file: Path) -> None:
    con = connect(cache_file.as_posix())
    create(con)  # TODO create only if not exists
    for path in notes_dir.rglob("*.md"):
        relpath = path.relative_to(notes_dir)
        page_name = str(relpath.parent / relpath.stem)
        cur = con.cursor()
        # TODO should filename also be relative to notes_dir, so we don't lose our db if we move the notes?
        # TODO if page exists, check that last modified is greater than last sync
        # if not, nothing to do
        # if so, remove the page and its descendant blocks (does sqlite handle cascade?)

        page_date = parse_date(relpath.stem)
        if page_date:
            page_name = page_date.strftime("%Y-%m-%d • %A")
        cur.execute(
            "insert into pages (name, filename, date) values (?, ?, ?)",
            (page_name, path.as_posix(), parse_date(relpath.stem)),
        )
        page_id = cur.lastrowid
        assert page_id
        items = parse(path.as_posix())
        # TODO: factor inserts out into model helpers?
        cur.executemany(
            "insert into blocks (page_id, path, content) values (?, ?, ?)",
            [(page_id,) + row for row in walk(items, [])],
        )
        con.commit()
