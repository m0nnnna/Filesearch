import os
import platform
import subprocess
import shutil

# Configuration
APP_NAME = "FileSearch"
MAIN_FILE = "file_search.py"
ICON_WINDOWS = "1.ico"    # Using .ico for Windows
ICON_MAC = "1.png"       # Using .png for Mac (can be converted to .icns)
OUTPUT_DIR = "dist"

def clean_previous_builds():
    """Remove previous build and dist directories."""
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    # Remove spec files from previous builds
    for file in os.listdir():
        if file.endswith(".spec"):
            os.remove(file)

def build_for_platform():
    """Build the application for the current platform."""
    system = platform.system().lower()
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # GUI application
        "--onefile",   # Single executable
        "--distpath", OUTPUT_DIR
    ]
    
    # Platform-specific options
    if system == "windows":
        if os.path.exists(ICON_WINDOWS):
            cmd.extend(["--icon", ICON_WINDOWS])
        else:
            print(f"Warning: Windows icon file {ICON_WINDOWS} not found")
    elif system == "darwin":  # macOS
        if os.path.exists(ICON_MAC):
            cmd.extend(["--icon", ICON_MAC])
        else:
            print(f"Warning: Mac icon file {ICON_MAC} not found")
    
    # Add the main file
    cmd.append(MAIN_FILE)
    
    print(f"Building for {system}...")
    try:
        subprocess.run(cmd, check=True)
        print(f"Build completed successfully! Executable is in {OUTPUT_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    return True

def main():
    # Verify main file exists
    if not os.path.exists(MAIN_FILE):
        print(f"Error: {MAIN_FILE} not found!")
        return
    
    # Verify icon files exist
    if not os.path.exists(ICON_WINDOWS):
        print(f"Warning: Windows icon {ICON_WINDOWS} not found")
    if not os.path.exists(ICON_MAC):
        print(f"Warning: Mac icon {ICON_MAC} not found")
    
    # Clean previous builds
    print("Cleaning previous builds...")
    clean_previous_builds()
    
    # Build for current platform
    if build_for_platform():
        # Clean up unnecessary files
        if os.path.exists("build"):
            shutil.rmtree("build")
        for file in os.listdir():
            if file.endswith(".spec"):
                os.remove(file)

if __name__ == "__main__":
    main()