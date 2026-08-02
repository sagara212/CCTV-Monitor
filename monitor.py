import config
import platform
import asyncio

async def ping_target_async(camera, semaphore):
    ip = camera["ip"]
    system = platform.system().lower()
    
    if system == "windows":
        timeout_ms = str(config.PING_TIMEOUT * 1000)
        command = ["ping", "-n", "1", "-w", timeout_ms, ip]
    else:
        timeout_sec = str(config.PING_TIMEOUT)
        command = ["ping", "-c", "1", "-W", timeout_sec, ip]
        
    async with semaphore:
        for attempt in range(1, config.PING_RETRY + 1):
            try:
                # Run the ping command asynchronously
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                
                returncode = await process.wait()
                
                if returncode == 0:
                    camera["status"] = "online"
                    camera["retry"] = attempt
                    return camera
            except Exception:
                pass
                
            if attempt < config.PING_RETRY:
                await asyncio.sleep(config.RETRY_DELAY)
                
        camera["status"] = "offline"
        camera["retry"] = config.PING_RETRY
        return camera

async def run_monitoring_async(cameras, progress_callback=None):
    semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_PINGS)
    
    tasks = [asyncio.create_task(ping_target_async(cam, semaphore)) for cam in cameras]
    
    results = []
    completed = 0
    total = len(cameras)
    online = 0
    offline = 0
    
    # We use asyncio.as_completed to update progress as each task finishes
    for f in asyncio.as_completed(tasks):
        res = await f
        results.append(res)
        completed += 1
        
        if res['status'] == 'online':
            online += 1
        else:
            offline += 1
            
        if progress_callback:
            progress_callback(completed, total, online, offline)
            
    # Urutkan berdasarkan grub lalu nama
    results.sort(key=lambda x: (x.get("grub", ""), x.get("nama", "")))
    return results