"""
Player module for Vibe Coder's Catch
Handles the player's boat and fisherman
"""
import pygame
import os
from config import Config

class Player:
    """Class to manage the player's boat and fisherman"""
    
    def __init__(self):
        # Player position (center of boat)
        self.x = Config.PLAYER_POS_X
        self.y = Config.PLAYER_POS_Y
        
        # Load boat sprite
        self.boat_image = self.load_image("player/boat.png")
        self.boat_rect = self.boat_image.get_rect()
        self.boat_rect.centerx = self.x
        self.boat_rect.bottom = self.y
        
        # Load fisherman sprite
        self.fisherman_image = self.load_image("player/fisherman.png")
        self.fisherman_rect = self.fisherman_image.get_rect()
        self.fisherman_rect.centerx = self.x
        self.fisherman_rect.bottom = self.boat_rect.top
        
        # Animation variables
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # milliseconds per frame
        
        # Rod position (where fishing line starts)
        self.rod_pos = (self.x + 20, self.fisherman_rect.centery)
        
    def load_image(self, image_path):
        """Load an image with error handling and placeholder fallback"""
        full_path = os.path.join(Config.SPRITE_PATH, image_path)
        try:
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
            else:
                # Create a placeholder image if file doesn't exist
                placeholder = pygame.Surface((50, 30))
                if "boat" in image_path:
                    placeholder.fill((139, 69, 19))  # Brown for boat
                else:
                    placeholder.fill((255, 0, 0))  # Red for fisherman
                return placeholder
        except pygame.error:
            # Create a placeholder on error
            placeholder = pygame.Surface((50, 30))
            placeholder.fill((255, 0, 0))
            return placeholder
            
    def update(self):
        """Update player animation"""
        # Update animation timer
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_speed:
            self.animation_timer = current_time
            self.animation_frame = (self.animation_frame + 1) % 2  # Toggle between 0 and 1
            
            # In a full implementation, we would load different animation frames here
            # For now, we'll just use the single image
            
    def get_rod_position(self):
        """Get the position where the fishing line should start"""
        return self.rod_pos
        
    def draw(self, surface):
        """Draw the player (boat and fisherman) on the given surface"""
        # Draw boat
        surface.blit(self.boat_image, self.boat_rect)
        
        # Draw fisherman
        surface.blit(self.fisherman_image, self.fisherman_rect)
        
        # For debugging, draw the rod position
        pygame.draw.circle(surface, (255, 0, 0), self.rod_pos, 3)
