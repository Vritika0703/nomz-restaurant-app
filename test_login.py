import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from nomz.forms import AdminLoginForm

form = AdminLoginForm(data={
    'username': 'admin',
    'password': 'adminnomz2026',
    'security_code': 'ADM123'
})

print(f"Is valid: {form.is_valid()}")
if not form.is_valid():
    print(form.errors)
else:
    user = form.get_user()
    print(f"User backend: getattr(user, 'backend', None) -> {getattr(user, 'backend', None)}")

