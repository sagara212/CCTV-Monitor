import config
import os
import platform
import subprocess
import shutil
import urllib.request
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

console = Console()

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
    console.print("[cyan][*] Melakukan Pre-Flight Check...[/cyan]")
    if not check_ping_command():
        console.print("[red][!] Error: Command 'ping' tidak ditemukan.[/red]")
        exit(1)
    if not check_internet():
        console.print("[red][!] Error: Tidak ada koneksi internet.[/red]")
        exit(1)
    config.validate_config()

def print_banner():
    width = 65
    title = f"[bold cyan]{config.APP_NAME}[/bold cyan]"
    panel = Panel(Align.center(title), width=width, border_style="cyan")
    console.print(panel)

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

from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Group

def generate_live_dashboard(completed, total, online, offline):
    pending = total - completed
    percent = (completed / total) * 100 if total > 0 else 0
    
    # Progress bar using rich.progress inside a renderable
    progress = Progress(
        TextColumn("[cyan]Pinging CCTV..."),
        BarColumn(bar_width=None, complete_style="green", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        expand=True
    )
    progress.add_task("ping", total=total, completed=completed)
    
    # Grid for stats
    stats_grid = Table.grid(expand=True)
    stats_grid.add_column(ratio=1)
    stats_grid.add_column(ratio=1)
    
    stats_grid.add_row(
        f"Total Kamera : [bold]{total}[/bold]",
        f"Online       : [bold green]{online} 🟢[/bold green]"
    )
    stats_grid.add_row(
        f"Menunggu     : [bold yellow]{pending} ⏳[/bold yellow]",
        f"Offline      : [bold red]{offline} 🔴[/bold red]"
    )
    
    content = Group(
        stats_grid,
        "",
        progress
    )
    
    return Panel(content, title="Live Scanning", border_style="cyan", padding=(1, 2))

def print_rich_report(stats, results, duration_sec):
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

    # Table 1: Summary
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("Key", style="bold")
    summary_table.add_column("Value")
    
    summary_table.add_row("Total Data", f"{total} (ON: {total_on} | OFF: {total_off})")
    if stats['invalid_data'] > 0:
        summary_table.add_row("Invalid Data", f"{stats['invalid_data']} baris diabaikan")
    
    summary_table.add_row("ONLINE", f"[green]{on_count}[/green]")
    summary_table.add_row("OFFLINE", f"[red]{off_count}[/red]")
    summary_table.add_row("DURASI", f"{duration_sec:.2f} Detik")
    
    health_color = "green" if percentage >= config.HEALTH_GOOD else "yellow" if percentage >= config.HEALTH_WARNING else "red"
    summary_table.add_row("HEALTH", f"[{health_color}]{percentage:.2f}% [{health_label}][/{health_color}]")
    
    # Table 2: Group Summary
    group_table = Table(show_header=False, box=None, padding=(0, 2))
    group_table.add_column("Group")
    group_table.add_column("Status")
    
    if config.SHOW_GROUP_SUMMARY and grub_stats:
        for g_name, g_data in sorted(grub_stats.items()):
            g_pct = (g_data['online'] / g_data['total']) * 100
            color = "green" if g_pct >= config.HEALTH_GOOD else "yellow" if g_pct >= config.HEALTH_WARNING else "red"
            icon = "🟢" if color == "green" else "🟡" if color == "yellow" else "🔴"
            group_table.add_row(
                f"* {g_name}", 
                f"{g_data['online']}/{g_data['total']} ({g_pct:>3.0f}%) {icon}"
            )
            
    # Responsive Side by side panel
    layout = Table.grid(expand=True)
    # Gunakan ratio agar otomatis membelah 50:50 pada layar besar, 
    # namun Rich akan mengaturnya jika layarnya sempit.
    layout.add_column(ratio=1)
    layout.add_column(ratio=1)
    
    group_panel = Panel(group_table, title="Group Summary", border_style="cyan") if grub_stats else ""
    layout.add_row(
        Panel(summary_table, title="Final Report", border_style="cyan"),
        group_panel
    )
    
    console.print(layout)
    
    if config.SHOW_OFFLINE_DETAIL and off_count > 0:
        offline_table = Table.grid(padding=(0, 2))
        offline_table.add_column("No", justify="right")
        offline_table.add_column("Detail")
        
        for idx, cam in enumerate(offline_cams, 1):
            offline_table.add_row(
                f"{idx:02d}.",
                f"[{cam['grub']}] {cam['nama']}\n[dim]└─ IP: {cam['ip']} | NVR: {cam['nvr']} | Lok: {cam['lokasi']}[/dim]\n"
            )
            
        console.print(Panel(offline_table, title=f"[bold red]CCTV OFFLINE ({off_count})[/bold red]", border_style="red"))