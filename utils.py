import config
import os
import platform
import subprocess
import shutil
from colorama import init, Fore, Style
import urllib.request
import sys

init(autoreset=True)

def clear_screen():
    os.system('cls' if platform.system().lower() == 'windows' else 'clear')

def check_internet():
    try:
        urllib.request.urlopen('https://8.8.8.8', timeout=3)
        return True
    except:
        return False

def check_ping_command():
    system = platform.system().lower()
    param = "-n" if system == "windows" else "-c"
    try:
        subprocess.run(["ping", param, "1", "127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def pre_flight_check():
    print(Fore.CYAN + "[*] Melakukan Pre-Flight Check..." + Style.RESET_ALL)
    if not check_ping_command():
        print(Fore.RED + "[!] Error: Command 'ping' tidak ditemukan." + Style.RESET_ALL)
        exit(1)
    if not check_internet():
        print(Fore.RED + "[!] Error: Tidak ada koneksi internet." + Style.RESET_ALL)
        exit(1)
    config.validate_config()

def print_banner():
    width = 65
    print("=" * width)
    print(Fore.CYAN + Style.BRIGHT + f"{config.APP_NAME}".center(width) + Style.RESET_ALL)
    print("=" * width)

def print_progress(current, total):
    if not config.SHOW_PROGRESS or total == 0: return
    term_width = shutil.get_terminal_size().columns
    bar_length = min(35, term_width - 30)
    filled_len = int(bar_length * current // total)
    bar = '█' * filled_len + '░' * (bar_length - filled_len)
    percent = (current / total) * 100
    # Menggunakan Carriage Return (\r) agar tertimpa rapi
    sys.stdout.write(f"\r {Fore.CYAN}[{bar}] {percent:.1f}% ({current}/{total}){Style.RESET_ALL}")
    sys.stdout.flush()
    if current == total:
        print("\n")

def get_network_health_label(percentage):
    if percentage >= config.HEALTH_EXCELLENT: return "EXCELLENT"
    elif percentage >= config.HEALTH_GOOD: return "GOOD"
    elif percentage >= config.HEALTH_WARNING: return "WARNING"
    else: return "CRITICAL"

def build_report(stats, results, duration_sec):
    total = stats['total']
    total_on = stats['aktif']
    total_off = stats['nonaktif']
    
    online_cams = [c for c in results if c['status'] == 'online']
    offline_cams = [c for c in results if c['status'] == 'offline']
    
    on_count = len(online_cams)
    off_count = len(offline_cams)
    percentage = (on_count / total_on * 100) if total_on > 0 else 0
    health_label = get_network_health_label(percentage)
    
    # Kumpulkan statistik per GRUB
    grub_stats = {}
    for cam in results:
        g = cam['grub'] or "UNGROUPED"
        if g not in grub_stats:
            grub_stats[g] = {'total': 0, 'online': 0}
        grub_stats[g]['total'] += 1
        if cam['status'] == 'online':
            grub_stats[g]['online'] += 1

    lines = []
    width = 65
    
    lines.append(f" Total Data   : {total} (ON: {total_on} | OFF: {total_off})")
    if stats['invalid_data'] > 0:
        lines.append(f" Invalid Data : {stats['invalid_data']} baris diabaikan")
    lines.append("-" * width)
    lines.append(f" ONLINE       : {on_count}")
    lines.append(f" OFFLINE      : {off_count}")
    lines.append(f" DURASI       : {duration_sec:.2f} Detik")
    lines.append(f" HEALTH       : {percentage:.2f}% [{health_label}]")
    lines.append("=" * width)
    
    if config.SHOW_GROUP_SUMMARY and grub_stats:
        lines.append("[ RINGKASAN GRUB ]".center(width))
        lines.append("=" * width)
        for g_name, g_data in sorted(grub_stats.items()):
            g_pct = (g_data['online'] / g_data['total']) * 100
            # Formating agar angka rata kanan rapi
            lines.append(f" * {g_name:<16} : {g_data['online']:>2}/{g_data['total']:<2} Online ({g_pct:>3.0f}%)")
        lines.append("=" * width)
        
    if config.SHOW_OFFLINE_DETAIL and off_count > 0:
        lines.append("[ DETAIL CCTV OFFLINE ]".center(width))
        lines.append("=" * width)
        for idx, cam in enumerate(offline_cams, 1):
            lines.append(f" {idx:02d}. [{cam['grub']}] {cam['nama']}")
            # Simbol L untuk visualisasi struktur data yang lebih modern
            lines.append(f"     └─ IP: {cam['ip']} | NVR: {cam['nvr']} | Lok: {cam['lokasi']}")
        lines.append("=" * width)
        
    return "\n".join(lines)