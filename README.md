# 🎵 Music Recommender Simulation

## Project Summary

This version of the music recommender simulation will model a simple content-based recommendation system that suggests songs by matching a user’s preferences to the musical attributes of each track. Instead of relying on the behavior of many other listeners, it uses song metadata such as genre, mood, energy, tempo, and acousticness to estimate how well a song fits a listener’s taste profile.

---

## How The System Works

Real streaming platforms often combine many signals, such as likes, skips, playlists, and listening habits, to predict what a user will enjoy next. In this simulation, I am using a simpler content-based approach: each song is described by features like genre, mood, energy, tempo, valence, danceability, and acousticness, while the user profile stores the listener’s preferred genre, preferred mood, target energy level, and whether they tend to like acoustic songs. The recommender will score each song based on how closely its features match the user’s preferences and then rank the highest-scoring songs at the top.

### Features used in the simulation

- `Song` objects will use: genre, mood, energy, tempo_bpm, valence, danceability, acousticness, title, and artist
- `UserProfile` objects will use: favorite_genre, favorite_mood, target_energy, and likes_acoustic
### Example User Profile

```python
{
    "favorite_genre": "indie pop",
    "favorite_mood": "happy",
    "target_energy": 0.75,
    "likes_acoustic": False
}
```

This profile represents a listener who enjoys upbeat, energetic indie pop music with happy vibes, and prefers songs with electronic/produced sounds over acoustic arrangements.

### Algorithm Recipe (Scoring Logic)

The recommender uses a **weighted feature-matching approach** to score each song:

1. **Genre Match**: +2.0 points if the song's genre matches the user's favorite genre
2. **Mood Match**: +1.0 point if the song's mood matches the user's favorite mood
3. **Energy Similarity**: Up to +1.0 points based on how close the song's energy is to the user's target energy
   - Formula: `1.0 - abs(song_energy - target_energy)` (rewards closer matches)
4. **Danceability Bonus**: +0.5 points if the song's danceability is high (>0.7) and user's energy target is high
5. **Acousticness Penalty**: -0.5 points if `likes_acoustic` is False and the song's acousticness is high (>0.6)

**Final Score**: Sum of all component scores (higher is better)

**Ranking**: Songs are ranked by score in descending order; the top K songs are recommended.

### Data Flow Diagram

```
┌─────────────────────┐
│   User Preferences  │
│  (favorite_genre,   │
│   favorite_mood,    │
│   target_energy)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│   Loop: For Each Song in Catalog        │
│  ┌───────────────────────────────────┐  │
│  │ Calculate Score Using Rules:      │  │
│  │ - Genre match points              │  │
│  │ - Mood match points               │  │
│  │ - Energy similarity points        │  │
│  │ - Danceability & acousticness adj │  │
│  └───────────────────────────────────┘  │
│   Store (Song, Score) pair              │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Sort by Score      │
│  (descending)       │
└──────────┬──────────┘
           │
           ▼
┌────────────────────────────┐
│ Return Top K Recommendations│
│ with explanations          │
└────────────────────────────┘
```

### Potential Biases and Limitations

- **Genre Bias**: The system heavily weights exact genre matches (+2.0 points), which means songs from adjacent genres (e.g., "indie pop" vs. "indie") may be unfairly penalized even if they fit the user's taste well.
- **Limited Feature Space**: With only 10 song features, the system cannot understand lyrics, artist popularity, or temporal trends (e.g., "songs trending now").
- **Mood Oversimplification**: A binary mood match (e.g., "happy" vs. "not happy") is coarse; songs with similar emotional tones but different mood labels may be missed.
- **Acousticness Assumption**: The penalty for acoustic songs assumes all users with `likes_acoustic=False` want electronic music, but acoustic indie pop or acoustic R&B may still appeal to them.
- **Catalog Size**: With only 18 songs, the recommender has limited diversity and may make recommendations based on the best available match rather than a truly good fit.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Running `python -m src.main` scores all 18 songs against each user profile and prints a ranked, explained list. Below is the output for the default **pop / happy / high-energy** profile:

```
Loading songs from data/songs.csv...
Loaded 18 songs.

================================================================================
🎵 Profile: High-Energy Pop Enthusiast
================================================================================
User Preferences:
  Genre: pop
  Mood: happy
  Target Energy: 0.8
  Likes Acoustic: False

Top 5 Recommendations:

1. Sunrise City by Neon Echo
   Genre: pop | Mood: happy | Energy: 0.82
   Score: 4.48
   Reasons: genre match (+2.0); mood match (+1.0); energy similarity (0.98); danceability bonus (+0.5)

2. Gym Hero by Max Pulse
   Genre: pop | Mood: intense | Energy: 0.93
   Score: 3.37
   Reasons: genre match (+2.0); energy similarity (0.87); danceability bonus (+0.5)

3. Rooftop Lights by Indigo Parade
   Genre: indie pop | Mood: happy | Energy: 0.76
   Score: 2.46
   Reasons: mood match (+1.0); energy similarity (0.96); danceability bonus (+0.5)

4. Golden Hour Drive by Arden West
   Genre: hip-hop | Mood: confident | Energy: 0.81
   Score: 1.49
   Reasons: energy similarity (0.99); danceability bonus (+0.5)

5. Night Drive Loop by Neon Echo
   Genre: synthwave | Mood: moody | Energy: 0.75
   Score: 1.45
   Reasons: energy similarity (0.95); danceability bonus (+0.5)
```

The top result (**Sunrise City**) is the only track that matches genre, mood, *and* the target energy, so it earns the highest score — exactly what we'd expect for this profile.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



