# Монгол дахь VPS дээр байршуулах (Ubuntu)

1. Сервер дээр:
   ```bash
   sudo apt update && sudo apt install -y python3-venv nginx certbot python3-certbot-nginx git
   sudo git clone <репо> /opt/engineers && cd /opt/engineers
   sudo python3 -m venv venv && sudo venv/bin/pip install -r requirements.txt gunicorn
   ```
2. `/opt/engineers/.env` үүсгэнэ:
   ```
   SECRET_KEY=<python3 -c "import secrets; print(secrets.token_hex(32))" гаргасан утга>
   DATABASE=/opt/engineers/instance/engineers.db
   BEHIND_PROXY=1
   ```
   `sudo mkdir -p instance && sudo chown -R www-data:www-data /opt/engineers/instance`
3. `deploy/engineers.service` → `/etc/systemd/system/`, дараа нь
   `sudo systemctl enable --now engineers`
4. `deploy/nginx.conf` → `/etc/nginx/sites-available/engineers` (домэйноо солино),
   `sudo ln -s /etc/nginx/sites-available/engineers /etc/nginx/sites-enabled/ && sudo systemctl reload nginx`
5. HTTPS: `sudo certbot --nginx -d <домэйн>`
6. Нөөцлөлт: `instance/engineers.db` файлыг өдөр бүр хуулна (жишээ нь cron + `sqlite3 engineers.db ".backup ..."`).
