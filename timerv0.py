import datetime
import time
import sys

try:
    while True:



        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        sys.stdout.write(f"\rCurrent Time: {current_time}")
        sys.stdout.flush()
        
        
        time.sleep(1)


except KeyboardInterrupt:
        print("\nClock stopped.")
