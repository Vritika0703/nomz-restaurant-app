import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.hashers import check_password
submitted_pw = "adminnomz2026"
hash_pw = "pbkdf2_sha256$600000$NvKgdMfTjHfGXwLuieCtCo$r3maZLapzui28vRpgClLYsUaBjSjBsyyBunVvCEoVNc="

print(f"Is match: {check_password(submitted_pw, hash_pw)}")
