"""
Music Recommender Simulation — CLI runner.

Demonstrates three challenges:
  1. Advanced features  — 5 new song attributes scored in every run
  2. Scoring modes      — genre_first / mood_first / energy_focused
  3. Diversity re-rank  — artist/genre penalty via diversity=True
  4. Tabulate output    — formatted ASCII tables for every result set
"""

from recommender import load_songs, recommend_songs, SCORING_MODES, ScoreWeights
from tabulate import tabulate

# ── USER PROFILES ─────────────────────────────────────────────────────────────
# Each profile now includes the five new preference fields:
#   target_popularity  — 0-100; matches against song's popularity score
#   preferred_decade   — 1990/2000/2010/2020; binary era bonus
#   wants_instrumental — True rewards high instrumentalness, False rewards vocals
PROFILES = [
    {
        "label": "High-Energy Pop",
        "prefs": {
            "genre": "pop", "mood": "happy",
            "energy": 0.90, "likes_acoustic": False,
            "target_popularity": 80, "preferred_decade": 2020,
            "wants_instrumental": False,
        },
    },
    {
        "label": "Chill Lofi",
        "prefs": {
            "genre": "lofi", "mood": "chill",
            "energy": 0.38, "likes_acoustic": True,
            "target_popularity": 45, "preferred_decade": 2020,
            "wants_instrumental": True,
        },
    },
    {
        "label": "Deep Intense Rock",
        "prefs": {
            "genre": "rock", "mood": "intense",
            "energy": 0.92, "likes_acoustic": False,
            "target_popularity": 60, "preferred_decade": 2010,
            "wants_instrumental": False,
        },
    },
    {
        "label": "Adversarial: High-Energy + Sad",
        "prefs": {
            "genre": "blues", "mood": "sad",
            "energy": 0.90, "likes_acoustic": False,
            "target_popularity": 30, "preferred_decade": 2000,
            "wants_instrumental": False,
        },
    },
    {
        "label": "Adversarial: Max Energy + Acoustic",
        "prefs": {
            "genre": "folk", "mood": "nostalgic",
            "energy": 1.0, "likes_acoustic": True,
            "target_popularity": 35, "preferred_decade": 2010,
            "wants_instrumental": False,
        },
    },
]


def print_results(
    label: str,
    recommendations: list,
    mode: str,
    weights: ScoreWeights,
    diversity: bool = False,
) -> None:
    """Print a tabulate table + per-song reason breakdown for one result set."""
    max_pts = weights.max_score
    tag = f"[{mode}{'  diversity' if diversity else ''}]"
    print(f"\n{'═' * 68}")
    print(f"  {label}  {tag}  (max {max_pts:.2f} pts)")
    print(f"{'═' * 68}")

    # Summary table: one row per recommended song
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        top_reason = explanation.split("; ")[0]
        rows.append([
            f"#{rank}",
            song["title"],
            song["artist"],
            f"{score:.3f} / {max_pts:.2f}",
            top_reason,
        ])

    print(tabulate(
        rows,
        headers=["Rank", "Title", "Artist", "Score", "Top Signal"],
        tablefmt="simple",
        colalign=("left", "left", "left", "right", "left"),
    ))

    # Full reason breakdown below the table
    print()
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"  #{rank} {song['title']}")
        for reason in explanation.split("; "):
            print(f"      • {reason}")


def main() -> None:
    """Load catalog and run all demo sections."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # ── SECTION 1: All profiles with default mode ──────────────────────────
    print(f"\n\n{'━' * 68}")
    print("  SECTION 1 — All profiles  (genre_first mode)")
    print(f"{'━' * 68}")
    for profile in PROFILES:
        recs = recommend_songs(profile["prefs"], songs, k=5, mode="genre_first")
        print_results(profile["label"], recs, "genre_first", SCORING_MODES["genre_first"])

    # ── SECTION 2: Mode comparison on Chill Lofi ───────────────────────────
    chill = next(p for p in PROFILES if p["label"] == "Chill Lofi")
    print(f"\n\n{'━' * 68}")
    print("  SECTION 2 — Mode comparison  (Chill Lofi)")
    print(f"{'━' * 68}")
    for mode_name, mode_weights in SCORING_MODES.items():
        recs = recommend_songs(chill["prefs"], songs, k=5, mode=mode_name)
        print_results(chill["label"], recs, mode_name, mode_weights)

    # ── SECTION 3: Diversity demo on Chill Lofi ───────────────────────────
    # LoRoom appears twice in the top-3 (Midnight Coding + Focus Flow).
    # With diversity=True, Focus Flow takes an artist penalty (-1.5) and a
    # genre penalty (-0.5, lofi already appears twice), dropping it from #3
    # to #4 and letting Spacewalk Thoughts (ambient) move up instead.
    print(f"\n\n{'━' * 68}")
    print("  SECTION 3 — Diversity penalty demo  (Chill Lofi)")
    print(f"{'━' * 68}")
    recs_plain = recommend_songs(chill["prefs"], songs, k=5, mode="genre_first")
    print_results(chill["label"], recs_plain, "genre_first", SCORING_MODES["genre_first"])
    recs_div = recommend_songs(chill["prefs"], songs, k=5, mode="genre_first", diversity=True)
    print_results(chill["label"], recs_div, "genre_first", SCORING_MODES["genre_first"], diversity=True)


if __name__ == "__main__":
    main()
