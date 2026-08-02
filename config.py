import sys
import os
from dotenv import load_dotenv

# Muat variabel dari .env jika ada
load_dotenv()

# App Info
APP_NAME = os.getenv("APP_NAME", "CCTV MONITOR")
VERSION = "2.0"
BUILD = "2026.1"
AUTHOR = "System Administrator"

# Data Source
CSV_URL = os.getenv("CSV_URL", "https://docs.google.com/spreadsheets/d/e/2PACX-1vRE3IbUnXuPF74otxx-O7TDJqjdWMLAzHW59FdX2a6zJ1tqxftDPTOYUoalovtBbG81YpA442DNhD_e/pub?output=csv")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

# Ping Engine Config
MAX_CONCURRENT_PINGS = int(os.getenv("MAX_CONCURRENT_PINGS", "100"))
PING_TIMEOUT = int(os.getenv("PING_TIMEOUT", "1"))      # dalam detik
PING_RETRY = int(os.getenv("PING_RETRY", "5"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "0.3"))     # dalam detik

# Logging Config
ENABLE_LOG = os.getenv("ENABLE_LOG", "True").lower() == "true"
LOG_FOLDER = "logs"

# Display Config
SHOW_PROGRESS = os.getenv("SHOW_PROGRESS", "True").lower() == "true"
SHOW_NETWORK_HEALTH = os.getenv("SHOW_NETWORK_HEALTH", "True").lower() == "true"
SHOW_OFFLINE_DETAIL = os.getenv("SHOW_OFFLINE_DETAIL", "True").lower() == "true"
SHOW_GROUP_SUMMARY = os.getenv("SHOW_GROUP_SUMMARY", "True").lower() == "true"
SHOW_INVALID_DATA = os.getenv("SHOW_INVALID_DATA", "True").lower() == "true"

# Column Mapping
COLUMN_NAME = "NAMA"
COLUMN_IP = "IP"
COLUMN_LOCATION = "LOKASI"
COLUMN_GROUP = "GRUB"
COLUMN_NVR = "NVR"
COLUMN_STATUS = "STATUS"

# Network Health Thresholds (%)
HEALTH_EXCELLENT = 100
HEALTH_GOOD = 98
HEALTH_WARNING = 95

def validate_config():
    if not CSV_URL.startswith("http"):
        print("Error: CSV_URL tidak valid.")
        sys.exit(1)
    if MAX_CONCURRENT_PINGS < 1 or MAX_CONCURRENT_PINGS > 500:
        print("Error: MAX_CONCURRENT_PINGS harus antara 1 dan 500.")
        sys.exit(1)