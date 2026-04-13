"""
Catalog expansion script: Ask Claude to generate new songs in valid CSV format
that extend the starter dataset with diverse genres and moods.

Claude is given the full existing songs.csv as context and asked to produce
10 new rows that fill genre/mood gaps, preserve the exact header format,
and use realistic audio feature values.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 src/expand_catalog.py

The script prints the new CSV rows to stdout so you can review them before
appending to data/songs.csv.  To append automatically, run:
    python3 src/expand_catalog.py --write
"""

import anthropic
import sys
import os

SONGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

EXISTING_CSV = """\
id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness
1,Sunrise City,Neon Echo,pop,happy,0.82,118,0.84,0.79,0.18
2,Midnight Coding,LoRoom,lofi,chill,0.42,78,0.56,0.62,0.71
3,Storm Runner,Voltline,rock,intense,0.91,152,0.48,0.66,0.10
4,Library Rain,Paper Lanterns,lofi,chill,0.35,72,0.60,0.58,0.86
5,Gym Hero,Max Pulse,pop,intense,0.93,132,0.77,0.88,0.05
6,Spacewalk Thoughts,Orbit Bloom,ambient,chill,0.28,60,0.65,0.41,0.92
7,Coffee Shop Stories,Slow Stereo,jazz,relaxed,0.37,90,0.71,0.54,0.89
8,Night Drive Loop,Neon Echo,synthwave,moody,0.75,110,0.49,0.73,0.22
9,Focus Flow,LoRoom,lofi,focused,0.40,80,0.59,0.60,0.78
10,Rooftop Lights,Indigo Parade,indie pop,happy,0.76,124,0.81,0.82,0.35\
"""

PROMPT = f"""
You are expanding a music dataset for a Python classroom recommender project.

Here is the current songs.csv file (10 songs, header + data rows):

```csv
{EXISTING_CSV}
```

Column definitions:
  id           : integer, auto-increment
  title        : string, creative song title
  artist       : string, invented artist or band name
  genre        : string, lowercase music genre label
  mood         : string, lowercase emotional label
  energy       : float 0.0–1.0  (0=very calm, 1=very intense)
  tempo_bpm    : float, beats per minute
  valence      : float 0.0–1.0  (0=dark/sad, 1=bright/joyful)
  danceability : float 0.0–1.0  (0=not danceable, 1=extremely danceable)
  acousticness : float 0.0–1.0  (0=fully electronic, 1=fully acoustic)

GENRES already in the catalog (do NOT duplicate these):
  pop, lofi, rock, ambient, jazz, synthwave, indie pop

MOODS already in the catalog (do NOT duplicate these):
  happy, chill, intense, relaxed, focused, moody

YOUR TASK:
Generate exactly 10 new song rows (ids 11–20) that satisfy ALL of these rules:

1. GENRE DIVERSITY: Every new row must use a genre NOT in the list above.
   Suggested new genres (use any): hip-hop, r&b, classical, metal, folk,
   electronic, soul, reggae, blues, country, funk, latin, k-pop, trap

2. MOOD DIVERSITY: Every new row must use a mood NOT in the list above.
   Suggested new moods (use any): sad, melancholy, nostalgic, romantic,
   angry, euphoric, uplifting, peaceful, dreamy, bittersweet, energetic

3. REALISTIC FEATURE VALUES:
   - Metal songs: energy 0.88–0.98, tempo 140–180, valence 0.15–0.35
   - Classical: energy 0.10–0.30, tempo 45–80, acousticness 0.90–1.0
   - Hip-hop/trap: high danceability 0.80–0.95, tempo 80–100
   - Reggae: mid energy 0.50–0.70, high danceability, high acousticness
   - Blues: low-mid energy, low valence (0.20–0.40), high acousticness
   - Soul: mid energy, mid-high acousticness, low-mid valence
   - Folk: low energy, very high acousticness (0.85–0.98), low tempo

4. FORMAT: Return ONLY the 10 data rows (no header, no markdown fences,
   no explanation text). Each row must be valid CSV with exactly 10 columns
   in the same order as the header:
   id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness

   Example of the required format (do not include this line):
   11,Example Title,Artist Name,hip-hop,energetic,0.83,92,0.74,0.91,0.09
"""


def generate_new_songs() -> list[str]:
    client = anthropic.Anthropic()

    print("Asking Claude to generate new catalog entries...\n")

    new_rows: list[str] = []
    buffer = ""

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": PROMPT}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    buffer += event.delta.text
                    print(event.delta.text, end="", flush=True)

    print("\n")

    # Parse the rows from the response
    for line in buffer.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "," in line:
            parts = line.split(",")
            # Accept only rows with 10 columns and numeric id
            if len(parts) == 10:
                try:
                    int(parts[0])
                    new_rows.append(line)
                except ValueError:
                    pass  # skip any header or explanation line

    return new_rows


def append_to_csv(new_rows: list[str]) -> None:
    with open(SONGS_PATH, "a", newline="") as f:
        for row in new_rows:
            f.write("\n" + row)
    print(f"Appended {len(new_rows)} new songs to {SONGS_PATH}")


if __name__ == "__main__":
    new_rows = generate_new_songs()

    print(f"Generated {len(new_rows)} valid rows.\n")

    if "--write" in sys.argv:
        append_to_csv(new_rows)
    else:
        print("Run with --write to append these rows to data/songs.csv")
        print("  python3 src/expand_catalog.py --write")
