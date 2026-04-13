"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs

WIDTH = 60


def main() -> None:
    """Load the catalog, run the recommender, and print a formatted top-k list."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # ── USER PROFILE ──────────────────────────────────────────────────────────
    # pop/happy listener who wants upbeat, non-acoustic energy
    user_prefs = {
        "genre":          "pop",
        "mood":           "happy",
        "energy":         0.80,
        "likes_acoustic": False,
    }
    # ─────────────────────────────────────────────────────────────────────────

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print()
    print("─" * WIDTH)
    print(f"  Top {len(recommendations)} recommendations")
    print(f"  Profile: genre={user_prefs['genre']} | mood={user_prefs['mood']} "
          f"| energy={user_prefs['energy']} | acoustic={user_prefs['likes_acoustic']}")
    print("─" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.3f} / 4.5")
        for reason in explanation.split("; "):
            print(f"       • {reason}")

    print()
    print("─" * WIDTH)


if __name__ == "__main__":
    main()
