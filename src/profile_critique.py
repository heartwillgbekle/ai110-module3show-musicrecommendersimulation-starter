"""
Inline critique of the user profile defined in main.py.

Runs the scoring formula against all 20 songs and answers:
  1. Does the profile clearly separate "intense rock" from "chill lofi"?
  2. Is the profile too narrow (does it rank non-lofi songs fairly)?
  3. What are the blind spots?

Usage:
    cd <project-root>
    python3 src/profile_critique.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, score_song

SONGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

# ── The profile under review ──────────────────────────────────────────────────
USER_PROFILE = {
    "genre":          "lofi",
    "mood":           "chill",
    "energy":         0.38,
    "likes_acoustic": True,
}
# ─────────────────────────────────────────────────────────────────────────────


def critique() -> None:
    songs = load_songs(SONGS_PATH)
    if not songs:
        print("No songs loaded — check SONGS_PATH.")
        return

    # Score every song
    results = []
    for song in songs:
        score, reasons = score_song(USER_PROFILE, song)
        results.append((score, song, reasons))
    results.sort(key=lambda x: x[0], reverse=True)

    # ── Full ranked table ─────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  PROFILE CRITIQUE — Full Ranked Scores")
    print("  Profile: genre=lofi | mood=chill | energy=0.38 | likes_acoustic=True")
    print("=" * 72)
    print(f"  {'Rank':<5} {'Score':<7} {'Genre':<12} {'Mood':<12} {'E':>5} {'A':>5}  Title")
    print("  " + "-" * 68)

    for rank, (score, song, _) in enumerate(results, 1):
        marker = " ◀" if song["genre"] in ("lofi", "folk", "classical", "blues") else ""
        print(
            f"  {rank:<5} {score:<7.3f} {song['genre']:<12} {song['mood']:<12} "
            f"{float(song['energy']):>5.2f} {float(song['acousticness']):>5.2f}  "
            f"{song['title']}{marker}"
        )

    # ── Critique Question 1: intense rock vs chill lofi ───────────────────────
    print("\n" + "─" * 72)
    print("  CRITIQUE Q1 — Does the profile separate 'intense rock' from 'chill lofi'?")
    print("─" * 72)

    targets = {
        "Storm Runner":  "intense rock",
        "Library Rain":  "chill lofi",
        "Midnight Coding": "chill lofi",
        "Iron Spiral":   "metal (angry)",
        "Morning Prelude": "classical (peaceful)",
    }

    for title, label in targets.items():
        song = next((s for s in songs if s["title"] == title), None)
        if song:
            score, reasons = score_song(USER_PROFILE, song)
            print(f"\n  {title} [{label}]  →  score = {score:.3f}")
            for r in reasons:
                print(f"    • {r}")

    sr_score = next(s for s, song, _ in results if song["title"] == "Storm Runner")
    lr_score = next(s for s, song, _ in results if song["title"] == "Library Rain")
    gap = lr_score - sr_score
    print(f"\n  Separation gap (Library Rain − Storm Runner): {gap:.3f}")
    verdict = "STRONG ✓" if gap >= 0.60 else ("MODERATE ⚠" if gap >= 0.35 else "WEAK ✗")
    print(f"  Verdict: {verdict} — gap of {gap:.2f} out of a maximum possible 1.0")

    # ── Critique Question 2: too narrow? ─────────────────────────────────────
    print("\n" + "─" * 72)
    print("  CRITIQUE Q2 — Is the profile too narrow?")
    print("─" * 72)

    chill_non_lofi = [
        (s, song) for s, song, _ in results
        if song["mood"] in ("chill", "relaxed", "peaceful", "nostalgic")
        and song["genre"] != "lofi"
    ]
    print("\n  Songs with a 'chill-adjacent' mood but non-lofi genre:")
    for score, song in chill_non_lofi:
        print(f"    {song['title']:<28} genre={song['genre']:<12} score={score:.3f}")

    top5_genres = [song["genre"] for _, song, _ in results[:5]]
    unique_in_top5 = len(set(top5_genres))
    print(f"\n  Top-5 recommendations contain {unique_in_top5} unique genre(s): "
          f"{', '.join(set(top5_genres))}")
    if unique_in_top5 == 1:
        print("  ⚠  Profile is narrow — top 5 are all the same genre.")
    elif unique_in_top5 <= 2:
        print("  ⚠  Profile is somewhat narrow — diversity is limited.")
    else:
        print("  ✓  Profile surfaces more than 2 genres in the top 5.")

    # ── Critique Question 3: blind spots ─────────────────────────────────────
    print("\n" + "─" * 72)
    print("  CRITIQUE Q3 — Blind spots in this profile")
    print("─" * 72)
    print("""
  1. GENRE PENALTY IS ABSOLUTE
     Any non-lofi song immediately loses 0.30 points regardless of how well
     it matches on mood, energy, and acousticness.  A perfect (1.0, 1.0, 1.0)
     non-lofi song can score at most 0.70 — tied with a mediocre lofi match.
     Real listeners often enjoy chill folk or jazz the same as chill lofi.

  2. MOOD IS AN EXACT STRING MATCH
     "relaxed" ≠ "chill" in this system even though they feel nearly identical.
     Coffee Shop Stories (jazz, relaxed) loses the full 0.25 mood weight despite
     being the kind of song a chill-lofi fan would almost certainly enjoy.

  3. NO TEMPO SIGNAL
     tempo_bpm is not used in scoring at all.  Midnight Coding (78 BPM) and
     Focus Flow (80 BPM) both feel slow and studious — but so does a 68 BPM
     soul track (Rain on My Window).  Without BPM, the system can't distinguish
     a slow jazz ballad from a slow electronic drone.

  4. NO VALENCE SIGNAL
     A user asking for "chill" music likely wants moderate-to-positive valence.
     3AM Diner (blues, melancholy, valence=0.27) could score well on energy and
     acousticness but the system doesn't know it's emotionally dark.
""")

    print("=" * 72)
    print("  Run python3 src/main.py to see the top-5 recommendations.")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    critique()
