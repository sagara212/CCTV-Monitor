import config
import utils
import google_sheet
import monitor
import logger
import sys
import time
from colorama import Fore, Style

def print_colored_report(report_string):
    # Menyuntikkan warna pada Terminal agar lebih cantik tanpa merusak log murni
    for line in report_string.split("\n"):
        if "HEALTH" in line:
            if "EXCELLENT" in line or "GOOD" in line:
                line = line.replace("[", f"[{Fore.GREEN}{Style.BRIGHT}").replace("]", f"{Style.RESET_ALL}]")
            elif "WARNING" in line:
                line = line.replace("[", f"[{Fore.YELLOW}{Style.BRIGHT}").replace("]", f"{Style.RESET_ALL}]")
            else:
                line = line.replace("[", f"[{Fore.RED}{Style.BRIGHT}").replace("]", f"{Style.RESET_ALL}]")
        elif "ONLINE" in line and "OFFLINE" not in line:
            line = line.replace("ONLINE", f"{Fore.GREEN}ONLINE{Style.RESET_ALL}")
        elif "OFFLINE" in line:
            line = line.replace("OFFLINE", f"{Fore.RED}OFFLINE{Style.RESET_ALL}")
        
        print(line)

def main():
    utils.clear_screen()
    utils.pre_flight_check()
    utils.clear_screen()
    utils.print_banner()
    
    print(Fore.YELLOW + " [*] Mendownload data dari Google Sheets..." + Style.RESET_ALL)
    sheet = google_sheet.GoogleSheet()
    if not sheet.download():
        sys.exit(1)
        
    stats = sheet.get_statistics()
    active_cams = sheet.get_active_cameras()
    
    print(f" [✓] Sinkronisasi Selesai. Total Status ON: {stats['aktif']}")
    print("-" * 65)
    
    if not active_cams:
        print("Tidak ada CCTV berstatus ON untuk diping.")
        sys.exit(0)
        
    start_time = time.time()
    
    def progress_handler(current, total):
        utils.print_progress(current, total)
        
    results = monitor.run_monitoring(active_cams, progress_callback=progress_handler)
    
    duration = time.time() - start_time
    
    # 1. Bangun 1 laporan murni
    report_string = utils.build_report(stats, results, duration)
    
    utils.clear_screen()
    utils.print_banner()
    
    # 2. Tampilkan dengan warna di terminal
    print_colored_report(report_string)
            
    # 3. Simpan format polos (tanpa kode ANSI) ke log file
    log_file = logger.save_log(report_string)
    if log_file:
        print(Fore.CYAN + f" [i] Log tersimpan di : {log_file}" + Style.RESET_ALL)
        print("=" * 65)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + Fore.RED + "[!] Proses dihentikan oleh pengguna." + Style.RESET_ALL)
        sys.exit(0)