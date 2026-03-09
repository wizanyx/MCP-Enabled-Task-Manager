# MCP-Enabled Task Manager

A JSON-backed task management service built with [FastMCP](https://github.com/jlowin/fastmcp), designed to be consumed by LLM agents via the Model Context Protocol. Built for CS 230.

## Table of Contents

- [Project Architecture](#project-architecture)
- [Setup](#setup)
- [MCP Tools](#mcp-tools)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Example Usage](#example-usage)

## Project Architecture

The application is organized into four distinct layers:

**`models.py`** — Defines the `Task` data model using Pydantic. Each task carries a UUID, a title, an optional description, a status (`pending` or `completed`), and a UTC creation timestamp. Field-level descriptions are included to guide LLM tool usage.

**`storage.py`** — Handles all file I/O against a JSON database located at `data/tasks.json`. Key behaviors include:

- Auto-initialization of the database file if it does not exist
- Atomic writes via a temporary file and `os.replace` to prevent corruption on crash
- Automatic quarantine of corrupt database files — a timestamped backup is created and a fresh empty database is initialized in its place

**`controller.py`** — Implements the core business logic as plain functions that accept an optional `file_path` parameter. This design decouples the logic from the filesystem, making the controller fully testable in isolation.

**`server.py`** — Exposes the controller functions as MCP tools using the `@mcp.tool()` decorator. Each tool returns a plain string that is easy for an LLM to parse and act on.

```
.
├── controller.py          # Business logic
├── models.py              # Task data model
├── server.py              # MCP tool definitions
├── storage.py             # JSON persistence layer
├── data/
│   └── tasks.json         # Runtime database (auto-created, git-ignored)
├── scripts/
│   └── generate_config.py # Prints Claude Desktop config for this project
└── tests/
    ├── test_server.py
    ├── test_storage.py
    └── test_task_manager.py
```

## Setup

Requires Python 3.10 or later.

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (includes pytest)
pip install -r requirements-dev.txt
```

To run the test suite:

```bash
pytest
```

## MCP Tools

The following tools are registered on the MCP server and available to any compatible LLM agent.

| Tool                    | Parameters                                              | Description                                                         |
| :---------------------- | :------------------------------------------------------ | :------------------------------------------------------------------ |
| `add_new_task`          | `title`, `description` (optional)                       | Creates a new task and returns its assigned UUID.                   |
| `get_task_by_id`        | `task_id`                                               | Retrieves full details for a single task by its UUID.               |
| `get_all_tasks`         | `status_filter` (optional)                              | Returns all tasks, optionally filtered by `pending` or `completed`. |
| `complete_task`         | `task_id`                                               | Marks a task as completed.                                          |
| `update_task`           | `task_id`, `title` (optional), `description` (optional) | Updates the title or description of an existing task.               |
| `remove_task`           | `task_id`                                               | Permanently deletes a task.                                         |
| `clear_completed_tasks` | —                                                       | Removes all tasks currently marked as `completed`.                  |

## Claude Desktop Integration

To connect this service to Claude Desktop, you need to register it in the Claude Desktop configuration file.

**Step 1 — Generate the configuration entry**

Run the following script from the project root. It will print a correctly formatted JSON snippet using your current Python environment and the absolute path to `server.py`:

```bash
python scripts/generate_config.py
```

**Step 2 — Add it to your Claude Desktop config**

Open the Claude Desktop configuration file for your platform:

| Platform | Path                                                              |
| :------- | :---------------------------------------------------------------- |
| macOS    | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows  | `%APPDATA%\Claude\claude_desktop_config.json`                     |

Merge the printed output into the `mcpServers` object. If the file does not exist yet, create it. The final file should look like this:

```json
{
    "mcpServers": {
        "todo-manager": {
            "command": "/path/to/your/project/.venv/bin/python",
            "args": ["/path/to/your/project/server.py"]
        }
    }
}
```

**Step 3 — Restart Claude Desktop**

Fully quit and relaunch Claude Desktop. The Task Manager tools will appear in the tool picker when starting a new conversation.

## Example Usage

Once the server is connected, you can interact with your task list through natural language. Claude will invoke the appropriate MCP tools automatically.

> **"Add a task to review the pull request for the auth module."**

Claude calls `add_new_task` and confirms the task was created with its ID.

> **"What tasks do I still have pending?"**

Claude calls `get_all_tasks` with `status_filter = "pending"` and lists the results.

> **"Mark the auth PR review as done."**

Claude calls `get_all_tasks` to locate the task by title, then calls `complete_task` with the corresponding ID.

> **"Clean up my completed tasks."**

Claude calls `clear_completed_tasks` and reports how many tasks were removed.
