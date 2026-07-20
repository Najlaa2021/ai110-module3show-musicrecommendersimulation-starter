from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

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
