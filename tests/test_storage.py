import builtins
import json

import pytest

import storage
from models import Task


@pytest.fixture
def storage_db_path(tmp_path):
    return str(tmp_path / "tasks.json")


def test_initialize_db_creates_empty_file(storage_db_path):
    storage.initialize_db(storage_db_path)

    with open(storage_db_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data == []


def test_save_and_load_roundtrip(storage_db_path):
    tasks = [
        Task(title="Task A", description="A"),
        Task(title="Task B", description="B", status="completed"),
    ]

    storage.save_tasks(tasks, storage_db_path)
    loaded = storage.load_tasks(storage_db_path)

    assert len(loaded) == 2
    assert [task.title for task in loaded] == ["Task A", "Task B"]
    assert [task.status for task in loaded] == ["pending", "completed"]


def test_load_tasks_quarantines_invalid_json(storage_db_path):
    with open(storage_db_path, "w", encoding="utf-8") as f:
        f.write("{not-valid-json")

    loaded = storage.load_tasks(storage_db_path)

    assert loaded == []

    with open(storage_db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == []


def test_load_tasks_quarantines_validation_error(storage_db_path):
    invalid_payload = [{"id": "1", "description": "missing title", "status": "pending"}]
    with open(storage_db_path, "w", encoding="utf-8") as f:
        json.dump(invalid_payload, f)

    loaded = storage.load_tasks(storage_db_path)

    assert loaded == []

    with open(storage_db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == []


def test_save_tasks_re_raises_on_write_error(storage_db_path, monkeypatch):
    def raise_on_replace(*_args, **_kwargs):
        raise OSError("disk error")

    monkeypatch.setattr(storage.os, "replace", raise_on_replace)

    with pytest.raises(OSError):
        storage.save_tasks([Task(title="X")], storage_db_path)


def test_quarantine_logs_error_and_leaves_file_intact_when_replace_fails(
    storage_db_path, monkeypatch
):
    with open(storage_db_path, "w", encoding="utf-8") as f:
        f.write("{bad-json")

    def raise_on_replace(*_args, **_kwargs):
        raise OSError("cannot move")

    monkeypatch.setattr(storage.os, "replace", raise_on_replace)

    loaded = storage.load_tasks(storage_db_path)

    assert loaded == []
    with open(storage_db_path, "r", encoding="utf-8") as f:
        assert f.read() == "{bad-json"


def test_load_tasks_handles_filenotfound_during_read(storage_db_path, monkeypatch):
    original_open = builtins.open

    def flaky_open(path, mode="r", *args, **kwargs):
        if path == storage_db_path and mode == "r":
            raise FileNotFoundError
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", flaky_open)

    loaded = storage.load_tasks(storage_db_path)

    assert loaded == []
    assert storage.os.path.exists(storage_db_path)


def test_save_tasks_logs_cleanup_failure_when_temp_remove_fails(
    storage_db_path, monkeypatch
):
    def flaky_replace(src, dst):
        if dst == storage_db_path:
            raise OSError("replace failed")

    def raise_on_remove(*_args, **_kwargs):
        raise OSError("remove failed")

    monkeypatch.setattr(storage.os, "replace", flaky_replace)
    monkeypatch.setattr(storage.os, "remove", raise_on_remove)

    with pytest.raises(OSError):
        storage.save_tasks([Task(title="X")], storage_db_path)
