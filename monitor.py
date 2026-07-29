import config
import platform
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

def ping_target(camera):
    ip = camera["ip"]
    system = platform.system().lower()
    
    if system == "windows":
        timeout_ms = str(config.PING_TIMEOUT * 1000)
        command = ["ping", "-n", "1", "-w", timeout_ms, ip]
    else:
        timeout_sec = str(config.PING_TIMEOUT)
        command = ["ping", "-c", "1", "-W", timeout_sec, ip]
        
    for attempt in range(1, config.PING_RETRY + 1):
        try:
            result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                camera["status"] = "online"
                camera["retry"] = attempt
                return camera
        except Exception:
            pass
            
        if attempt < config.PING_RETRY:
            time.sleep(config.RETRY_DELAY)
            
    camera["status"] = "offline"
    camera["retry"] = config.PING_RETRY
    return camera

def run_monitoring(cameras, progress_callback=None):
    results = []
    completed = 0
    total = len(cameras)
    
    with ThreadPoolExecutor(max_workers=config.MAX_THREADS) as executor:
        futures = {executor.submit(ping_target, cam): cam for cam in cameras}
        for future in futures:
            res = future.result()
            results.append(res)
            completed += 1
            if progress_callback:
                progress_callback(completed, total)
                
    # Urutkan berdasarkan grub lalu nama
    results.sort(key=lambda x: (x.get("grub", ""), x.get("nama", "")))
    return results