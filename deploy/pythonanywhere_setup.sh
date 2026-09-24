#!/bin/bash
# PythonAnywhere-ийн Bash console дээр ажиллуулна:
#   bash <(curl -s https://raw.githubusercontent.com/bbatdelger8888-ctrl/my-project/claude/mongolian-language-support-ttie5m/deploy/pythonanywhere_setup.sh)
set -e
REPO=https://github.com/bbatdelger8888-ctrl/my-project.git
DIR=~/my-project

if [ -d "$DIR/.git" ]; then
  git -C "$DIR" pull --ff-only
else
  git clone "$REPO" "$DIR"
fi
mkdir -p "$DIR/instance"

WSGI=$(ls /var/www/*_wsgi.py 2>/dev/null | head -1)
if [ -z "$WSGI" ]; then
  echo "АЛДАА: Web таб дээр эхлээд web app үүсгэнэ үү (Manual configuration)."
  exit 1
fi

# Flask ихэвчлэн суусан байдаг; байхгүй хувилбарт л суулгана (2 минутын хязгаартай).
for v in 3.10 3.11 3.12 3.13 3.14; do
  if command -v "python$v" >/dev/null; then
    if "python$v" -c "import flask" 2>/dev/null; then
      echo "python$v: Flask бэлэн"
    else
      echo "python$v: Flask суулгаж байна..."
      timeout 120 "python$v" -m pip install --user -q "flask>=3.0" || echo "python$v: алгаслаа"
    fi
  fi
done
cp "$DIR/deploy/pythonanywhere_wsgi.py" "$WSGI"
touch "$WSGI"  # web app-ийг дахин ачаална
echo "БЭЛЭН: https://$(basename "$WSGI" _wsgi.py | tr _ .)"
