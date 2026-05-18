import os
import random
from datetime import datetime, timezone


QUOTES = [
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("The best way to predict the future is to implement it.", "David Heinemeier Hansson"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("Simplicity is the soul of efficiency.", "Austin Freeman"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("It's not a bug — it's an undocumented feature.", "Unknown"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In open source, we feel strongly that to really do something well, you have to get a lot of people involved.", "Linus Torvalds"),
    ("Software is like sex: it's better when it's free.", "Linus Torvalds"),
    ("Bad programmers worry about the code. Good programmers worry about data structures and their relationships.", "Linus Torvalds"),
    ("I will not lie to you, I am a huge nerd.", "Richard Stallman"),
]


def progress_bar():
    now = datetime.now(timezone.utc)
    start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    total = (end - start).total_seconds()
    elapsed = (now - start).total_seconds()
    pct = elapsed / total
    filled = int(pct * 30)
    bar = "█" * filled + "░" * (30 - filled)
    return bar, round(pct * 100, 1)


def uptime():
    # Fake uptime based on days since account creation (approximate)
    created = datetime(2024, 4, 26, tzinfo=timezone.utc)
    days = (datetime.now(timezone.utc) - created).days
    return f"{days} days"


def generate():
    quote, author = random.choice(QUOTES)
    bar, pct = progress_bar()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    template = open("README.md.template", "r", encoding="utf-8").read()
    out = template.replace("{{progress_bar}}", bar)
    out = out.replace("{{progress_percent}}", str(pct))
    out = out.replace("{{quote}}", quote)
    out = out.replace("{{quote_author}}", author)
    out = out.replace("{{last_updated}}", now)
    out = out.replace("{{uptime}}", uptime())

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(out)


if __name__ == "__main__":
    generate()
