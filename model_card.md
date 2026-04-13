# Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder picks the top 5 songs from a catalog that best match a listener's taste.
It is a content-based recommender — it compares song attributes to user preferences.
It does not learn from behavior. It just scores and ranks.

---

## 3. Data Used

- **Size:** 20 songs in `data/songs.csv`
- **Features used in scoring:** genre, mood, energy (0–1), acousticness (0–1)
- **Features stored but not scored:** tempo BPM, valence, danceability
- **Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop,
  r&b, classical, metal, folk, electronic, soul, reggae, blues, country
- **Limits:** The catalog only represents Western popular music. Genres like
  Afrobeats, cumbia, or K-pop are missing. Most genres have only one song, so
  variety is very limited.

---

## 4. Algorithm Summary

Every song gets a score out of 4.5 points. Higher score = better match.

| Signal | Max points | Rule |
|---|---|---|
| Genre match | 2.0 | Full points if genre matches exactly. Zero if not. |
| Mood match | 1.0 | Full points if mood matches exactly. Zero if not. |
| Energy closeness | 1.0 | Closer to the user's target = more points. Partial credit allowed. |
| Acoustic texture | 0.5 | High acousticness earns more if the user likes acoustic sound. |

After every song is scored, the list is sorted highest to lowest. The top 5 are returned.
Genre and mood are worth 3.0 points combined — most of the score is decided before energy even matters.

---

## 5. Observed Behavior / Biases

**Genre dominates.** Any song outside the user's genre is capped at 2.5 points max.
A perfect energy and mood match in the wrong genre will almost always lose to a mediocre same-genre song.
In experiments, halving the genre weight (2.0 → 1.0) moved better-fitting songs from other genres into the top 5.

**Exact string matching ignores synonyms.** The mood "relaxed" is treated as completely different from "chill."
The genre "indie pop" gets zero overlap credit with "pop."
Real listeners hear these as nearly the same thing. The system does not.

**Conflicting preferences produce averaged-out results.** A user who asked for high energy AND sad mood got a confusing list.
The system cannot resolve a contradiction — it just adds the points.
3AM Diner (blues/sad) ranked #1 on genre, but high-energy songs with no mood match filled spots 3–5.

**Invisible features.** Valence and tempo are never scored.
A dark blues ballad and a bright folk song can score identically.
A user who wants "chill" music probably does not want low-valence sadness, but the system cannot tell the difference.

**Tiny catalog creates false defaults.** Several genres have only one song.
A blues listener gets that one song at #1 and then a random pile of mismatches below it.
That is not a real recommendation — it is just the only option.

---

## 6. Evaluation Process

**Five profiles were tested:**

1. **High-Energy Pop** (genre=pop, mood=happy, energy=0.90) — Sunrise City ranked #1 at 4.33 pts. Felt right. Gym Hero ranked #2 despite being "intense" not "happy" — only because its energy was close.
2. **Chill Lofi** (genre=lofi, mood=chill, energy=0.38) — Library Rain and Midnight Coding topped the list with scores above 4.3. The most convincing result.
3. **Deep Intense Rock** (genre=rock, mood=intense, energy=0.92) — Storm Runner ranked #1 correctly. But spots 3–5 were electronic and hip-hop songs whose only connection to rock was a similar energy level.
4. **Adversarial: High-Energy + Sad Mood** — Exposed that conflicting preferences produce unreliable results. The genre bonus decided #1; energy alone filled the rest.
5. **Adversarial: Max Energy + Loves Acoustic** — Showed that acoustic and high-energy preferences fight each other. Acoustic songs are almost always low energy, so no song could score well on both.

**Weight-shift experiment:** Genre weight was cut from 2.0 to 1.0, and energy max was raised from 1.0 to 2.0.
The #1 result stayed the same for all three standard profiles.
Spots 3–5 shifted toward energetically similar songs from nearby genres — which felt more musically honest.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- A classroom demo of how content-based filtering works
- Learning how point-based scoring translates song attributes into a ranked list
- Exploring how weight choices affect recommendations

**Not intended for:**
- Real music discovery for actual users
- Any production or commercial application
- Users whose taste falls outside Western popular music genres
- Making decisions about what music is "good" or "popular"

---

## 8. Ideas for Improvement

1. **Add fuzzy matching for genre and mood.**
   Build a small similarity table so "lofi" gives partial credit toward "ambient,"
   and "chill" gives partial credit toward "relaxed."
   This would fix the biggest unfairness in the current system.

2. **Score valence and tempo.**
   Even a small weight on valence would stop dark or angry songs from ranking
   well for a user who asked for something happy or calm.

3. **Add a diversity rule.**
   After scoring, penalize any genre that already appears in the top results.
   This would prevent the top 5 from being all the same genre every time.

---

## 9. Personal Reflection

**Biggest learning moment:**
I assumed genre was obviously the most important signal — so I gave it 2.0 points.
That felt right until I ran the weight-shift experiment.
When I cut genre to 1.0, songs that were acoustically and energetically similar — but in a different genre — moved up.
Those songs often felt *more* correct to me as a listener.
The biggest learning was that the weight I was most confident about was also the one creating the most bias.

**How AI tools helped — and when I had to double-check:**
AI tools helped me write cleaner code faster and suggested the list comprehension version of `recommend_songs`.
But I had to verify all the score math manually.
When I asked for the weight-shift experiment, the suggestion was right in structure but I ran the numbers myself to confirm the rankings actually changed the way I expected.
AI tools are good at drafting — they still need a human to check if the output makes sense.

**What surprised me about simple algorithms:**
The output really did *feel* like a recommendation, even though the logic is just addition.
Library Rain and Midnight Coding rising to the top of the Chill Lofi list felt natural — those are genuinely good matches.
What surprised me is that the illusion breaks immediately at the edge cases.
As soon as preferences conflicted or the catalog ran out of options, the numbers stopped making sense musically.
Simple math can feel intelligent inside its comfort zone. Outside it, the seams show fast.

**What I would try next:**
I would add valence to the scoring formula and test whether it fixes the adversarial sad/high-energy profile.
I would also build a fuzzy genre/mood similarity table — even a hand-coded one with five categories — to see how much it improves recommendations for listeners who cross genre lines.
If I had more time, I would replace the fixed weights entirely with a small set of user ratings and let the system learn its own weights from feedback.
