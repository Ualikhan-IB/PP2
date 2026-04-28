"""
Persistence Module - Save/Load settings and leaderboard to JSON files
"""

import json
import os

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"


def load_settings():
    """Load settings from JSON file"""
    default_settings = {
        'difficulty': 'medium',
        'car_color': [30, 100, 220],  # BLUE
        'sound': True
    }
    
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            # Convert list back to tuple for color
            if 'car_color' in settings and isinstance(settings['car_color'], list):
                settings['car_color'] = tuple(settings['car_color'])
            return settings
    except (json.JSONDecodeError, IOError):
        return default_settings


def save_settings(settings):
    """Save settings to JSON file"""
    # Convert tuple color to list for JSON serialization
    save_data = settings.copy()
    if 'car_color' in save_data and isinstance(save_data['car_color'], tuple):
        save_data['car_color'] = list(save_data['car_color'])
    
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(save_data, f, indent=2)


def load_leaderboard():
    """Load leaderboard from JSON file, sorted by score (highest first)"""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            data = json.load(f)
            # Sort by score descending
            return sorted(data, key=lambda x: x.get('score', 0), reverse=True)
    except (json.JSONDecodeError, IOError):
        return []


def save_score(name, score, distance, coins):
    """Save a score entry to the leaderboard"""
    leaderboard = load_leaderboard()
    
    # Create new entry
    entry = {
        'name': name[:15],  # Limit name length
        'score': score,
        'distance': distance,
        'coins': coins
    }
    
    leaderboard.append(entry)
    
    # Sort by score descending and keep top 20
    leaderboard.sort(key=lambda x: x.get('score', 0), reverse=True)
    leaderboard = leaderboard[:20]
    
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f, indent=2)


def clear_leaderboard():
    """Clear all scores (for testing)"""
    if os.path.exists(LEADERBOARD_FILE):
        os.remove(LEADERBOARD_FILE)