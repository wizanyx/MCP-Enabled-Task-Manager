import pytest
from pydantic import ValidationError

import controller
from models import Task


@pytest.fixture
def test_db_path(tmp_path):
    return str(tmp_path / "tasks.json")


def test_crud_operations_success(test_db_path):
    created = controller.add_task("Write tests", "Add coverage", file_path=test_db_path)

    fetched = controller.get_task(created.id, file_path=test_db_path)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Write tests"
    assert fetched.status == "pending"

    updated = controller.update_task(
        created.id,
        title="Write integration tests",
        description="Add reliable coverage",
        status="completed",
        file_path=test_db_path,
    )
    assert updated is not None
    assert updated.title == "Write integration tests"
    assert updated.description == "Add reliable coverage"
    assert updated.status == "completed"

    deleted = controller.delete_task(created.id, file_path=test_db_path)
    assert deleted is True
    assert controller.get_task(created.id, file_path=test_db_path) is None


def test_validation_failures_block_malformed_data():
    with pytest.raises(ValidationError):
        Task.model_validate({})

    with pytest.raises(ValidationError):
        Task.model_validate({"title": ""})


def test_delete_from_empty_list_returns_false(test_db_path):
    deleted = controller.delete_task("missing-id", file_path=test_db_path)
    assert deleted is False


def test_clear_completed_on_empty_list_returns_zero(test_db_path):
    removed_count = controller.clear_completed(file_path=test_db_path)
    assert removed_count == 0


def test_get_tasks_with_status_filters(test_db_path):
    pending = controller.add_task("Pending task", file_path=test_db_path)
    completed = controller.add_task("Completed task", file_path=test_db_path)
    controller.update_task(completed.id, status="completed", file_path=test_db_path)

    all_tasks = controller.get_tasks(file_path=test_db_path)
    pending_tasks = controller.get_tasks(status="pending", file_path=test_db_path)
    completed_tasks = controller.get_tasks(status="completed", file_path=test_db_path)

    assert len(all_tasks) == 2
    assert {task.id for task in all_tasks} == {pending.id, completed.id}
    assert len(pending_tasks) == 1
    assert pending_tasks[0].id == pending.id
    assert len(completed_tasks) == 1
    assert completed_tasks[0].id == completed.id


def test_update_task_not_found_returns_none(test_db_path):
    result = controller.update_task("missing-id", title="X", file_path=test_db_path)
    assert result is None


def test_update_task_partial_update_preserves_other_fields(test_db_path):
    created = controller.add_task(
        "Original", "Initial description", file_path=test_db_path
    )

    updated_description = controller.update_task(
        created.id, description="Updated description", file_path=test_db_path
    )
    assert updated_description is not None
    assert updated_description.title == "Original"
    assert updated_description.description == "Updated description"
    assert updated_description.status == "pending"

    updated_title = controller.update_task(
        created.id, title="Renamed", file_path=test_db_path
    )
    assert updated_title is not None
    assert updated_title.title == "Renamed"
    assert updated_title.description == "Updated description"
    assert updated_title.status == "pending"


def test_clear_completed_removes_completed_tasks(test_db_path):
    pending = controller.add_task("Keep me", file_path=test_db_path)
    completed = controller.add_task("Remove me", file_path=test_db_path)
    controller.update_task(completed.id, status="completed", file_path=test_db_path)

    removed_count = controller.clear_completed(file_path=test_db_path)
    remaining = controller.get_tasks(file_path=test_db_path)

    assert removed_count == 1
    assert len(remaining) == 1
    assert remaining[0].id == pending.id


def test_update_and_delete_missing_id_in_non_empty_list(test_db_path):
    existing = controller.add_task("Existing", file_path=test_db_path)

    updated = controller.update_task("missing-id", title="Nope", file_path=test_db_path)
    deleted = controller.delete_task("missing-id", file_path=test_db_path)
    still_there = controller.get_task(existing.id, file_path=test_db_path)

    assert updated is None
    assert deleted is False
    assert still_there is not None
    assert still_there.id == existing.id


def test_update_and_delete_match_on_later_item(test_db_path):
    first = controller.add_task("First", file_path=test_db_path)
    second = controller.add_task("Second", file_path=test_db_path)

    updated_second = controller.update_task(
        second.id, title="Second updated", file_path=test_db_path
    )
    deleted_second = controller.delete_task(second.id, file_path=test_db_path)
    remaining = controller.get_tasks(file_path=test_db_path)

    assert updated_second is not None
    assert updated_second.id == second.id
    assert updated_second.title == "Second updated"
    assert deleted_second is True
    assert len(remaining) == 1
    assert remaining[0].id == first.id


def test_get_task_missing_id_in_non_empty_list_returns_none(test_db_path):
    controller.add_task("Existing", file_path=test_db_path)

    missing = controller.get_task("missing-id", file_path=test_db_path)

    assert missing is None
