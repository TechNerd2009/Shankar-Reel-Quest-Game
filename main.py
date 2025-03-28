#!/usr/bin/env python3
"""
Vibe Coder's Catch - A fishing adventure game built with Pygame
Main game script containing initialization and game loop
"""
import pygame
import sys
from enum import Enum

# Import game modules
# These will be created in separate files
from config import Config
from game_state import GameState
from player import Player
from fishing import FishingLine
from fish import FishManager
from ui import UI
from sound import SoundManager

class GameScreen(Enum):
    """Enum for different game screens/states"""
    MAIN_GAME = 0
    RESULTS = 1
    SHOP = 2

class Game:
    """Main game class that manages the game loop and states"""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Vibe Coder's Catch")
        
        # Create the screen
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Initialize game components
        self.game_state = GameState()
        self.player = Player()
        self.fishing_line = FishingLine(self.player, self.game_state)  # Pass game_state to fishing line
        self.fish_manager = FishManager(self.game_state)
        self.ui = UI(self.game_state)
        self.sound_manager = SoundManager()
        
        # Game state variables
        self.current_screen = GameScreen.MAIN_GAME
        self.round_active = False
        self.round_start_time = 0
        self.round_timer = 0
        
        # Load game data if available
        self.game_state.load_game()
        
    def start_round(self):
        """Start a new fishing round"""
        self.round_active = True
        self.round_start_time = pygame.time.get_ticks()
        
        # Fully reset the fishing line including depth
        self.fishing_line.full_reset()
        
        # Reset fish manager with a clean slate
        self.fish_manager.reset_round()
        
        # Play casting sound
        self.sound_manager.play_sfx("cast")
        
    def end_round(self):
        """End the current fishing round and show results"""
        self.round_active = False
        
        # Calculate the value of all caught fish and add to player's balance
        round_value = self.fish_manager.calculate_round_value()
        self.game_state.add_coins(round_value)
        
        # Switch to results screen
        self.current_screen = GameScreen.RESULTS
        
        # Play round end sound
        self.sound_manager.play_sfx("reel_complete")
        
    def handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Handle clicks based on current screen
                    if self.current_screen == GameScreen.RESULTS:
                        if self.ui.check_continue_button(mouse_pos):
                            self.current_screen = GameScreen.SHOP
                            
                    elif self.current_screen == GameScreen.SHOP:
                        upgrade_clicked = self.ui.check_upgrade_buttons(mouse_pos)
                        if upgrade_clicked:
                            self.game_state.purchase_upgrade(upgrade_clicked)
                            self.sound_manager.play_sfx("purchase")
                            
                        if self.ui.check_start_button(mouse_pos):
                            self.current_screen = GameScreen.MAIN_GAME
                            self.start_round()
                        
                        if self.ui.check_reset_button(mouse_pos):
                            # Reset game progress and save state
                            self.game_state.reset_progress()
                            self.game_state.save_game()
                            self.sound_manager.play_sfx("reset")
                            
    def update(self):
        """Update game state"""
        # Get current mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()
        
        if self.current_screen == GameScreen.MAIN_GAME:
            if self.round_active:
                # Update round timer
                current_time = pygame.time.get_ticks()
                self.round_timer = current_time - self.round_start_time
                
                # Update fishing line horizontal position based on mouse
                rod_pos_x = self.player.get_rod_position()[0]
                # Calculate horizontal offset from rod position to mouse
                horizontal_offset = mouse_pos[0] - rod_pos_x
                # Limit the offset to the maximum range
                max_range = self.fishing_line.max_horizontal_range
                if horizontal_offset > max_range:
                    horizontal_offset = max_range
                elif horizontal_offset < -max_range:
                    horizontal_offset = -max_range
                # Set the horizontal offset in the fishing line
                self.fishing_line.horizontal_offset = horizontal_offset
                
                # Update fishing line
                self.fishing_line.update()
                
                # Update fish with current depth for camera tracking
                self.fish_manager.update(self.fishing_line.get_hook_rect(), self.fishing_line.get_current_depth())
                
                # Check for fish catches (hover mechanic)
                caught_fish = self.fish_manager.check_catches(mouse_pos, self.fishing_line)
                if caught_fish:
                    self.sound_manager.play_sfx("catch")
                    
                # Check if round should end
                # Only end if timer is up or hook is at capacity
                if (self.round_timer >= self.game_state.get_round_duration() or
                    self.fishing_line.is_at_capacity()):
                    self.end_round()
            else:
                # If no round is active, start a new one
                self.start_round()
                
        elif self.current_screen == GameScreen.RESULTS:
            # Update results screen animations if any
            pass
            
        elif self.current_screen == GameScreen.SHOP:
            # Update shop screen hover effects
            self.ui.update_shop_hover(mouse_pos)
            
    def render(self):
        """Render the game"""
        # Clear the screen
        self.screen.fill(Config.BACKGROUND_COLOR)
        
        if self.current_screen == GameScreen.MAIN_GAME:
            # Draw the background based on depth
            self.fish_manager.draw_background(self.screen, self.fishing_line.get_current_depth())
            
            # Draw fish (must be drawn before the player to create depth illusion)
            self.fish_manager.draw(self.screen)
            
            # Draw the player (boat/fisherman)
            self.player.draw(self.screen)
            
            # Draw the fishing line and hook
            self.fishing_line.draw(self.screen)
            
            # Draw UI elements (timer, depth, coins)
            self.ui.draw_game_ui(self.screen, self.round_timer, self.fishing_line.get_current_depth())
            
        elif self.current_screen == GameScreen.RESULTS:
            # Draw results screen
            self.ui.draw_results(self.screen, self.fish_manager.get_caught_fish())
            
        elif self.current_screen == GameScreen.SHOP:
            # Draw shop screen
            self.ui.draw_shop(self.screen)
            
        # Update the display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(Config.FPS)
            
    def quit_game(self):
        """Save game and exit"""
        self.game_state.save_game()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
