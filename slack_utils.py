import re


def clean_mention_text(text: str) -> str:
    return re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()
