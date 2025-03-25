import pygame
import math
import sys
from pygame.locals import *

# Initialize pygame2
pygame.init()
pygame.font.init()
pygame.mixer.init()  # Initialize sound mixer

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FOV = math.pi / 3  # 60 degrees field of view
HALF_FOV = FOV / 2
NUM_RAYS = SCREEN_WIDTH // 2  # Number of rays to cast
MAX_DEPTH = 20  # Maximum ray distance
CELL_SIZE = 64  # Size of each cell in the map
PLAYER_SIZE = 10  # Size of player for collision detection
PLAYER_SPEED = 5  # Movement speed
ROTATION_SPEED = 0.1  # Rotation speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Doom Python')

# Clock for controlling game speed
clock = pygame.time.Clock()

# Simple map (1 represents walls, 0 represents empty space)
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

MAP_WIDTH = len(MAP[0])
MAP_HEIGHT = len(MAP)

# Player position and direction
player_x = CELL_SIZE * 1.5
player_y = CELL_SIZE * 1.5
player_angle = math.pi / 4  # Initial angle (45 degrees)

# Textures (simple color patterns for walls)
TEXTURES = [
    pygame.Surface((CELL_SIZE, CELL_SIZE)),  # Empty texture (not used)
    pygame.Surface((CELL_SIZE, CELL_SIZE))   # Wall texture
]

# Create a simple brick pattern for the wall texture
TEXTURES[1].fill(DARK_GRAY)
for y in range(0, CELL_SIZE, 8):
    for x in range(0, CELL_SIZE, 16):
        offset = 8 if y % 16 == 0 else 0
        pygame.draw.rect(TEXTURES[1], GRAY, (x + offset, y, 8, 8))

# Sound effects
try:
    # Load sound effects (using simple beeps for now)
    shoot_sound = pygame.mixer.Sound(buffer=bytes([128] * 1000))
    shoot_sound.set_volume(0.2)
    
    hit_sound = pygame.mixer.Sound(buffer=bytes([128] * 500))
    hit_sound.set_volume(0.3)
except:
    # If sound creation fails, we'll continue without sound
    shoot_sound = None
    hit_sound = None

# Weapon class
class Weapon:
    def __init__(self, name, damage, fire_rate, ammo_capacity, reload_time):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.ammo_capacity = ammo_capacity
        self.current_ammo = ammo_capacity
        self.reload_time = reload_time
        self.last_fire_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 100  # milliseconds per frame
        self.last_frame_update = 0

    def can_fire(self, current_time):
        return (current_time - self.last_fire_time >= self.fire_rate and 
                not self.is_reloading and 
                self.current_ammo > 0)

    def fire(self, current_time):
        if self.can_fire(current_time):
            self.last_fire_time = current_time
            self.current_ammo -= 1
            return True
        return False

    def reload(self, current_time):
        if not self.is_reloading and self.current_ammo < self.ammo_capacity:
            self.is_reloading = True
            self.reload_start_time = current_time
            return True
        return False

    def update(self, current_time):
        if self.is_reloading:
            if current_time - self.reload_start_time >= self.reload_time:
                self.current_ammo = self.ammo_capacity
                self.is_reloading = False
                return True

        # Update weapon animation
        if current_time - self.last_frame_update >= self.animation_speed:
            self.last_frame_update = current_time
            if self.current_frame < len(self.frames) - 1:
                self.current_frame += 1
            else:
                self.current_frame = 0

        return False

# Initialize weapons
weapons = {
    "pistol": Weapon("Pistol", 20, 250, 12, 1000),
    "shotgun": Weapon("Shotgun", 40, 800, 8, 1500),
    "plasma": Weapon("Plasma", 60, 400, 50, 2000)
}

# Create weapon textures
def create_weapon_textures():
    for weapon in weapons.values():
        # Create base weapon texture
        base = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(base, (100, 100, 100), (20, 40, 60, 20))  # Handle
        pygame.draw.rect(base, (150, 150, 150), (70, 45, 20, 10))  # Barrel
        
        # Add some details based on weapon type
        if weapon.name == "Pistol":
            pygame.draw.circle(base, (200, 200, 200), (85, 50), 5)  # Muzzle
        elif weapon.name == "Shotgun":
            pygame.draw.rect(base, (200, 200, 200), (75, 40, 15, 20))  # Wider barrel
        elif weapon.name == "Plasma":
            pygame.draw.rect(base, (0, 255, 255), (75, 45, 15, 10))  # Glowing barrel
        
        weapon.frames.append(base)
        
        # Create firing animation frame
        fire_frame = base.copy()
        if weapon.name == "Pistol":
            pygame.draw.circle(fire_frame, (255, 255, 0), (90, 50), 10)  # Muzzle flash
        elif weapon.name == "Shotgun":
            pygame.draw.circle(fire_frame, (255, 255, 0), (95, 50), 15)  # Larger flash
        elif weapon.name == "Plasma":
            pygame.draw.circle(fire_frame, (0, 255, 255), (90, 50), 20)  # Plasma burst
        
        weapon.frames.append(fire_frame)

create_weapon_textures()

# Update weapon state
weapon_state = {
    "current": "pistol",
    "firing": False,
    "last_fire_time": 0
}

# Enemy class
class Enemy:
    def __init__(self, x, y, enemy_type="imp"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.size = CELL_SIZE // 2
        
        # Enemy type-specific attributes
        if enemy_type == "imp":
            self.health = 100
            self.speed = 2
            self.attack_range = 200
            self.damage = 10
            self.attack_rate = 1000  # milliseconds
            self.color = RED
        elif enemy_type == "cacodemon":
            self.health = 150
            self.speed = 3
            self.attack_range = 300
            self.damage = 15
            self.attack_rate = 800
            self.color = (255, 0, 255)  # Purple
        elif enemy_type == "baron":
            self.health = 300
            self.speed = 1.5
            self.attack_range = 400
            self.damage = 25
            self.attack_rate = 1500
            self.color = (139, 0, 0)  # Dark red
        
        self.is_alive = True
        self.last_attack_time = 0
        self.texture = pygame.Surface((self.size, self.size))
        self.texture.fill(self.color)
        
        # Add enemy-specific details
        if enemy_type == "imp":
            # Horned imp
            pygame.draw.circle(self.texture, BLACK, (self.size // 3, self.size // 3), self.size // 10)
            pygame.draw.circle(self.texture, BLACK, (2 * self.size // 3, self.size // 3), self.size // 10)
            pygame.draw.polygon(self.texture, BLACK, [
                (self.size // 4, self.size // 4),
                (self.size // 2, 0),
                (3 * self.size // 4, self.size // 4)
            ])
        elif enemy_type == "cacodemon":
            # Floating eye
            pygame.draw.circle(self.texture, WHITE, (self.size // 2, self.size // 2), self.size // 3)
            pygame.draw.circle(self.texture, BLACK, (self.size // 2, self.size // 2), self.size // 4)
            pygame.draw.circle(self.texture, WHITE, (self.size // 2, self.size // 2), self.size // 8)
        elif enemy_type == "baron":
            # Horned demon
            pygame.draw.circle(self.texture, BLACK, (self.size // 3, self.size // 3), self.size // 8)
            pygame.draw.circle(self.texture, BLACK, (2 * self.size // 3, self.size // 3), self.size // 8)
            pygame.draw.polygon(self.texture, BLACK, [
                (self.size // 4, self.size // 4),
                (self.size // 2, 0),
                (3 * self.size // 4, self.size // 4)
            ])
            pygame.draw.polygon(self.texture, BLACK, [
                (self.size // 4, self.size // 4),
                (self.size // 2, self.size),
                (3 * self.size // 4, self.size // 4)
            ])

    def update(self, player_x, player_y, current_time):
        if not self.is_alive:
            return False

        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # Move towards player if within attack range
        if distance < self.attack_range:
            # Normalize direction vector
            if distance > 0:
                dx = dx / distance * self.speed
                dy = dy / distance * self.speed
                self.x += dx
                self.y += dy

            # Attack if within range and cooldown is ready
            if distance < self.size * 2 and current_time - self.last_attack_time >= self.attack_rate:
                self.last_attack_time = current_time
                return True  # Signal that the enemy is attacking

        return False

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False
            return True  # Enemy died
        return False

# Create enemies with different types
enemies = [
    Enemy(CELL_SIZE * 3.5, CELL_SIZE * 3.5, "imp"),
    Enemy(CELL_SIZE * 5.5, CELL_SIZE * 5.5, "cacodemon"),
    Enemy(CELL_SIZE * 7.5, CELL_SIZE * 2.5, "baron")
]

def cast_ray(angle):
    """Cast a ray and return the distance to the wall and the wall texture coordinate."""
    # Ray direction
    ray_dir_x = math.cos(angle)
    ray_dir_y = math.sin(angle)
    
    # Player's current map cell
    map_x = int(player_x / CELL_SIZE)
    map_y = int(player_y / CELL_SIZE)
    
    # Length of ray from current position to next x or y-side
    delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
    delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
    
    # Direction to step in x or y direction (either +1 or -1)
    step_x = 1 if ray_dir_x >= 0 else -1
    step_y = 1 if ray_dir_y >= 0 else -1
    
    # Length of ray from one side to next in map
    if ray_dir_x < 0:
        side_dist_x = (player_x / CELL_SIZE - map_x) * delta_dist_x
    else:
        side_dist_x = (map_x + 1.0 - player_x / CELL_SIZE) * delta_dist_x
    
    if ray_dir_y < 0:
        side_dist_y = (player_y / CELL_SIZE - map_y) * delta_dist_y
    else:
        side_dist_y = (map_y + 1.0 - player_y / CELL_SIZE) * delta_dist_y
    
    # Perform DDA (Digital Differential Analysis)
    hit = False
    side = 0  # 0 for x-side, 1 for y-side
    
    while not hit and (map_x >= 0 and map_x < MAP_WIDTH and map_y >= 0 and map_y < MAP_HEIGHT):
        # Jump to next map square
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        
        # Check if ray has hit a wall
        if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT and MAP[map_y][map_x] > 0:
            hit = True
    
    # Calculate distance projected on camera direction
    if hit:
        if side == 0:
            perp_wall_dist = (map_x - player_x / CELL_SIZE + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_wall_dist = (map_y - player_y / CELL_SIZE + (1 - step_y) / 2) / ray_dir_y
        
        # Calculate wall x coordinate (texture)
        if side == 0:
            wall_x = player_y + perp_wall_dist * ray_dir_y
        else:
            wall_x = player_x + perp_wall_dist * ray_dir_x
        
        wall_x = wall_x % CELL_SIZE
        
        # Return the distance and texture coordinate
        return perp_wall_dist * CELL_SIZE, wall_x, side
    
    # If no hit, return maximum distance
    return MAX_DEPTH * CELL_SIZE, 0, 0

def render_walls():
    """Render the walls using raycasting."""
    # Clear the screen
    screen.fill(BLACK)
    
    # Draw ceiling (dark blue)
    pygame.draw.rect(screen, (0, 0, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    
    # Draw floor (dark gray)
    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    
    # Cast rays
    for x in range(SCREEN_WIDTH):
        # Calculate ray position and direction
        camera_x = 2 * x / SCREEN_WIDTH - 1  # x-coordinate in camera space
        ray_angle = player_angle + math.atan(camera_x * math.tan(HALF_FOV))
        
        # Cast the ray
        distance, tex_x, side = cast_ray(ray_angle)
        
        # Calculate wall height
        if distance > 0:
            wall_height = min(int(SCREEN_HEIGHT / distance * CELL_SIZE / 2), SCREEN_HEIGHT)
        else:
            wall_height = SCREEN_HEIGHT
        
        # Calculate wall top and bottom
        wall_top = (SCREEN_HEIGHT - wall_height) // 2
        wall_bottom = wall_top + wall_height
        
        # Get the wall texture
        tex_x = int(tex_x)
        
        # Draw the wall slice
        if side == 1:  # Darker for y-side walls
            color_intensity = 0.7
        else:
            color_intensity = 1.0
        
        # Get a column of the texture
        tex_column = pygame.Surface((1, CELL_SIZE))
        tex_column.blit(TEXTURES[1], (0, 0), (tex_x, 0, 1, CELL_SIZE))
        
        # Scale the texture column to the wall height
        if wall_height > 0:
            scaled_column = pygame.transform.scale(tex_column, (1, wall_height))
            
            # Apply shading based on distance and side
            if color_intensity < 1.0:
                scaled_column.fill((0, 0, 0, int(255 * (1 - color_intensity))), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Draw the scaled column
            screen.blit(scaled_column, (x, wall_top))

def render_enemies():
    """Render the enemies using sprite projection."""
    # Sort enemies by distance (furthest first for correct rendering)
    sorted_enemies = []
    for enemy in enemies:
        if enemy.is_alive:
            # Calculate distance to player
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Calculate angle relative to player's view
            angle = math.atan2(dy, dx) - player_angle
            
            # Normalize angle
            while angle < -math.pi:
                angle += 2 * math.pi
            while angle > math.pi:
                angle += -2 * math.pi
            
            # Only render if in field of view
            if abs(angle) < FOV / 1.5:
                sorted_enemies.append((distance, enemy, angle))
    
    # Sort by distance (furthest first)
    sorted_enemies.sort(reverse=True)
    
    # Render enemies
    for distance, enemy, angle in sorted_enemies:
        # Calculate sprite size based on distance
        sprite_size = min(int(SCREEN_HEIGHT / distance * enemy.size), SCREEN_HEIGHT)
        if sprite_size <= 0:
            continue
        
        # Calculate sprite screen position
        sprite_x = int(SCREEN_WIDTH / 2 + angle / FOV * SCREEN_WIDTH - sprite_size / 2)
        sprite_y = int((SCREEN_HEIGHT - sprite_size) / 2)
        
        # Scale the enemy texture
        scaled_sprite = pygame.transform.scale(enemy.texture, (sprite_size, sprite_size))
        
        # Apply distance fog
        fog_intensity = min(1.0, distance / (MAX_DEPTH * CELL_SIZE / 2))
        if fog_intensity > 0:
            fog = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            fog.fill((0, 0, 0, int(255 * fog_intensity)))
            scaled_sprite.blit(fog, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw the sprite
        screen.blit(scaled_sprite, (sprite_x, sprite_y))

def render_weapon():
    """Render the current weapon."""
    current_time = pygame.time.get_ticks()
    weapon = weapons[weapon_state["current"]]
    
    # Update weapon state
    weapon.update(current_time)
    
    # Get current weapon frame
    frame = weapon.frames[weapon.current_frame]
    
    # Scale the weapon texture
    scaled_weapon = pygame.transform.scale(frame, (200, 200))
    
    # Position the weapon at the bottom right of the screen
    weapon_pos = (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 250)
    
    # Draw the weapon
    screen.blit(scaled_weapon, weapon_pos)
    
    # Draw ammo count
    ammo_text = f"{weapon.current_ammo}/{weapon.ammo_capacity}"
    font = pygame.font.SysFont(None, 36)
    text_surface = font.render(ammo_text, True, WHITE)
    screen.blit(text_surface, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50))
    
    # Draw reload indicator
    if weapon.is_reloading:
        reload_text = "RELOADING..."
        text_surface = font.render(reload_text, True, RED)
        screen.blit(text_surface, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))

def render_hud():
    """Render the heads-up display."""
    # Draw health bar
    health_width = 200
    health_height = 20
    health_x = 20
    health_y = SCREEN_HEIGHT - 40
    
    # Health bar background
    pygame.draw.rect(screen, DARK_GRAY, (health_x, health_y, health_width, health_height))
    # Health bar
    health_percent = player_health / max_health
    pygame.draw.rect(screen, RED, (health_x, health_y, health_width * health_percent, health_height))
    
    # Draw armor bar
    armor_y = health_y - 25
    pygame.draw.rect(screen, DARK_GRAY, (health_x, armor_y, health_width, health_height))
    armor_percent = player_armor / max_armor
    pygame.draw.rect(screen, BLUE, (health_x, armor_y, health_width * armor_percent, health_height))
    
    # Draw health and armor numbers
    health_text = f"HP: {player_health}/{max_health}"
    armor_text = f"ARMOR: {player_armor}/{max_armor}"
    
    text_surface = font.render(health_text, True, WHITE)
    screen.blit(text_surface, (health_x + health_width + 10, health_y))
    
    text_surface = font.render(armor_text, True, WHITE)
    screen.blit(text_surface, (health_x + health_width + 10, armor_y))

def check_collision(x, y):
    """Check if the position (x, y) collides with a wall."""
    # Convert position to map coordinates
    map_x = int(x / CELL_SIZE)
    map_y = int(y / CELL_SIZE)
    
    # Check if position is inside a wall
    if 0 <= map_x < MAP_WIDTH and 0 <= map_y < MAP_HEIGHT:
        return MAP[map_y][map_x] > 0
    
    return True  # Collide with boundaries

def fire_weapon():
    """Fire the current weapon."""
    weapon_state["firing"] = True
    weapon_state["last_fire_time"] = pygame.time.get_ticks()
    
    # Play shooting sound
    if shoot_sound:
        try:
            shoot_sound.play()
        except:
            pass
    
    # Check for hits on enemies
    for enemy in enemies:
        if enemy.is_alive:
            # Calculate direction to enemy
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Calculate angle to enemy
            angle_to_enemy = math.atan2(dy, dx)
            
            # Normalize angles for comparison
            player_angle_normalized = player_angle % (2 * math.pi)
            angle_to_enemy_normalized = angle_to_enemy % (2 * math.pi)
            
            # Calculate angle difference
            angle_diff = abs(player_angle_normalized - angle_to_enemy_normalized)
            angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
            
            # Check if enemy is in front of player and within field of view
            if angle_diff < FOV / 2 and distance < MAX_DEPTH * CELL_SIZE:
                # Check if there's a wall between player and enemy
                hit_wall = False
                ray_dist, _, _ = cast_ray(angle_to_enemy)
                
                if ray_dist >= distance:
                    # Hit the enemy
                    enemy.take_damage(25)  # Damage amount
                    
                    # Play hit sound
                    if hit_sound:
                        try:
                            hit_sound.play()
                        except:
                            pass
                    
                    break  # Only hit one enemy per shot

def render_minimap():
    """Render a small minimap in the corner."""
    map_size = 150
    cell_size = map_size / max(MAP_WIDTH, MAP_HEIGHT)
    map_x = SCREEN_WIDTH - map_size - 10
    map_y = 10
    
    # Draw map background
    pygame.draw.rect(screen, BLACK, (map_x, map_y, map_size, map_size))
    pygame.draw.rect(screen, WHITE, (map_x, map_y, map_size, map_size), 1)
    
    # Draw walls
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if MAP[y][x] > 0:
                pygame.draw.rect(screen, GRAY, 
                                (map_x + x * cell_size, map_y + y * cell_size, 
                                 cell_size, cell_size))
    
    # Draw player
    player_map_x = map_x + (player_x / CELL_SIZE) * cell_size
    player_map_y = map_y + (player_y / CELL_SIZE) * cell_size
    pygame.draw.circle(screen, GREEN, (int(player_map_x), int(player_map_y)), int(cell_size / 2))
    
    # Draw player direction
    dir_x = player_map_x + math.cos(player_angle) * cell_size
    dir_y = player_map_y + math.sin(player_angle) * cell_size
    pygame.draw.line(screen, GREEN, (int(player_map_x), int(player_map_y)), (int(dir_x), int(dir_y)), 2)
    
    # Draw enemies
    for enemy in enemies:
        if enemy.is_alive:
            enemy_map_x = map_x + (enemy.x / CELL_SIZE) * cell_size
            enemy_map_y = map_y + (enemy.y / CELL_SIZE) * cell_size
            pygame.draw.circle(screen, RED, (int(enemy_map_x), int(enemy_map_y)), int(cell_size / 2))

# Player stats
player_health = 100
player_armor = 0
max_health = 100
max_armor = 100

# Power-up class
class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.size = CELL_SIZE // 2
        self.is_active = True
        
        # Create power-up texture
        self.texture = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if power_type == "health":
            self.value = 25
            self.color = GREEN
            # Draw health symbol
            pygame.draw.circle(self.texture, self.color, (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.circle(self.texture, WHITE, (self.size // 2, self.size // 2), self.size // 3)
            pygame.draw.circle(self.texture, self.color, (self.size // 2, self.size // 2), self.size // 4)
        elif power_type == "armor":
            self.value = 25
            self.color = BLUE
            # Draw armor symbol
            pygame.draw.circle(self.texture, self.color, (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.circle(self.texture, WHITE, (self.size // 2, self.size // 2), self.size // 3)
            pygame.draw.rect(self.texture, self.color, (self.size // 4, self.size // 4, self.size // 2, self.size // 2))
        elif power_type == "ammo":
            self.value = 50
            self.color = YELLOW
            # Draw ammo symbol
            pygame.draw.circle(self.texture, self.color, (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.rect(self.texture, WHITE, (self.size // 4, self.size // 4, self.size // 2, self.size // 2))

# Create power-ups
power_ups = [
    PowerUp(CELL_SIZE * 2.5, CELL_SIZE * 2.5, "health"),
    PowerUp(CELL_SIZE * 4.5, CELL_SIZE * 4.5, "armor"),
    PowerUp(CELL_SIZE * 6.5, CELL_SIZE * 3.5, "ammo")
]

def check_power_up_collision():
    global player_health, player_armor
    
    for power_up in power_ups:
        if not power_up.is_active:
            continue
            
        # Calculate distance to power-up
        dx = player_x - power_up.x
        dy = player_y - power_up.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if player picked up the power-up
        if distance < CELL_SIZE:
            if power_up.power_type == "health":
                player_health = min(player_health + power_up.value, max_health)
            elif power_up.power_type == "armor":
                player_armor = min(player_armor + power_up.value, max_armor)
            elif power_up.power_type == "ammo":
                # Refill all weapons
                for weapon in weapons.values():
                    weapon.current_ammo = weapon.ammo_capacity
            
            power_up.is_active = False
            # Play pickup sound (you'll need to add this)

def render_power_ups():
    for power_up in power_ups:
        if power_up.is_active:
            # Calculate power-up position on screen
            dx = power_up.x - player_x
            dy = power_up.y - player_y
            angle = math.atan2(dy, dx) - player_angle
            
            # Normalize angle
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            
            # Check if power-up is in view
            if abs(angle) < HALF_FOV:
                # Calculate distance
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Calculate screen position
                screen_x = (angle + HALF_FOV) * (SCREEN_WIDTH / FOV)
                screen_y = SCREEN_HEIGHT // 2
                
                # Scale power-up based on distance
                scale = min(1.0, CELL_SIZE / distance)
                scaled_size = int(power_up.size * scale)
                
                # Draw power-up
                scaled_texture = pygame.transform.scale(power_up.texture, (scaled_size, scaled_size))
                screen.blit(scaled_texture, (screen_x - scaled_size // 2, screen_y - scaled_size // 2))

# Game state
game_state = "playing"  # "playing", "game_over", "win"

# Game variables
score = 0
high_score = 0
kills = 0
total_enemies = len(enemies)

def update_score(points):
    global score, high_score
    score += points
    if score > high_score:
        high_score = score

def render_game_over():
    # Create semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    
    # Game Over text
    game_over_font = pygame.font.SysFont(None, 74)
    game_over_text = game_over_font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
    
    # Stats
    stats_font = pygame.font.SysFont(None, 36)
    stats = [
        f"Score: {score}",
        f"High Score: {high_score}",
        f"Kills: {kills}/{total_enemies}",
        "",
        "Press R to Restart",
        "Press ESC to Quit"
    ]
    
    for i, stat in enumerate(stats):
        text = stats_font.render(stat, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + i * 40))

def reset_game():
    global player_health, player_armor, score, kills, game_state
    global player_x, player_y, player_angle
    global enemies, power_ups, weapons
    
    # Reset player
    player_health = max_health
    player_armor = 0
    player_x = CELL_SIZE * 1.5
    player_y = CELL_SIZE * 1.5
    player_angle = math.pi / 4
    
    # Reset game state
    score = 0
    kills = 0
    game_state = "playing"
    
    # Reset enemies
    enemies = [
        Enemy(CELL_SIZE * 3.5, CELL_SIZE * 3.5, "imp"),
        Enemy(CELL_SIZE * 5.5, CELL_SIZE * 5.5, "cacodemon"),
        Enemy(CELL_SIZE * 7.5, CELL_SIZE * 2.5, "baron")
    ]
    
    # Reset power-ups
    power_ups = [
        PowerUp(CELL_SIZE * 2.5, CELL_SIZE * 2.5, "health"),
        PowerUp(CELL_SIZE * 4.5, CELL_SIZE * 4.5, "armor"),
        PowerUp(CELL_SIZE * 6.5, CELL_SIZE * 3.5, "ammo")
    ]
    
    # Reset weapons
    for weapon in weapons.values():
        weapon.current_ammo = weapon.ammo_capacity
        weapon.is_reloading = False

# Update the main game loop to handle game over state
def update_game_state():
    global game_state, kills
    
    current_time = pygame.time.get_ticks()
    
    # Check for power-up collisions
    check_power_up_collision()
    
    # Update enemies
    for enemy in enemies:
        if enemy.update(player_x, player_y, current_time):
            # Enemy is attacking
            damage = enemy.damage
            # Apply armor first
            if player_armor > 0:
                if player_armor >= damage:
                    player_armor -= damage
                    damage = 0
                else:
                    damage -= player_armor
                    player_armor = 0
            # Apply remaining damage to health
            player_health -= damage
            if player_health <= 0:
                return "game_over"
    
    # Check for win condition
    if kills >= total_enemies:
        return "win"
    
    return "playing"

# Main game loop
running = True
while running:
    # Keep the loop running at the right speed
    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    
    # Process events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_r and game_state in ["game_over", "win"]:
                reset_game()
            elif event.key == K_SPACE and game_state == "playing":
                current_time = pygame.time.get_ticks()
                weapon = weapons[weapon_state["current"]]
                if weapon.fire(current_time):
                    weapon_state["firing"] = True
                    weapon_state["last_fire_time"] = current_time
                    # Play shooting sound
                    if shoot_sound:
                        shoot_sound.play()
            elif event.key == K_r:
                current_time = pygame.time.get_ticks()
                weapon = weapons[weapon_state["current"]]
                if weapon.reload(current_time):
                    # Play reload sound (you'll need to add this)
                    pass
            elif event.key == K_1:
                weapon_state["current"] = "pistol"
            elif event.key == K_2:
                weapon_state["current"] = "shotgun"
            elif event.key == K_3:
                weapon_state["current"] = "plasma"
        elif event.type == MOUSEBUTTONDOWN and event.button == 1 and game_state == "playing":
            fire_weapon()
    
    if game_state == "playing":
        # Handle player movement
        keys = pygame.key.get_pressed()
        
        # Movement direction
        move_x = 0
        move_y = 0
        
        if keys[K_w]:  # Forward
            move_x += math.cos(player_angle) * PLAYER_SPEED
            move_y += math.sin(player_angle) * PLAYER_SPEED
        if keys[K_s]:  # Backward
            move_x -= math.cos(player_angle) * PLAYER_SPEED
            move_y -= math.sin(player_angle) * PLAYER_SPEED
        if keys[K_a]:  # Strafe left
            move_x += math.cos(player_angle - math.pi/2) * PLAYER_SPEED
            move_y += math.sin(player_angle - math.pi/2) * PLAYER_SPEED
        if keys[K_d]:  # Strafe right
            move_x += math.cos(player_angle + math.pi/2) * PLAYER_SPEED
            move_y += math.sin(player_angle + math.pi/2) * PLAYER_SPEED
        
        # Rotation with arrow keys
        if keys[K_LEFT]:
            player_angle -= ROTATION_SPEED
        if keys[K_RIGHT]:
            player_angle += ROTATION_SPEED
        
        # Normalize angle
        player_angle = player_angle % (2 * math.pi)
        
        # Check collision before moving
        new_x = player_x + move_x
        new_y = player_y + move_y
        
        # Check collision with some margin for player size
        if not check_collision(new_x + PLAYER_SIZE, player_y) and not check_collision(new_x - PLAYER_SIZE, player_y):
            player_x = new_x
        if not check_collision(player_x, new_y + PLAYER_SIZE) and not check_collision(player_x, new_y - PLAYER_SIZE):
            player_y = new_y
        
        # Check win condition (all enemies defeated)
        all_enemies_defeated = True
        for enemy in enemies:
            if enemy.is_alive:
                all_enemies_defeated = False
                break
        
        if all_enemies_defeated:
            game_state = "win"
    
    # Render the game
    if game_state == "playing":
        render_walls()
        render_enemies()
        render_weapon()
        render_power_ups()
        render_hud()
        render_minimap()
    elif game_state == "game_over":
        render_walls()  # Keep the 3D view visible
        render_game_over()
    elif game_state == "win":
        render_walls()
        render_win_screen()
    
    # Flip the display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
