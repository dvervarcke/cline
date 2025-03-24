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

# Weapon state
weapon_state = {
    "current": "pistol",
    "frame": 0,
    "firing": False,
    "last_fire_time": 0
}

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = CELL_SIZE // 2
        self.health = 100
        self.is_alive = True
        self.texture = pygame.Surface((self.size, self.size))
        self.texture.fill(RED)
        # Add some details to the enemy texture
        pygame.draw.circle(self.texture, BLACK, (self.size // 3, self.size // 3), self.size // 10)
        pygame.draw.circle(self.texture, BLACK, (2 * self.size // 3, self.size // 3), self.size // 10)
        pygame.draw.rect(self.texture, BLACK, (self.size // 4, 2 * self.size // 3, self.size // 2, self.size // 10))

# Create some enemies
enemies = [
    Enemy(CELL_SIZE * 3.5, CELL_SIZE * 3.5),
    Enemy(CELL_SIZE * 5.5, CELL_SIZE * 5.5),
    Enemy(CELL_SIZE * 7.5, CELL_SIZE * 2.5)
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
    """Render the player's weapon."""
    # Simple pistol rendering
    weapon_height = SCREEN_HEIGHT // 3
    weapon_width = weapon_height * 2 // 3
    
    # Weapon position (centered at bottom)
    weapon_x = (SCREEN_WIDTH - weapon_width) // 2
    weapon_y = SCREEN_HEIGHT - weapon_height
    
    # Create weapon surface
    weapon = pygame.Surface((weapon_width, weapon_height), pygame.SRCALPHA)
    
    # Draw pistol
    if weapon_state["firing"] and pygame.time.get_ticks() - weapon_state["last_fire_time"] < 200:
        # Firing animation (pistol moved up)
        pygame.draw.rect(weapon, DARK_GRAY, (weapon_width // 3, weapon_height // 4 - 10, weapon_width // 3, weapon_height // 2))
        pygame.draw.rect(weapon, GRAY, (weapon_width // 3 + 2, weapon_height // 4 - 8, weapon_width // 3 - 4, weapon_height // 2 - 4))
        pygame.draw.rect(weapon, DARK_GRAY, (weapon_width // 3, weapon_height // 4 + weapon_height // 2 - 10, weapon_width // 3, weapon_height // 8))
    else:
        # Normal pistol position
        pygame.draw.rect(weapon, DARK_GRAY, (weapon_width // 3, weapon_height // 4, weapon_width // 3, weapon_height // 2))
        pygame.draw.rect(weapon, GRAY, (weapon_width // 3 + 2, weapon_height // 4 + 2, weapon_width // 3 - 4, weapon_height // 2 - 4))
        pygame.draw.rect(weapon, DARK_GRAY, (weapon_width // 3, weapon_height // 4 + weapon_height // 2, weapon_width // 3, weapon_height // 8))
    
    # Draw the weapon
    screen.blit(weapon, (weapon_x, weapon_y))
    
    # Reset firing state after animation
    if weapon_state["firing"] and pygame.time.get_ticks() - weapon_state["last_fire_time"] >= 200:
        weapon_state["firing"] = False

def render_hud():
    """Render the heads-up display."""
    # Draw health bar
    health = 100  # Placeholder for player health
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = 20
    health_bar_y = SCREEN_HEIGHT - 30
    
    # Background
    pygame.draw.rect(screen, DARK_GRAY, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    # Health level
    pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_width * health // 100, health_bar_height))
    # Border
    pygame.draw.rect(screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)
    
    # Draw ammo counter
    ammo = 50  # Placeholder for ammo count
    font = pygame.font.SysFont(None, 36)
    ammo_text = font.render(f"AMMO: {ammo}", True, WHITE)
    screen.blit(ammo_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))

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
                    enemy.health -= 25  # Damage amount
                    
                    # Check if enemy is defeated
                    if enemy.health <= 0:
                        enemy.is_alive = False
                    
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

# Game state
game_state = "playing"  # "playing", "game_over", "win"

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
            elif event.key == K_SPACE and game_state == "playing":
                fire_weapon()
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
    render_walls()
    render_enemies()
    render_weapon()
    render_hud()
    render_minimap()
    
    # Draw game state messages
    if game_state == "game_over":
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text, text_rect)
        
        font = pygame.font.SysFont(None, 36)
        text = font.render("Press ESC to quit", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
        screen.blit(text, text_rect)
    
    elif game_state == "win":
        font = pygame.font.SysFont(None, 72)
        text = font.render("YOU WIN!", True, GREEN)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text, text_rect)
        
        font = pygame.font.SysFont(None, 36)
        text = font.render("Press ESC to quit", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
        screen.blit(text, text_rect)
    
    # Flip the display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
