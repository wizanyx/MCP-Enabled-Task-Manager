from types import SimpleNamespace

import server


def test_add_new_task_returns_created_id_and_logs(monkeypatch, caplog):
    captured = {}

    def fake_add_task(title, description):
        captured["title"] = title
        captured["description"] = description
        return SimpleNamespace(id="task-123")

    monkeypatch.setattr(server.controller, "add_task", fake_add_task)

    with caplog.at_level("INFO", logger="mcp-todo"):
        result = server.add_new_task("Write docs", "MCP tests")

    assert result == "Task created with ID: task-123"
    assert captured == {"title": "Write docs", "description": "MCP tests"}
    assert "Tool called: add_new_task(title = 'Write docs')" in caplog.text


def test_get_task_by_id_success(monkeypatch):
    task = SimpleNamespace(title="Demo", status="pending", description="Details")
    monkeypatch.setattr(server.controller, "get_task", lambda _task_id: task)

    result = server.get_task_by_id("abc")

    assert result == "Task: Demo\nStatus: pending\nDescription: Details"


def test_get_task_by_id_not_found(monkeypatch):
    monkeypatch.setattr(server.controller, "get_task", lambda _task_id: None)

    result = server.get_task_by_id("missing")

    assert result == "Error: Task with ID missing not found."


def test_get_all_tasks_no_results(monkeypatch):
    monkeypatch.setattr(server.controller, "get_tasks", lambda status=None: [])

    result = server.get_all_tasks()

    assert result == "No tasks found"


def test_get_all_tasks_formats_pending_and_completed(monkeypatch):
    tasks = [
        SimpleNamespace(id="1", title="One", status="pending", description="A"),
        SimpleNamespace(id="2", title="Two", status="completed", description="B"),
    ]

    monkeypatch.setattr(server.controller, "get_tasks", lambda status=None: tasks)

    result = server.get_all_tasks(status_filter="pending")

    assert result.startswith("Current Tasks:\n")
    assert "- [⏳] One (ID: 1)\n  A\n" in result
    assert "- [✅] Two (ID: 2)\n  B\n" in result


def test_complete_task_success_and_not_found(monkeypatch):
    monkeypatch.setattr(
        server.controller,
        "update_task",
        lambda task_id, status=None, title=None, description=None: (
            SimpleNamespace(title="Ship it") if task_id == "ok" else None
        ),
    )

    success = server.complete_task("ok")
    not_found = server.complete_task("missing")

    assert success == "Task 'Ship it' marked as completed"
    assert not_found == "Error: Task with ID missing not found."


def test_update_task_success_and_not_found(monkeypatch):
    monkeypatch.setattr(
        server.controller,
        "update_task",
        lambda task_id, title=None, description=None, status=None: (
            SimpleNamespace(id="abc") if task_id == "abc" else None
        ),
    )

    success = server.update_task("abc", title="New")
    not_found = server.update_task("missing", description="x")

    assert success == "Task 'abc' updated successfully."
    assert not_found == "Error: Task with ID missing not found."


def test_remove_task_success_and_not_found(monkeypatch):
    monkeypatch.setattr(
        server.controller, "delete_task", lambda task_id: task_id == "ok"
    )

    success = server.remove_task("ok")
    not_found = server.remove_task("missing")

    assert success == "Task successfully deleted"
    assert not_found == "Error: Task with ID missing not found"


def test_clear_completed_tasks_returns_count(monkeypatch):
    monkeypatch.setattr(server.controller, "clear_completed", lambda: 3)

    result = server.clear_completed_tasks()

    assert result == "Removed 3 completed task(s)."
