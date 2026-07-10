from pathlib import Path

from openai import OpenAI

from config import settings
from tools import TOOL_DEFINITIONS, call_tool


APP_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT = (APP_DIR / "prompts" / "system.md").read_text(encoding="utf-8")


class SlackAgent:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)

    def run(self, user_text: str, slack_context: dict[str, str] | None = None) -> str:
        if not settings.openai_api_key:
            return "OpenAI is not configured yet. Add `OPENAI_API_KEY` to your environment and restart the app."

        context = slack_context or {}
        input_items = [
            {
                "role": "developer",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    f"Slack context: channel={context.get('channel', 'unknown')}, "
                    f"thread_ts={context.get('thread_ts', 'none')}\n\n"
                    f"User message: {user_text}"
                ),
            },
        ]

        response = self.client.responses.create(
            model=settings.openai_model,
            input=input_items,
            tools=TOOL_DEFINITIONS,
        )

        for _ in range(5):
            tool_outputs = []
            for item in response.output:
                if item.type != "function_call":
                    continue
                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": call_tool(item.name, item.arguments),
                    }
                )

            if not tool_outputs:
                return response.output_text or "I ran, but did not get any text back."

            response = self.client.responses.create(
                model=settings.openai_model,
                input=tool_outputs,
                previous_response_id=response.id,
                tools=TOOL_DEFINITIONS,
            )

        return "I hit the tool-call limit for this demo. Try asking a narrower question."
