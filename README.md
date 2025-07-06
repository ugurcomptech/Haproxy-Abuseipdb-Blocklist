# HAProxy ile AbuseIPDB Tehdit İstihbaratı Entegrasyonu

Bu proje, HAProxy yük dengeleyici ile AbuseIPDB tehdit istihbaratını entegre ederek kötü niyetli IP’leri otomatik olarak engellemeyi sağlar. Mevcut HAProxy güvenlik önlemleriyle (örneğin, rate limiting, User-Agent filtreleme) uyumludur.

## Özellikler
- AbuseIPDB’den günlük 10.000’e kadar kötü niyetli IP çekme.
- HAProxy ACL ile otomatik IP engelleme.
- Periyodik güncelleme için cron job desteği.
- Loglama ve izleme.

## Gereksinimler
- HAProxy 1.8 veya üstü
- Python 3.x (`requests` kütüphanesi)
- Linux tabanlı bir sistem (Ubuntu/Debian önerilir)
- AbuseIPDB API anahtarı (https://www.abuseipdb.com)

## Kurulum
1. **AbuseIPDB API Anahtarı Alın**:
   - https://www.abuseipdb.com adresinden ücretsiz bir hesap oluşturun ve API anahtarınızı alın.

2. **Python Scriptini Kurun**:
   ```bash
   sudo pip3 install requests
   sudo mkdir -p /usr/local/bin
   sudo cp fetch_abuseipdb.py /usr/local/bin/
   sudo chmod +x /usr/local/bin/fetch_abuseipdb.py
   ```
   `fetch_abuseipdb.py` içindeki `api_key` değişkenini kendi API anahtarınızla güncelleyin.

3. **HAProxy Konfigürasyonunu Güncelleyin**:
   `/etc/haproxy/haproxy.cfg` dosyasına aşağıdaki ACL’yi ekleyin:
   ```haproxy
   acl is_blacklisted src -f /etc/haproxy/blacklist.txt
   http-request deny deny_status 403 content-type text/html file /etc/haproxy/errors/403-blacklist.html if is_blacklisted
   ```

4. **Hata Sayfasını Oluşturun**:
   ```bash
   sudo mkdir -p /etc/haproxy/errors
   sudo bash -c 'cat > /etc/haproxy/errors/403-blacklist.html <<EOF
   <html>
   <head><title>403 Forbidden</title></head>
   <body>
   <h1>403 Forbidden</h1>
   <p>Erişim engellendi: IP adresiniz güvenlik tehdit listesinde bulunuyor.</p>
   </body>
   </html>
   EOF'
   ```

5. **Otomasyon Scriptini Kurun**:
   ```bash
   sudo cp update_blacklist.sh /usr/local/bin/
   sudo chmod +x /usr/local/bin/update_blacklist.sh
   ```

6. **Cron Job Ayarlayın**:
   ```bash
   crontab -e
   ```
   Şunu ekleyin:
   ```bash
   0 * * * * /usr/local/bin/update_blacklist.sh >> /var/log/haproxy/blacklist_update.log 2>&1
   ```

7. **HAProxy’yi Test Edin ve Yeniden Yükleyin**:
   ```bash
   sudo haproxy -c -f /etc/haproxy/haproxy.cfg
   sudo systemctl reload haproxy
   ```

## Kullanım
- IP listesini manuel olarak güncellemek için:
  ```bash
  python3 /usr/local/bin/fetch_abuseipdb.py
  ```
- Otomasyonu çalıştırmak için:
  ```bash
  /usr/local/bin/update_blacklist.sh
  ```

## Loglama
- IP çekme logları: `/var/log/haproxy/abuseipdb.log`
- Otomasyon logları: `/var/log/haproxy/blacklist_update.log`
- Engellenen istekler: `/var/log/haproxy.log` (örneğin, `grep "403-blacklist.html" /var/log/haproxy.log`)

## Yanlış Pozitifleri Azaltma
- Güvenilir IP’ler için bir whitelist ekleyin:
  ```haproxy
  acl is_whitelisted src -f /etc/haproxy/whitelist.txt
  http-request allow if is_whitelisted
  ```
  `/etc/haproxy/whitelist.txt` dosyasına IP’leri ekleyin:
  ```bash
  echo "192.168.1.100" | sudo tee /etc/haproxy/whitelist.txt
  ```

## Katkıda Bulunma
Hatalar veya öneriler için lütfen bir issue açın veya pull request gönderin.
