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


