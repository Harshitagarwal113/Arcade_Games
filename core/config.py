# core/config.py

WIDTH = 800
HEIGHT = 600
FPS = 60

THEMES = {
    "NEON": {
        "BG_COLOR": (20, 15, 35),
        "PRIMARY": (57, 255, 20),    
        "SECONDARY": (255, 20, 147), 
        "TERTIARY": (0, 255, 255),   
        "TEXT": (255, 255, 255),     
        "TEXT_MUTED": (100, 100, 120),
        "PANEL": (30, 30, 50),       
        "SHADOW": (10, 5, 20),
        "SNAKE_HEAD": (57, 255, 20),
        "SNAKE_BODY": (100, 255, 100),
        "FOOD": (255, 20, 147)
    },
    "RETRO": {
        "BG_COLOR": (40, 40, 40),
        "PRIMARY": (245, 152, 66),   
        "SECONDARY": (66, 245, 138), 
        "TERTIARY": (245, 66, 66),   
        "TEXT": (230, 230, 230),
        "TEXT_MUTED": (150, 150, 150),
        "PANEL": (60, 60, 60),
        "SHADOW": (20, 20, 20),
        "SNAKE_HEAD": (245, 152, 66),
        "SNAKE_BODY": (200, 120, 50),
        "FOOD": (245, 66, 66)
    },
    "MIDNIGHT": {
        "BG_COLOR": (10, 10, 15),
        "PRIMARY": (150, 100, 255),  
        "SECONDARY": (100, 200, 255),
        "TERTIARY": (255, 100, 150), 
        "TEXT": (220, 220, 255),
        "TEXT_MUTED": (80, 80, 120),
        "PANEL": (25, 25, 35),
        "SHADOW": (5, 5, 10),
        "SNAKE_HEAD": (150, 100, 255),
        "SNAKE_BODY": (120, 80, 200),
        "FOOD": (255, 100, 150)
    },
    "CYBERPUNK": {
        "BG_COLOR": (25, 0, 51),     
        "PRIMARY": (255, 255, 0),    
        "SECONDARY": (0, 255, 255),  
        "TERTIARY": (255, 0, 60),    
        "TEXT": (255, 255, 255),
        "TEXT_MUTED": (120, 80, 150),
        "PANEL": (50, 0, 80),
        "SHADOW": (10, 0, 20),
        "SNAKE_HEAD": (255, 255, 0),
        "SNAKE_BODY": (200, 200, 0),
        "FOOD": (255, 0, 60)
    }
}
