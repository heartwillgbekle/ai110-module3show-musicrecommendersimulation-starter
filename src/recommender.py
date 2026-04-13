from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            # Cast numeric columns from string to float
            for col in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
                row[col] = float(row[col])
            row["id"] = int(row["id"])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using an additive
    point-based recipe.  Maximum possible score = 4.5.

    ALGORITHM RECIPE
    ─────────────────────────────────────────────────────────────────
    +2.0  genre match     binary: full points if genre == user genre
    +1.0  mood match      binary: full points if mood  == user mood
    +1.0  energy proximity  (1 - |song.energy - target|) × 1.0
                            → 1.0 pts for perfect match, 0.0 for max gap
    +0.5  acoustic proximity  (1 - |song.acousticness - target_ac|) × 0.5
                            target_ac = 1.0 if likes_acoustic else 0.0
    ─────────────────────────────────────────────────────────────────
    Design rationale:
      • Genre (2.0) > Mood (1.0): genre defines the full sonic world
        (instrumentation, production, tempo range).  A genre mismatch
        is harder to ignore than a mood mismatch.
      • Continuous features use proximity, not threshold, so songs that
        are "close but not perfect" still earn partial credit.
      • Acousticness cap (0.5) is lower than energy (1.0) because it is
        a texture preference, not a primary listening driver.
    """
    reasons: List[str] = []
    score = 0.0

    # ── +2.0  genre match ─────────────────────────────────────────────────
    if song["genre"] == user_prefs["genre"]:
        score += 2.0
        reasons.append(f"+2.0 genre '{song['genre']}' matches")

    # ── +1.0  mood match ──────────────────────────────────────────────────
    if song["mood"] == user_prefs["mood"]:
        score += 1.0
        reasons.append(f"+1.0 mood '{song['mood']}' matches")

    # ── +1.0  energy proximity ────────────────────────────────────────────
    energy_pts = (1.0 - abs(song["energy"] - user_prefs["energy"])) * 1.0
    score += energy_pts
    if energy_pts >= 0.85:
        reasons.append(f"+{energy_pts:.2f} energy {song['energy']} ≈ target {user_prefs['energy']}")
    elif energy_pts < 0.55:
        reasons.append(f"+{energy_pts:.2f} energy {song['energy']} far from target {user_prefs['energy']}")
    else:
        reasons.append(f"+{energy_pts:.2f} energy proximity")

    # ── +0.5  acoustic proximity ──────────────────────────────────────────
    target_ac   = 1.0 if user_prefs["likes_acoustic"] else 0.0
    acoustic_pts = (1.0 - abs(song["acousticness"] - target_ac)) * 0.5
    score += acoustic_pts
    if acoustic_pts >= 0.40:
        reasons.append(
            f"+{acoustic_pts:.2f} acousticness fits your "
            f"{'acoustic' if user_prefs['likes_acoustic'] else 'electronic'} preference"
        )

    return round(score, 3), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Scoring Rule  — scores every song individually via score_song()
    Ranking Rule  — sorts all scored songs and returns the top k
    """
    # SCORING PHASE: evaluate every song independently
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))

    # RANKING PHASE: sort by score descending, return top k
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
