import config
import urllib.request
import csv
import io
import ipaddress

class GoogleSheet:
    def __init__(self):
        self.raw_data = []
        self.active_cameras = []
        self.stats = {
            "total": 0, "aktif": 0, "nonaktif": 0, 
            "invalid_ip": 0, "invalid_data": 0
        }

    def _is_status_on(self, status_str):
        active_keywords = ["on", "true", "yes", "aktif"]
        return str(status_str).strip().lower() in active_keywords

    def _is_valid_ip(self, ip_str):
        try:
            ipaddress.ip_address(ip_str.strip())
            return True
        except ValueError:
            return False

    def download(self):
        try:
            # Menggunakan urllib bawaan (Lebih ringan dari requests)
            req = urllib.request.Request(config.CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=config.REQUEST_TIMEOUT) as response:
                csv_data = response.read().decode('utf-8')
            
            reader = csv.DictReader(io.StringIO(csv_data))
            
            headers = reader.fieldnames
            required_headers = [config.COLUMN_NAME, config.COLUMN_IP, config.COLUMN_LOCATION, 
                                config.COLUMN_GROUP, config.COLUMN_NVR, config.COLUMN_STATUS]
            
            if not headers or not all(h in headers for h in required_headers):
                raise ValueError("Header CSV tidak sesuai dengan konfigurasi.")

            for row_num, row in enumerate(reader, start=2):
                self.stats["total"] += 1
                
                ip = row.get(config.COLUMN_IP, "").strip()
                status = row.get(config.COLUMN_STATUS, "").strip()
                nama = row.get(config.COLUMN_NAME, "").strip()
                
                if not ip or not nama:
                    self.stats["invalid_data"] += 1
                    continue
                    
                if not self._is_valid_ip(ip):
                    self.stats["invalid_ip"] += 1
                    self.stats["invalid_data"] += 1
                    continue

                cam_data = {
                    "row": row_num, "nama": nama, "ip": ip,
                    "lokasi": row.get(config.COLUMN_LOCATION, "").strip(),
                    "grub": row.get(config.COLUMN_GROUP, "").strip(),
                    "nvr": row.get(config.COLUMN_NVR, "").strip()
                }

                if self._is_status_on(status):
                    self.stats["aktif"] += 1
                    self.active_cameras.append(cam_data)
                else:
                    self.stats["nonaktif"] += 1

            return True
        except Exception as e:
            print(f"Error mendownload/parsing CSV: {e}")
            return False

    def get_statistics(self):
        return self.stats

    def get_active_cameras(self):
        return self.active_cameras