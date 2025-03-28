"""
Sound module for Vibe Coder's Catch
Handles sound effects and music
"""
import pygame
import os
from config import Config

class SoundManager:
    """Class to manage game sounds and music"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Sound effect dictionary
        self.sfx = {}
        
        # Load sound effects
        self.load_sound_effects()
        
    def load_sound_effects(self):
        """Load all sound effects"""
        # Define sound effects to load
        sound_files = {
            "cast": "sfx/cast.wav",
            "catch": "sfx/catch.wav",
            "reel_complete": "sfx/reel_complete.wav",
            "purchase": "sfx/purchase.wav",
            "reset": "sfx/reset.wav"
        }
        
        # Load each sound effect
        for name, file_path in sound_files.items():
            full_path = os.path.join(Config.AUDIO_PATH, file_path)
            try:
                if os.path.exists(full_path):
                    self.sfx[name] = pygame.mixer.Sound(full_path)
                else:
                    print(f"Sound file not found: {full_path}")
            except pygame.error:
                print(f"Error loading sound: {full_path}")
                
    def play_sfx(self, name, volume=1.0):
        """Play a sound effect by name"""
        if name in self.sfx:
            self.sfx[name].set_volume(volume)
            self.sfx[name].play()
        else:
            print(f"Sound effect not found: {name}")
