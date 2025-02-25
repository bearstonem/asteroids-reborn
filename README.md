# Asteroids Reborn

A modern reimagining of the classic arcade game Asteroids, featuring momentum-based physics, procedural generation, various asteroid types, and roguelike progression.

## Features

- **Momentum-based movement** with realistic physics
- **Multiple asteroid types** with unique behaviors:
  - Normal rocky asteroids
  - Ice asteroids that shatter
  - Mineral-rich asteroids that drop resources
  - Unstable asteroids that explode
- **Power-up system** with shields, rapid fire, and extra lives
- **Particle effects** for explosions and visual flair
- **Progressive difficulty** with increasing levels

## Installation

### Requirements
- Python 3.7+
- Pygame 2.0.0+

### Setup

1. Clone this repository:
```
git clone https://github.com/yourusername/asteroidsreborn.git
cd asteroidsreborn
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the game:
```
python main.py
```

## Controls

- **Arrow Keys** or **W/A/S/D**: Control ship movement
  - Up/W: Thrust
  - Left/A: Rotate left
  - Right/D: Rotate right
- **Space**: Fire weapons
- **Escape**: Pause game
- **R**: Restart (after game over)

## Gameplay Tips

- Momentum is conserved in space - you'll continue moving until you apply thrust in the opposite direction.
- Different asteroid types have different behaviors:
  - Unstable asteroids (red) explode and damage nearby asteroids when destroyed.
  - Mineral asteroids (gold/copper) are tougher but worth more points.
  - Ice asteroids (light blue) are fragile but fast.
- Power-ups appear randomly when destroying asteroids:
  - Blue shield: Temporary invulnerability
  - Orange lightning: Rapid fire mode
  - Green heart: Extra life
- The game gets progressively harder with each level:
  - More asteroids
  - Faster asteroid movement
  - More challenging asteroid types

## Development Roadmap

- [x] Core gameplay mechanics
- [x] Basic asteroid types
- [x] Power-up system
- [ ] Advanced enemy types (alien ships)
- [ ] Weapon upgrades
- [ ] Campaign mode with missions
- [ ] Multiplayer support

## Credits

Developed as a modern reimagining of the classic Atari game Asteroids (1979). 