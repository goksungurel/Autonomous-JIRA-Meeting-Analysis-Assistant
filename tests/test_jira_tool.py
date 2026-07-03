import re
from meeting_assistant import JiraTaskTool


def test_returns_success_message():
    tool = JiraTaskTool()
    result = tool._run(summary="Fix login bug", description="Users can't log in on mobile.")
    assert result.startswith("SUCCESS:")


def test_returns_valid_jira_key():
    tool = JiraTaskTool()
    result = tool._run(summary="Fix login bug", description="Details here.")
    match = re.search(r"KAN-\d{3}", result)
    assert match is not None


def test_summary_in_output(capsys):
    tool = JiraTaskTool()
    tool._run(summary="Deploy API v2", description="Deploy to production.")
    captured = capsys.readouterr()
    assert "Deploy API v2" in captured.out
