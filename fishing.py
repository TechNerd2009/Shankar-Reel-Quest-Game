"""
Fishing module for Vibe Coder's Catch
Handles the fishing line, hook, and catching mechanics
"""
import pygame
import os
import random
from config import Config

class FishingLine:
    """Class to manage the fishing line and hook"""
    
    def __init__(self, player, game_state=None):
        self.player = player
        self.game_state = game_state  # Store reference to game state
        
        # Line properties
        self.start_pos = player.get_rod_position()
        self.current_depth = 0  # This now represents virtual depth, not visual position
        self.descending = True
        
        # Fixed hook vertical position (constant screen position)
        self.hook_fixed_y = Config.SCREEN_HEIGHT // 2  # Middle of the screen
        
        # Hook properties
        self.hook_image = self.load_image("hook.png")
        self.hook_rect = self.hook_image.get_rect()
        self.hook_rect.centerx = self.start_pos[0]
        self.hook_rect.top = self.hook_fixed_y
        
        # Horizontal movement properties
        self.horizontal_offset = 0  # Offset from the rod position
        self.max_horizontal_range = 350  # Maximum horizontal distance from center (increased from 200)
        
        # Caught fish
        self.caught_fish = []
        
    def load_image(self, image_path):
        """Load an image with error handling and placeholder fallback"""
        full_path = os.path.join(Config.SPRITE_PATH, image_path)
        try:
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
            else:
                # Create a placeholder image
                placeholder = pygame.Surface((Config.HOOK_WIDTH, Config.HOOK_HEIGHT))
                placeholder.fill((200, 200, 200))  # Gray for hook
                pygame.draw.circle(placeholder, (150, 150, 150), 
                                  (Config.HOOK_WIDTH // 2, Config.HOOK_HEIGHT // 2), 
                                  min(Config.HOOK_WIDTH, Config.HOOK_HEIGHT) // 2 - 2)
                return placeholder
        except pygame.error:
            # Create a placeholder on error
            placeholder = pygame.Surface((Config.HOOK_WIDTH, Config.HOOK_HEIGHT))
            placeholder.fill((200, 200, 200))
            return placeholder
            
    def update(self):
        """Update fishing line and hook position"""
        # Update start position (in case player moved)
        self.start_pos = self.player.get_rod_position()
        
        if self.descending:
            # Increase virtual depth (camera will follow)
            self.current_depth += Config.BASE_LINE_SPEED
            
            # Check if max depth reached
            if self.current_depth >= self.get_max_depth():
                self.current_depth = self.get_max_depth()
                # Stay at max depth instead of reeling back in
                # self.descending = False
        else:
            # Only used when manually reeling in (e.g., when round ends)
            self.current_depth -= Config.BASE_REEL_SPEED
            
            # Check if fully reeled in
            if self.current_depth <= 0:
                self.current_depth = 0
                # Reset for next cast
                self.descending = True
                self.horizontal_offset = 0
                self.caught_fish = []
                
        # Update hook position - only horizontal position changes
        # Vertical position stays fixed at hook_fixed_y
        self.hook_rect.centerx = self.start_pos[0] + self.horizontal_offset
        self.hook_rect.top = self.hook_fixed_y
        
    def add_caught_fish(self, fish):
        """Add a fish to the caught list if there's capacity"""
        if len(self.caught_fish) < self.get_hook_capacity():
            # Check if this fish is already caught (prevent duplicates)
            if fish not in self.caught_fish:
                self.caught_fish.append(fish)
                # Don't change depth or direction when catching a fish
                return True
        return False
        
    def is_at_capacity(self):
        """Check if hook is at maximum capacity"""
        return len(self.caught_fish) >= self.get_hook_capacity()
        
    def reached_max_depth(self):
        """Check if the hook has reached maximum depth"""
        return self.current_depth >= self.get_max_depth() and not self.descending
        
    def get_hook_rect(self):
        """Get the rectangle representing the hook for collision detection"""
        return self.hook_rect
        
    def get_current_depth(self):
        """Get the current depth of the hook"""
        return self.current_depth
        
    def get_caught_fish(self):
        """Get the list of caught fish"""
        return self.caught_fish
        
    def reset(self):
        """Reset the fishing line for a new round but preserve depth"""
        # Don't reset depth - preserve current depth
        # Only reset direction, horizontal offset, and caught fish
        self.descending = True
        self.horizontal_offset = 0
        self.caught_fish = []
        
    def full_reset(self):
        """Completely reset the fishing line including depth"""
        self.current_depth = 0  # Reset depth to surface
        self.descending = True
        self.horizontal_offset = 0
        self.caught_fish = []
        
    def get_max_depth(self):
        """Get the maximum depth from game state"""
        if self.game_state:
            return self.game_state.get_max_depth()
        return Config.BASE_MAX_DEPTH
        
    # Removed get_reel_speed method as it's no longer needed
    # Fishing line now stays at max depth until round ends
        
    def get_hook_capacity(self):
        """Get the hook capacity from game state"""
        if self.game_state:
            return self.game_state.get_hook_capacity()
        return Config.BASE_HOOK_CAPACITY
        
    def draw(self, surface):
        """Draw the fishing line and hook"""
        # Draw the line (curved based on horizontal offset)
        if abs(self.horizontal_offset) > 10:
            # Draw a curved line when there's significant horizontal offset
            # Calculate control point for the curve
            control_point_x = self.start_pos[0] + (self.horizontal_offset * 0.5)
            # Control point y is halfway between start and hook
            control_point_y = self.start_pos[1] + (self.hook_fixed_y - self.start_pos[1]) * 0.5
            
            # Draw the curved line using multiple short line segments
            steps = 20
            prev_point = self.start_pos
            
            for i in range(1, steps + 1):
                t = i / steps
                # Quadratic Bezier curve formula
                x = (1-t)**2 * self.start_pos[0] + 2*(1-t)*t * control_point_x + t**2 * self.hook_rect.centerx
                y = (1-t)**2 * self.start_pos[1] + 2*(1-t)*t * control_point_y + t**2 * self.hook_rect.top
                
                current_point = (int(x), int(y))
                pygame.draw.line(surface, Config.LINE_COLOR, prev_point, current_point, 2)
                prev_point = current_point
        else:
            # Draw a straight line when there's minimal horizontal offset
            pygame.draw.line(
                surface,
                Config.LINE_COLOR,
                self.start_pos,
                (self.hook_rect.centerx, self.hook_rect.top),
                2
            )
        
        # Draw the hook
        surface.blit(self.hook_image, self.hook_rect)
        
        # Draw caught fish
        for i, fish in enumerate(self.caught_fish):
            # Position fish along the line above the hook
            offset = (i + 1) * 30  # Space fish 30 pixels apart
            
            # Add a small wiggle effect for more natural movement
            wiggle_x = random.randint(-3, 3) if random.random() < 0.4 else 0
            
            # Position fish with wiggle effect
            fish_pos = (self.hook_rect.centerx + wiggle_x, self.hook_rect.top - offset)
            fish.draw_on_hook(surface, fish_pos)
