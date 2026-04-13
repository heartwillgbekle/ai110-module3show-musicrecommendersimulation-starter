# Music Recommender — Data Flow

Traces the path from raw inputs to ranked output, showing exactly how
a single song moves through the system.

```mermaid
flowchart TD

    %% ── INPUTS ─────────────────────────────────────────────────────────────
    UP["User Preferences\ngenre · mood · energy · likes_acoustic"]
    CSV[("songs.csv\n20 songs")]

    %% ── LOADING ─────────────────────────────────────────────────────────────
    CSV --> LOAD["load_songs()\nparse CSV rows into dicts\ncast numeric columns to float"]
    LOAD --> SONGS["songs list — 20 dicts"]

    %% ── HAND-OFF ─────────────────────────────────────────────────────────────
    UP   --> REC
    SONGS --> REC

    %% ── MAIN PROCESS ─────────────────────────────────────────────────────────
    subgraph REC["recommend_songs(user_prefs, songs, k=5)"]
        direction TB

        ITER{"more songs\nto score?"}

        %% ── SCORING RULE (one song at a time) ───────────────────────────────
        subgraph SF["score_song(user_prefs, song)  ← called once per song"]
            direction TB
            G{"genre ==\nuser.genre ?"}
            MO{"mood ==\nuser.mood ?"}
            EN["energy_pts\n= (1 - abs(song.energy - target)) x 1.0\nmax 1.0 pts"]
            AC["acoustic_pts\n= (1 - abs(song.acousticness - target_ac)) x 0.5\ntarget_ac = 1.0 if likes_acoustic else 0.0\nmax 0.5 pts"]
            TOT(["score  0.0 – 4.5 pts\n+ reasons list"])

            G -- "+2.0 pts" --> MO
            G -- "+0.0 pts" --> MO
            MO -- "+1.0 pts" --> EN
            MO -- "+0.0 pts" --> EN
            EN --> AC --> TOT
        end

        %% ── LOOP CONTROL ─────────────────────────────────────────────────────
        ITER -- "yes — next song" --> SF
        SF  --> COL["scored_songs.append\n(song, score, explanation)"]
        COL --> ITER

        %% ── RANKING RULE ─────────────────────────────────────────────────────
        ITER -- "no — all 20 songs scored" --> SRT["sort scored_songs\nby score descending"]
        SRT --> SLC["scored_songs[ :k ]\nkeep top k only"]
    end

    %% ── OUTPUT ──────────────────────────────────────────────────────────────
    SLC --> OUT["Top K Recommendations\n1. Library Rain          4.400 pts\n2. Midnight Coding       4.315 pts\n3. Focus Flow            3.370 pts\n4. Spacewalk Thoughts    2.360 pts\n5. Coffee Shop Stories   1.435 pts"]
```

---

## Score Breakdown — What Each Component Contributes

| Component | Rule | Max pts | Source in `score_song()` |
|---|---|---|---|
| Genre match | binary — full or nothing | **2.0** | `if song["genre"] == user_prefs["genre"]` |
| Mood match | binary — full or nothing | **1.0** | `if song["mood"] == user_prefs["mood"]` |
| Energy proximity | `(1 - abs(Δenergy)) × 1.0` | **1.0** | continuous, partial credit |
| Acoustic proximity | `(1 - abs(Δacoustic)) × 0.5` | **0.5** | continuous, partial credit |
| **Total possible** | | **4.5** | |

## Key Design Choices Visible in the Diagram

- **Genre outweighs Mood (2.0 vs 1.0):** A genre miss loses twice as many
  points as a mood miss, because genre defines the full sonic world
  (instrumentation, tempo range, production style).

- **Continuous features use proximity, not threshold:** Both energy and
  acousticness give *partial* points for near-misses. A song at energy 0.79
  still earns 0.59 pts toward a target of 0.38 — it is not simply zeroed out.

- **Scoring Rule and Ranking Rule are separate functions:**
  `score_song()` evaluates one song in isolation; `recommend_songs()` owns
  the loop, the collection, and the sort. Each can be changed independently.
