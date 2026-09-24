# PythonAnywhere-ийн WSGI файл. deploy/pythonanywhere_setup.sh үүнийг
# /var/www/<хэрэглэгч>_pythonanywhere_com_wsgi.py руу автоматаар хуулна.
import os
import secrets
import sys

HOME = os.path.expanduser("~")
PROJECT = os.path.join(HOME, "my-project")

key_file = os.path.join(HOME, ".engineers_secret")
if not os.path.exists(key_file):
    with open(key_file, "w") as f:
        f.write(secrets.token_hex(32))
    os.chmod(key_file, 0o600)
with open(key_file) as f:
    os.environ.setdefault("SECRET_KEY", f.read().strip())
os.environ.setdefault("DATABASE", os.path.join(PROJECT, "instance", "engineers.db"))

sys.path.insert(0, PROJECT)
from app import create_app  # noqa: E402

application = create_app()
