from slack_utils import clean_mention_text


def test_clean_mention_text_removes_slack_app_id() -> None:
    assert clean_mention_text("<@U123ABC> what changed today?") == "what changed today?"


def test_clean_mention_text_handles_plain_text() -> None:
    assert clean_mention_text("hello") == "hello"
