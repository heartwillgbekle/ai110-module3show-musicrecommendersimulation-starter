# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests up to five songs from a 20-song catalog based on a
listener's preferred genre, mood, energy level, and texture preference
(acoustic vs. electronic). It is built for classroom exploration only — not
for real users — and is meant to illustrate how a content-based recommender
turns song attributes into a ranked list.

The system assumes the user can describe their taste with a single genre label
and a single mood label. It does not learn from listening history, skips, or
any real user behavior.

---

## 3. How the Model Works

Every song in the catalog gets a numeric score from 0 to 4.5 points. Points
come from four sources:

- **Genre** (up to 2.0 pts): If the song's genre exactly matches the user's
  preferred genre, it earns the full 2.0 points. If not, it earns zero.
- **Mood** (up to 1.0 pt): Same all-or-nothing rule for mood.
- **Energy closeness** (up to 1.0 pt): The closer the song's energy level is
  to the user's target, the more points it earns. A perfect match gives 1.0;
  a song at the opposite extreme of the scale gives 0.0. Songs in between earn
  partial credit.
- **Acoustic texture** (up to 0.5 pts): If the user likes acoustic music, songs
  with high acousticness earn more points; if the user prefers electronic sound,
  songs with low acousticness earn more.

After every song is scored, they are sorted from highest to lowest and the top
five are returned. Songs that match on genre and mood can earn up to 3.0 of the
4.5 possible points before energy or texture are even considered.

---

## 4. Data

The catalog contains 20 songs stored in `data/songs.csv`. Each song has ten
attributes: title, artist, genre, mood, energy (0–1), tempo in BPM, valence
(emotional brightness, 0–1), danceability (0–1), and acousticness (0–1).

The catalog covers 17 genres — pop, lofi, rock, ambient, jazz, synthwave,
indie pop, hip-hop, r&b, classical, metal, folk, electronic, soul, reggae,
blues, and country — and 15 moods. The original starter file had 10 songs; 10
more were added to improve coverage.

The dataset reflects common Western popular music. Genres like Afrobeats, K-pop,
cumbia, or classical Indian music are absent, so the system would be unhelpful
to listeners whose taste falls outside this cultural frame.

---

## 5. Strengths

- **Transparent scoring.** Every recommendation comes with a plain-English
  explanation ("genre match (+2.0); energy proximity (+0.97)") so a user can
  understand exactly why a song was chosen.
- **Strong separation for clear-cut profiles.** For the "Chill Lofi" profile,
  the top two results (Library Rain, Midnight Coding) both score above 4.3 out
  of 4.5 — a convincing match. For "Deep Intense Rock," Storm Runner scores
  4.440, leaving the runner-up more than 2 points behind.
- **Partial credit for near-misses.** The proximity formula means a song that
  is slightly off on energy still earns something, rather than being zeroed out
  by a hard cutoff.

---

## 6. Limitations and Bias

**Genre over-dominates.** Genre is worth 2.0 out of 4.5 possible points —
44% of the maximum. Any song outside the user's preferred genre is permanently
capped at 2.5 points no matter how well it matches on every other dimension. A
weight-shift experiment (genre 2.0 → 1.0, energy max 1.0 → 2.0) showed that
Spacewalk Thoughts (ambient, chill) jumped from 2.36 to 3.26 for the Chill Lofi
profile — a song most listeners would consider a reasonable recommendation that
the original weights buried.

**Mood and genre use exact string matching.** "relaxed" and "chill" are scored
as completely different moods. "indie pop" and "pop" are scored as completely
different genres. Real listeners treat these as near-synonyms, but the system
cannot. Coffee Shop Stories (jazz, relaxed) loses its full mood bonus even
though a chill-lofi fan would very likely enjoy it.

**Valence and tempo are invisible.** The system cannot tell the difference
between a slow, dark blues ballad and a slow acoustic folk song because it does
not use valence or tempo in scoring. A user asking for "chill" music almost
certainly wants positive or neutral emotional tone, but the system has no way
to enforce that.

**Filter bubble risk.** For profiles where even one song has a genre+mood match
(3.0 pts), the remaining catalog is essentially unreachable. The top of the list
is always dominated by the handful of songs that share the user's genre, and the
system has no diversity mechanism to surface anything unexpected.

**Tiny catalog.** With only 20 songs, several genres have only one
representative. A "blues" listener gets 3AM Diner at the top and then a list of
songs that do not match at all, because there is no second blues song to compete.

---

## 7. Evaluation

**Profiles tested:** High-Energy Pop, Chill Lofi, Deep Intense Rock, and two
adversarial edge cases (High-Energy + Sad Mood; Max Energy + Loves Acoustic).

**What the results showed:**

- **Chill Lofi** produced the most convincing top-2 (Library Rain 4.400,
  Midnight Coding 4.315). Both songs are lofi/chill with energy near 0.38 and
  moderate-to-high acousticness — exactly the profile target. This felt right.
- **Deep Intense Rock** surfaced Storm Runner at the top (4.440), which is
  correct, but positions 3–5 were filled by electronic, metal, and hip-hop songs
  — not because they are similar to rock, but purely because their energy
  happened to be close to 0.92. This revealed that energy similarity alone does
  not capture "rock feel."
- **Adversarial: High-Energy + Sad Mood** exposed a contradiction: the catalog's
  only blues song (3AM Diner) won the genre match bonus but scored poorly on
  energy (0.53 pts), while purely high-energy songs with no mood match climbed
  to positions 3–5. The system could not resolve the conflict — it just averaged
  it out.
- **Adversarial: Max Energy + Loves Acoustic** showed that the two continuous
  features work against each other. Acoustic songs tend to be low-energy, so
  asking for energy=1.0 and likes_acoustic=True produced low scores across the
  board, with Porch Light Lullaby (folk/nostalgic) winning on genre+mood alone
  despite an energy proximity of only 0.30.

**Weight-shift experiment:** Halving the genre weight (2.0 → 1.0) and doubling
the energy weight (max 1.0 → 2.0) kept the #1 result the same for all three
standard profiles but meaningfully reshuffled positions 3–5. Songs that were
acoustically and energetically similar but belonged to a different genre moved
up — suggesting the original weights may be overly genre-centric for listeners
with broad taste.

---

## 8. Future Work

- **Fuzzy genre/mood matching.** A small similarity table (e.g., "lofi" is 0.7
  similar to "ambient", "chill" is 0.8 similar to "relaxed") would replace the
  binary match and fix the exact-string problem.
- **Add valence and tempo to scoring.** Even a small weight on valence would
  prevent a sad blues track from ranking well for a happy-mood listener.
- **Diversity re-ranking.** After scoring, apply a penalty if a genre is already
  represented in the top-k results, so the list surfaces at least two or three
  different sonic worlds.
- **Larger, more balanced catalog.** Twenty songs is enough to illustrate the
  algorithm but too small for meaningful variety. A 200-song catalog with at
  least 10 songs per genre would make the ranking far more interesting.
- **User feedback loop.** Let the user mark recommendations as "liked" or
  "skipped" and adjust the genre/mood weights over time.

---

## 9. Personal Reflection

Building this system made clear how much work a genre label is doing quietly in
the background. Assigning 2.0 points to genre match — nearly half the possible
score — essentially pre-sorts the entire catalog before energy or mood even
matter. That felt natural at first because genre really does define a lot about a
song, but the experiments showed it can lock users into a narrow slice of the
catalog even when musically adjacent songs exist.

The adversarial profiles were the most revealing part. A "high-energy + sad
mood" listener exposed that the scoring formula has no way to prioritize one
signal over another when they conflict — it just adds the numbers. Real
recommender systems probably handle this with learned weights or by treating
mood and energy as a joint embedding rather than two independent additive terms.
That gap between a simple additive recipe and a learned model became very
concrete through these tests.
