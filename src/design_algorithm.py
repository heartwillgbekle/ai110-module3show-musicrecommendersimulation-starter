"""
Algorithm recipe script: Ask Claude to design the scoring and ranking
rules for the Music Recommender Simulation.

This script sends three targeted questions to Claude:
  1. How to score a single song against a user profile (Scoring Rule)
  2. How to choose weights for each feature
  3. Why a Ranking Rule is also needed on top of the Scoring Rule

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 src/design_algorithm.py
"""

import anthropic

# ---------- project context injected into every prompt ----------
PROJECT_CONTEXT = """
You are helping design the scoring algorithm for a Python classroom project:
a content-based music recommender simulation.

SONG attributes (all songs share these fields):
  - genre        : str  — e.g. "lofi", "pop", "rock", "jazz", "ambient"
  - mood         : str  — e.g. "chill", "happy", "intense", "relaxed", "focused", "moody"
  - energy       : float 0.0–1.0   (low = calm, high = intense)
  - tempo_bpm    : float 60–155
  - valence      : float 0.0–1.0   (low = dark, high = positive/happy)
  - danceability : float 0.0–1.0
  - acousticness : float 0.0–1.0   (low = electronic, high = acoustic)

USER PROFILE fields:
  - favorite_genre : str
  - favorite_mood  : str
  - target_energy  : float 0.0–1.0
  - likes_acoustic : bool

The functions to implement are in recommender.py:
  score_song(user_prefs: dict, song: dict) -> (float, list[str])
  recommend_songs(user_prefs, songs, k=5)  -> list[(song, score, explanation)]
"""

QUESTION_1 = """
## Question 1 — Proximity Scoring for Numerical Features

For a numerical feature like `energy` (range 0.0–1.0), I want to reward songs
that are CLOSE to the user's target_energy, not just songs with the highest or
lowest energy.

Please explain and derive a simple math formula for this "proximity score":
  - Show the formula
  - Explain intuitively why it works (what does the output mean at 0, 0.5, 1.0?)
  - Give 3 concrete examples using target_energy=0.4 and these song energy values:
      song A: energy=0.38  (nearly perfect match)
      song B: energy=0.70  (moderate mismatch)
      song C: energy=0.95  (strong mismatch)
  - Extend this to `acousticness` for a user with likes_acoustic=True
    (target_acousticness=1.0) vs likes_acoustic=False (target_acousticness=0.0)
"""

QUESTION_2 = """
## Question 2 — Feature Weights

I have 4 scoring components:
  A. genre_match    (1.0 if genre matches, 0.0 if not)
  B. mood_match     (1.0 if mood matches, 0.0 if not)
  C. energy_score   (proximity formula from Q1)
  D. acoustic_score (proximity formula from Q1)

The final score formula will be:
  score = wA * genre_match + wB * mood_match + wC * energy_score + wD * acoustic_score

Questions:
  1. Should genre_match (wA) be weighted higher than mood_match (wB)? Make the case
     both ways, then recommend which should be higher and why.
  2. Recommend specific numerical weights (wA, wB, wC, wD) that sum to 1.0.
     Justify each weight choice in one sentence.
  3. What happens if we give equal weight (0.25) to all four features? Is that
     better or worse for a music recommender — and why?
"""

QUESTION_3 = """
## Question 3 — Why We Need Both a Scoring Rule AND a Ranking Rule

In the recommender.py file I have two functions:
  - score_song(user_prefs, song)          → scores ONE song
  - recommend_songs(user_prefs, songs, k) → returns the TOP K songs

Explain clearly:
  1. What is the Scoring Rule's job? What does it take in and return?
  2. What is the Ranking Rule's job? What does it take in and return?
  3. Why can't we just combine them into one function?
     Give a concrete example of why keeping them separate is useful.
  4. In Python pseudocode (no imports, just plain logic), show how
     recommend_songs() would call score_song() internally to produce
     a ranked list of the top K songs.

Keep the explanation accessible to a student learning Python for the first time.
"""


def ask_claude(question_text: str, question_label: str) -> None:
    client = anthropic.Anthropic()

    full_prompt = PROJECT_CONTEXT + "\n\n" + question_text

    print(f"\n{'=' * 70}")
    print(f"  {question_label}")
    print(f"{'=' * 70}\n")

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": full_prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

        final = stream.get_final_message()

    print(f"\n\n[tokens: in={final.usage.input_tokens} out={final.usage.output_tokens}]")


def main() -> None:
    print("Designing the Algorithm Recipe with Claude API...")
    ask_claude(QUESTION_1, "QUESTION 1 — Proximity Scoring for Numerical Features")
    ask_claude(QUESTION_2, "QUESTION 2 — Feature Weights")
    ask_claude(QUESTION_3, "QUESTION 3 — Scoring Rule vs Ranking Rule")


if __name__ == "__main__":
    main()
