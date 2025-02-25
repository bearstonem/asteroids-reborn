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

## Web Version

Asteroids Reborn can also be played directly in a web browser, and can be deployed to GitHub Pages.

### Building for Web

1. Install the required dependencies:
```
pip install -r requirements.txt
```

2. Run the build script:
```
python build_web.py
```

3. The built web files will be in the `web/build` directory.

### Deploying to GitHub Pages

1. Push the built web files to your GitHub repository:
```
git add web
git commit -m "Add web build"
git push
```

2. In your GitHub repository, go to Settings > Pages.

3. Set the source to either:
   - The `/docs` folder on your main branch (rename `web` folder to `docs` first)
   - OR configure GitHub Actions to deploy from your `web` folder

4. Your game will be available at `https://[yourusername].github.io/[repositoryname]/`

### Troubleshooting Web Build

- Some browsers may have issues with WebAssembly. Chrome and Firefox are recommended.
- **Audio requires user interaction**: Due to browser policies, you must click the "Click to Start Game" button when the game loads to enable audio.
- If you see "Error occurred: The play method is not allowed by the user agent or the platform in the current context," this means the user hasn't interacted with the game yet. This is normal and will be resolved after clicking.
- If you want audio but don't hear any, check that your browser's volume is not muted.
- If you see any CORS errors, make sure your server is configured correctly.

## Development Roadmap

- [x] Core gameplay mechanics
- [x] Basic asteroid types
- [x] Power-up system
- [x] Web browser support
- [ ] Advanced enemy types (alien ships)
- [ ] Weapon upgrades
- [ ] Campaign mode with missions
- [ ] Multiplayer support

## Credits

Developed as a modern reimagining of the classic Atari game Asteroids (1979). 