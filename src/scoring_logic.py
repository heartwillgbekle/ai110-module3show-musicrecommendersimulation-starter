"""
Scoring Logic Design Session — Claude API chat
================================================
Models a focused "new chat session" dedicated entirely to designing
the point-based scoring recipe for the music recommender.

Sends the songs.csv catalog as context and asks three questions:
  1. Genre vs Mood — which should be worth more points, and why?
  2. Energy similarity — what math turns a float distance into points?
  3. Final recipe validation — do the chosen weights produce sensible
     rankings on concrete song pairs from the catalog?

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 src/scoring_logic.py
"""

import anthropic

CSV_CONTEXT = """\
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
10,Rooftop Lights,Indigo Parade,indie pop,happy,0.76,124,0.81,0.82,0.35
11,Neon Bounce,Pulse District,hip-hop,energetic,0.84,94,0.73,0.92,0.08
12,Velvet Night,Sable Moon,r&b,romantic,0.55,85,0.68,0.74,0.34
13,Morning Prelude,Clara Voss,classical,peaceful,0.17,52,0.72,0.22,0.98
14,Iron Spiral,Redline,metal,angry,0.97,168,0.24,0.51,0.04
15,Porch Light Lullaby,June Hollow,folk,nostalgic,0.30,74,0.61,0.44,0.94
16,Ultraviolet,Axiom,electronic,euphoric,0.89,128,0.83,0.94,0.03
17,Rain on My Window,Delroy & The Echoes,soul,sad,0.38,68,0.30,0.47,0.66
18,Coastal Drift,Sunroot,reggae,uplifting,0.59,82,0.79,0.81,0.55
19,3AM Diner,Mabel Cross,blues,melancholy,0.43,76,0.27,0.45,0.73
20,Harvest Road,The Copperfields,country,nostalgic,0.62,104,0.70,0.67,0.76\
"""

PROMPT = f"""
You are helping design the scoring recipe for a Python music recommender
simulation. This is a content-based system — it scores each song in the
catalog against a user's taste profile using a simple additive point formula.

Here is the full 20-song catalog (songs.csv):

```
{CSV_CONTEXT}
```

The user profile has four fields:
  genre        : str   — user's preferred genre  (e.g. "lofi")
  mood         : str   — user's preferred mood   (e.g. "chill")
  energy       : float — target energy level 0.0–1.0  (e.g. 0.38)
  likes_acoustic : bool — True = prefers acoustic sound

The candidate scoring formula is:

  score  =  GENRE_PTS   (if genre matches)
          + MOOD_PTS    (if mood matches)
          + ENERGY_PTS  (up to max, based on proximity)
          + ACOUSTIC_PTS (up to max, based on proximity)

Answer the following three questions precisely, using actual data from
the catalog above to support every claim.

─────────────────────────────────────────────────────
QUESTION 1 — Genre vs Mood point values
─────────────────────────────────────────────────────
The starter recipe suggests +2.0 for a genre match and +1.0 for a mood
match.  Using this catalog as evidence:

a) Give one concrete example where genre matters MORE than mood —
   show the two songs and explain why ranking them by genre first
   produces a better recommendation than ranking by mood first.

b) Give one concrete example where mood arguably matters MORE than genre —
   show the two songs and explain the case for flipping the weights.

c) Give your final recommendation: should GENRE_PTS > MOOD_PTS, or
   should they be equal?  State the exact values you recommend and why.

─────────────────────────────────────────────────────
QUESTION 2 — Energy similarity formula
─────────────────────────────────────────────────────
For a user with target_energy = 0.40, the system needs to convert
each song's energy value into a point bonus.  The goal: songs closer
to 0.40 earn more points, songs far away earn fewer.

a) Show the math for the proximity formula using these three songs:
     Midnight Coding  energy=0.42
     Rooftop Lights   energy=0.76
     Iron Spiral      energy=0.97
   If ENERGY_PTS has a max of 1.0, what does each song earn?

b) Why is  (1 - |song.energy - target|) × MAX_PTS  better than
   simply checking  song.energy > target  for a binary bonus?

c) Should ENERGY_PTS max be 1.0 or 1.5?  Justify with a concrete
   example of how the choice changes the rankings in this catalog.

─────────────────────────────────────────────────────
QUESTION 3 — Final recipe validation
─────────────────────────────────────────────────────
Given this finalized recipe:
  +2.0  genre match     (binary)
  +1.0  mood match      (binary)
  +1.0  energy proximity  (1 - |song.energy - 0.40|) × 1.0
  +0.5  acoustic proximity (song.acousticness × 0.5 if likes_acoustic=True)

  User profile: genre=lofi, mood=chill, energy=0.40, likes_acoustic=True
  Maximum possible score = 4.5

a) Calculate the exact score for each of these four songs and rank them:
     Library Rain    (lofi, chill,   energy=0.35, acousticness=0.86)
     Midnight Coding (lofi, chill,   energy=0.42, acousticness=0.71)
     Coffee Shop Stories (jazz, relaxed, energy=0.37, acousticness=0.89)
     Storm Runner    (rock, intense, energy=0.91, acousticness=0.10)

b) Does this ranking feel musically correct to a real listener?
   If not, what single weight adjustment would fix it?

c) What is the maximum score a non-lofi song could ever achieve with
   this profile?  Is that ceiling fair or too restrictive?
"""


def run_scoring_design_session() -> None:
    client = anthropic.Anthropic()

    print("Scoring Logic Design Session")
    print("=" * 70)
    print()

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=3000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": PROMPT}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)

        final = stream.get_final_message()

    print(f"\n\n[tokens — in: {final.usage.input_tokens}  out: {final.usage.output_tokens}]")


if __name__ == "__main__":
    run_scoring_design_session()
