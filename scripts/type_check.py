import subprocess
import sys
import os

def run_mypy():
    venv_path = os.path.dirname(sys.executable)
    mypy_path = os.path.join(venv_path, 'mypy')
    
    if not os.path.exists(mypy_path):
        print(f"Error: mypy not found at {mypy_path}")
        print("Make sure mypy is installed in your virtual environment.")
        sys.exit(1)

    cmd = [mypy_path, 'colbert_rag']
    try:
        subprocess.run(cmd, check=True)
        print("Type checking completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Type checking failed with error code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    run_mypy()