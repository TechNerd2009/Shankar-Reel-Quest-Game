"""
Game state management for Vibe Coder's Catch
Handles coins, upgrades, and game progression
"""
import os
import json
from config import Config

class GameState:
    """Class to manage game state, including coins, upgrades, and progression"""
    
    def __init__(self):
        # Player currency
        self.coins = 0
        
        # Upgrade levels (all start at level 0)
        self.upgrades = {
            "line_length": 0,  # Affects max depth
            "hook_capacity": 0,  # Affects how many fish can be caught
            "round_timer": 0   # Affects round duration
        }
        
        # Power-ups (single-use items)
        self.power_ups = {
            "coin_multiplier": 0,
            "rare_fish_lure": 0,
            "magnet_hook": 0,
            "depth_rush": 0
        }
        
        # Unlocked depth zones
        self.unlocked_zones = ["surface"]  # Start with only surface unlocked
        
        # Stats
        self.total_fish_caught = 0
        self.total_coins_earned = 0
        self.deepest_depth_reached = 0
        
    def add_coins(self, amount):
        """Add coins to the player's balance"""
        self.coins += amount
        self.total_coins_earned += amount
        
    def get_coins(self):
        """Get the current coin balance"""
        return self.coins
        
    def purchase_upgrade(self, upgrade_name):
        """
        Attempt to purchase an upgrade
        Returns True if purchase was successful, False otherwise
        """
        # Check if upgrade exists
        if upgrade_name not in self.upgrades:
            return False
            
        # Get current level and check if it's maxed out
        current_level = self.upgrades[upgrade_name]
        if current_level >= len(Config.UPGRADE_COSTS[upgrade_name]):
            return False  # Max level reached
            
        # Check if player has enough coins
        cost = Config.UPGRADE_COSTS[upgrade_name][current_level]
        if self.coins < cost:
            return False  # Not enough coins
            
        # Purchase the upgrade
        self.coins -= cost
        self.upgrades[upgrade_name] += 1
        
        # Update unlocked zones based on line_length upgrade
        self._update_unlocked_zones()
        
        return True
        
    def purchase_power_up(self, power_up_name, cost):
        """
        Attempt to purchase a power-up
        Returns True if purchase was successful, False otherwise
        """
        if power_up_name not in self.power_ups:
            return False
            
        if self.coins < cost:
            return False  # Not enough coins
            
        # Purchase the power-up
        self.coins -= cost
        self.power_ups[power_up_name] += 1
        return True
        
    def use_power_up(self, power_up_name):
        """
        Attempt to use a power-up
        Returns True if successful, False otherwise
        """
        if power_up_name not in self.power_ups:
            return False
            
        if self.power_ups[power_up_name] <= 0:
            return False  # No power-ups of this type available
            
        # Use the power-up
        self.power_ups[power_up_name] -= 1
        return True
        
    def get_max_depth(self):
        """Get the maximum depth the player can reach based on upgrades"""
        base_depth = Config.BASE_MAX_DEPTH
        depth_increase = self.upgrades["line_length"] * Config.DEPTH_INCREASE_PER_LEVEL
        return base_depth + depth_increase
        
    # Removed get_reel_speed method as the reel_speed upgrade has been removed
        
    def get_hook_capacity(self):
        """Get the hook capacity based on upgrades"""
        base_capacity = Config.BASE_HOOK_CAPACITY
        capacity_increase = self.upgrades["hook_capacity"] * Config.CAPACITY_INCREASE_PER_LEVEL
        return base_capacity + capacity_increase
        
    def get_round_duration(self):
        """Get the round duration in milliseconds based on upgrades"""
        base_duration = Config.BASE_ROUND_DURATION
        duration_increase = self.upgrades["round_timer"] * Config.TIMER_INCREASE_PER_LEVEL
        return base_duration + duration_increase
        
    def _update_unlocked_zones(self):
        """Update the unlocked depth zones based on line_length upgrade"""
        zones = list(Config.DEPTH_ZONES.keys())
        # The number of zones unlocked is based on line_length upgrade level + 1 (for the starting zone)
        unlocked_count = min(len(zones), self.upgrades["line_length"] + 1)
        self.unlocked_zones = zones[:unlocked_count]
        
    def get_unlocked_zones(self):
        """Get the list of unlocked depth zones"""
        return self.unlocked_zones
        
    def update_stats(self, depth, fish_caught):
        """Update game statistics"""
        self.total_fish_caught += fish_caught
        if depth > self.deepest_depth_reached:
            self.deepest_depth_reached = depth
            
    def save_game(self):
        """Save the game state to a file"""
        save_data = {
            "coins": self.coins,
            "upgrades": self.upgrades,
            "power_ups": self.power_ups,
            "unlocked_zones": self.unlocked_zones,
            "stats": {
                "total_fish_caught": self.total_fish_caught,
                "total_coins_earned": self.total_coins_earned,
                "deepest_depth_reached": self.deepest_depth_reached
            }
        }
        
        # Create saves directory if it doesn't exist
        os.makedirs(os.path.dirname(Config.SAVE_FILE), exist_ok=True)
        
        # Save to file
        with open(Config.SAVE_FILE, 'w') as f:
            json.dump(save_data, f)
            
    def load_game(self):
        """Load the game state from a file if it exists"""
        try:
            if os.path.exists(Config.SAVE_FILE):
                with open(Config.SAVE_FILE, 'r') as f:
                    save_data = json.load(f)
                    
                    # Load saved data
                    self.coins = save_data.get("coins", 0)
                    self.upgrades = save_data.get("upgrades", self.upgrades)
                    self.power_ups = save_data.get("power_ups", self.power_ups)
                    self.unlocked_zones = save_data.get("unlocked_zones", ["surface"])
                    
                    # Load stats
                    stats = save_data.get("stats", {})
                    self.total_fish_caught = stats.get("total_fish_caught", 0)
                    self.total_coins_earned = stats.get("total_coins_earned", 0)
                    self.deepest_depth_reached = stats.get("deepest_depth_reached", 0)
                    
                return True
        except Exception as e:
            print(f"Error loading game: {e}")
        return False

    def reset_progress(self):
        """Reset all game progress to initial values"""
        # Reset currency
        self.coins = 0
        
        # Reset upgrades
        self.upgrades = {
            "line_length": 0,
            "hook_capacity": 0,
            "round_timer": 0
        }
        
        # Reset power-ups
        self.power_ups = {
            "coin_multiplier": 0,
            "rare_fish_lure": 0,
            "magnet_hook": 0,
            "depth_rush": 0
        }
        
        # Reset unlocked zones
        self.unlocked_zones = ["surface"]
        
        # Reset stats
        self.total_fish_caught = 0
        self.total_coins_earned = 0
        self.deepest_depth_reached = 0
        
        # Optionally, save the reset state immediately
        # self.save_game() 
        # Or let the game handle saving at the appropriate time
        print("Game progress has been reset.")
