import os
import subprocess
import sys
import shutil
from pathlib import Path

def build_exe():
    """Compiles the application into a standalone executable using PyInstaller."""
    
    print("🚀 Starting compilation process...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Define paths
    base_path = Path.cwd()
    dist_path = base_path / "dist"
    build_path = base_path / "build"
    static_path = base_path / "static"
    output_name = "LBC_Automation_Bot"
    
    # Clean previous builds
    # ignore_errors=True permet d'éviter de planter si un fichier est locké (ex: app.log)
    if dist_path.exists():
        try:
            shutil.rmtree(dist_path)
        except OSError:
            print("⚠️ Impossible de supprimer totalement le dossier dist (fichiers verrouillés ?)")
            print("   On continue quand même la compilation...")
            
    if build_path.exists():
        try:
            shutil.rmtree(build_path)
        except OSError:
            pass
    
    # PyInstaller arguments
    args = [
        "start_app.py",                  # Entry point
        f"--name={output_name}",         # Executable name
        "--noconsole",                   # Hide terminal
        "--onefile",                     # Single exe file
        "--clean",                       # Clean cache
        # Include static files: source;dest
        f"--add-data={static_path}{os.pathsep}static", 
        
        # Hidden imports (dependencies that PyInstaller might miss)
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=engineio.async_drivers.asgi",
        "--hidden-import=socketio.async_drivers.asgi",
        
        # Exclude unnecessary modules to save space (optional)
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=notebook",
        "--exclude-module=scipy",
    ]
    
    # Run PyInstaller
    print(f"📦 Building {output_name}.exe with PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller"] + args)
        print("\n✅ Build successful!")
        print(f"👉 Your executable is located in: {dist_path / (output_name + '.exe')}")
        print("\n⚠️  IMPORTANT: The first time you run the .exe, it might need to download Chromium.")
        print("    Ensure you have an internet connection.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")

if __name__ == "__main__":
    build_exe()
