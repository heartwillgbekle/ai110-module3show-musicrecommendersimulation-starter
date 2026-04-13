# Reflection: Profile Comparisons and What They Reveal

---

## High-Energy Pop vs. Chill Lofi

These two profiles are almost opposites: one wants loud, upbeat pop, the other
wants quiet, acoustic background music. The output reflects that clearly —
Sunrise City tops the pop list while Library Rain tops the lofi list, and the
two lists share zero songs.

What is interesting is *why* they share zero songs. It is not that the songs
are perfectly tailored — it is that the genre weight is so heavy (2.0 out of
4.5) that any song outside the target genre can never outscore a mediocre
in-genre match. The system works well here, but it works by brute force: genre
dominates, not nuance.

---

## High-Energy Pop vs. Deep Intense Rock

Both profiles want high energy (0.90 and 0.92). The difference is genre and
mood. Gym Hero (pop, intense) appears at #2 for *both* profiles — for rock it
earns only the energy proximity points, but that is still enough to beat most
of the catalog.

This reveals a subtle problem: the system uses energy similarity as a
tiebreaker, but energy alone does not capture "rock feel." Iron Spiral (metal)
and Storm Runner (rock) sound like rock. Ultraviolet (electronic) and Neon
Bounce (hip-hop) do not. But at energy 0.92, all four songs score within 0.06
points of each other. To a real listener, that is not a tie — it is completely
wrong.

---

## Chill Lofi vs. Adversarial: High-Energy + Sad Mood

The Chill Lofi profile gave the most confident, convincing results in the whole
experiment. The Adversarial High-Energy + Sad profile gave the least confident.

Why? The lofi profile is internally consistent — every preference points in the
same direction (quiet, slow, acoustic, mellow). The adversarial profile pulls
in two directions at once: high energy usually means excitement, but sad mood
means something heavy and slow. No song in the catalog satisfies both.

The system responded by letting the genre bonus decide #1 (3AM Diner, the only
blues song), then filling spots 3–5 with high-energy songs that have no mood
or genre match at all. The output technically "ran correctly" but the list would
feel wrong to any real listener. This shows that additive scoring cannot
represent preference conflicts — it just averages them.

---

## Deep Intense Rock vs. Adversarial: Max Energy + Loves Acoustic

The rock profile and the max-energy-acoustic profile both request energy near
1.0, but the acoustic preference flips the second half of the score completely.

Rock listeners typically prefer produced, amplified sound — likes_acoustic=False.
The acoustic-lover profile sets likes_acoustic=True. The result: Iron Spiral
(metal, energy 0.97) scores near the *bottom* of the acoustic profile's list
because its acousticness is 0.04, earning almost zero texture points. That same
song scores near the top of the rock profile's list.

This comparison makes the acousticness weight's role very visible. It is only
0.5 points, but when the catalog is small and many songs cluster near the same
energy level, that half-point can separate rank #2 from rank #5.

---

## Why Does "Gym Hero" Keep Showing Up?

To explain this to someone who does not write code:

Imagine you are rating restaurants. You award 2 points if it serves your
favorite cuisine, 1 point if it matches your preferred vibe (casual or fancy),
and up to 1 point based on how close the price is to your budget.

Gym Hero is a pop song with intense energy (0.93). For a pop/happy listener it
earns 2 genre points + 1 mood point + almost 1 energy point = ~4 points.
For a rock/intense listener it earns 0 genre points + 1 mood point + almost 1
energy point = ~2 points — still near the top because nothing else in the
catalog earns much more without the genre bonus.

The song is not the "best" recommendation for a rock fan; it is just the
least-wrong option when the catalog has only one rock song. A real platform with
millions of songs would never surface a pop song for a rock listener. Our system
does because the catalog is too small to offer meaningful alternatives.

---

## What I Learned

Building this experiment confirmed that a recommender system is only as good as
its data and its weights. The weights I chose — especially 2.0 for genre — made
the algorithm confident and predictable for users whose taste fits neatly into
a single genre. But for edge-case users, or users who like music across genre
lines, the system becomes rigid in ways that feel unfair.

Real platforms like Spotify spend enormous effort learning weights from billions
of listening events precisely because static, hand-tuned weights like these
cannot capture the full complexity of what people actually enjoy.
