import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurants.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from nomz.models import FriendConversation, UserProfile  # noqa: E402

u1, _ = User.objects.get_or_create(
    username="admin", defaults={"email": "admin@example.com"}
)
u1.set_password("admin_password")
u1.is_staff = True
u1.is_superuser = True
u1.save()

u2, _ = User.objects.get_or_create(
    username="friend", defaults={"email": "friend@example.com"}
)
u2.set_password("friend_password")
u2.save()

UserProfile.objects.get_or_create(user=u1, defaults={"role": "diner"})
UserProfile.objects.get_or_create(user=u2, defaults={"role": "diner"})

conv, created = FriendConversation.objects.get_or_create(
    user1=u1, user2=u2, is_group=False
)
if created:
    conv.participants.add(u1, u2)

print("Setup complete. admin/admin_password and friend/friend_password created.")
