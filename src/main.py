"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # ── USER PROFILE ──────────────────────────────────────────────────────────
    # This taste profile represents a listener who wants quiet, acoustic,
    # low-energy background music for studying or winding down.
    #
    # Design decisions:
    #   genre="lofi"        → targets the lofi cluster in the catalog
    #   mood="chill"        → rewards calm, relaxed-feeling songs
    #   energy=0.38         → close to the lofi average in songs.csv (0.35–0.42)
    #   likes_acoustic=True → penalizes electronic/produced sound (acousticness→1.0)
    #
    # Critique question: Does this profile clearly separate "intense rock" from
    # "chill lofi", or is it too narrow to be useful across the full 20-song catalog?
    # See src/profile_critique.py for the full scored breakdown.
    user_prefs = {
        "genre":          "lofi",
        "mood":           "chill",
        "energy":         0.38,
        "likes_acoustic": True,
    }
    # ─────────────────────────────────────────────────────────────────────────

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for song, score, explanation in recommendations:
        print(f"{song['title']} by {song['artist']}  —  Score: {score:.3f}")
        print(f"  Why: {explanation}")
        print()


if __name__ == "__main__":
    main()
