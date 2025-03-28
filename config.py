"""
Configuration settings for Vibe Coder's Catch
Contains game constants, screen dimensions, colors, etc.
"""

class Config:
    """Class containing game configuration constants"""
    
    # Screen settings
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    
    # Colors (RGB)
    BACKGROUND_COLOR = (135, 206, 235)  # Sky blue
    WATER_COLOR = (0, 105, 148)
    TEXT_COLOR = (255, 255, 255)
    TEXT_SHADOW_COLOR = (0, 0, 0)
    BUTTON_COLOR = (50, 50, 200)
    BUTTON_HOVER_COLOR = (70, 70, 220)
    BUTTON_TEXT_COLOR = (255, 255, 255)
    LINE_COLOR = (50, 50, 50)
    
    # Game settings
    BASE_ROUND_DURATION = 10000  # milliseconds (10 seconds)
    BASE_LINE_SPEED = 0.5  # pixels per frame (reduced for slower descent)
    BASE_REEL_SPEED = 5  # pixels per frame
    BASE_HOOK_CAPACITY = 4  # number of fish
    BASE_MAX_DEPTH = 300  # pixels
    
    # Upgrade settings
    UPGRADE_COSTS = {
        "line_length": [100, 250, 500, 1000, 2000],
        "hook_capacity": [200, 400, 800, 1600, 3200],
        "round_timer": [150, 300, 600, 1200, 2400]
    }
    
    # Upgrade effects
    DEPTH_INCREASE_PER_LEVEL = 100  # pixels
    CAPACITY_INCREASE_PER_LEVEL = 1  # fish
    TIMER_INCREASE_PER_LEVEL = 5000  # milliseconds (5 seconds)
    
    # Depth zones (in pixels from top of water)
    DEPTH_ZONES = {
        "surface": (0, 100),
        "shallows": (101, 200),
        "mid_water": (201, 300),
        "deep_sea": (301, 400),
        "abyss": (401, 500)
    }
    
    # Asset paths
    ASSET_PATH = "assets/"
    SPRITE_PATH = ASSET_PATH + "sprites/"
    AUDIO_PATH = ASSET_PATH + "audio/"
    FONT_PATH = ASSET_PATH + "fonts/"
    
    # Player settings
    PLAYER_POS_X = SCREEN_WIDTH // 2
    PLAYER_POS_Y = 50  # Distance from top of screen
    
    # Hook settings
    HOOK_WIDTH = 20
    HOOK_HEIGHT = 20
    
    # Fish settings
    MIN_FISH_SPEED = 1
    MAX_FISH_SPEED = 3
    FISH_SPAWN_RATE = 1  # Fish per second
    
    # UI settings
    UI_PADDING = 10
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    BUTTON_RADIUS = 10  # For rounded corners
    
    # Save file
    SAVE_FILE = "saves/game_save.json"
