import os
import time
from datetime import datetime

# Path to your log file
FILE_PATH = "network_performance_report.csv"
MAX_DELAY_MINUTES = 40  # Set higher than 30-min interval to allow for processing time

if os.path.exists(FILE_PATH):
    mod_time = os.path.getmtime(FILE_PATH)
    last_modified = datetime.fromtimestamp(mod_time)
    minutes_ago = (datetime.now() - last_modified).total_seconds() / 60
    
    print(f"Last Log Entry: {last_modified.strftime('%H:%M:%S')} ({int(minutes_ago)} mins ago)")
    
    if minutes_ago < MAX_DELAY_MINUTES:
        print("✅ STATUS: RUNNING ACTIVE")
    else:
        print("❌ STATUS: STOPPED or STUCK")
else:
    print("❌ Error: Log file not found.")

input("\nPress Enter to exit...")