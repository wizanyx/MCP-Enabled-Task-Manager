# MCP-Enabled Task Manager

Basic JSON-based back-end service with MCP integration for CS 230.

## Setup
This project has been designed for MCP with any AI agents, but it has only been tested with Claude.
Use the commands below to set up the project. 

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Project Architecture
The program uses a Task class and stores them in list of Tasks. Each task has a unique ID and contains information such as the title and description of the task and when it was created.
The program stores tasks in a JSON database using a FastMCP server, where tasks can be accessed or updated. The server protects against corrupted or empty database files and includes logging.
Since the program uses FastMCP it is also designed to be used by LLMs.

The user can create a new task, get information about a specific task, see the list of current tasks, remove a task, update an individual task, and also clear all completed tasks from the list of tasks.


## MCP Tools

The application exposes the backend logic to LLMs via the following Model Context Protocol tools. Each tool is decorated with `@mcp.tool()` and includes metadata to help the AI understand when and how to use it.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `add_new_task` | `title`, `description` | Creates a new task and assigns a unique UUID. |
| `get_all_tasks` | `status` (optional) | Returns a list of tasks, optionally filtered by 'pending' or 'completed'. |
| `complete_task` | `task_id` | Marks a specific task as completed using its unique ID string. |
| `remove_task` | `task_id` | Permanently deletes a task from the JSON database. |
| `clear_completed`| None | Removes all tasks currently marked as 'completed' to clean the list. |


## 🔧 Claude Desktop Integration

To use this service with Claude Desktop, you must point the client to your project's Python environment. 

1. Locate your configuration file:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add this project to the `mcpServers` object:

```json
{
  "mcpServers": {
    "mcp-task-manager": {
      "command": "/path/to/your/project/.venv/bin/python",
      "args": [
        "/path/to/your/project/server.py"
      ]
    }
  }
}
