import json
from typing import Any, Callable

from tools.github import create_github_issue, summarize_github_activity
from tools.travel import check_demo_travel
from tools.weather import get_weather_forecast


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "summarize_github_activity",
        "description": "Summarize recent GitHub activity for configured repositories.",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "How many days of GitHub activity to inspect.",
                    "minimum": 1,
                    "maximum": 30,
                },
                "repo": {
                    "type": "string",
                    "description": "Optional repository name. If omitted, all configured repositories are summarized.",
                },
            },
            "required": ["days"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "create_github_issue",
        "description": "Create a GitHub issue in a configured repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository name."},
                "title": {"type": "string", "description": "Issue title."},
                "body": {"type": "string", "description": "Issue body."},
            },
            "required": ["repo", "title", "body"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_weather_forecast",
        "description": "Get a simple weather forecast for a US city or 'City, State' location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Location such as 'Denver, CO'."},
                "days": {
                    "type": "integer",
                    "description": "Number of forecast days to return.",
                    "minimum": 1,
                    "maximum": 7,
                },
            },
            "required": ["location", "days"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "check_demo_travel",
        "description": "Read simulated travel-confirmation data from a local JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Optional destination filter, such as 'Denver'.",
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    },
]


TOOL_HANDLERS: dict[str, Callable[..., Any]] = {
    "summarize_github_activity": summarize_github_activity,
    "create_github_issue": create_github_issue,
    "get_weather_forecast": get_weather_forecast,
    "check_demo_travel": check_demo_travel,
}


def call_tool(name: str, arguments_json: str) -> str:
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        arguments = json.loads(arguments_json or "{}")
        result = handler(**arguments)
        return json.dumps(result, default=str)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
