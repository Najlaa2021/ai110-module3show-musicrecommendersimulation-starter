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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by their score for this user."""
        user_prefs = asdict(user)
        scored = [(song, score_song(user_prefs, asdict(song))[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why this song scored as it did."""
        score, reasons = score_song(asdict(user), asdict(song))
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

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences using weighted feature matching.
    Returns (score, list_of_reasons) where reasons explain the score breakdown.
    """
    score = 0.0
    reasons = []
    
    # Extract user preferences (handle both singular and plural key names)
    user_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre', '')
    user_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood', '')
    user_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
    user_likes_acoustic = user_prefs.get('likes_acoustic', True)
    
    # 1. Genre match: +2.0 points
    if song.get('genre', '').lower() == user_genre.lower():
        score += 2.0
        reasons.append("genre match (+2.0)")
    
    # 2. Mood match: +1.0 point
    if song.get('mood', '').lower() == user_mood.lower():
        score += 1.0
        reasons.append("mood match (+1.0)")
    
    # 3. Energy similarity: up to +1.0 points
    song_energy = float(song.get('energy', 0.5))
    energy_diff = abs(song_energy - user_energy)
    energy_score = max(0, 1.0 - energy_diff)
    score += energy_score
    reasons.append(f"energy similarity ({energy_score:.2f})")
    
    # 4. Danceability bonus: +0.5 if high danceability and user prefers high energy
    song_danceability = float(song.get('danceability', 0))
    if song_danceability > 0.7 and user_energy > 0.7:
        score += 0.5
        reasons.append("danceability bonus (+0.5)")
    
    # 5. Acousticness penalty: -0.5 if user doesn't like acoustic and song is acoustic
    song_acousticness = float(song.get('acousticness', 0))
    if not user_likes_acoustic and song_acousticness > 0.6:
        score -= 0.5
        reasons.append("acoustic penalty (-0.5)")

    # --- Advanced features (Challenge 1) ---------------------------------
    # These are secondary signals: each is smaller than genre/mood so it
    # refines ties rather than overriding the primary vibe.

    # 6. Release-decade match: +0.75 if the song is from the user's favorite decade.
    user_decade = user_prefs.get('favorite_decade')
    if user_decade is not None and 'release_decade' in song:
        if int(song.get('release_decade')) == int(user_decade):
            score += 0.75
            reasons.append(f"decade match {user_decade}s (+0.75)")

    # 7. Detailed mood-tag overlap: +0.4 per shared tag, capped at +0.8.
    user_tags = user_prefs.get('mood_tags') or []
    if isinstance(user_tags, str):
        user_tags = [t.strip() for t in user_tags.split('|') if t.strip()]
    song_tags = [t.strip().lower() for t in str(song.get('mood_tags', '')).split('|') if t.strip()]
    if user_tags and song_tags:
        shared = [t for t in user_tags if t.lower() in song_tags]
        if shared:
            tag_score = min(0.8, 0.4 * len(shared))
            score += tag_score
            reasons.append(f"mood tags {shared} (+{tag_score:.2f})")

    # 8. Language match: +0.5 if the song is in the user's preferred language.
    user_language = (user_prefs.get('favorite_language') or '').lower()
    if user_language and str(song.get('language', '')).lower() == user_language:
        score += 0.5
        reasons.append(f"language match ({user_language}) (+0.5)")

    # 9. Instrumental preference: +/-0.3 for clearly instrumental tracks.
    likes_instrumental = user_prefs.get('likes_instrumental')
    song_instrumentalness = float(song.get('instrumentalness', 0) or 0)
    if likes_instrumental is not None and song_instrumentalness > 0.5:
        if likes_instrumental:
            score += 0.3
            reasons.append("instrumental bonus (+0.3)")
        else:
            score -= 0.3
            reasons.append("instrumental penalty (-0.3)")

    # 10. Popularity preference: up to +0.5 toward mainstream or niche taste.
    popularity_pref = (user_prefs.get('popularity_pref') or 'any').lower()
    if popularity_pref in ('mainstream', 'niche') and 'popularity' in song:
        pop_norm = max(0.0, min(1.0, float(song.get('popularity', 50)) / 100.0))
        pop_score = 0.5 * (pop_norm if popularity_pref == 'mainstream' else (1.0 - pop_norm))
        score += pop_score
        reasons.append(f"{popularity_pref} taste (+{pop_score:.2f})")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores all songs and returns the top k recommendations ranked by score.
    Returns list of (song_dict, score, explanation_string) tuples.
    """
    scored_songs = []
    
    # Score every song in the catalog
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored_songs.append((song, score, explanation))
    
    # Sort by score in descending order (highest scores first)
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k results
    return scored_songs[:k]
