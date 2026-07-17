# 🎵 Music Recommender Simulation

## Project Summary

This version of the music recommender simulation will model a simple content-based recommendation system that suggests songs by matching a user’s preferences to the musical attributes of each track. Instead of relying on the behavior of many other listeners, it uses song metadata such as genre, mood, energy, tempo, and acousticness to estimate how well a song fits a listener’s taste profile.

---

## How The System Works

Real streaming platforms often combine many signals, such as likes, skips, playlists, and listening habits, to predict what a user will enjoy next. In this simulation, I am using a simpler content-based approach: each song is described by features like genre, mood, energy, tempo, valence, danceability, and acousticness, while the user profile stores the listener’s preferred genre, preferred mood, target energy level, and whether they tend to like acoustic songs. The recommender will score each song based on how closely its features match the user’s preferences and then rank the highest-scoring songs at the top.

### Features used in the simulation

- `Song` objects will use: genre, mood, energy, tempo_bpm, valence, danceability, acousticness, title, and artist
- `UserProfile` objects will use: favorite_genre, favorite_mood, target_energy, and likes_acoustic

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

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

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



