# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatcher 1.0** — A content-based music recommender that matches songs to user preferences using weighted genre, mood, and energy similarity scoring.

---

## 2. Intended Use  

VibeMatcher is designed as an educational simulation to demonstrate how music streaming platforms can recommend songs based on user preferences. It generates a ranked list of song suggestions personalized to a listener's favorite genre, mood, and desired energy level. The system assumes users have a single dominant "vibe" preference and that musical taste can be modeled primarily through three attributes: genre, mood, and energy. This is a classroom exploration tool, not a production recommender—it demonstrates the core logic of content-based filtering.

---

## 3. How the Model Works  

Think of the recommender as a judge that hands out points to every song, then lines the songs up from most points to fewest. For each song it looks at four things and compares them to what the listener said they want:

- **Genre** — if the song's genre is exactly the listener's favorite, it earns **+2.0 points** (the biggest reward).
- **Mood** — if the mood matches (happy, chill, intense, etc.), it earns **+1.0 point**.
- **Energy** — the closer the song's energy is to the listener's target energy, the more points it gets, **up to +1.0**. A perfect energy match is worth a full point; a big gap is worth almost nothing.
- **Danceability** — a small **+0.5 bonus** for very danceable songs, but only for listeners who want high energy.
- **Acousticness** — a **−0.5 penalty** for acoustic songs, but only for listeners who said they *don't* like acoustic.

The song with the most total points goes to the top of the list. Compared to the starter logic (which just returned the first few songs unchanged), this version actually reads the listener's preferences, does the math, and — importantly — records a short "reason" for every point it awards so the output can explain *why* each song was picked.

---

## 4. Data  

The catalog is a single CSV (`data/songs.csv`) with **18 songs**. Each song carries 10 fields: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, and acousticness.

- **Genres represented:** lofi (×3), pop (×2), hip-hop (×2), folk (×2), and one each of rock, jazz, ambient, synthwave, indie pop, electronic, country, classical, and R&B.
- **Moods represented:** chill (×3), intense (×2), happy (×2), and one each of relaxed, focused, moody, nostalgic, confident, peaceful, romantic, dreamy, upbeat, calm, and energetic.

The dataset is small and deliberately spread thin — most genres and moods appear only once. That breadth is good for demos but means there is rarely more than one "perfect" match for any given profile. Parts of musical taste that are **missing**: no lyrics/theme data, no era/decade, no popularity or listen-history signal, and no notion of artist similarity. Some genres a real user would ask for (metal, EDM, punk, classical crossover) simply aren't present.

---

## 5. Strengths  

- **Clear, well-matched profiles work great.** When a listener's genre, mood, and energy all point the same direction, the right song wins decisively. The pop/happy profile puts *Sunrise City* on top (4.48); lofi/chill puts *Library Rain* on top (4.00); rock/intense puts *Storm Runner* on top (3.99). These all match musical intuition.
- **Every recommendation is explained.** Because each point comes with a reason string, the output never feels like a black box — you can see exactly why *Sunrise City* beat *Gym Hero* (it added the mood match).
- **It degrades gracefully.** Even when nothing matches (the "metal/angry" profile), the system still returns a sensible energy-based list instead of crashing or returning nothing.

---

## 6. Limitations and Bias 

The clearest weakness I found is that **the "likes_acoustic" preference is almost useless, and the danceability bonus quietly favors high-energy listeners.** The scoring only *subtracts* 0.5 for acoustic songs when a user says they dislike acoustic — but it never *rewards* acoustic songs for the users who love them. So the "Chill Lofi Lover" and "Jazz/Relaxed Listener," who both set `likes_acoustic: True`, get zero benefit from that preference; it is dead weight. At the same time, the +0.5 danceability bonus only fires when target energy is above 0.7, so calm, low-energy listeners can *never* earn it. The combined effect is that mellow, acoustic-loving users see compressed, lower scores and less differentiation between their top picks, while gym/party users get an extra reliable boost — a subtle bias toward high-energy taste. A second bias is the **genre filter bubble**: because a genre match (+2.0) is worth more than everything else combined can easily overcome, a handful of high-energy, high-danceability tracks (*Gym Hero*, *Neon Skyline*, *Sunrise City*, *Golden Hour Drive*) reappear at the top of nearly every high-energy profile, crowding out variety.

---

## 7. Evaluation  

**Profiles tested (8 total).** Five "realistic" profiles — High-Energy Pop, Chill Lofi, Intense Rock, Ambient Relaxation, and Jazz/Relaxed — plus three adversarial edge cases designed to trick the scorer: *Contradictory Vibe* (rock genre but a peaceful mood and acoustic taste at 0.9 energy), *Ghost Genre* (genre "metal" and mood "angry," neither of which exists in the catalog), and *Acoustic Raver* (electronic/dreamy at 0.98 energy while claiming to love acoustic). Full terminal output for all eight is in Section 10 below.

**What I looked for:** whether the #1 pick made sense, whether the same songs monopolized the top of every list, and how the system behaved when preferences conflicted or pointed at data that isn't there.

**What surprised me:**
- **Genre dominance is stronger than I expected.** In the *Acoustic Raver* run, *City of Echoes* wins with 4.15 even though its energy (0.63) is nowhere near the requested 0.98 — the +3.0 from genre+mood completely swamped a huge energy gap. Matching the label matters far more than matching the actual feel.
- **The "acoustic" flag did nothing.** *Contradictory Vibe* asked for acoustic music but got *Storm Runner* (acousticness 0.10, about as electric as it gets) at #1, because genre+energy carried it and the acoustic preference has no positive weight.
- **A missing genre silently becomes a high-energy playlist.** *Ghost Genre* ("metal/angry") returned *Gym Hero* and *Neon Skyline* — the system can't say "I don't have that," it just falls back to energy and hands over pop/hip-hop.

**Profile-pair comparisons (plain language):**
- **High-Energy Pop vs. Chill Lofi:** Pop pulls loud, danceable, low-acoustic tracks (*Sunrise City*, *Gym Hero*); Lofi pulls quiet, high-acoustic study music (*Library Rain*, *Midnight Coding*). Opposite ends of the energy dial, exactly as intended.
- **Intense Rock vs. Ambient Relaxation:** Rock rewards fast, aggressive songs near 0.9 energy; Ambient rewards near-silent 0.25-energy tracks (*Spacewalk Thoughts*). Same scoring rules, mirror-image results.
- **Chill Lofi vs. Jazz/Relaxed:** These two look similar (both calm and acoustic), and the overlap shows — *Midnight Coding*, *Focus Flow*, and *Library Rain* appear in both lists. The only real separator is the genre bonus, which lifts the one lofi/jazz song that exactly matches.
- **Ghost Genre vs. High-Energy Pop:** *Why does "Gym Hero" keep showing up for people who just want "Happy Pop"?* In plain terms: *Gym Hero* is loud and very danceable, so it collects energy + danceability points for anyone who likes high energy — even when its actual genre/mood is wrong. It's the song that's "always in the gym," so it sneaks onto every high-energy list, pop or not.

**A small experiment (weight shift).** I temporarily **halved the genre weight (2.0 → 1.0) and doubled the energy weight (1.0 → 2.0)**, then reran the pop/happy profile and reverted. The #1 pick (*Sunrise City*) stayed on top because it matches everything, but the middle of the list reshuffled: *Rooftop Lights* (indie pop, mood match, high energy) jumped from #3 to #2 and overtook *Gym Hero*, and the pure-energy *Golden Hour Drive* climbed into the top 4. Takeaway: leaning on energy instead of genre made the list **more diverse in genre and more "feel"-driven** — not obviously more *accurate*, but noticeably less dominated by the exact-genre bonus. It confirmed that the genre weight is the single biggest lever on how repetitive the recommendations feel.

---

## 8. Future Work  

- **Make preferences symmetric:** add an acoustic *bonus* for users who like acoustic (not just a penalty for those who don't), and let the danceability bonus help low-energy users too.
- **Normalize the weights** so genre can't single-handedly outweigh a good mood + energy match, reducing the filter bubble.
- **Handle unknown requests** by telling the user "no metal in the catalog" instead of silently returning high-energy pop.
- **Add a diversity rule** (e.g., don't let one artist or one song type take multiple top slots) and richer features like tempo, valence, or era.

---

## 9. Personal Reflection  

Building this made recommender systems feel a lot less magical and a lot more like a spreadsheet of weighted opinions. The most eye-opening moment was watching a single number — the genre weight — quietly decide how repetitive every playlist felt, and seeing how a preference I "coded in" (likes_acoustic) turned out to do almost nothing in practice. It changed how I think about the apps I use every day: when the same song keeps showing up in my recommendations, it's probably not that the app "knows me" — it's that one feature is weighted too heavily and a few catchy tracks are gaming the math.

---

## 10. Evaluation Runs (Terminal Output)

Full top-5 output from `python -m src.main` for all eight profiles. The first three are the standard profiles; the last three are the adversarial edge cases.

```
🎵 High-Energy Pop Enthusiast  (pop / happy / 0.8 / likes_acoustic=False)
1. Sunrise City — Neon Echo        pop/happy/0.82     4.48  genre(+2.0); mood(+1.0); energy(0.98); dance(+0.5)
2. Gym Hero — Max Pulse            pop/intense/0.93   3.37  genre(+2.0); energy(0.87); dance(+0.5)
3. Rooftop Lights — Indigo Parade  indie pop/happy/0.76  2.46  mood(+1.0); energy(0.96); dance(+0.5)
4. Golden Hour Drive — Arden West  hip-hop/confident/0.81  1.49  energy(0.99); dance(+0.5)
5. Night Drive Loop — Neon Echo    synthwave/moody/0.75  1.45  energy(0.95); dance(+0.5)

🎵 Chill Lofi Lover  (lofi / chill / 0.35 / likes_acoustic=True)
1. Library Rain — Paper Lanterns   lofi/chill/0.35    4.00  genre(+2.0); mood(+1.0); energy(1.00)
2. Midnight Coding — LoRoom        lofi/chill/0.42    3.93  genre(+2.0); mood(+1.0); energy(0.93)
3. Focus Flow — LoRoom             lofi/focused/0.40  2.95  genre(+2.0); energy(0.95)
4. Spacewalk Thoughts — Orbit Bloom ambient/chill/0.28  1.93  mood(+1.0); energy(0.93)
5. Coffee Shop Stories — Slow Stereo jazz/relaxed/0.37  0.98  energy(0.98)

🎵 Intense Rock Fan  (rock / intense / 0.9 / likes_acoustic=False)
1. Storm Runner — Voltline         rock/intense/0.91  3.99  genre(+2.0); mood(+1.0); energy(0.99)
2. Gym Hero — Max Pulse            pop/intense/0.93   2.47  mood(+1.0); energy(0.97); dance(+0.5)
3. Neon Skyline — Pixel Harbor     hip-hop/energetic/0.88  1.48  energy(0.98); dance(+0.5)
4. Sunrise City — Neon Echo        pop/happy/0.82     1.42  energy(0.92); dance(+0.5)
5. Golden Hour Drive — Arden West  hip-hop/confident/0.81  1.41  energy(0.91); dance(+0.5)

🎵 Ambient Relaxation Seeker  (ambient / chill / 0.25 / likes_acoustic=True)
1. Spacewalk Thoughts — Orbit Bloom ambient/chill/0.28  3.97  genre(+2.0); mood(+1.0); energy(0.97)
2. Library Rain — Paper Lanterns   lofi/chill/0.35    1.90  mood(+1.0); energy(0.90)
3. Midnight Coding — LoRoom        lofi/chill/0.42    1.83  mood(+1.0); energy(0.83)
4. Winter Window — Clara Row       classical/peaceful/0.22  0.97  energy(0.97)
5. Coffee Shop Stories — Slow Stereo jazz/relaxed/0.37  0.88  energy(0.88)

🎵 Jazz/Relaxed Listener  (jazz / relaxed / 0.4 / likes_acoustic=True)
1. Coffee Shop Stories — Slow Stereo jazz/relaxed/0.37  3.97  genre(+2.0); mood(+1.0); energy(0.97)
2. Focus Flow — LoRoom             lofi/focused/0.40  1.00  energy(1.00)
3. Midnight Coding — LoRoom        lofi/chill/0.42    0.98  energy(0.98)
4. Library Rain — Paper Lanterns   lofi/chill/0.35    0.95  energy(0.95)
5. Midnight Bloom — The Velvet Tones folk/calm/0.48    0.92  energy(0.92)

--- ADVERSARIAL EDGE CASES ---

🎵 Contradictory Vibe  (rock / peaceful / 0.9 / likes_acoustic=True)
1. Storm Runner — Voltline         rock/intense/0.91  2.99  genre(+2.0); energy(0.99)      [mood ignored]
2. Neon Skyline — Pixel Harbor     hip-hop/energetic/0.88  1.48  energy(0.98); dance(+0.5)
3. Gym Hero — Max Pulse            pop/intense/0.93   1.47  energy(0.97); dance(+0.5)
4. Sunrise City — Neon Echo        pop/happy/0.82     1.42  energy(0.92); dance(+0.5)
5. Golden Hour Drive — Arden West  hip-hop/confident/0.81  1.41  energy(0.91); dance(+0.5)
   → Asked for a peaceful, acoustic vibe but got the most aggressive, electric rock track. Genre + energy win; mood and acoustic taste are ignored.

🎵 Ghost Genre  (metal / angry / 0.95 / likes_acoustic=False)   [neither value exists in catalog]
1. Gym Hero — Max Pulse            pop/intense/0.93   1.48  energy(0.98); dance(+0.5)
2. Neon Skyline — Pixel Harbor     hip-hop/energetic/0.88  1.43  energy(0.93); dance(+0.5)
3. Sunrise City — Neon Echo        pop/happy/0.82     1.37  energy(0.87); dance(+0.5)
4. Golden Hour Drive — Arden West  hip-hop/confident/0.81  1.36  energy(0.86); dance(+0.5)
5. Rooftop Lights — Indigo Parade  indie pop/happy/0.76  1.31  energy(0.81); dance(+0.5)
   → No genre/mood match possible, so it silently falls back to a generic high-energy playlist instead of flagging "no metal available."

🎵 Acoustic Raver  (electronic / dreamy / 0.98 / likes_acoustic=True)
1. City of Echoes — Northline      electronic/dreamy/0.63  4.15  genre(+2.0); mood(+1.0); energy(0.65); dance(+0.5)
2. Gym Hero — Max Pulse            pop/intense/0.93   1.45  energy(0.95); dance(+0.5)
3. Neon Skyline — Pixel Harbor     hip-hop/energetic/0.88  1.40  energy(0.90); dance(+0.5)
4. Sunrise City — Neon Echo        pop/happy/0.82     1.34  energy(0.84); dance(+0.5)
5. Golden Hour Drive — Arden West  hip-hop/confident/0.81  1.33  energy(0.83); dance(+0.5)
   → Wanted 0.98 energy but the genre+mood match (City of Echoes, energy 0.63) still wins by a mile — labels beat the actual feel.
```
