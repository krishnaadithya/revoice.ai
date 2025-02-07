import subprocess
import sys
from pathlib import Path
import os

def main():
    # Add project root to Python path
    project_root = Path(__file__).parent.absolute()
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Start FastAPI backend
    backend_path = project_root / "backend" / "main.py"
    backend_process = subprocess.Popen([sys.executable, str(backend_path)])
    
    # Start Gradio frontend
    frontend_path = project_root / "frontend" / "app.py"
    frontend_process = subprocess.Popen([sys.executable, str(frontend_path)])
    
    try:
        # Wait for processes to complete
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        # Handle graceful shutdown
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()

if __name__ == "__main__":
    main() 