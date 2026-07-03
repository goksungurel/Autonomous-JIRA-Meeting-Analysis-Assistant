import pytest
from app import _action_items_to_markdown


def test_basic_list():
    result = _action_items_to_markdown(["Task A", "Task B"])
    assert result == "- Task A\n- Task B"


def test_empty_list():
    assert _action_items_to_markdown([]) == ""


def test_single_item():
    assert _action_items_to_markdown(["Task A"]) == "- Task A"


def test_empty_strings_filtered():
    result = _action_items_to_markdown(["Task A", "", "Task B"])
    assert result == "- Task A\n- Task B"


def test_whitespace_only_filtered():
    result = _action_items_to_markdown(["Task A", "   ", "Task B"])
    assert result == "- Task A\n- Task B"
