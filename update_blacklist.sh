#!/bin/bash

# Sabitler
PYTHON_SCRIPT="/usr/local/bin/fetch_abuseipdb.py"
HAPROXY_CFG="/etc/haproxy/haproxy.cfg"
LOG_FILE="/var/log/haproxy/blacklist_update.log"

# IP listesini çek
python3 "$PYTHON_SCRIPT"

# HAProxy konfigürasyonunu kontrol et
if haproxy -c -f "$HAPROXY_CFG"; then
    systemctl reload haproxy
    echo "$(date): HAProxy başarıyla güncellendi" >> "$LOG_FILE"
else
    echo "$(date): HAProxy konfigürasyonunda hata var!" >> "$LOG_FILE"
    exit 1
fi
