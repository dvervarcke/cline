# Space Invaders Game

A simple Space Invaders game implemented in Python using Pygame with visual effects, sound effects, and level progression.

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. Install the Pygame library using pip:
   ```
   pip3 install pygame
   ```

## How to Run the Game

Run the game by executing the Python script:
```
python3 space_invaders.py
```

## Controls

- **Left Arrow**: Move the player ship left
- **Right Arrow**: Move the player ship right
- **Space**: Shoot bullets
- **Escape**: Quit the game
- **R**: Restart the game after Game Over

## Game Rules

- Control the green ship at the bottom of the screen
- Shoot the red enemy invaders before they reach the bottom
- Each enemy destroyed earns you 10 points
- The game ends if an enemy reaches the bottom of the screen or collides with your ship
- After all enemies are destroyed, a new wave will appear

## Game Features

- Player ship that can move left and right
- Enemies that move across the screen and down
- Shooting mechanics to destroy enemies
- Score tracking
- Game over and restart functionality
- Visual effects:
  - Animated star background for space atmosphere
  - Explosion animations when enemies are destroyed
  - Visually detailed player ship and enemies
- Sound effects:
  - Simple beep sounds for game events (shooting, explosions, etc.)
  - Graceful fallback if sound system is unavailable
- Level progression with increasing difficulty

## Game Mechanics

- Each level increases enemy movement speed
- When all enemies are destroyed, a new level begins with faster enemies
- Explosions appear when enemies are hit
- Background stars create a scrolling space effect
- The game tracks both score and current level
- Sound effects provide audio feedback for game events

## Customization

You can modify the game by adjusting the constants at the top of the script:
- `SCREEN_WIDTH` and `SCREEN_HEIGHT`: Change the game window size
- `PLAYER_SPEED`: Adjust how fast the player ship moves
- `ENEMY_SPEED`: Change the enemy movement speed (base speed, increases with levels)
- `BULLET_SPEED`: Modify how fast bullets travel
- `ENEMY_ROWS` and `ENEMY_COLS`: Adjust the number of enemies
- `ENEMY_SPACING`: Change the spacing between enemies
- `ENEMY_DROP`: Adjust how far enemies move down when they reach the edge

## Future Improvements

Potential enhancements for the game:
- Implement different enemy types with varying behaviors
- Add power-ups and special abilities (shields, multi-shot, etc.)
- Create boss enemies at milestone levels
- Add a high score system with persistent storage
- Implement a pause feature
- Add a start menu and game settings
- Improve sound effects with real audio files
- Add background music
