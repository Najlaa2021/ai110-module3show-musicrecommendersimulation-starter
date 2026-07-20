"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender. It demonstrates:
- the core scoring/ranking (load_songs, score_song, recommend_songs)
- switchable scoring modes (Challenge 2)
- the diversity/fairness penalty (Challenge 3)
- a formatted summary table with reasons (Challenge 4)
"""

import textwrap

from .recommender import load_songs, recommend_songs, SCORING_MODES

# Use the tabulate library for the summary table when it is installed, and fall
# back to a self-contained ASCII table so the app always runs (Challenge 4).
try:
    from tabulate import tabulate as _tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False


def _ascii_table(headers: list, rows: list, wrap_cols: dict = None) -> str:
    """Render a grid table, wrapping the columns named in wrap_cols {index: width}."""
    wrap_cols = wrap_cols or {}
    ncol = len(headers)

    # Pre-wrap each cell into a list of display lines.
    grid = []
    for row in rows:
        cells = []
        for ci, val in enumerate(row):
            text = str(val)
            if ci in wrap_cols:
                cells.append(textwrap.wrap(text, wrap_cols[ci]) or [""])
            else:
                cells.append([text])
        grid.append(cells)

    widths = []
    for ci in range(ncol):
        w = len(str(headers[ci]))
        for cells in grid:
            for line in cells[ci]:
                w = max(w, len(line))
        widths.append(w)

    sep = "+" + "+".join("-" * (widths[c] + 2) for c in range(ncol)) + "+"
    fmt = lambda cols: "| " + " | ".join(cols[c].ljust(widths[c]) for c in range(ncol)) + " |"

    out = [sep, fmt([str(h) for h in headers]), sep]
    for cells in grid:
        height = max(len(c) for c in cells)
        for li in range(height):
            out.append(fmt([cells[c][li] if li < len(cells[c]) else "" for c in range(ncol)]))
        out.append(sep)
    return "\n".join(out)


def format_recommendations_table(recommendations: list) -> str:
    """Build a readable table of recommendations including the scoring reasons."""
    headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Score", "Reasons"]
    rows = []
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        rows.append([
            i, song["title"], song["artist"], song["genre"], song["mood"],
            f"{float(song['energy']):.2f}", f"{score:.2f}", explanation,
        ])
    if _HAS_TABULATE:
        try:
            return _tabulate(rows, headers=headers, tablefmt="grid",
                             maxcolwidths=[None, 22, 16, 10, 10, 6, 6, 44])
        except TypeError:
            # Older tabulate without maxcolwidths — pre-wrap the reasons ourselves.
            for r in rows:
                r[7] = "\n".join(textwrap.wrap(r[7], 44))
            return _tabulate(rows, headers=headers, tablefmt="grid")
    return _ascii_table(headers, rows, wrap_cols={1: 22, 2: 16, 7: 44})


def print_recommendations(profile_name: str, user_prefs: dict, recommendations: list,
                          mode: str = "balanced", diversity: bool = False) -> None:
    """Pretty print a profile's recommendations as a summary table."""
    print("\n" + "=" * 80)
    print(f"🎵 Profile: {profile_name}")
    print("=" * 80)
    print("User Preferences:")
    print(f"  Genre: {user_prefs.get('genre', 'N/A')} | Mood: {user_prefs.get('mood', 'N/A')} "
          f"| Target Energy: {user_prefs.get('energy', 'N/A')} "
          f"| Likes Acoustic: {user_prefs.get('likes_acoustic', True)}")
    # Show any advanced preferences in play (Challenge 1).
    advanced = {k: user_prefs[k] for k in
                ("favorite_decade", "mood_tags", "favorite_language",
                 "likes_instrumental", "popularity_pref") if k in user_prefs}
    if advanced:
        print(f"  Advanced: {advanced}")
    print(f"  Scoring mode: {mode} | Diversity penalty: {'on' if diversity else 'off'}")
    print(f"\nTop {len(recommendations)} Recommendations:\n")
    print(format_recommendations_table(recommendations))


def demo_scoring_modes(user_prefs: dict, songs: list, k: int = 3) -> None:
    """Show how the same profile reranks under each scoring mode (Challenge 2)."""
    print("\n" + "=" * 80)
    print("🎛  Scoring Mode Comparison  (High-Energy Pop profile, top 3)")
    print("=" * 80)
    for mode in SCORING_MODES:
        top = recommend_songs(user_prefs, songs, k=k, mode=mode)
        picks = ", ".join(f"{s['title']} ({score:.2f})" for s, score, _ in top)
        print(f"  {mode:15}: {picks}")


def main() -> None:
    songs = load_songs("data/songs.csv")

    if not songs:
        print("Error: No songs loaded. Exiting.")
        return

    # Each profile can pick a scoring mode and toggle the diversity penalty.
    profiles = [
        {
            "name": "High-Energy Pop Enthusiast",
            "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8,
                      "likes_acoustic": False, "popularity_pref": "mainstream"},
            "mode": "balanced", "diversity": True,
        },
        {
            "name": "Chill Lofi Lover",
            "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True,
                      "favorite_decade": 2020, "mood_tags": ["focused", "mellow"],
                      "favorite_language": "instrumental", "likes_instrumental": True,
                      "popularity_pref": "niche"},
            "mode": "mood-first", "diversity": True,
        },
        {
            "name": "Intense Rock Fan",
            "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
            "mode": "energy-focused", "diversity": False,
        },
        {
            "name": "Ambient Relaxation Seeker",
            "prefs": {"genre": "ambient", "mood": "chill", "energy": 0.25, "likes_acoustic": True,
                      "likes_instrumental": True},
            "mode": "balanced", "diversity": True,
        },
        {
            "name": "Jazz/Relaxed Listener",
            "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": True},
            "mode": "balanced", "diversity": False,
        },
        # --- Adversarial / edge-case profiles (System Evaluation phase) ---
        {
            "name": "Contradictory Vibe (high energy + peaceful + acoustic)",
            "prefs": {"genre": "rock", "mood": "peaceful", "energy": 0.9, "likes_acoustic": True},
            "mode": "balanced", "diversity": False,
        },
        {
            "name": "Ghost Genre (metal/angry not in catalog)",
            "prefs": {"genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": False},
            "mode": "balanced", "diversity": True,
        },
        {
            "name": "Acoustic Raver (loves acoustic but wants max energy)",
            "prefs": {"genre": "electronic", "mood": "dreamy", "energy": 0.98, "likes_acoustic": True},
            "mode": "balanced", "diversity": False,
        },
    ]

    # Run recommendations for each profile using its chosen mode and diversity setting.
    for profile in profiles:
        mode = profile.get("mode", "balanced")
        diversity = profile.get("diversity", False)
        recommendations = recommend_songs(profile["prefs"], songs, k=5,
                                          mode=mode, diversity=diversity)
        print_recommendations(profile["name"], profile["prefs"], recommendations,
                              mode=mode, diversity=diversity)

    # Demonstrate how scoring modes change the ranking for one profile.
    demo_scoring_modes(profiles[0]["prefs"], songs)

    print("\n" + "=" * 80)
    print("Evaluation Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
