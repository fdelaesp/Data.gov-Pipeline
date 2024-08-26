import subprocess
import os
import sys

# List of scripts to run
scripts = ['Downloader.py', 'Complier.py', 'Reshaped.py']

base_dir = os.path.dirname(os.path.abspath(__file__))

for script in scripts:
    script_path = os.path.join(base_dir, script)
    if os.path.isfile(script_path):
        print(f"Running {script_path}...")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Error:\n{result.stderr}")
    else:
        print(f"Script does not exist: {script_path}")
