from typing import Literal

from mcp.server.fastmcp import FastMCP
import controller
import logging

# Initialize FastMCP server
# The name "TaskManager" is what will show up in the LLM UI
mcp = FastMCP("Task Manager")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-todo")


@mcp.tool()
def add_new_task(title: str, description: str = "") -> str:
    """Add a new task to the to do list"""
    logger.info(f"Tool called: add_new_task(title = '{title}')")
    task = controller.add_task(title, description)
    return f"Task created with ID: {task.id}"


@mcp.tool()
def get_task_by_id(task_id: str) -> str:
    """Retrieve a single task by its ID."""
    logger.info(f"Tool called: get_task_by_id(id = '{task_id}')")
    task = controller.get_task(task_id)
    if task:
        return f"Task: {task.title}\nStatus: {task.status}\nDescription: {task.description}"
    return f"Error: Task with ID {task_id} not found."


@mcp.tool()
def get_all_tasks(status_filter: Literal["pending", "completed"] | None = None) -> str:
    """
    List tasks from the database.
    Optional status filter: 'pending' or 'completed'
    """
    logger.info(f"Tool called: get_all_tasks(status_filter = '{status_filter}')")
    tasks = controller.get_tasks(status=status_filter)
    if not tasks:
        return "No tasks found"

    # Format the list for the LLM to read easily
    output = "Current Tasks:\n"
    for t in tasks:
        status_icon = "✅" if t.status == "completed" else "⏳"
        output += f"- [{status_icon}] {t.title} (ID: {t.id})\n  {t.description}\n"
    return output


@mcp.tool()
def complete_task(task_id: str) -> str:
    """Mark a specific task as completed using its ID."""
    logger.info(f"Tool called: complete_task(id = '{task_id}')")
    task = controller.update_task(task_id, status="completed")
    if task:
        return f"Task '{task.title}' marked as completed"
    return f"Error: Task with ID {task_id} not found."


@mcp.tool()
def update_task(
    task_id: str, title: str | None = None, description: str | None = None
) -> str:
    """Update the title or description of an existing task."""
    logger.info(f"Tool called: update_task(id='{task_id}')")
    task = controller.update_task(task_id, title=title, description=description)
    if task:
        return f"Task '{task.id}' updated successfully."
    return f"Error: Task with ID {task_id} not found."


@mcp.tool()
def remove_task(task_id: str) -> str:
    """Delete a task from the list permanently."""
    logger.info(f"Tool called: remove_task(id='{task_id}')")
    success = controller.delete_task(task_id)
    if success:
        return "Task successfully deleted"
    return f"Error: Task with ID {task_id} not found"


@mcp.tool()
def clear_completed_tasks() -> str:
    """Remove all completed tasks from the list."""
    logger.info("Tool called: clear_completed_tasks()")
    count = controller.clear_completed()
    return f"Removed {count} completed task(s)."


if __name__ == "__main__":
    logger.info("Server start: Task Manager MCP server is starting")
    mcp.run()
