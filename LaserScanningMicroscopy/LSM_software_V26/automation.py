import subprocess, os, time
from pathlib import Path
import json

settings_list = []
current_folder = Path(__file__).resolve().parent

print(current_folder)

# for settings in settings_list:

    
#     process = subprocess.Popen(["python", str(Path(__file__).parent) + "/GUI.py " + settings])
#     process.wait()  # Wait for script to exit
#     print("Script exited, restarting...")
#     time.sleep(0.05)  # Optional delay before restart
 
