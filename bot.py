import os
import random
import time

import praw


def get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_reddit_client() -> praw.Reddit:
    reddit = praw.Reddit(
        client_id=get_env("REDDIT_CLIENT_ID", required=True),
        client_secret=get_env("REDDIT_CLIENT_SECRET", required=True),
        username=get_env("REDDIT_USERNAME", required=True),
        password=get_env("REDDIT_PASSWORD", required=True),
        user_agent=get_env(
            "REDDIT_USER_AGENT",
            "phaws-reddit-bot/0.1 by u/{}".format(get_env("REDDIT_USERNAME", "")),
        ),
    )
    # Sanity check – throws if credentials are wrong
    _ = reddit.user.me()
    return reddit


def get_target_subreddits() -> list[str]:
    raw = os.environ.get(
        "REDDIT_TARGET_SUBREDDITS",
        "Artificial,LocalLLaMA,MachineLearning,ChatGPT,DataIsBeautiful",
    )
    return [s.strip() for s in raw.split(",") if s.strip()]


def build_content_queue() -> list[dict]:
    return [
        {
            "title": "What are your favorite underrated AI research directions right now?",
            "selftext": (
                "Everyone talks about ever-bigger LLMs, but I'm curious about the "
                "more niche or overlooked areas.\n\n"
                "What are you working on or quietly bullish on that almost nobody "
                "else around you is talking about?"
            ),
        },
        {
            "title": "Show me your most practical AI workflow that saves you real hours",
            "selftext": (
                "Not demos, not hype — the boring-but-powerful stuff.\n\n"
                "What AI workflow actually saves you hours every week, and how "
                "did you wire it together?"
            ),
        },
        {
            "title": "LLMs as teammates, not tools: how are you structuring that?",
            "selftext": (
                "If you treat models as persistent collaborators, not just chat boxes, "
                "how are you setting up memory, task queues, and guardrails right now?"
            ),
        },
    ]


def choose_post_payload() -> dict:
    queue = build_content_queue()
    choice = random.choice(queue)
    suffix = os.environ.get("PHAWS_EXPERIMENT_TAG", "").strip()
    if suffix:
        choice = choice.copy()
        choice["title"] = f"{choice['title']} [{suffix}]"
    return choice


def submit_post(reddit: praw.Reddit) -> None:
    subreddits = get_target_subreddits()
    subreddit_name = random.choice(subreddits)
    subreddit = reddit.subreddit(subreddit_name)

    payload = choose_post_payload()
    title = payload["title"]
    url = payload.get("url")
    selftext = payload.get("selftext")

    print(f"[bot] Target subreddit: r/{subreddit_name}")
    print(f"[bot] Title: {title!r}")

    if url and selftext:
        submission = subreddit.submit(title=title, url=url)
    elif url:
        submission = subreddit.submit(title=title, url=url)
    else:
        submission = subreddit.submit(title=title, selftext=selftext or "")

    print(f"[bot] Submitted post: https://reddit.com{submission.permalink}")


def main() -> None:
    print("[bot] Starting Phaws Reddit bot run...")
    try:
        reddit = build_reddit_client()
    except Exception as e:
        print(f"[bot] ERROR during Reddit auth: {e}")
        raise

    submit_post(reddit)
    print("[bot] Done.")


if __name__ == "__main__":
    time.sleep(2)
    main()
