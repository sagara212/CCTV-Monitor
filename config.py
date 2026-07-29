import sys

# App Info
APP_NAME = "CCTV MONITOR"
VERSION = "2.0"
BUILD = "2026.1"
AUTHOR = "System Administrator"

# Data Source
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRE3IbUnXuPF74otxx-O7TDJqjdWMLAzHW59FdX2a6zJ1tqxftDPTOYUoalovtBbG81YpA442DNhD_e/pub?output=csv"
REQUEST_TIMEOUT = 15

# Ping Engine Config
MAX_THREADS = 100
PING_TIMEOUT = 1      # dalam detik
PING_RETRY = 5
RETRY_DELAY = 0.3     # dalam detik

# Logging Config
ENABLE_LOG = True
LOG_FOLDER = "logs"

# Display Config
SHOW_PROGRESS = True
SHOW_NETWORK_HEALTH = True
SHOW_OFFLINE_DETAIL = True
SHOW_GROUP_SUMMARY = True
SHOW_INVALID_DATA = True

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
    if MAX_THREADS < 1 or MAX_THREADS > 500:
        print("Error: MAX_THREADS harus antara 1 dan 500.")
        sys.exit(1)