# Python Doom

A simplified implementation of the classic first-person shooter game Doom using Python and Pygame. This implementation uses raycasting techniques to create a 3D-like environment from a 2D map.

## Features

- First-person perspective with raycasting rendering
- Textured walls with distance-based shading
- Enemy sprites with basic AI
- Weapon system with shooting mechanics
- Collision detection
- Minimap for navigation
- Health and ammo display
- Sound effects

## Requirements

- Python 3.8 or higher
- Pygame 2.0 or higher

## Installation

1. Ensure you have Python installed on your system
2. Install Pygame using pip:
   ```
   pip install pygame
   ```
3. Download or clone this repository

## How to Run

Run the game by executing the `doom.py` file:

```
python doom.py
```

## Controls

- **W**: Move forward
- **S**: Move backward
- **A**: Strafe left
- **D**: Strafe right
- **Left Arrow**: Rotate left
- **Right Arrow**: Rotate right
- **Space** or **Left Mouse Button**: Fire weapon
- **ESC**: Quit game

## Game Mechanics

- Navigate through the maze-like environment
- Shoot enemies to defeat them
- Defeat all enemies to win the game
- Avoid getting too close to enemies

## Technical Implementation

This game uses several key techniques:

1. **Raycasting**: Creates a 3D-like view from a 2D map by casting rays from the player's position
2. **DDA Algorithm**: Efficient ray-wall intersection calculation
3. **Texture Mapping**: Applies textures to walls with perspective correction
4. **Sprite Rendering**: Renders enemies as billboarded sprites
5. **Collision Detection**: Grid-based collision system

## Future Improvements

- Multiple levels with increasing difficulty
- More enemy types with different behaviors
- Additional weapons with varying characteristics
- Power-ups and collectibles
- More detailed textures and sprites
- Enhanced lighting effects
- Sound effects and music

## Acknowledgements

This implementation is inspired by the original Doom game created by id Software. The raycasting technique is based on principles similar to those used in Wolfenstein 3D.
