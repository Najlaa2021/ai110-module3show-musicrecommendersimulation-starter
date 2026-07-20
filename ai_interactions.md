# AI Interactions Log

> Documentation of the agentic AI workflow used to build the stretch features
> (Challenges 1–4) on top of the core Music Recommender.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent to make multi-step changes autonomously.

**What task did you give the agent?**

Add advanced song features to the dataset and make the recommender score them (Challenge 1), then layer on switchable scoring modes, a diversity penalty, and a formatted output table (Challenges 2–4).

**Prompts used:**

- *"Introduce 5+ new attributes to `data/songs.csv` (popularity 0–100, release decade, detailed mood tags, language, instrumentalness) with sensible values for all 18 songs. Then update `load_songs` to parse the new numeric fields and extend `score_song` so each new attribute contributes points — but keep each new signal smaller than the genre (+2.0) and mood (+1.0) weights so they refine ties instead of dominating. Add the fields to the `Song`/`UserProfile` dataclasses with defaults so the existing tests still pass."*
- *"Verify the math stays valid and that the two existing pytest tests still pass after the change."*

**What did the agent generate or change?**

- `data/songs.csv`: added five columns — `popularity`, `release_decade`, `mood_tags` (pipe-separated), `language`, `instrumentalness` — populated across all 18 tracks.
- `src/recommender.py`: extended `Song` and `UserProfile` with the new fields (all defaulted); taught `load_songs` to cast `popularity`/`release_decade` to int and `instrumentalness` to float; added five scoring rules to `score_song` — decade match (+0.75), mood-tag overlap (+0.4/tag, capped +0.8), language match (+0.5), instrumental preference (±0.3), and mainstream/niche popularity (up to +0.5).

**What did you verify or fix manually?**

- Confirmed `pytest` still shows `2 passed` — the defaults on the new dataclass fields were essential; without them the tests (which construct `Song`/`UserProfile` with the original argument counts) would break.
- Spot-checked a scored song by hand (Midnight Coding under a matching lofi profile) and confirmed the reason breakdown summed to the printed score.
- Made sure the new signals stay secondary: because each is ≤ 0.8, a genre match still outranks any stack of the new bonuses, which matches the intended design.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

The **Strategy pattern**, to support multiple scoring modes (Challenge 2).

**How did AI help you brainstorm or implement it?**

I attached `recommender.py` and asked the assistant to suggest a modular way to support several ranking strategies (genre-first, mood-first, energy-focused) without duplicating the scoring logic or filling `score_song` with `if mode == ...` branches. It compared a few options — subclass-per-strategy, a registry of scoring functions, and a weights-table approach — and recommended the lightweight weights-table version as the cleanest fit: one algorithm, many interchangeable weight sets. Prompt used:

- *"Attached is `recommender.py`. I want 3–4 switchable ranking strategies. Suggest a simple Strategy pattern that keeps the code modular and avoids a giant if/elif in the scoring function. Show how a caller would pick a mode."*

**How does the pattern appear in your final code?**

- `ScoringWeights` (a dataclass) is the **strategy object** — it holds one multiplier per scoring component.
- `SCORING_MODES` is a registry of named preset strategies: `balanced`, `genre-first`, `mood-first`, `energy-focused`.
- `score_song(user_prefs, song, mode=...)` runs a **single algorithm** and multiplies each component by the selected strategy's weight, so swapping modes changes the ranking with no change to the scoring code. `recommend_songs` and the `Recommender` class thread the same `mode` argument through.

---

## Diversity & Fairness Logic (Challenge 3)

**Prompt used:**

- *"In `recommend_songs`, add an optional diversity penalty: when selecting the top-k, subtract points from any candidate whose artist or genre already appears higher in the chosen list, so one artist or genre can't dominate the top results. Show the applied penalty in each song's reasons."*

**What the AI generated / how I verified it:**

- Implemented a greedy selection loop: at each step it picks the highest *adjusted* score, subtracting `1.0` per already-chosen song by the same artist and `0.5` per same-genre song. Penalties are appended to the reason string (e.g. `artist repeat (-1.00)`).
- Verified on the lofi profile: without diversity the top 5 were dominated by LoRoom/lofi; with diversity on, the second LoRoom track (*Focus Flow*) drops and an ambient track surfaces into the top 3 — confirming the penalty rebalances the list.

---

## Visual Summary Table (Challenge 4)

**Prompt used:**

- *"Format the recommendation output as a readable table that includes the reasons column. Prefer `tabulate` if available but fall back to plain ASCII so the app runs without the dependency."*

**What the AI generated / how I verified it:**

- Added `format_recommendations_table`, which uses `tabulate` (grid format, wrapped reasons) when installed and otherwise renders a self-contained ASCII grid with a wrapped reasons column. Added `tabulate` to `requirements.txt`.
- Verified the app runs and prints an aligned grid (with reasons) for every profile even without `tabulate` installed, via the ASCII fallback.
