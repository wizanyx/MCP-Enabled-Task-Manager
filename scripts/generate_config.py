import json
import sys
from pathlib import Path

config = {
    "mcpServers": {
        "todo-manager": {
            "command": sys.executable,
            "args": [str(Path(__file__).parent.parent / "server.py")],
        }
    }
}
print(json.dumps(config, indent=2))
