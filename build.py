import os
import platform
import subprocess
import shutil
import sys

# Configuration
APP_NAME = "FileSearch"
MAIN_FILE = "file_search.py"
ICON_WINDOWS = "1.ico"    # Using .ico for Windows
ICON_MAC = "1.icns"      # Using .icns for Mac
ICON_LINUX = "1.png"     # Using .png for Linux
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

def get_platform_icon():
    """Get the appropriate icon file for the current platform."""
    system = platform.system().lower()
    if system == "windows" and os.path.exists(ICON_WINDOWS):
        return ICON_WINDOWS
    elif system == "darwin" and os.path.exists(ICON_MAC):
        return ICON_MAC
    elif system == "linux" and os.path.exists(ICON_LINUX):
        return ICON_LINUX
    return None

def build_for_platform():
    """Build the application for the current platform."""
    system = platform.system().lower()
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # GUI application
        "--onefile",   # Single executable
        "--clean",     # Clean PyInstaller cache
        "--noconfirm", # Replace existing spec file
        "--distpath", OUTPUT_DIR,
        # Add hidden imports
        "--hidden-import", "PyQt6",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        # Add data files
        "--add-data", f"{get_platform_icon()}:." if get_platform_icon() else "",
    ]
    
    # Remove empty add-data argument if no icon
    cmd = [arg for arg in cmd if arg]
    
    # Platform-specific options
    if system == "windows":
        cmd.extend([
            "--win-private-assemblies",
            "--win-no-prefer-redirects",
        ])
    elif system == "darwin":  # macOS
        cmd.extend([
            "--target-architecture", "universal2",
            "--osx-bundle-identifier", "com.filesearch.app",
        ])
    elif system == "linux":
        cmd.extend([
            "--runtime-hook", "linux_hook.py",
        ])
    
    # Add the main file
    cmd.append(MAIN_FILE)
    
    print(f"Building for {system}...")
    try:
        subprocess.run(cmd, check=True)
        print(f"Build completed successfully! Executable is in {OUTPUT_DIR}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def create_linux_hook():
    """Create a runtime hook for Linux to handle file associations."""
    hook_content = """
import os
import sys

def handle_file_associations():
    # Add any Linux-specific initialization here
    pass

handle_file_associations()
"""
    with open("linux_hook.py", "w") as f:
        f.write(hook_content)

def verify_dependencies():
    """Verify that all required dependencies are installed."""
    required_packages = [
        "PyQt6",
        "pyinstaller",
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("Dependencies installed successfully.")

def main():
    # Verify dependencies
    verify_dependencies()
    
    # Verify main file exists
    if not os.path.exists(MAIN_FILE):
        print(f"Error: {MAIN_FILE} not found!")
        return
    
    # Create Linux hook if needed
    if platform.system().lower() == "linux":
        create_linux_hook()
    
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
        if os.path.exists("linux_hook.py"):
            os.remove("linux_hook.py")
        
        print("\nBuild process completed!")
        print(f"Executable location: {os.path.abspath(os.path.join(OUTPUT_DIR, APP_NAME))}")
    else:
        print("\nBuild process failed!")

if __name__ == "__main__":
    main()