import config
import os
from datetime import datetime

def save_log(report_string):
    if not config.ENABLE_LOG:
        return
        
    if not os.path.exists(config.LOG_FOLDER):
        os.makedirs(config.LOG_FOLDER)
        
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.log"
    filepath = os.path.join(config.LOG_FOLDER, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_string)
        return filepath
    except Exception as e:
        print(f"Gagal menyimpan log: {e}")
        return None