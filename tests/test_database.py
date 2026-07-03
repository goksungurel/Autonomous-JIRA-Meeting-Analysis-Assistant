import pytest
import database


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.init_db()


def test_save_meeting_returns_id():
    meeting_id = database.save_meeting("standup.txt", "transcript", "- Task A", "KAN-101")
    assert isinstance(meeting_id, int)
    assert meeting_id > 0


def test_get_meeting_returns_correct_record():
    meeting_id = database.save_meeting("standup.txt", "transcript", "- Task A", "KAN-101")
    record = database.get_meeting(meeting_id)
    assert record["file_name"] == "standup.txt"
    assert record["transcript"] == "transcript"
    assert record["action_items"] == "- Task A"
    assert record["jira_output"] == "KAN-101"


def test_get_meeting_nonexistent_returns_none():
    result = database.get_meeting(99999)
    assert result is None


def test_get_all_meetings_newest_first():
    database.save_meeting("first.txt", "", "- Task A", "")
    database.save_meeting("second.txt", "", "- Task B", "")
    meetings = database.get_all_meetings()
    assert meetings[0]["file_name"] == "second.txt"
    assert meetings[1]["file_name"] == "first.txt"


def test_delete_meeting_removes_record():
    meeting_id = database.save_meeting("standup.txt", "transcript", "- Task A", "KAN-101")
    database.delete_meeting(meeting_id)
    assert database.get_meeting(meeting_id) is None


def test_get_all_meetings_empty():
    assert database.get_all_meetings() == []


def test_search_by_file_name():
    database.save_meeting("standup.txt", "", "- Task A", "")
    database.save_meeting("sprint_review.txt", "", "- Task B", "")
    results = database.search_meetings(file_name="standup")
    assert len(results) == 1
    assert results[0]["file_name"] == "standup.txt"


def test_search_by_file_name_no_match():
    database.save_meeting("standup.txt", "", "- Task A", "")
    results = database.search_meetings(file_name="nonexistent")
    assert results == []


def test_search_by_date():
    database.save_meeting("standup.txt", "", "- Task A", "")
    results = database.search_meetings(date="2099-01-01")
    assert results == []


def test_search_no_filters_returns_all():
    database.save_meeting("a.txt", "", "", "")
    database.save_meeting("b.txt", "", "", "")
    results = database.search_meetings()
    assert len(results) == 2
