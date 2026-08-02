import config
import utils
import google_sheet
import monitor
import logger
import sys
import time
import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()

async def main():
    utils.clear_screen()
    utils.pre_flight_check()
    
    while True:
        utils.clear_screen()
        utils.print_banner()
        
        console.print("[yellow] [*] Mendownload data dari Google Sheets...[/yellow]")
        sheet = google_sheet.GoogleSheet()
        
        if not sheet.download():
            console.print("[red] [!] Gagal mengunduh data. Periksa koneksi internet.[/red]")
            sys.exit(1)
            
        stats = sheet.get_statistics()
        active_cams = sheet.get_active_cameras()
        
        console.print(f"[green] [✓] Sinkronisasi Selesai. Total Status ON: {stats['aktif']}[/green]")
        console.print("-" * 65)
        
        if not active_cams:
            console.print("[yellow] [!] Tidak ada CCTV berstatus ON untuk diping.[/yellow]")
        else:
            start_time = time.time()
            
            # Using rich Live dashboard
            from rich.live import Live
            with Live(utils.generate_live_dashboard(0, len(active_cams), 0, 0), console=console, refresh_per_second=10) as live:
                def progress_handler(current, total, online, offline):
                    live.update(utils.generate_live_dashboard(current, total, online, offline))
                    
                results = await monitor.run_monitoring_async(active_cams, progress_callback=progress_handler)
            
            duration = time.time() - start_time
            
            # 1. Bangun laporan murni untuk log
            report_string = utils.build_report(stats, results, duration)
            
            utils.clear_screen()
            utils.print_banner()
            
            # 2. Tampilkan laporan dengan Rich Table
            utils.print_rich_report(stats, results, duration)
                    
            # 3. Simpan format polos ke log file
            log_file = logger.save_log(report_string)
            if log_file:
                console.print(f"[cyan] [i] Log tersimpan di : {log_file}[/cyan]")
                console.print("=" * 65)
        
        # 4. Pertanyaan Looping
        print("\n")
        choice = console.input("[yellow bold] [?] Apakah Anda ingin mengecek ulang? (y/n): [/yellow bold]").strip().lower()
        if choice != 'y':
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[red][!] Proses dihentikan oleh pengguna.[/red]")
        sys.exit(0)