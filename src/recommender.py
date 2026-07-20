from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Advanced features (Challenge 1) — defaults keep existing callers/tests valid.
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: str = ""
    language: str = "english"
    instrumentalness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Advanced preferences (Challenge 1) — defaults keep existing callers/tests valid.
    favorite_decade: Optional[int] = None
    mood_tags: Optional[List[str]] = None
    favorite_language: str = ""
    likes_instrumental: Optional[bool] = None
    popularity_pref: str = "any"  # "mainstream" | "niche" | "any"

@dataclass
class ScoringWeights:
    """
    A scoring strategy: a multiplier for each scoring component.

    This is the 'Strategy' in a lightweight Strategy pattern — score_song runs
    one algorithm, and swapping the ScoringWeights object swaps the ranking
    behavior without touching the scoring code. Presets live in SCORING_MODES.
    """
    genre: float = 1.0
    mood: float = 1.0
    energy: float = 1.0
    danceability: float = 1.0
    acoustic: float = 1.0
    decade: float = 1.0
    mood_tags: float = 1.0
    language: float = 1.0
    instrumental: float = 1.0
    popularity: float = 1.0


# Named ranking strategies the user can switch between (Challenge 2).
SCORING_MODES: Dict[str, ScoringWeights] = {
    "balanced": ScoringWeights(),
    "genre-first": ScoringWeights(genre=1.5, mood=0.75, energy=0.5, danceability=0.5,
                                  decade=0.5, mood_tags=0.5, language=0.5,
                                  instrumental=0.5, popularity=0.5),
    "mood-first": ScoringWeights(genre=0.75, mood=2.0, energy=0.75, mood_tags=1.75,
                                 danceability=0.75),
    "energy-focused": ScoringWeights(genre=0.5, mood=0.5, energy=2.5, danceability=1.5,
                                     decade=0.5, mood_tags=0.5, language=0.5,
                                     instrumental=0.5, popularity=0.5),
}

DEFAULT_MODE = "balanced"


def get_strategy(mode) -> ScoringWeights:
    """Resolve a mode name (or ScoringWeights) into a ScoringWeights strategy."""
    if isinstance(mode, ScoringWeights):
        return mode
    if mode is None:
        return SCORING_MODES[DEFAULT_MODE]
    return SCORING_MODES.get(str(mode).lower(), SCORING_MODES[DEFAULT_MODE])


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, mode=None) -> List[Song]:
        """Return the top-k songs ranked by their score for this user under `mode`."""
        user_prefs = asdict(user)
        scored = [(song, score_song(user_prefs, asdict(song), mode=mode)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song, mode=None) -> str:
        """Return a human-readable explanation of why this song scored as it did."""
        score, reasons = score_song(asdict(user), asdict(song), mode=mode)
        detail = "; ".join(reasons) if reasons else "no strong matches, ranked by overall fit"
        return f"{song.title} scored {score:.2f} — {detail}"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file and converts numeric values to floats.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields to floats
                row['id'] = int(row['id'])
                row['energy'] = float(row['energy'])
                row['tempo_bpm'] = float(row['tempo_bpm'])
                row['valence'] = float(row['valence'])
                row['danceability'] = float(row['danceability'])
                row['acousticness'] = float(row['acousticness'])
                # Advanced features (Challenge 1) — optional so older CSVs still load.
                if 'popularity' in row:
                    row['popularity'] = int(row['popularity'])
                if 'release_decade' in row:
                    row['release_decade'] = int(row['release_decade'])
                if 'instrumentalness' in row:
                    row['instrumentalness'] = float(row['instrumentalness'])
                songs.append(row)
        print(f"Loaded {len(songs)} songs.")
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
    except Exception as e:
        print(f"Error loading songs: {e}")
    return songs

def score_song(user_prefs: Dict, song: Dict, mode=None) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using weighted feature matching.

    `mode` selects a scoring strategy (a name from SCORING_MODES or a
    ScoringWeights object); it defaults to the balanced strategy so existing
    callers keep their original behavior. Returns (score, list_of_reasons).
    """
    w = get_strategy(mode)
    score = 0.0
    reasons = []

    def add(points: float, label: str):
        """Apply a component's strategy weight, add to score, and log a reason."""
        weighted = points * label_weight
        if weighted != 0:
            nonlocal score
            score += weighted
            reasons.append(f"{label} ({weighted:+.2f})")
        return weighted

    # Extract user preferences (handle both singular and plural key names)
    user_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre', '')
    user_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood', '')
    user_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
    user_likes_acoustic = user_prefs.get('likes_acoustic', True)

    # 1. Genre match
    label_weight = w.genre
    if song.get('genre', '').lower() == user_genre.lower():
        add(2.0, "genre match")

    # 2. Mood match
    label_weight = w.mood
    if song.get('mood', '').lower() == user_mood.lower():
        add(1.0, "mood match")

    # 3. Energy similarity (always contributes)
    label_weight = w.energy
    song_energy = float(song.get('energy', 0.5))
    energy_base = max(0.0, 1.0 - abs(song_energy - user_energy))
    add(energy_base, "energy similarity")

    # 4. Danceability bonus: high danceability for a high-energy listener
    label_weight = w.danceability
    if float(song.get('danceability', 0)) > 0.7 and user_energy > 0.7:
        add(0.5, "danceability bonus")

    # 5. Acousticness penalty: user dislikes acoustic but song is acoustic
    label_weight = w.acoustic
    if not user_likes_acoustic and float(song.get('acousticness', 0)) > 0.6:
        add(-0.5, "acoustic penalty")

    # --- Advanced features (Challenge 1) ---------------------------------
    # Secondary signals: each is smaller than genre/mood so it refines ties.

    # 6. Release-decade match
    label_weight = w.decade
    user_decade = user_prefs.get('favorite_decade')
    if user_decade is not None and 'release_decade' in song:
        if int(song.get('release_decade')) == int(user_decade):
            add(0.75, f"decade match {user_decade}s")

    # 7. Detailed mood-tag overlap: +0.4 per shared tag, capped at +0.8
    label_weight = w.mood_tags
    user_tags = user_prefs.get('mood_tags') or []
    if isinstance(user_tags, str):
        user_tags = [t.strip() for t in user_tags.split('|') if t.strip()]
    song_tags = [t.strip().lower() for t in str(song.get('mood_tags', '')).split('|') if t.strip()]
    if user_tags and song_tags:
        shared = [t for t in user_tags if t.lower() in song_tags]
        if shared:
            add(min(0.8, 0.4 * len(shared)), f"mood tags {shared}")

    # 8. Language match
    label_weight = w.language
    user_language = (user_prefs.get('favorite_language') or '').lower()
    if user_language and str(song.get('language', '')).lower() == user_language:
        add(0.5, f"language match ({user_language})")

    # 9. Instrumental preference: +/-0.3 for clearly instrumental tracks
    label_weight = w.instrumental
    likes_instrumental = user_prefs.get('likes_instrumental')
    if likes_instrumental is not None and float(song.get('instrumentalness', 0) or 0) > 0.5:
        add(0.3 if likes_instrumental else -0.3,
            "instrumental bonus" if likes_instrumental else "instrumental penalty")

    # 10. Popularity preference: up to +0.5 toward mainstream or niche taste
    label_weight = w.popularity
    popularity_pref = (user_prefs.get('popularity_pref') or 'any').lower()
    if popularity_pref in ('mainstream', 'niche') and 'popularity' in song:
        pop_norm = max(0.0, min(1.0, float(song.get('popularity', 50)) / 100.0))
        pop_base = pop_norm if popularity_pref == 'mainstream' else (1.0 - pop_norm)
        add(0.5 * pop_base, f"{popularity_pref} taste")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode=None) -> List[Tuple[Dict, float, str]]:
    """
    Scores all songs and returns the top k recommendations ranked by score.

    `mode` selects a scoring strategy (see SCORING_MODES). Returns a list of
    (song_dict, score, explanation_string) tuples.
    """
    scored_songs = []

    # Score every song in the catalog under the chosen strategy
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        explanation = "; ".join(reasons)
        scored_songs.append((song, score, explanation))

    # Sort by score in descending order (highest scores first)
    scored_songs.sort(key=lambda x: x[1], reverse=True)

    # Return top k results
    return scored_songs[:k]
