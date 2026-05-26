import os
import json
from core.config import THEMES

DATA_FILE = "data.json"

DEFAULT_DATA = {
    "theme": "NEON",
    "high_scores": {
        "Snake": 0,
        "Pong": 0,
        "TicTacToe": 0,
        "Flappy": 0,
        "BrickBreaker": 0,
        "SpaceShooter": 0,
        "Tetris": 0,
        "2048": 0,
        "Frogger": 0
    }
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            for key in DEFAULT_DATA:
                if key not in data:
                    data[key] = DEFAULT_DATA[key]
            for game in DEFAULT_DATA["high_scores"]:
                if game not in data["high_scores"]:
                    data["high_scores"][game] = DEFAULT_DATA["high_scores"][game]
            return data
    except (json.JSONDecodeError, IOError):
        return DEFAULT_DATA.copy()

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving data: {e}")

def get_high_score(game_name):
    data = load_data()
    return data["high_scores"].get(game_name, 0)

def set_high_score(game_name, score):
    data = load_data()
    if game_name not in data["high_scores"] or score > data["high_scores"][game_name]:
        data["high_scores"][game_name] = score
        save_data(data)
        return True
    return False

def get_theme_name():
    data = load_data()
    return data.get("theme", "NEON")

def set_theme_name(name):
    data = load_data()
    data["theme"] = name
    save_data(data)
    update_theme()

# Global Theme
theme_name = get_theme_name()
theme = THEMES.get(theme_name, THEMES["NEON"])

def update_theme():
    global theme_name, theme
    theme_name = get_theme_name()
    theme = THEMES.get(theme_name, THEMES["NEON"])
