import os
import sys
import django

# Add the project directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurants.settings")
# Force DEBUG=True to use SQLite
os.environ["DEBUG"] = "True"
django.setup()

from nomz.models import (  # noqa: E402
    Restaurant,
    RestaurantSearch,
    RestaurantSourceRecord,
    User,
)  # noqa: E402


def find_rest2():
    print("Searching for 'rest2'...")

    # Search User (in case it's a username)
    u = User.objects.filter(username__icontains="rest2")
    print(
        f"User (username): {u.count()} found. {list(u.values_list('username', flat=True))}"
    )

    # Search Restaurant
    res1 = Restaurant.objects.filter(name__icontains="rest2")
    print(
        f"Restaurant (name): {res1.count()} found. {list(res1.values_list('name', flat=True))}"
    )

    res2 = Restaurant.objects.filter(display_name__icontains="rest2")
    print(
        f"Restaurant (display_name): {res2.count()} found. {list(res2.values_list('display_name', flat=True))}"
    )

    # Search RestaurantSearch
    try:
        res3 = RestaurantSearch.objects.filter(name__icontains="rest2")
        print(
            f"RestaurantSearch (name): {res3.count()} found. {list(res3.values_list('name', flat=True))}"
        )
    except Exception as e:
        print(f"RestaurantSearch check failed: {e}")

    # Search RestaurantSourceRecord
    try:
        res4 = RestaurantSourceRecord.objects.filter(name__icontains="rest2")
        print(f"RestaurantSourceRecord (name): {res4.count()} found.")
    except Exception as e:
        print(f"RestaurantSourceRecord check failed: {e}")


if __name__ == "__main__":
    find_rest2()
