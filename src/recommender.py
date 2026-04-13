from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """Represents a song and its attributes.
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
    popularity: int = 50
    release_decade: int = 2020
    liveness: float = 0.10
    speechiness: float = 0.05
    instrumentalness: float = 0.10

@dataclass
class UserProfile:
    """Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_popularity: int = 50
    preferred_decade: Optional[int] = None
    wants_instrumental: bool = False

@dataclass
class ScoreWeights:
    """Point budget for each scoring component.

    Strategy pattern — swap in a different ScoreWeights instance to change
    how the recommender ranks songs without touching the scoring math.

    Default (genre_first) max = 5.75 pts.
    """
    genre: float = 2.0
    mood: float = 1.0
    energy: float = 1.0
    acoustic: float = 0.5
    popularity: float = 0.5
    decade: float = 0.5
    instrumental: float = 0.25

    @property
    def max_score(self) -> float:
        """Theoretical maximum a song can earn under these weights."""
        return (self.genre + self.mood + self.energy + self.acoustic
                + self.popularity + self.decade + self.instrumental)

# ── Scoring modes (Strategy pattern) ─────────────────────────────────────────
# Each mode shifts emphasis without changing the underlying math.
# genre_first   — default; genre dominates
# mood_first    — swap genre/mood weights; rewards vibe over sonic category
# energy_focused — energy worth 3× more; surfaces high/low-energy clusters
SCORING_MODES: Dict[str, ScoreWeights] = {
    "genre_first": ScoreWeights(
        genre=2.0, mood=1.0, energy=1.0, acoustic=0.5,
        popularity=0.5, decade=0.5, instrumental=0.25,
    ),
    "mood_first": ScoreWeights(
        genre=1.0, mood=2.0, energy=1.0, acoustic=0.5,
        popularity=0.5, decade=0.5, instrumental=0.25,
    ),
    "energy_focused": ScoreWeights(
        genre=0.5, mood=0.5, energy=3.0, acoustic=0.5,
        popularity=0.25, decade=0.25, instrumental=0.25,
    ),
}

class Recommender:
    """OOP implementation of the recommendation logic.
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
    """Load songs from CSV, casting every numeric column to float or int."""
    import csv
    songs = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            row["id"]               = int(row["id"])
            row["energy"]           = float(row["energy"])
            row["tempo_bpm"]        = float(row["tempo_bpm"])
            row["valence"]          = float(row["valence"])
            row["danceability"]     = float(row["danceability"])
            row["acousticness"]     = float(row["acousticness"])
            row["popularity"]       = int(row["popularity"])
            row["release_decade"]   = int(row["release_decade"])
            row["liveness"]         = float(row["liveness"])
            row["speechiness"]      = float(row["speechiness"])
            row["instrumentalness"] = float(row["instrumentalness"])
            songs.append(row)
    return songs

def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: ScoreWeights = None,
) -> Tuple[float, List[str]]:
    """Score one song against user preferences using an additive point recipe.

    ALGORITHM RECIPE (genre_first defaults, max 5.75 pts)
    ─────────────────────────────────────────────────────
    +2.0  genre match        binary
    +1.0  mood match         binary
    +1.0  energy proximity   (1 - |Δenergy|) × weight
    +0.5  acoustic proximity (1 - |Δacousticness|) × weight
    +0.5  popularity prox.   (1 - |Δpop/100|) × weight
    +0.5  decade match       binary (skipped if preferred_decade is None)
    +0.25 instrumental prox. (1 - |Δinstrumentalness|) × weight
    ─────────────────────────────────────────────────────
    Pass a different ScoreWeights to switch scoring mode.
    """
    if weights is None:
        weights = ScoreWeights()

    reasons: List[str] = []
    score = 0.0

    # ── genre ─────────────────────────────────────────────────────────────────
    if song["genre"] == user_prefs["genre"]:
        score += weights.genre
        reasons.append(f"genre match (+{weights.genre:.1f})")
    else:
        reasons.append(f"genre mismatch (+0.0)")

    # ── mood ──────────────────────────────────────────────────────────────────
    if song["mood"] == user_prefs["mood"]:
        score += weights.mood
        reasons.append(f"mood match (+{weights.mood:.1f})")
    else:
        reasons.append(f"mood mismatch (+0.0)")

    # ── energy proximity ──────────────────────────────────────────────────────
    energy_pts = (1.0 - abs(song["energy"] - user_prefs["energy"])) * weights.energy
    score += energy_pts
    reasons.append(f"energy proximity (+{energy_pts:.2f})")

    # ── acoustic proximity ────────────────────────────────────────────────────
    target_ac = 1.0 if user_prefs["likes_acoustic"] else 0.0
    acoustic_pts = (1.0 - abs(song["acousticness"] - target_ac)) * weights.acoustic
    score += acoustic_pts
    reasons.append(f"acousticness proximity (+{acoustic_pts:.2f})")

    # ── popularity proximity (new) ────────────────────────────────────────────
    # Rewards songs close to the user's desired popularity level.
    target_pop = user_prefs.get("target_popularity", 50)
    pop_pts = (1.0 - abs(song["popularity"] / 100 - target_pop / 100)) * weights.popularity
    score += pop_pts
    reasons.append(f"popularity proximity (+{pop_pts:.2f})")

    # ── decade match (new) ────────────────────────────────────────────────────
    # Binary bonus for songs from the user's preferred release era.
    preferred_decade = user_prefs.get("preferred_decade")
    if preferred_decade is not None:
        if song["release_decade"] == preferred_decade:
            score += weights.decade
            reasons.append(f"decade match (+{weights.decade:.1f})")
        else:
            reasons.append(f"decade mismatch (+0.0)")

    # ── instrumentalness proximity (new) ─────────────────────────────────────
    # Rewards purely instrumental songs if wants_instrumental=True, and
    # songs with vocals if wants_instrumental=False.
    target_inst = 1.0 if user_prefs.get("wants_instrumental", False) else 0.0
    inst_pts = (1.0 - abs(song["instrumentalness"] - target_inst)) * weights.instrumental
    score += inst_pts
    reasons.append(f"instrumental proximity (+{inst_pts:.2f})")

    return round(score, 3), reasons


def diversity_rerank(
    scored: List[Tuple[Dict, float, str]],
    k: int,
    artist_penalty: float = 1.5,
    genre_penalty: float = 0.5,
) -> List[Tuple[Dict, float, str]]:
    """Greedily select top-k songs while penalising repeated artists and genres.

    After each song is selected, any remaining candidate from the same artist
    has its effective score reduced by artist_penalty. Any genre that already
    appears twice in the selected set triggers an additional genre_penalty.

    This prevents the top-5 from being dominated by one artist or one genre
    even when a narrow slice of the catalog scores very highly.
    """
    selected: List[Tuple[Dict, float, str]] = []
    remaining = list(scored)  # copy — do not mutate the original

    while len(selected) < k and remaining:
        selected_artists = {s["artist"] for s, _, _ in selected}
        genre_counts: Dict[str, int] = {}
        for s, _, _ in selected:
            genre_counts[s["genre"]] = genre_counts.get(s["genre"], 0) + 1

        best_idx, best_eff = 0, float("-inf")
        for i, (song, raw_score, explanation) in enumerate(remaining):
            eff = raw_score
            if song["artist"] in selected_artists:
                eff -= artist_penalty
            if genre_counts.get(song["genre"], 0) >= 2:
                eff -= genre_penalty
            if eff > best_eff:
                best_eff, best_idx = eff, i

        selected.append(remaining.pop(best_idx))

    return selected


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "genre_first",
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top-k, with optional diversity re-ranking.

    Scoring Rule  — scores every song individually via score_song()
    Ranking Rule  — sorted() returns a new list; original catalog is untouched
    Diversity     — if True, applies artist/genre penalties before selecting top-k

    mode: "genre_first" | "mood_first" | "energy_focused"
    """
    weights = SCORING_MODES.get(mode, ScoreWeights())

    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song, weights)]
    ]
    scored.sort(key=lambda item: item[1], reverse=True)

    if diversity:
        return diversity_rerank(scored, k)
    return scored[:k]
