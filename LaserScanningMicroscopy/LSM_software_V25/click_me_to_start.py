import subprocess, os, time
from pathlib import Path
import json

running_time = 0
max_running_times = 50

current_dir = os.path.dirname(os.path.abspath(__file__))
if_reopen_settings_window_after_finish = current_dir +'/running_files/if_reopen_settings_window_after_finish.json'
if not os.path.exists(if_reopen_settings_window_after_finish):
    with open(if_reopen_settings_window_after_finish, 'w') as json_file:
        json.dump(True, json_file, indent=4)




while running_time < max_running_times:
    if running_time > 0:
        with open(if_reopen_settings_window_after_finish, 'r') as file:
            reopen_state = json.load(file) 
        if not reopen_state:
            break
    
    process = subprocess.Popen(["python3", str(Path(__file__).parent) + "/GUI.py"])
    process.wait()  # Wait for script to exit
    print("Script exited, restarting...")
    time.sleep(1)  # Optional delay before restart
    running_time += 1
