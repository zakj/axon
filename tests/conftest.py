from pathlib import Path

import pytest


@pytest.fixture
def contents():
    dir = Path(__file__).parent

    def _contents(filename):
        with open(dir / filename) as f:
            return f.read()

    return _contents
