import urllib.request
import os

# Make sure sounds directory exists
os.makedirs('game/assets/sounds', exist_ok=True)

# Define sound URLs and filenames using files from free sound effect sources
sounds = {
    'player_shoot.mp3': 'https://archive.org/download/Sound_Effects/gunshot.mp3',
    'explosion.mp3': 'https://freesound.org/data/previews/123/123456_3355425-lq.mp3',
    'thrust.mp3': 'https://freesound.org/people/qubodup/sounds/147242/download/car_engine_loop.mp3',
    'powerup.mp3': 'https://freesound.org/people/StudioCopsey/sounds/77245/download/power-up.mp3',
    'game_over.mp3': 'https://pixabay.com/sound-effects/mp3/game_over.mp3',
    'level_up.mp3': 'https://freesound.org/people/elmasmalo1/sounds/350841/download/level-up-sound-fx.mp3'
}

# Download each sound file
for filename, url in sounds.items():
    print(f"Downloading {filename}...")
    try:
        output_path = os.path.join('game/assets/sounds', filename)
        urllib.request.urlretrieve(url, output_path)
        print(f"Downloaded {filename} successfully!")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print("Download process completed!")