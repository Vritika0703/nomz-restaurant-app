import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurants.settings")
os.environ["DEBUG"] = "True"
django.setup()

from nomz.models import Restaurant, User  # noqa: E402


def check_rest2_owner():
    print("Checking for user 'rest2' and its restaurant...")
    try:
        user = User.objects.get(username="rest2")
        print(f"User found: ID={user.id}, Username={user.username}")

        # Check if this user has a restaurant profile
        if hasattr(user, "restaurant_profile"):
            res = user.restaurant_profile
            print(
                f"Restaurant Profile found: ID={res.id}, Name='{res.name}', DisplayName='{res.display_name}'"
            )
        else:
            print("User 'rest2' has NO restaurant_profile.")

            # Check if there's a restaurant with this owner_id
            res = Restaurant.objects.filter(owner=user).first()
            if res:
                print(
                    f"Restaurant linked by owner_id found: ID={res.id}, Name='{res.name}'"
                )
            else:
                print(f"No Restaurant found with owner_id={user.id}")
    except User.DoesNotExist:
        print("User 'rest2' NOT found.")


if __name__ == "__main__":
    check_rest2_owner()
