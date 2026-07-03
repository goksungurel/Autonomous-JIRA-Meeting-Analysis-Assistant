import pytest
from meeting_assistant import _parse_action_items


def test_dash_bullets():
    result = _parse_action_items("- Task A\n- Task B")
    assert result == ["Task A", "Task B"]


def test_star_bullets():
    result = _parse_action_items("* Task A\n* Task B")
    assert result == ["Task A", "Task B"]


def test_dot_bullets():
    result = _parse_action_items("• Task A\n• Task B")
    assert result == ["Task A", "Task B"]


def test_mixed_bullets():
    result = _parse_action_items("- Task A\n* Task B\n• Task C")
    assert result == ["Task A", "Task B", "Task C"]


def test_plain_lines():
    result = _parse_action_items("Task A\nTask B")
    assert result == ["Task A", "Task B"]


def test_empty_lines_ignored():
    result = _parse_action_items("- Task A\n\n\n- Task B")
    assert result == ["Task A", "Task B"]


def test_whitespace_only_lines_ignored():
    result = _parse_action_items("- Task A\n   \n- Task B")
    assert result == ["Task A", "Task B"]


def test_empty_string():
    assert _parse_action_items("") == []


def test_none_input():
    assert _parse_action_items(None) == []


def test_strips_leading_trailing_whitespace():
    result = _parse_action_items("  - Task A  \n  - Task B  ")
    assert result == ["Task A", "Task B"]
