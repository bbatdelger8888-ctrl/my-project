# PythonAnywhere дээр үнэгүй байршуулах (3 алхам)

1. **Бүртгүүлэх:** pythonanywhere.com → Pricing → үнэгүй (Beginner) багц.
2. **Web app үүсгэх:** дээд цэсний **Web** → **Add a new web app** → **Next** →
   **Manual configuration** → Python хувилбар (хамгийн сүүлийнх) → **Next**.
3. **Суулгах:** дээд цэсний **Consoles** → **Bash** → доорх нэг мөрийг хуулж Enter дарна:
   ```bash
   bash <(curl -s https://raw.githubusercontent.com/bbatdelger8888-ctrl/my-project/claude/mongolian-language-support-ttie5m/deploy/pythonanywhere_setup.sh)
   ```
   Төгсгөлд `БЭЛЭН: https://<нэр>.pythonanywhere.com` гэж гарна. **Web** таб дээр **Reload** дарж, хаягаа нээнэ.

## Анхаарах
- Үнэгүй сайт 1 сарын хугацаатай: **Web** таб дээр сар бүр сунгах товч дарна.
- Шинэчлэл гаргахдаа 3-р алхамын командыг дахин ажиллуулахад хангалттай (өгөгдөл устахгүй).
- Өгөгдөл: `~/my-project/instance/engineers.db`. Нууц түлхүүр: `~/.engineers_secret`.
