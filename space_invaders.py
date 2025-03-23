import pygame
import random
import sys
import os
from pygame.locals import *

# Initialize pygame vs 2.0.1
pygame.init()
pygame.font.init()
pygame.mixer.init()  # Initialize sound mixer

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 7
ENEMY_ROWS = 5
ENEMY_COLS = 10
ENEMY_SPACING = 60
ENEMY_DROP = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Space Invaders')

# Clock for controlling game speed
clock = pygame.time.Clock()

# Sound effects - using simple beeps instead of complex sound generation
# This avoids the need for NumPy
shoot_sound = None
explosion_sound = None
level_up_sound = None
game_over_sound = None

# Try to create simple sound effects
try:
    # Create a simple beep sound for shooting
    shoot_sound = pygame.mixer.Sound(buffer=bytes([128] * 1000))
    shoot_sound.set_volume(0.2)
    
    # Create a simple beep sound for explosions
    explosion_sound = pygame.mixer.Sound(buffer=bytes([128] * 2000))
    explosion_sound.set_volume(0.3)
    
    # Create a simple beep sound for level up
    level_up_sound = pygame.mixer.Sound(buffer=bytes([128] * 1500))
    level_up_sound.set_volume(0.4)
    
    # Create a simple beep sound for game over
    game_over_sound = pygame.mixer.Sound(buffer=bytes([128] * 3000))
    game_over_sound.set_volume(0.5)
except:
    # If sound creation fails, we'll continue without sound
    pass

# Star background
stars = []
for i in range(100):
    x = random.randrange(0, SCREEN_WIDTH)
    y = random.randrange(0, SCREEN_HEIGHT)
    speed = random.randrange(1, 3)
    stars.append([x, y, speed])

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a more detailed player ship
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        # Draw a triangular ship
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 40), (50, 40)])
        # Add some details
        pygame.draw.rect(self.image, BLUE, (15, 25, 20, 10))
        pygame.draw.rect(self.image, YELLOW, (23, 35, 4, 5))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
    
    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[K_LEFT]:
            self.speed_x = -PLAYER_SPEED
        if keystate[K_RIGHT]:
            self.speed_x = PLAYER_SPEED
        self.rect.x += self.speed_x
        
        # Keep player on the screen
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        # Play shooting sound if available
        if shoot_sound:
            try:
                shoot_sound.play()
            except:
                pass

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Draw a more interesting enemy shape
        pygame.draw.ellipse(self.image, RED, (0, 0, 40, 40))
        pygame.draw.ellipse(self.image, (200, 0, 0), (10, 10, 20, 20))
        # Add "eyes"
        pygame.draw.circle(self.image, WHITE, (15, 15), 5)
        pygame.draw.circle(self.image, WHITE, (25, 15), 5)
        pygame.draw.circle(self.image, BLACK, (15, 15), 2)
        pygame.draw.circle(self.image, BLACK, (25, 15), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = ENEMY_SPEED
        self.move_down = False
    
    def update(self):
        self.rect.x += self.speed_x
        
        # Check if any enemy has reached the edge
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            return True
        return False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15), pygame.SRCALPHA)
        # Create a glowing bullet effect
        pygame.draw.rect(self.image, YELLOW, (0, 0, 5, 15))
        pygame.draw.rect(self.image, WHITE, (1, 1, 3, 10))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -BULLET_SPEED
    
    def update(self):
        self.rect.y += self.speed_y
        # Kill the bullet if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.size = 20
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (self.size//2, self.size//2), self.size//2)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # milliseconds

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == 1:
                # Second frame: larger yellow circle
                self.size = 30
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, YELLOW, (self.size//2, self.size//2), self.size//2)
                self.rect = self.image.get_rect(center=self.rect.center)
            elif self.frame == 2:
                # Third frame: orange circle
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 165, 0), (self.size//2, self.size//2), self.size//2)
            elif self.frame == 3:
                # Fourth frame: red circle
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, RED, (self.size//2, self.size//2), self.size//2)
            elif self.frame == 4:
                # Fifth frame: smaller red circle
                self.size = 20
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, RED, (self.size//2, self.size//2), self.size//2)
                self.rect = self.image.get_rect(center=self.rect.center)
            elif self.frame == 5:
                # Kill the sprite when the animation is done
                self.kill()

# Game initialization
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Create enemies
def create_enemies():
    enemies.empty()
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            enemy = Enemy(col * ENEMY_SPACING + 50, row * ENEMY_SPACING + 50)
            all_sprites.add(enemy)
            enemies.add(enemy)

create_enemies()

# Game variables
score = 0
game_over = False
direction_change = False
font = pygame.font.SysFont(None, 36)
level = 1

# Main game loop
running = True
while running:
    # Keep the loop running at the right speed
    clock.tick(60)
    
    # Process events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.shoot()
            elif event.key == K_ESCAPE:
                running = False
            elif event.key == K_r and game_over:
                # Reset the game
                game_over = False
                score = 0
                level = 1
                create_enemies()
                player.rect.centerx = SCREEN_WIDTH // 2
    
    if not game_over:
        # Update
        all_sprites.update()
        
        # Check if any enemy needs to change direction
        direction_change = False
        for enemy in enemies:
            if enemy.update():
                direction_change = True
                break
        
        # Change direction and move down if needed
        if direction_change:
            for enemy in enemies:
                enemy.speed_x *= -1
                enemy.rect.y += ENEMY_DROP
        
        # Check for bullet-enemy collisions
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            score += 10
            # Create an explosion at the enemy's position
            explosion = Explosion(hit.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            # Play explosion sound if available
            if explosion_sound:
                try:
                    explosion_sound.play()
                except:
                    pass
        
        # Check if enemies have reached the bottom
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                game_over = True
                # Play game over sound if available
                if game_over_sound:
                    try:
                        game_over_sound.play()
                    except:
                        pass
        
        # Check if all enemies are destroyed
        if len(enemies) == 0:
            level += 1
            # Play level up sound if available
            if level_up_sound:
                try:
                    level_up_sound.play()
                except:
                    pass
            create_enemies()
            # Increase enemy speed with each level
            for enemy in enemies:
                enemy.speed_x = ENEMY_SPEED + (level - 1) * 0.5
        
        # Check for enemy-player collisions
        if pygame.sprite.spritecollide(player, enemies, False):
            game_over = True
            # Play game over sound if available
            if game_over_sound:
                try:
                    game_over_sound.play()
                except:
                    pass
    
    # Draw / render
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), 1)
        # Move stars down to create scrolling effect
        star[1] += star[2]
        # If the star has moved off the bottom of the screen, reset it to the top
        if star[1] > SCREEN_HEIGHT:
            star[1] = 0
            star[0] = random.randrange(0, SCREEN_WIDTH)
    
    all_sprites.draw(screen)
    
    # Draw score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    
    # Draw game over message
    if game_over:
        game_over_text = font.render("GAME OVER - Press R to restart", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
    
    # Flip the display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
