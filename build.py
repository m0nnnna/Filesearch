import os
import platform
import subprocess
import shutil
import sys
import site
import PyQt6

# Configuration
APP_NAME = "FileSearch"
MAIN_FILE = "file_search.py"
ICON_WINDOWS = "1.ico"    # Using .ico for Windows
ICON_MAC = "1.icns"      # Using .icns for Mac
ICON_LINUX = "1.png"     # Using .png for Linux
OUTPUT_DIR = "dist"

def get_pyqt_paths():
    """Get all PyQt6 related paths that need to be included."""
    pyqt_path = os.path.dirname(PyQt6.__file__)
    paths = []
    
    # Add PyQt6 directory
    paths.append(("PyQt6", pyqt_path))
    
    # Add platform-specific plugins
    plugins_path = os.path.join(pyqt_path, "Qt6", "plugins")
    if os.path.exists(plugins_path):
        paths.append(("PyQt6/Qt6/plugins", plugins_path))
    
    # Add platform-specific libraries
    lib_path = os.path.join(pyqt_path, "Qt6", "lib")
    if os.path.exists(lib_path):
        paths.append(("PyQt6/Qt6/lib", lib_path))
    
    return paths

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
    
    # Get PyQt6 paths
    pyqt_paths = get_pyqt_paths()
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--windowed",  # GUI application
        "--onefile",   # Single executable
        "--clean",     # Clean PyInstaller cache
        "--noconfirm", # Replace existing spec file
        "--distpath", OUTPUT_DIR,
    ]
    
    # Add PyQt6 paths
    for dest, src in pyqt_paths:
        if system == "windows":
            cmd.extend(["--add-data", f"{src};{dest}"])  # Windows uses semicolon
        else:
            cmd.extend(["--add-data", f"{src}:{dest}"])  # Unix uses colon
    
    # Add hidden imports
    cmd.extend([
        "--hidden-import", "PyQt6",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.sip",
        "--hidden-import", "PyQt6.QtPrintSupport",
        "--hidden-import", "PyQt6.QtSvg",
        "--hidden-import", "PyQt6.QtXml",
        # Add standard library modules
        "--hidden-import", "pkgutil",
        "--hidden-import", "importlib",
        "--hidden-import", "importlib.machinery",
        "--hidden-import", "importlib.util",
        "--hidden-import", "site",
        "--hidden-import", "os",
        "--hidden-import", "sys",
        "--hidden-import", "json",
        "--hidden-import", "datetime",
        "--hidden-import", "shutil",
        "--hidden-import", "platform",
        "--hidden-import", "subprocess",
        "--hidden-import", "re",
        "--hidden-import", "math",
        "--hidden-import", "random",
    ])
    
    # Add icon if available
    icon_file = get_platform_icon()
    if icon_file:
        if system == "windows":
            cmd.extend(["--icon", icon_file])
        else:
            cmd.extend(["--add-data", f"{icon_file}:."])
    
    # Platform-specific options
    if system == "windows":
        # Windows-specific optimizations
        cmd.extend([
            "--uac-admin",  # Request admin privileges
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
    """Create a runtime hook for Linux to handle file associations and PyQt6 paths."""
    hook_content = """
import os
import sys
import site
import importlib.util

def setup_environment():
    # Add the PyInstaller temporary directory to sys.path
    if hasattr(sys, '_MEIPASS'):
        sys.path.insert(0, sys._MEIPASS)
        
        # Add PyQt6 to the path
        pyqt_path = os.path.join(sys._MEIPASS, 'PyQt6')
        if os.path.exists(pyqt_path):
            sys.path.insert(0, pyqt_path)
            
            # Set up Qt plugin paths
            qt_plugin_path = os.path.join(pyqt_path, 'Qt6', 'plugins')
            if os.path.exists(qt_plugin_path):
                os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
                
                # Add library path for Qt
                from PyQt6.QtCore import QCoreApplication
                QCoreApplication.addLibraryPath(qt_plugin_path)

# Run the setup
setup_environment()
"""
    with open("linux_hook.py", "w") as f:
        f.write(hook_content)

def verify_dependencies():
    """Verify that all required dependencies are installed."""
    required_packages = [
        "PyQt6",
        "pyinstaller",
        "pyinstaller-hooks-contrib",
    ]
    
    # First upgrade pip
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Then install/upgrade required packages
    for package in required_packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package])
    
    print("Dependencies installed/upgraded successfully.")

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
        
        # Print platform-specific instructions
        system = platform.system().lower()
        if system == "windows":
            print("\nTo run the application:")
            print("1. Navigate to the dist folder")
            print("2. Double-click FileSearch.exe")
            print("Note: The application may request administrator privileges.")
        elif system == "linux":
            print("\nTo run the application:")
            print("1. Open terminal in the dist folder")
            print("2. Run: chmod +x FileSearch")
            print("3. Run: ./FileSearch")
        elif system == "darwin":
            print("\nTo run the application:")
            print("1. Navigate to the dist folder")
            print("2. Double-click FileSearch.app")
    else:
        print("\nBuild process failed!")

if __name__ == "__main__":
    main()