"""
UI module for Vibe Coder's Catch
Handles game UI, menus, and screens
"""
import pygame
import os
from config import Config

class UI:
    """Class to manage game UI, menus, and screens"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        
        # Load fonts
        pygame.font.init()
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_medium = pygame.font.SysFont("Arial", 24)
        self.font_large = pygame.font.SysFont("Arial", 32)
        
        # Try to load custom font if available
        try:
            font_path = os.path.join(Config.FONT_PATH, "game_font.ttf")
            if os.path.exists(font_path):
                self.font_small = pygame.font.Font(font_path, 20)
                self.font_medium = pygame.font.Font(font_path, 24)
                self.font_large = pygame.font.Font(font_path, 32)
        except pygame.error:
            pass  # Fall back to system font
            
        # UI elements
        self.buttons = {}
        self.hover_button = None
        
        # Initialize UI elements
        self.init_ui_elements()
        
    def init_ui_elements(self):
        """Initialize UI elements like buttons"""
        # Continue button for results screen
        self.buttons["continue"] = pygame.Rect(
            Config.SCREEN_WIDTH // 2 - Config.BUTTON_WIDTH // 2,
            Config.SCREEN_HEIGHT - 100,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT
        )
        
        # Start button for shop screen
        self.buttons["start"] = pygame.Rect(
            Config.SCREEN_WIDTH // 2 - Config.BUTTON_WIDTH // 2,
            Config.SCREEN_HEIGHT - 150,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT
        )
        
        # Reset button
        self.buttons["reset"] = pygame.Rect(
            Config.SCREEN_WIDTH // 2 - Config.BUTTON_WIDTH // 2,
            Config.SCREEN_HEIGHT - 85,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT
        )
        
        # Upgrade buttons
        upgrade_y = 180
        for upgrade in ["line_length", "hook_capacity", "round_timer"]:
            self.buttons[upgrade] = pygame.Rect(
                Config.SCREEN_WIDTH - Config.BUTTON_WIDTH - Config.UI_PADDING,
                upgrade_y,
                Config.BUTTON_WIDTH,
                Config.BUTTON_HEIGHT
            )
            upgrade_y += Config.BUTTON_HEIGHT + 20
            
    def draw_text(self, surface, text, font, color, position, shadow=True):
        """Draw text with optional shadow"""
        if shadow:
            shadow_surface = font.render(text, True, Config.TEXT_SHADOW_COLOR)
            shadow_rect = shadow_surface.get_rect(center=(position[0] + 2, position[1] + 2))
            surface.blit(shadow_surface, shadow_rect)
            
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        surface.blit(text_surface, text_rect)
        
    def draw_button(self, surface, rect, text, hover=False):
        """Draw a button with text"""
        # Draw button background
        color = Config.BUTTON_HOVER_COLOR if hover else Config.BUTTON_COLOR
        pygame.draw.rect(surface, color, rect, border_radius=Config.BUTTON_RADIUS)
        
        # Draw button border
        pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=Config.BUTTON_RADIUS)
        
        # Draw button text
        font = self.font_small if text == "Continue to Shop" else self.font_medium
        self.draw_text(
            surface,
            text,
            font,
            Config.BUTTON_TEXT_COLOR,
            rect.center
        )
        
    def draw_game_ui(self, surface, round_timer, current_depth):
        """Draw in-game UI elements"""
        # Draw timer
        time_left = max(0, (self.game_state.get_round_duration() - round_timer) // 1000)
        self.draw_text(
            surface,
            f"Time: {time_left}s",
            self.font_medium,
            Config.TEXT_COLOR,
            (Config.SCREEN_WIDTH // 2, 30)
        )
        
        # Draw depth
        self.draw_text(
            surface,
            f"Depth: {int(current_depth)}m",
            self.font_medium,
            Config.TEXT_COLOR,
            (Config.SCREEN_WIDTH - 100, 30)
        )
        
        # Draw coins
        self.draw_text(
            surface,
            f"Coins: {self.game_state.get_coins()}",
            self.font_medium,
            Config.TEXT_COLOR,
            (100, 30)
        )
        
    def draw_results(self, surface, caught_fish):
        """Draw the results screen"""
        # Background
        surface.fill((0, 50, 100))  # Dark blue background
        
        # Title
        self.draw_text(
            surface,
            "Round Results",
            self.font_large,
            Config.TEXT_COLOR,
            (Config.SCREEN_WIDTH // 2, 50)
        )
        
        # Calculate total value
        total_value = sum(fish.get_value() for fish in caught_fish)
        
        # Show total
        self.draw_text(
            surface,
            f"Total Catch Value: {total_value} coins",
            self.font_medium,
            Config.TEXT_COLOR,
            (Config.SCREEN_WIDTH // 2, 100)
        )
        
        # List caught fish
        y_pos = 150
        if caught_fish:
            for fish in caught_fish:
                self.draw_text(
                    surface,
                    f"{fish.get_name()} ({fish.get_rarity()}) - {fish.get_value()} coins",
                    self.font_small,
                    Config.TEXT_COLOR,
                    (Config.SCREEN_WIDTH // 2, y_pos)
                )
                y_pos += 30
        else:
            self.draw_text(
                surface,
                "No fish caught!",
                self.font_medium,
                Config.TEXT_COLOR,
                (Config.SCREEN_WIDTH // 2, y_pos)
            )
            
        # Continue button
        self.draw_button(
            surface,
            self.buttons["continue"],
            "Continue to Shop",
            hover=(self.hover_button == "continue")
        )
        
    def draw_shop(self, surface):
        """Draw the shop screen"""
        # Background
        surface.fill((50, 30, 80))  # Purple-ish background
        
        # Title
        self.draw_text(
            surface,
            "Upgrade Shop",
            self.font_large,
            Config.TEXT_COLOR,
            (Config.SCREEN_WIDTH // 2, 50)
        )
        
        # Show coins
        self.draw_text(
            surface,
            f"Coins: {self.game_state.get_coins()}",
            self.font_medium,
            Config.TEXT_COLOR,
            (Config.SCREEN_WIDTH // 2, 100)
        )
        
        # Draw upgrade buttons and info
        self.draw_upgrades(surface)
        
        # Reset button
        self.draw_button(
            surface,
            self.buttons["reset"],
            "Reset Progress",
            hover=(self.hover_button == "reset")
        )
        
        # Start button
        self.draw_button(
            surface,
            self.buttons["start"],
            "Start Fishing",
            hover=(self.hover_button == "start")
        )
        
    def draw_upgrades(self, surface):
        """Draw upgrade options"""
        # Upgrade names and descriptions
        upgrades = {
            "line_length": "Line Length",
            "hook_capacity": "Hook Capacity",
            "round_timer": "Round Timer"
        }
        
        descriptions = {
            "line_length": "Increases maximum fishing depth",
            "hook_capacity": "Increases number of fish you can catch",
            "round_timer": "Increases round duration"
        }
        
        # Draw each upgrade option
        for upgrade_id, upgrade_name in upgrades.items():
            # Get current level and cost
            level = self.game_state.upgrades[upgrade_id]
            
            # Check if max level reached
            if level >= len(Config.UPGRADE_COSTS[upgrade_id]):
                cost_text = "MAX"
                can_afford = False
            else:
                cost = Config.UPGRADE_COSTS[upgrade_id][level]
                cost_text = f"{cost} coins"
                can_afford = self.game_state.get_coins() >= cost
                
            # Get button position
            button_rect = self.buttons[upgrade_id]
            
            # Draw upgrade info
            self.draw_text(
                surface,
                f"{upgrade_name} (Level {level})",
                self.font_medium,
                Config.TEXT_COLOR,
                (230, button_rect.y + 10)  
            )
            
            # Draw description
            self.draw_text(
                surface,
                descriptions[upgrade_id],
                self.font_small,
                Config.TEXT_COLOR,
                (230, button_rect.y + 35)  
            )
            
            # Draw button
            button_color = Config.BUTTON_COLOR
            if not can_afford and cost_text != "MAX":
                button_color = (100, 100, 100)  # Gray out if can't afford
                
            hover = (self.hover_button == upgrade_id and can_afford and cost_text != "MAX")
            
            pygame.draw.rect(
                surface,
                button_color if not hover else Config.BUTTON_HOVER_COLOR,
                button_rect,
                border_radius=Config.BUTTON_RADIUS
            )
            
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                button_rect,
                2,
                border_radius=Config.BUTTON_RADIUS
            )
            
            self.draw_text(
                surface,
                cost_text,
                self.font_small,
                Config.BUTTON_TEXT_COLOR,
                button_rect.center
            )
            
    def update_shop_hover(self, mouse_pos):
        """Update hover state for shop buttons"""
        self.hover_button = None
        
        # Check each button
        for button_id, button_rect in self.buttons.items():
            if button_rect.collidepoint(mouse_pos):
                self.hover_button = button_id
                break
                
    def check_continue_button(self, mouse_pos):
        """Check if continue button was clicked"""
        return self.buttons["continue"].collidepoint(mouse_pos)
        
    def check_start_button(self, mouse_pos):
        """Check if start button was clicked"""
        return self.buttons["start"].collidepoint(mouse_pos)
        
    def check_upgrade_buttons(self, mouse_pos):
        """Check if any upgrade button was clicked, return the upgrade id or None"""
        for upgrade_id in ["line_length", "hook_capacity", "round_timer"]:
            if self.buttons[upgrade_id].collidepoint(mouse_pos):
                # Check if upgrade is available (not max level and can afford)
                level = self.game_state.upgrades[upgrade_id]
                
                if level >= len(Config.UPGRADE_COSTS[upgrade_id]):
                    return None  # Max level reached
                    
                cost = Config.UPGRADE_COSTS[upgrade_id][level]
                if self.game_state.get_coins() < cost:
                    return None  # Can't afford
                    
                return upgrade_id
                
        return None
        
    def check_reset_button(self, mouse_pos):
        """Check if reset button was clicked"""
        return self.buttons["reset"].collidepoint(mouse_pos)
