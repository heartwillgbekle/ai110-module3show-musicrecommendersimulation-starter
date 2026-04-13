"""
Research script: How streaming platforms predict music preferences.

Sends a structured prompt to Claude covering:
  - Collaborative filtering (other users' behavior)
  - Content-based filtering (song attributes)
  - Key data types: likes, skips, tempo, mood, energy, etc.
  - Direct comparison of the two approaches

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 src/research_recommender.py
"""

import anthropic

PROMPT = """
You are an expert in music recommendation systems and machine learning.

I am building a Python music recommender for a classroom project that uses
content-based filtering. To understand the broader landscape, I need a clear
research summary on how major streaming platforms (Spotify, YouTube Music,
Apple Music) predict what users will love next.

Please structure your answer around these four sections:

─────────────────────────────────────────────────────────────────────────
SECTION 1 — COLLABORATIVE FILTERING  (using other users' behavior)
─────────────────────────────────────────────────────────────────────────
Explain this approach as if teaching a beginner:
• What is the core idea? (no math needed, just the logic)
• What raw data does it collect from users to find "people like you"?
  List at least 5 specific data signals with a one-line description each.
• Walk through a concrete micro-example:
    "User A and User B both skipped Song X and replayed Song Y.
     Therefore the system predicts..."
• What is the cold-start problem and why does it hurt collaborative filtering?
• One real-world strength and one real-world weakness.

─────────────────────────────────────────────────────────────────────────
SECTION 2 — CONTENT-BASED FILTERING  (using song attributes)
─────────────────────────────────────────────────────────────────────────
Explain this approach as if teaching a beginner:
• What is the core idea? (how does it build a "taste profile" for a user?)
• List at least 6 song attribute features used in real systems, organized into:
    - Audio features  (things extracted from the sound wave itself)
    - Metadata        (labels, tags, human-curated info)
  For each feature name its data type (number, category, boolean) and its range.
• Walk through a concrete micro-example:
    "The user liked three songs with high energy and low acousticness.
     Therefore the system predicts..."
• How does it handle new songs vs new users differently from collaborative?
• One real-world strength and one real-world weakness.

─────────────────────────────────────────────────────────────────────────
SECTION 3 — SIDE-BY-SIDE COMPARISON TABLE
─────────────────────────────────────────────────────────────────────────
Create a clear comparison table with these rows:
  • Primary input data
  • Data type of that input (behavior signals vs audio/metadata)
  • Cold-start: new user
  • Cold-start: new song
  • Recommendation diversity
  • Explainability ("why was this recommended?")
  • Best suited for...

─────────────────────────────────────────────────────────────────────────
SECTION 4 — COMPLETE DATA TYPE INVENTORY
─────────────────────────────────────────────────────────────────────────
Provide a definitive list of every important data type in music recommender
systems, split into two clearly labeled groups:

GROUP A — User Behavior Signals
  Include: name | signal type (explicit/implicit) | what it tells the system
  Cover at minimum: likes, dislikes, skips, replays, playlist adds,
  listening duration, saves/downloads, search queries, share actions,
  listening context (time of day, device), shuffle on/off

GROUP B — Song Attribute Features
  Include: feature name | data type | typical range | what it captures
  Cover at minimum: tempo_bpm, energy, valence, danceability, acousticness,
  mood, genre, key, loudness, speechiness, instrumentalness, liveness

End with one paragraph connecting these data types back to real Spotify
features (Discover Weekly, Daily Mix, Radio) — which data types power which
feature?
"""


def research_recommendation_systems() -> None:
    client = anthropic.Anthropic()

    print("Querying Claude on music recommendation systems...\n")
    print("=" * 70)
    print()

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": PROMPT}],
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
    research_recommendation_systems()
