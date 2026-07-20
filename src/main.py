"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def print_recommendations(profile_name: str, user_prefs: dict, recommendations: list) -> None:
    """Pretty print recommendations for a given user profile."""
    print("\n" + "="*80)
    print(f"🎵 Profile: {profile_name}")
    print("="*80)
    print(f"User Preferences:")
    print(f"  Genre: {user_prefs.get('genre', 'N/A')}")
    print(f"  Mood: {user_prefs.get('mood', 'N/A')}")
    print(f"  Target Energy: {user_prefs.get('energy', 'N/A')}")
    print(f"  Likes Acoustic: {user_prefs.get('likes_acoustic', True)}")
    print(f"\nTop 5 Recommendations:\n")
    
    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        print(f"{i}. {song['title']} by {song['artist']}")
        print(f"   Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"   Score: {score:.2f}")
        print(f"   Reasons: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    
    if not songs:
        print("Error: No songs loaded. Exiting.")
        return
    
    # Define multiple diverse user profiles for testing
    profiles = [
        {
            "name": "High-Energy Pop Enthusiast",
            "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
        },
        {
            "name": "Chill Lofi Lover",
            "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
        },
        {
            "name": "Intense Rock Fan",
            "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}
        },
        {
            "name": "Ambient Relaxation Seeker",
            "prefs": {"genre": "ambient", "mood": "chill", "energy": 0.25, "likes_acoustic": True}
        },
        {
            "name": "Jazz/Relaxed Listener",
            "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": True}
        }
    ]
    
    # Run recommendations for each profile
    for profile in profiles:
        recommendations = recommend_songs(profile["prefs"], songs, k=5)
        print_recommendations(profile["name"], profile["prefs"], recommendations)
    
    print("="*80)
    print("Evaluation Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
