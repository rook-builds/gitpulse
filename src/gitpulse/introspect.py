"""Agent-CLI introspection: `gitpulse introspect` and `gitpulse skill`.

Lets any AI agent discover how to drive this tool without a human in the loop.
"""
import json

from . import __version__


def get_introspect_json() -> str:
    return json.dumps(
        {
            "name": "gitpulse",
            "version": __version__,
            "description": "Git repository health analyzer — commit velocity, hot files, author stats, activity patterns",
            "commands": [
                {
                    "usage": "gitpulse [TARGET] --limit N --output text|json|table|csv",
                    "description": "Git repository health analyzer — commit velocity, hot files, author stats, activity patterns",
                }
            ],
        },
        indent=2,
    )


def get_skill_md() -> str:
    return (
        "# gitpulse\n\n"
        "Git repository health analyzer — commit velocity, hot files, author stats, activity patterns\n\n"
        "## Usage\n\n"
        "```\n"
        "gitpulse [TARGET] --limit 10 --output json\n"
        "```\n\n"
        "Outputs: text (default), json, table, csv.\n"
    )
