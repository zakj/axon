import pytest
from axon.markdown.plugins import _reference_rule


@pytest.fixture
def mock_state(mocker):
    class MockStateInline:
        push = mocker.stub()
        src = ""
        pos = 0

    return MockStateInline()


def test_parse_reference_tag(mock_state):
    mock_state.src = "a #tagged reference"
    mock_state.pos = 2
    _reference_rule(mock_state, 0)
    assert mock_state.push.call_count == 1


def test_parse_reference_escaped(mock_state):
    mock_state.src = "an \\#escaped reference"
    mock_state.pos = 4
    _reference_rule(mock_state, 0)
    assert mock_state.push.call_count == 0


def test_parse_reference_bracket(mock_state):
    mock_state.src = "a [[Bracketed reference]]"
    mock_state.pos = 2
    _reference_rule(mock_state, 0)
    assert mock_state.push.call_count == 1


def test_parse_reference_unclosed_bracket(mock_state):
    mock_state.src = "a [[Bracketed reference]"
    mock_state.pos = 2
    _reference_rule(mock_state, 0)
    assert mock_state.push.call_count == 0
