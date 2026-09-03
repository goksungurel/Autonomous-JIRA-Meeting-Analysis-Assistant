"""Keeps a RagTool's vector collection in sync with a directory of documents.

The goal: adding, editing, or removing a file under knowledge_base/ should be
enough to change what the RAG agent retrieves on the next run — no manual
re-indexing command, no code change. This module fingerprints the directory
(relative path + content hash of every file) and only touches the vector
store — the expensive, Ollama-dependent part — when that fingerprint has
actually changed since the last successful sync.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Outcome of a sync() call, useful for logging or surfacing in a UI."""

    changed: bool
    file_count: int
    files: list[str] = field(default_factory=list)


class KnowledgeBaseSync:
    """Reconciles a RagTool's vector collection with a directory on disk.

    On change, this does a full rebuild (clear the collection, then re-add
    every current file) rather than tracking per-chunk state — simpler and
    more robust than incremental updates, at the cost of a full re-embed
    when anything in the directory changes. For a small, occasionally-edited
    knowledge base this trade-off favors simplicity.
    """

    def __init__(self, rag_tool: Any, directory: Path, state_file: Path):
        self._rag_tool = rag_tool
        self._directory = Path(directory)
        self._state_file = Path(state_file)

    def _current_files(self) -> list[Path]:
        if not self._directory.is_dir():
            return []
        return sorted(
            p
            for p in self._directory.rglob("*")
            if p.is_file() and not p.name.startswith(".") and "__pycache__" not in p.parts
        )

    def _fingerprint(self, files: list[Path]) -> str:
        digest = hashlib.sha256()
        for path in files:
            digest.update(path.relative_to(self._directory).as_posix().encode("utf-8"))
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        return digest.hexdigest()

    def _load_last_fingerprint(self) -> str | None:
        try:
            data = json.loads(self._state_file.read_text())
            return data.get("fingerprint")
        except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
            return None

    def _save_fingerprint(self, fingerprint: str, file_count: int) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps({"fingerprint": fingerprint, "file_count": file_count}))

    def _clear_collection(self) -> None:
        """Best-effort wipe of the existing collection before a rebuild.

        RagTool's public Adapter interface only exposes add()/query(), not
        delete(), so this reaches into a private client attribute to call
        the (public, stable) delete_collection() method. If that internal
        path ever breaks in a future crewai_tools version, we log a warning
        and continue — re-adding is a safe upsert for unchanged files, so
        the worst case is a few harmless orphaned chunks for removed files,
        not a crash.
        """
        try:
            client = self._rag_tool.adapter._client
            collection_name = self._rag_tool.collection_name
            client.delete_collection(collection_name=collection_name)
            client.get_or_create_collection(collection_name=collection_name)
        except Exception:
            logger.warning(
                "Could not clear the existing RAG collection before rebuild; "
                "re-adding current files on top of it instead.",
                exc_info=True,
            )

    def list_files(self) -> list[str]:
        """Names of documents currently on disk — no vector store access, so
        this is safe to call on every UI render even if Ollama is down."""
        return [f.relative_to(self._directory).as_posix() for f in self._current_files()]

    def sync(self, force: bool = False) -> SyncResult:
        """Rebuild the vector collection if the directory has changed.

        Args:
            force: rebuild unconditionally, even if the fingerprint matches
                the last synced state (used by a manual "resync" action).
        """
        files = self._current_files()
        fingerprint = self._fingerprint(files)
        file_names = [f.relative_to(self._directory).as_posix() for f in files]

        if not force and fingerprint == self._load_last_fingerprint():
            return SyncResult(changed=False, file_count=len(files), files=file_names)

        self._clear_collection()
        if files:
            self._rag_tool.add(data_type="directory", path=str(self._directory))
        self._save_fingerprint(fingerprint, len(files))
        return SyncResult(changed=True, file_count=len(files), files=file_names)
