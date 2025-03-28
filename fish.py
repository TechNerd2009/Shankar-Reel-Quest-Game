"""
Fish module for Vibe Coder's Catch
Handles fish sprites, behavior, and the fish manager
"""
import pygame
import os
import random
from config import Config

class Fish(pygame.sprite.Sprite):
    """Class for individual fish sprites"""
    
    def __init__(self, fish_data, depth_zone):
        super().__init__()
        
        # Fish properties from data
        self.name = fish_data["name"]
        self.rarity = fish_data["rarity"]
        self.value = fish_data["value"]
        self.depth_range = fish_data["depth_range"]
        
        # Load image
        self.image = self.load_image(fish_data["image"])
        self.rect = self.image.get_rect()
        
        # Position and movement
        self.direction = random.choice([-1, 1])  # -1 for left, 1 for right
        self.speed = random.uniform(Config.MIN_FISH_SPEED, Config.MAX_FISH_SPEED)
        
        # Set initial position based on depth zone
        self.rect.y = random.randint(depth_zone[0], depth_zone[1])
        
        # Start from edge of screen based on direction
        if self.direction == -1:  # Moving left
            self.rect.x = Config.SCREEN_WIDTH + self.rect.width
        else:  # Moving right
            self.rect.x = -self.rect.width
            
        # State
        self.caught = False
        
        # Original depth zone for reference
        self.original_zone = fish_data["depth_range"]
        
    def load_image(self, image_path):
        """Load fish image with error handling and placeholder fallback"""
        full_path = os.path.join(Config.SPRITE_PATH, image_path)
        try:
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
            else:
                # Create a placeholder fish image
                placeholder = pygame.Surface((40, 20))
                placeholder.fill((0, 0, 255))  # Blue for fish
                # Add eye
                pygame.draw.circle(placeholder, (255, 255, 255), (30, 10), 5)
                pygame.draw.circle(placeholder, (0, 0, 0), (30, 10), 2)
                return placeholder
        except pygame.error:
            # Create a placeholder on error
            placeholder = pygame.Surface((40, 20))
            placeholder.fill((0, 0, 255))
            return placeholder
            
    def update(self):
        """Update fish position and check if it's off-screen"""
        if not self.caught:
            # Move fish horizontally
            self.rect.x += self.direction * self.speed
            
            # Always move fish upward
            self.rect.y -= self.speed * 0.5  # Move upward at half the horizontal speed
            
            # Add a small random variation to the upward movement
            if random.random() < 0.2:  # 20% chance each frame
                self.rect.y -= random.randint(0, 2)  # Can move up faster
            
            # Check if fish is off-screen
            if (self.direction == -1 and self.rect.right < 0) or \
               (self.direction == 1 and self.rect.left > Config.SCREEN_WIDTH) or \
               self.rect.top > Config.SCREEN_HEIGHT:  # Off bottom of screen
                self.kill()  # Remove from sprite group
                
    def catch(self):
        """Mark fish as caught"""
        if not self.caught:
            self.caught = True
            return True
        return False
        
    def draw_on_hook(self, surface, position):
        """Draw the fish when caught on the hook"""
        # Create a copy of the image for rotation if needed
        fish_image = self.image.copy()
        
        # For caught fish, we might want to rotate them to hang vertically
        if self.direction == -1:
            fish_image = pygame.transform.flip(fish_image, True, False)
            
        # Draw fish at the specified position
        fish_rect = fish_image.get_rect(center=position)
        surface.blit(fish_image, fish_rect)
        
    def get_value(self):
        """Get the coin value of the fish"""
        return self.value
        
    def get_name(self):
        """Get the name of the fish"""
        return self.name
        
    def get_rarity(self):
        """Get the rarity of the fish"""
        return self.rarity


class FishManager:
    """Class to manage fish spawning, movement, and catching"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        
        # Sprite group for all fish
        self.all_fish = pygame.sprite.Group()
        
        # List of caught fish for the current round
        self.caught_fish = []
        
        # Fish data
        self.fish_data = self.initialize_fish_data()
        
        # Background images for different depth zones
        self.background_images = self.load_background_images()
        
        # Spawn timer
        self.last_spawn_time = 0
        self.spawn_interval = 1000  # milliseconds
        
        # Camera tracking variables
        self.previous_depth = 0  # To track depth changes
        self.camera_offset_y = 0  # Vertical camera offset
        
    def initialize_fish_data(self):
        """Initialize fish data with names, rarities, values, and depth ranges"""
        return [
            {
                "name": "Clownfish",
                "image": "fish/clownfish.png",
                "rarity": "Common",
                "value": 10,
                "depth_range": "surface"
            },
            {
                "name": "Blue Tang",
                "image": "fish/blue_tang.png",
                "rarity": "Common",
                "value": 15,
                "depth_range": "surface"
            },
            {
                "name": "Yellowtail",
                "image": "fish/yellowtail.png",
                "rarity": "Uncommon",
                "value": 25,
                "depth_range": "shallows"
            },
            {
                "name": "Grouper",
                "image": "fish/grouper.png",
                "rarity": "Uncommon",
                "value": 35,
                "depth_range": "shallows"
            },
            {
                "name": "Tuna",
                "image": "fish/tuna.png",
                "rarity": "Rare",
                "value": 50,
                "depth_range": "mid_water"
            },
            {
                "name": "Swordfish",
                "image": "fish/swordfish.png",
                "rarity": "Rare",
                "value": 75,
                "depth_range": "mid_water"
            },
            {
                "name": "Angler",
                "image": "fish/angler.png",
                "rarity": "Epic",
                "value": 100,
                "depth_range": "deep_sea"
            },
            {
                "name": "Oarfish",
                "image": "fish/oarfish.png",
                "rarity": "Epic",
                "value": 150,
                "depth_range": "deep_sea"
            },
            {
                "name": "Kraken",
                "image": "fish/kraken.png",
                "rarity": "Legendary",
                "value": 300,
                "depth_range": "abyss"
            }
        ]
        
    def load_background_images(self):
        """Load background images for different depth zones"""
        backgrounds = {}
        
        for zone in Config.DEPTH_ZONES.keys():
            bg_path = os.path.join(Config.SPRITE_PATH, f"backgrounds/{zone}_bg.png")
            try:
                if os.path.exists(bg_path):
                    # Load and scale the background to match screen dimensions
                    bg = pygame.image.load(bg_path).convert()
                    bg = pygame.transform.scale(bg, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                    backgrounds[zone] = bg
                else:
                    # Create placeholder background
                    bg = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                    
                    # Different colors for different zones
                    if zone == "surface":
                        bg.fill((135, 206, 235))  # Sky blue
                    elif zone == "shallows":
                        bg.fill((64, 164, 223))  # Light blue
                    elif zone == "mid_water":
                        bg.fill((28, 107, 160))  # Medium blue
                    elif zone == "deep_sea":
                        bg.fill((8, 37, 103))  # Dark blue
                    elif zone == "abyss":
                        bg.fill((3, 11, 42))  # Very dark blue
                        
                    backgrounds[zone] = bg
            except pygame.error:
                # Create placeholder on error
                bg = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
                bg.fill((0, 0, 100))  # Default blue
                backgrounds[zone] = bg
                
        return backgrounds
        
    def update(self, hook_rect, current_depth=0):
        """Update all fish and check for collisions with hook"""
        # Calculate depth change since last update
        depth_change = current_depth - self.previous_depth
        self.previous_depth = current_depth
        
        # Move all fish vertically based on depth change (camera tracking)
        if depth_change != 0:
            # Apply a multiplier to make the movement more pronounced
            # This creates a stronger visual effect of descending/ascending
            movement_multiplier = 3.0  # Increased from 1.5 to make fish move up faster
            effective_depth_change = depth_change * movement_multiplier
            
            for fish in self.all_fish.sprites():
                if not fish.caught:
                    # Move fish up when going deeper, down when reeling in
                    fish.rect.y -= effective_depth_change
                    
                    # Add slight randomization to vertical movement for more natural feel
                    if random.random() < 0.1:  # 10% chance
                        fish.rect.y += random.uniform(-2, 2)
            
            # Update camera offset
            self.camera_offset_y += depth_change
        
        # Dynamically adjust spawn rate based on depth
        # Deeper = more frequent spawns to maintain fish density
        base_spawn_interval = 1000  # Base interval in milliseconds
        depth_factor = min(1.0, current_depth / 500)  # Cap at 500 depth
        self.spawn_interval = base_spawn_interval * (1.0 - (depth_factor * 0.5))  # Up to 50% faster at max depth
        
        # Spawn new fish if it's time
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_interval:
            self.last_spawn_time = current_time
            self.spawn_fish(current_depth)
            
            # Occasionally spawn an extra fish at deeper depths
            if current_depth > 200 and random.random() < 0.3:  # 30% chance when deeper than 200
                self.spawn_fish(current_depth)
            
        # Update all fish horizontal movement
        self.all_fish.update()
        
        # Remove fish that are too far off-screen vertically
        for fish in self.all_fish.sprites():
            if not fish.caught and (fish.rect.y < -100 or fish.rect.y > Config.SCREEN_HEIGHT + 100):
                fish.kill()
        
    def spawn_fish(self, current_depth=0):
        """Spawn a new fish based on current depth and unlocked zones"""
        # Get unlocked zones
        unlocked_zones = self.game_state.get_unlocked_zones()
        
        # Choose a random zone from unlocked zones
        if not unlocked_zones:
            return  # No zones unlocked (shouldn't happen)
            
        # Determine which zone we're in based on current depth
        current_zone = "surface"  # Default
        for zone, (min_depth, max_depth) in Config.DEPTH_ZONES.items():
            if min_depth <= current_depth <= max_depth:
                current_zone = zone
                break
                
        # Make sure current_zone is in unlocked_zones, otherwise default to first unlocked zone
        if current_zone not in unlocked_zones and unlocked_zones:
            current_zone = unlocked_zones[0]
                
        # Only spawn fish from the current zone or adjacent zones
        available_zones = []
        if current_zone in unlocked_zones:
            available_zones.append(current_zone)
            
        zone_list = list(Config.DEPTH_ZONES.keys())
        if current_zone in zone_list:
            current_index = zone_list.index(current_zone)
            
            # Add adjacent zones if they exist and are unlocked
            if current_index > 0 and zone_list[current_index-1] in unlocked_zones:
                available_zones.append(zone_list[current_index-1])  # Zone above
            if current_index < len(zone_list)-1 and zone_list[current_index+1] in unlocked_zones:
                available_zones.append(zone_list[current_index+1])  # Zone below
        
        # If no available zones after filtering, just use all unlocked zones
        if not available_zones:
            available_zones = unlocked_zones.copy()
            
        # Choose a random zone from available zones
        zone_name = random.choice(available_zones)
        
        # Get the depth range for this zone
        zone_depth = Config.DEPTH_ZONES.get(zone_name)
        if not zone_depth:
            return  # Invalid zone (shouldn't happen)
            
        # If we're in the abyss (depth > 500), allow all fish types to spawn
        if current_depth > 500:
            valid_fish = self.fish_data  # Use all fish types
        else:
            # Filter fish that can spawn in this zone
            valid_fish = [fish for fish in self.fish_data if fish["depth_range"] == zone_name]
        
        if not valid_fish:
            return  # No fish for this zone (shouldn't happen)
            
        # Choose a random fish based on rarity
        # For now, just choose randomly
        fish_data = random.choice(valid_fish)
        
        # Determine spawn position based on zone and current depth
        # Get the actual zone depth range from Config
        zone_min_depth, zone_max_depth = Config.DEPTH_ZONES[zone_name]
        
        # Calculate where in the zone we currently are (as a percentage)
        zone_range = zone_max_depth - zone_min_depth
        if zone_range > 0:
            zone_progress = (current_depth - zone_min_depth) / zone_range
        else:
            zone_progress = 0
        
        # Always spawn fish near the bottom of the screen regardless of depth
        # This ensures players can always catch fish even at maximum depth
        screen_height = Config.SCREEN_HEIGHT
        
        # Set spawn range to be at the bottom portion of the screen
        # The range is from 3/4 of the screen height to just below the screen
        spawn_min_y = screen_height * 0.75  # Bottom quarter of the screen
        spawn_max_y = screen_height + 50    # Just below the visible screen
        
        # Add a small variation based on zone depth to maintain some depth feeling
        # Deeper zone fish will spawn slightly higher than surface fish
        zone_index = list(Config.DEPTH_ZONES.keys()).index(zone_name)
        zone_count = len(Config.DEPTH_ZONES)
        if zone_count > 1:
            # Small adjustment based on zone (max 50 pixels difference between zones)
            zone_offset = (zone_index / (zone_count - 1)) * 50
            spawn_min_y -= zone_offset
            spawn_max_y -= zone_offset
        
        # Final spawn depth range
        adjusted_depth = (int(spawn_min_y), int(spawn_max_y))
        
        # Create and add the fish
        new_fish = Fish(fish_data, adjusted_depth)
        self.all_fish.add(new_fish)
        
    def check_catches(self, mouse_pos, fishing_line):
        """Check if mouse is hovering over any fish to catch them"""
        caught_any = False
        
        # Get hook rect once
        hook_rect = fishing_line.get_hook_rect()
        hook_center = hook_rect.center
        
        # Define the catch area (smaller hitbox as requested)
        catch_radius = 80  # Reduced from 120 for a smaller hitbox
        
        # Check each fish
        for fish in self.all_fish.sprites():
            # Skip already caught fish
            if fish.caught:
                continue
                
            # Calculate distance between fish and hook
            fish_center = fish.rect.center
            dx = fish_center[0] - hook_center[0]
            dy = fish_center[1] - hook_center[1]
            distance = (dx**2 + dy**2)**0.5
            
            # Two ways to catch a fish:
            # 1. Mouse is over fish AND fish is near hook
            # 2. Fish is very close to hook (automatic catch for better UX)
            if ((fish.rect.collidepoint(mouse_pos) and distance <= catch_radius) or 
                distance <= 30):  # Auto-catch when very close to hook (reduced from 50)
                
                # Try to catch the fish
                if fish.catch() and fishing_line.add_caught_fish(fish):
                    self.caught_fish.append(fish)
                    # Remove the fish from the all_fish sprite group
                    self.all_fish.remove(fish)
                    caught_any = True
                        
        return caught_any
        
    def reset_round(self):
        """Reset for a new round"""
        # Clear all fish
        self.all_fish.empty()
        self.caught_fish = []
        
    def get_caught_fish(self):
        """Get the list of caught fish for the current round"""
        return self.caught_fish
        
    def calculate_round_value(self):
        """Calculate the total value of caught fish"""
        return sum(fish.get_value() for fish in self.caught_fish)
        
    def draw(self, surface):
        """Draw all fish on the surface"""
        self.all_fish.draw(surface)
        
    def draw_background(self, surface, current_depth):
        """Draw the appropriate background based on current depth with smooth transitions"""
        # Determine which zone we're in based on depth
        current_zone = "surface"  # Default
        next_zone = None
        transition_progress = 0.0
        
        # Find current zone and check if we're near a transition point
        zones = list(Config.DEPTH_ZONES.keys())
        for i, (zone, (min_depth, max_depth)) in enumerate(Config.DEPTH_ZONES.items()):
            if min_depth <= current_depth <= max_depth:
                current_zone = zone
                
                # Check if we're approaching the next zone (within 20 units of boundary)
                transition_distance = 20
                if i < len(zones) - 1 and current_depth > max_depth - transition_distance:
                    next_zone = zones[i + 1]
                    # Calculate transition progress (0.0 to 1.0)
                    transition_progress = (current_depth - (max_depth - transition_distance)) / transition_distance
                    transition_progress = max(0.0, min(1.0, transition_progress))  # Clamp between 0 and 1
                break
                
        # If depth exceeds the maximum defined depth (500), stay in abyss zone
        if current_depth > 500:
            current_zone = "abyss"
            next_zone = None
            transition_progress = 0.0
        
        # Draw the background with smooth transition if applicable
        if current_zone in self.background_images:
            # Draw the current zone background
            surface.blit(self.background_images[current_zone], (0, 0))
            
            # If we're transitioning to next zone, blend it with alpha transparency
            if next_zone and next_zone in self.background_images and transition_progress > 0:
                # Create a copy of the next zone background
                next_bg = self.background_images[next_zone].copy()
                # Set alpha based on transition progress
                next_bg.set_alpha(int(255 * transition_progress))
                # Overlay the next zone background directly on the main surface
                surface.blit(next_bg, (0, 0))
