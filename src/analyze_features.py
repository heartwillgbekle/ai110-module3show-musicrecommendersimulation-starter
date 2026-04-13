"""
Feature analysis script: Ask Claude to evaluate which song attributes
from songs.csv are most effective for a content-based music recommender.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 src/analyze_features.py
"""

import anthropic
import csv
import os

SONGS_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


def load_csv_as_text(path: str) -> str:
    """Read the CSV and return it as a formatted string for the prompt."""
    with open(path, newline="") as f:
        return f.read().strip()


def analyze_features() -> None:
    client = anthropic.Anthropic()

    csv_content = load_csv_as_text(SONGS_CSV_PATH)

    prompt = f"""You are analyzing a song dataset for a classroom music recommender simulation
built in Python. The recommender uses content-based filtering — it scores each song
against a user's taste profile using the song's attributes (no other-user data).

Here is the complete dataset (songs.csv):

```
{csv_content}
```

The columns are:
- id, title, artist — identifiers
- genre   — categorical: pop, lofi, rock, ambient, jazz, synthwave, indie pop
- mood    — categorical: happy, chill, intense, relaxed, focused, moody
- energy  — float 0.0–1.0  (intensity / activity level)
- tempo_bpm — float  (beats per minute, ~60–155 in this set)
- valence — float 0.0–1.0  (musical positiveness / happiness)
- danceability — float 0.0–1.0  (rhythmic regularity and beat strength)
- acousticness — float 0.0–1.0  (acoustic vs electronic sound)

Please answer the following questions:

## Q1 — Feature Effectiveness Ranking
Rank ALL eight features (genre, mood, energy, tempo_bpm, valence, danceability,
acousticness) from most to least effective for a simple content-based recommender
on this 10-song dataset. For each feature, explain why it is or isn't effective,
referencing specific songs from the dataset as evidence.

## Q2 — Defining "Musical Vibe"
Which 3–4 features together best capture what most people mean by a song's
"vibe" — the overall feel or atmosphere? Explain the combination intuitively,
without jargon. Give a concrete example using two contrasting songs from the dataset.

## Q3 — Feature Interactions
Are there any pairs of features that work better TOGETHER than either does alone?
For example, does combining energy + valence tell you more than either individually?
Identify the most powerful combination for this dataset and explain why.

## Q4 — Dataset Gaps and Blind Spots
What musical qualities that matter to real listeners are NOT captured by any
feature in this dataset? Name 2–3 specific things a user might care about
that this recommender would be blind to.

## Q5 — Recommended Scoring Strategy
Given the 10 songs in this exact dataset and a user with these preferences:
  genre=lofi, mood=chill, energy=0.4, likes_acoustic=True
Suggest a simple numerical scoring formula (weights for each feature) and show
the expected top-3 ranked songs from the dataset. Justify your weights.

Keep answers practical and grounded in the actual data values shown above."""

    print("Analyzing songs.csv features with Claude API...\n")
    print("=" * 70)
    print()

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

        final = stream.get_final_message()

    print("\n\n" + "=" * 70)
    print(f"Tokens — input: {final.usage.input_tokens}, "
          f"output: {final.usage.output_tokens}")


if __name__ == "__main__":
    analyze_features()
