mport requests
import os
import json
from datetime import datetime

def fetch_abuseipdb(api_key, output_file, confidence_min=75):
    """
    AbuseIPDB'den kötü niyetli IP'leri çek ve ACL dosyasına yaz.
    confidence_min: Minimum güven skoru (25-100)
    """
    url = "https://api.abuseipdb.com/api/v2/blacklist"
    headers = {
        "Key": api_key,
        "Accept": "text/plain"
    }
    params = {
        "confidenceMinimum": confidence_min,
        "limit": 100000  # Maksimum IP sayısı (ücretsiz planda 1000/gün)
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        ip_list = response.text.splitlines()

        # IP'leri dosyaya yaz
        with open(output_file, "w") as f:
            for ip in ip_list:
                f.write(f"{ip}\n")

        print(f"{len(ip_list)} IP {output_file} dosyasına yazıldı.")

        # Loglama için tehdit istatistiklerini kaydet
        log_file = "/var/log/haproxy/abuseipdb.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as log:
            log.write(f"{datetime.now()}: {len(ip_list)} IP çekildi, confidence_min={confidence_min}\n")
    
    except requests.RequestException as e:
        print(f"AbuseIPDB API hatası: {e}")
        exit(1)

def main():
    api_key = ""
    output_file = "/etc/haproxy/blacklist.txt"
    
    # Çıktı dizini kontrolü
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    fetch_abuseipdb(api_key, output_file)

if __name__ == "__main__":
    main()
