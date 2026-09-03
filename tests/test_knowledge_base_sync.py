"""Unit tests for KnowledgeBaseSync — no Ollama/Chroma involved, only a fake
rag_tool double, so these run fast and fully offline.
"""
from types import SimpleNamespace

import pytest

from knowledge_base_sync import KnowledgeBaseSync


class FakeClient:
    def __init__(self):
        self.deleted = []
        self.recreated = []
        self.raise_on_delete = False

    def delete_collection(self, collection_name):
        if self.raise_on_delete:
            raise RuntimeError("boom")
        self.deleted.append(collection_name)

    def get_or_create_collection(self, collection_name):
        self.recreated.append(collection_name)


class FakeRagTool:
    def __init__(self):
        self.collection_name = "test_collection"
        self.client = FakeClient()
        self.adapter = SimpleNamespace(_client=self.client)
        self.add_calls = []

    def add(self, **kwargs):
        self.add_calls.append(kwargs)


@pytest.fixture
def rag_tool():
    return FakeRagTool()


def _sync(rag_tool, tmp_path, subdir="kb"):
    directory = tmp_path / subdir
    directory.mkdir(exist_ok=True)
    state_file = tmp_path / "state.json"
    return KnowledgeBaseSync(rag_tool, directory, state_file), directory


def test_first_sync_adds_and_reports_changed(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    (directory / "a.md").write_text("Rule A")
    (directory / "b.md").write_text("Rule B")

    result = sync.sync()

    assert result.changed is True
    assert result.file_count == 2
    assert sorted(result.files) == ["a.md", "b.md"]
    assert len(rag_tool.add_calls) == 1


def test_second_sync_with_no_changes_is_a_noop(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    (directory / "a.md").write_text("Rule A")
    sync.sync()

    result = sync.sync()

    assert result.changed is False
    assert result.file_count == 1
    assert len(rag_tool.add_calls) == 1  # not called a second time


def test_adding_a_file_triggers_rebuild(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    (directory / "a.md").write_text("Rule A")
    sync.sync()

    (directory / "b.md").write_text("Rule B")
    result = sync.sync()

    assert result.changed is True
    assert result.file_count == 2
    assert len(rag_tool.add_calls) == 2


def test_editing_a_file_triggers_rebuild(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    doc = directory / "a.md"
    doc.write_text("Rule A")
    sync.sync()

    doc.write_text("Rule A, updated")
    result = sync.sync()

    assert result.changed is True
    assert len(rag_tool.add_calls) == 2


def test_removing_a_file_triggers_rebuild_and_clears_collection(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    a = directory / "a.md"
    a.write_text("Rule A")
    (directory / "b.md").write_text("Rule B")
    sync.sync()

    a.unlink()
    result = sync.sync()

    assert result.changed is True
    assert result.file_count == 1
    assert result.files == ["b.md"]
    assert rag_tool.client.deleted == ["test_collection", "test_collection"]


def test_removing_all_files_clears_without_calling_add_again(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    a = directory / "a.md"
    a.write_text("Rule A")
    sync.sync()

    a.unlink()
    result = sync.sync()

    assert result.changed is True
    assert result.file_count == 0
    assert len(rag_tool.add_calls) == 1  # add() not called again — nothing to add


def test_missing_directory_is_treated_as_empty(rag_tool, tmp_path):
    directory = tmp_path / "does_not_exist"
    sync = KnowledgeBaseSync(rag_tool, directory, tmp_path / "state.json")

    result = sync.sync()

    assert result.changed is True
    assert result.file_count == 0
    assert rag_tool.add_calls == []


def test_force_rebuilds_even_without_changes(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    (directory / "a.md").write_text("Rule A")
    sync.sync()

    result = sync.sync(force=True)

    assert result.changed is True
    assert len(rag_tool.add_calls) == 2


def test_corrupt_state_file_is_treated_as_never_synced(rag_tool, tmp_path):
    directory = tmp_path / "kb"
    directory.mkdir()
    (directory / "a.md").write_text("Rule A")
    state_file = tmp_path / "state.json"
    state_file.write_text("{ not valid json")

    sync = KnowledgeBaseSync(rag_tool, directory, state_file)
    result = sync.sync()

    assert result.changed is True
    assert len(rag_tool.add_calls) == 1


def test_clear_collection_failure_does_not_break_sync(rag_tool, tmp_path):
    rag_tool.client.raise_on_delete = True
    sync, directory = _sync(rag_tool, tmp_path)
    (directory / "a.md").write_text("Rule A")

    result = sync.sync()

    assert result.changed is True
    assert len(rag_tool.add_calls) == 1


def test_list_files_does_not_touch_the_vector_store(rag_tool, tmp_path):
    sync, directory = _sync(rag_tool, tmp_path)
    (directory / "a.md").write_text("Rule A")
    (directory / "b.md").write_text("Rule B")

    names = sync.list_files()

    assert sorted(names) == ["a.md", "b.md"]
    assert rag_tool.add_calls == []
    assert rag_tool.client.deleted == []


def test_ensure_knowledge_base_loaded_delegates_to_kb_sync(monkeypatch):
    import meeting_assistant

    calls = []
    monkeypatch.setattr(meeting_assistant.kb_sync, "sync", lambda: calls.append(True))

    meeting_assistant._ensure_knowledge_base_loaded()

    assert calls == [True]
