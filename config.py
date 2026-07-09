import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6")
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_owner: str = os.getenv("GITHUB_OWNER", "")
    github_repos: tuple[str, ...] = tuple(
        repo.strip()
        for repo in os.getenv("GITHUB_REPOS", "").split(",")
        if repo.strip()
    )
    weather_api_key: str = os.getenv("WEATHER_API_KEY", "")
    travel_data_path: str = os.getenv("TRAVEL_DATA_PATH", "demo_travel.json")
    port: int = int(os.getenv("PORT", "8080"))


settings = Settings()
