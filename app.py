import logging
import uvicorn
from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from agent import SlackAgent
from config import settings
from slack_utils import clean_mention_text


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bolt_app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)
handler = SlackRequestHandler(bolt_app)
api = FastAPI(title="Slack Agent Demo")
agent = SlackAgent()


@api.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "slack-agent-demo"}


@api.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)


@bolt_app.event("app_mention")
def handle_app_mention(event, client, logger):
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event["ts"]
    prompt = clean_mention_text(event.get("text", ""))

    if not prompt:
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text="Ask me about a GitHub repo, weather, or the demo travel file.",
        )
        return

    placeholder = client.chat_postMessage(
        channel=channel,
        thread_ts=thread_ts,
        text="Checking that for you...",
    )

    try:
        answer = agent.run(
            prompt,
            {
                "channel": channel,
                "thread_ts": thread_ts,
                "user": event.get("user", "unknown"),
            },
        )
        client.chat_update(channel=channel, ts=placeholder["ts"], text=answer)
    except Exception:
        logger.exception("Agent failed")
        client.chat_update(
            channel=channel,
            ts=placeholder["ts"],
            text="I hit an error while handling that. Check the app logs for details.",
        )


@bolt_app.event("message")
def handle_direct_message_events(event, client):
    if event.get("channel_type") != "im" or event.get("bot_id"):
        return

    prompt = event.get("text", "").strip()
    if not prompt:
        return

    thread_ts = event.get("thread_ts") or event["ts"]
    answer = agent.run(prompt, {"channel": event["channel"], "thread_ts": thread_ts})
    client.chat_postMessage(channel=event["channel"], thread_ts=thread_ts, text=answer)


if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=settings.port)
