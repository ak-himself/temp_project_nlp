"""Minimal command-line summarizer for the FactIndic baseline."""

import os
import sys

from dotenv import load_dotenv
from groq import Groq


TERMINATION_MARKER = "END"


def read_input() -> str:
    """Read multiline source text until the termination marker is entered."""
    print(f"Enter text to summarize. Type {TERMINATION_MARKER} on its own line when done.")
    lines: list[str] = []
    for line in sys.stdin:
        line = line.rstrip("\n")
        if line == TERMINATION_MARKER:
            break
        lines.append(line)
    return "\n".join(lines).strip()


def summarize(text: str, client: Groq, model: str) -> str:
    """Ask the configured Groq model for a source-grounded summary."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Summarize the user's text concisely. Preserve key facts, "
                    "names, dates, and numbers. Write the summary in the same "
                    "language as the input. Do not add information that is not "
                    "supported by the input."
                ),
            },
            {"role": "user", "content": text},
        ],
        max_completion_tokens=300,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("The model returned an empty summary.")
    return content.strip()


def main() -> int:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")

    if not api_key:
        print("Error: GROQ_API_KEY is missing from .env or the environment.", file=sys.stderr)
        return 1
    if not model:
        print("Error: GROQ_MODEL is missing from .env or the environment.", file=sys.stderr)
        return 1

    text = read_input()
    if not text:
        print("Error: input text is empty. Enter text before typing END.", file=sys.stderr)
        return 1

    client = Groq(api_key=api_key, timeout=30, max_retries=1)
    try:
        print("\nSummary:")
        print(summarize(text, client, model))
    except Exception as exc:
        print(
            f"Error: the Groq API request failed ({type(exc).__name__}).",
            file=sys.stderr,
        )
        return 1
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
