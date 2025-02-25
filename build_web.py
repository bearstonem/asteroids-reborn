import os
import subprocess
import shutil

def build_web_game():
    """
    Build the web version of the game using pygbag
    """
    print("Building web version of Asteroids Reborn...")
    
    # Create web directory if it doesn't exist
    os.makedirs("web", exist_ok=True)
    
    # Run pygbag to build the game
    subprocess.run(
        ["python", "-m", "pygbag", "--ume_block=0", "main_web.py"],
        check=True
    )
    
    # Copy the build files to the web directory
    if os.path.exists("build/web"):
        # Clear previous build if exists
        if os.path.exists("web/build"):
            shutil.rmtree("web/build")
        
        # Copy new build
        shutil.copytree("build/web", "web/build")
        print("Web build completed successfully! Files copied to web/build/")
    else:
        print("Error: Build files not found. Check for errors in the build process.")

if __name__ == "__main__":
    build_web_game() 