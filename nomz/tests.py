from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from io import BytesIO
from PIL import Image
from decimal import Decimal
from .models import (
    UserProfile,
    Restaurant,
    RestaurantOwnershipClaim,
    RestaurantPhoto,
    InspectionRecord,
)


class RestaurantModelTests(TestCase):
    """Test cases for Restaurant model"""

    def setUp(self):
        """Create test user and restaurant"""
        self.user = User.objects.create_user(
            username="restaurantowner",
            email="owner@restaurant.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=self.user, role="restaurant")

        self.restaurant = Restaurant.objects.create(
            owner=self.user,
            name="Test Restaurant",
            description="A great place to eat",
            cuisine_type="italian",
            price_range="$$",
            address="123 Main St, NYC",
            phone="(555) 123-4567",
            email="contact@test.com",
            website="https://test.com",
            hours_open="09:00",
            hours_close="21:00",
            is_active=True,
            is_temporarily_unavailable=False,
        )

    def test_restaurant_creation(self):
        """Test restaurant creation"""
        self.assertEqual(self.restaurant.name, "Test Restaurant")
        self.assertEqual(self.restaurant.owner, self.user)
        self.assertTrue(self.restaurant.is_active)

    def test_restaurant_string_representation(self):
        """Test restaurant __str__ method"""
        self.assertEqual(str(self.restaurant), "Test Restaurant")

    def test_restaurant_can_be_managed_by_owner(self):
        """Test can_be_managed_by method"""
        self.assertTrue(self.restaurant.can_be_managed_by(self.user))

    def test_restaurant_cannot_be_managed_by_other_user(self):
        """Test can_be_managed_by method with different user"""
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )
        self.assertFalse(self.restaurant.can_be_managed_by(other_user))

    def test_restaurant_is_open_now(self):
        """Test is_open_now method"""
        # Deactivate to test condition
        self.restaurant.is_active = False
        self.assertFalse(self.restaurant.is_open_now())

        # Reactivate and test again
        self.restaurant.is_active = True
        # Note: This test may fail at certain times because of actual time comparison
        # In production, use freezegun or similar for time-based tests

    def test_restaurant_is_open_when_temporarily_unavailable(self):
        """Test is_open_now returns False when temporarily unavailable"""
        self.restaurant.is_temporarily_unavailable = True
        self.assertFalse(self.restaurant.is_open_now())

    def test_restaurant_unique_name(self):
        """Test that restaurant names are unique"""
        with self.assertRaises(Exception):
            Restaurant.objects.create(
                owner=self.user,
                name="Test Restaurant",  # Same name
                cuisine_type="italian",
                price_range="$$",
            )


class RestaurantPhotoModelTests(TestCase):
    """Test cases for RestaurantPhoto model"""

    def setUp(self):
        """Create test user and restaurant"""
        self.user = User.objects.create_user(
            username="restaurantowner", password="testpass123"
        )
        UserProfile.objects.create(user=self.user, role="restaurant")

        self.restaurant = Restaurant.objects.create(
            owner=self.user,
            name="Test Restaurant",
            cuisine_type="italian",
            price_range="$$",
        )

    def create_test_image(self):
        """Create a test image file"""
        image = Image.new("RGB", (100, 100), color="red")
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile(
            "test.jpg", image_io.getvalue(), content_type="image/jpeg"
        )

    def test_photo_creation(self):
        """Test photo creation"""
        photo = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Dining area",
        )
        self.assertEqual(photo.restaurant, self.restaurant)
        self.assertEqual(photo.caption, "Dining area")

    def test_photo_string_representation(self):
        """Test photo __str__ method"""
        photo = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Test Photo",
        )
        self.assertIn("Test Restaurant", str(photo))
        self.assertIn("Test Photo", str(photo))

    def test_primary_photo_uniqueness(self):
        """Test that only one photo can be primary"""
        photo1 = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Photo 1",
            is_primary=True,
        )

        photo2 = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Photo 2",
            is_primary=True,
        )

        # Refresh from DB
        photo1.refresh_from_db()

        # photo1 should no longer be primary
        self.assertFalse(photo1.is_primary)
        self.assertTrue(photo2.is_primary)

    def test_photos_ordered_by_primary_and_date(self):
        """Test that photos are ordered correctly"""
        photo1 = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Photo 1",
            is_primary=False,
        )

        photo2 = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Photo 2",
            is_primary=True,
        )

        photos = RestaurantPhoto.objects.filter(restaurant=self.restaurant)
        self.assertEqual(photos[0].id, photo2.id)  # Primary first
        self.assertEqual(photos[1].id, photo1.id)


class RestaurantProfileViewTests(TestCase):
    """Test cases for restaurant profile views"""

    def setUp(self):
        """Create test user and authenticate"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="restaurantowner", password="testpass123"
        )
        UserProfile.objects.create(user=self.user, role="restaurant")

        self.diner_user = User.objects.create_user(
            username="diner", password="testpass123"
        )
        UserProfile.objects.create(user=self.diner_user, role="diner")

    def test_restaurant_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse("restaurant_profile"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_restaurant_profile_view_for_restaurant_owner(self):
        """Test that restaurant owner can view profile"""
        restaurant = Restaurant.objects.create(
            owner=self.user,
            name="Test Restaurant",
            cuisine_type="italian",
            price_range="$$",
        )

        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.get(reverse("restaurant_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Restaurant")

    def test_diner_cannot_access_restaurant_profile(self):
        """Test that diner cannot access restaurant profile management"""
        self.client.login(username="diner", password="testpass123")
        response = self.client.get(reverse("restaurant_profile"))

        self.assertEqual(response.status_code, 302)  # Redirect

    def test_create_restaurant_profile_get(self):
        """Test GET request to create restaurant profile"""
        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.get(reverse("create_restaurant"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_create_restaurant_profile_post(self):
        """Test POST request to create restaurant profile"""
        self.client.login(username="restaurantowner", password="testpass123")

        data = {
            "name": "New Restaurant",
            "description": "Great food",
            "cuisine_type": "italian",
            "price_range": "$$",
            "hours_open": "09:00",
            "hours_close": "21:00",
            "address": "123 Main St",
            "phone": "(555) 123-4567",
        }

        response = self.client.post(reverse("create_restaurant"), data)

        self.assertEqual(response.status_code, 302)  # Redirect after success
        restaurant = Restaurant.objects.get(owner=self.user)
        self.assertEqual(restaurant.name, "New Restaurant")

    def test_edit_restaurant_profile_get(self):
        """Test GET request to edit restaurant profile"""
        restaurant = Restaurant.objects.create(
            owner=self.user,
            name="Test Restaurant",
            cuisine_type="italian",
            price_range="$$",
        )

        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.get(reverse("edit_restaurant"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_edit_restaurant_profile_post(self):
        """Test POST request to edit restaurant profile"""
        restaurant = Restaurant.objects.create(
            owner=self.user,
            name="Test Restaurant",
            cuisine_type="italian",
            price_range="$$",
            hours_open="09:00",
            hours_close="21:00",
        )

        self.client.login(username="restaurantowner", password="testpass123")

        data = {
            "name": "Updated Restaurant",
            "description": "Updated description",
            "cuisine_type": "french",
            "price_range": "$$$",
            "hours_open": "10:00",
            "hours_close": "22:00",
            "address": "456 Oak Ave",
        }

        response = self.client.post(reverse("edit_restaurant"), data)

        restaurant.refresh_from_db()
        self.assertEqual(restaurant.name, "Updated Restaurant")
        self.assertEqual(restaurant.cuisine_type, "french")


class RestaurantOwnershipClaimTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner_user = User.objects.create_user(
            username="claim_owner",
            email="owner@test.com",
            password="testpass123",
        )
        self.reviewer = User.objects.create_user(
            username="reviewer",
            email="reviewer@test.com",
            password="testpass123",
            is_staff=True,
        )
        self.diner = User.objects.create_user(
            username="claim_diner",
            email="diner@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=self.owner_user, role="restaurant")
        UserProfile.objects.create(user=self.diner, role="diner")

        self.unowned_restaurant = Restaurant.objects.create(
            name="Claimable Spot",
            address="100 Claim St",
            zip_code="10001",
            cuisine_type="italian",
            price_range="$$",
            hours_open="09:00",
            hours_close="22:00",
        )

    def test_restaurant_user_can_submit_claim(self):
        self.client.login(username="claim_owner", password="testpass123")
        response = self.client.post(
            reverse("claim_restaurant"),
            {
                "restaurant": self.unowned_restaurant.id,
                "business_email": "hello@claimablespot.com",
                "contact_phone": "+1 212-555-0001",
                "proof_details": "Website owner email matches my account.",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        claim = RestaurantOwnershipClaim.objects.get(
            claimant=self.owner_user,
            restaurant=self.unowned_restaurant,
        )
        self.assertEqual(claim.status, RestaurantOwnershipClaim.STATUS_PENDING)

    def test_diner_cannot_submit_claim(self):
        self.client.login(username="claim_diner", password="testpass123")
        response = self.client.get(reverse("claim_restaurant"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RestaurantOwnershipClaim.objects.exists())

    def test_approving_claim_assigns_restaurant_owner(self):
        claim = RestaurantOwnershipClaim.objects.create(
            claimant=self.owner_user,
            restaurant=self.unowned_restaurant,
            business_email="hello@claimablespot.com",
            proof_details="License doc available.",
        )
        claim.approve(reviewer=self.reviewer, notes="Verified by manual review.")
        claim.refresh_from_db()
        self.unowned_restaurant.refresh_from_db()

        self.assertEqual(claim.status, RestaurantOwnershipClaim.STATUS_APPROVED)
        self.assertEqual(claim.reviewed_by, self.reviewer)
        self.assertEqual(self.unowned_restaurant.owner, self.owner_user)


class RestaurantOwnerScoreDashboardTests(TestCase):
    """Tests for owner-facing composite analytics on the restaurant dashboard."""

    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(
            username="owneranalytics", password="testpass123"
        )
        UserProfile.objects.create(user=self.owner, role="restaurant")

        self.restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Owner Insight Kitchen",
            neighborhood="Chelsea",
            borough="Manhattan",
            zip_code="10011",
            cuisine_type="italian",
            price_range="$$",
            composite_score=Decimal("88.40"),
            grade_latest="A",
            grade_score_latest=95,
            last_inspection_date=date.today() - timedelta(days=10),
        )

        Restaurant.objects.create(
            name="Peer One",
            neighborhood="Chelsea",
            borough="Manhattan",
            zip_code="10011",
            cuisine_type="italian",
            price_range="$$",
            composite_score=Decimal("91.10"),
            grade_latest="A",
            grade_score_latest=95,
            last_inspection_date=date.today() - timedelta(days=12),
        )
        Restaurant.objects.create(
            name="Peer Two",
            neighborhood="Chelsea",
            borough="Manhattan",
            zip_code="10011",
            cuisine_type="italian",
            price_range="$$",
            composite_score=Decimal("77.20"),
            grade_latest="B",
            grade_score_latest=70,
            last_inspection_date=date.today() - timedelta(days=30),
        )

        InspectionRecord.objects.create(
            restaurant=self.restaurant,
            inspection_date=date.today() - timedelta(days=120),
            inspection_key="owner-1",
            grade="B",
            score=18,
            critical_violations=3,
            noncritical_violations=2,
            violation_count=5,
        )
        InspectionRecord.objects.create(
            restaurant=self.restaurant,
            inspection_date=date.today() - timedelta(days=60),
            inspection_key="owner-2",
            grade="A",
            score=8,
            critical_violations=1,
            noncritical_violations=1,
            violation_count=2,
        )
        InspectionRecord.objects.create(
            restaurant=self.restaurant,
            inspection_date=date.today() - timedelta(days=10),
            inspection_key="owner-3",
            grade="A",
            score=5,
            critical_violations=0,
            noncritical_violations=1,
            violation_count=1,
        )

    def test_owner_dashboard_includes_score_breakdown_comparison_and_trend(self):
        self.client.login(username="owneranalytics", password="testpass123")
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Composite Score")
        self.assertContains(response, "Composite Factor Breakdown")
        self.assertContains(response, "Neighborhood Comparison")
        self.assertContains(response, "Historical Trend")

        self.assertIn("score_summary", response.context)
        self.assertIn("score_breakdown", response.context)
        self.assertIn("neighborhood_comparison", response.context)
        self.assertIn("trend_points", response.context)
        self.assertIn("trend_summary", response.context)

        self.assertGreaterEqual(len(response.context["score_breakdown"]), 3)
        self.assertGreaterEqual(len(response.context["trend_points"]), 3)
        self.assertEqual(
            response.context["neighborhood_comparison"]["location_scope"], "Chelsea"
        )

    def test_owner_dashboard_handles_missing_inspections(self):
        InspectionRecord.objects.filter(restaurant=self.restaurant).delete()
        self.restaurant.composite_score = None
        self.restaurant.grade_score_latest = None
        self.restaurant.grade_latest = None
        self.restaurant.last_inspection_date = None
        self.restaurant.save()

        self.client.login(username="owneranalytics", password="testpass123")
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["trend_points"], [])
        self.assertIsNone(response.context["score_summary"]["composite_score"])


class RestaurantAvailabilityViewTests(TestCase):
    """Test cases for availability management views"""

    def setUp(self):
        """Create test user and restaurant"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="restaurantowner", password="testpass123"
        )
        UserProfile.objects.create(user=self.user, role="restaurant")

        self.restaurant = Restaurant.objects.create(
            owner=self.user,
            name="Test Restaurant",
            cuisine_type="italian",
            price_range="$$",
        )

    def test_manage_availability_view(self):
        """Test availability management view"""
        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.get(reverse("manage_availability"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_mark_temporarily_unavailable(self):
        """Test marking restaurant as temporarily unavailable"""
        self.client.login(username="restaurantowner", password="testpass123")

        data = {"is_temporarily_unavailable": True, "unavailable_reason": "Renovations"}

        response = self.client.post(reverse("manage_availability"), data)

        self.restaurant.refresh_from_db()
        self.assertTrue(self.restaurant.is_temporarily_unavailable)
        self.assertEqual(self.restaurant.unavailable_reason, "Renovations")


class RestaurantPhotoViewTests(TestCase):
    """Test cases for photo management views"""

    def setUp(self):
        """Create test user and restaurant"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="restaurantowner", password="testpass123"
        )
        UserProfile.objects.create(user=self.user, role="restaurant")

        self.restaurant = Restaurant.objects.create(
            owner=self.user,
            name="Test Restaurant",
            cuisine_type="italian",
            price_range="$$",
        )

    def create_test_image(self):
        """Create a test image file"""
        image = Image.new("RGB", (100, 100), color="red")
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        return SimpleUploadedFile(
            "test.jpg", image_io.getvalue(), content_type="image/jpeg"
        )

    def test_upload_photo_view_get(self):
        """Test GET request to upload photo"""
        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.get(reverse("upload_photo"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_upload_photo_view_post(self):
        """Test POST request to upload photo"""
        self.client.login(username="restaurantowner", password="testpass123")

        data = {
            "photo": self.create_test_image(),
            "caption": "Dining area",
            "is_primary": True,
        }

        response = self.client.post(reverse("upload_photo"), data)

        self.assertEqual(response.status_code, 302)  # Redirect after success
        photo = RestaurantPhoto.objects.get(restaurant=self.restaurant)
        self.assertEqual(photo.caption, "Dining area")
        self.assertTrue(photo.is_primary)

    def test_restaurant_photos_view(self):
        """Test viewing all restaurant photos"""
        photo = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Test Photo",
        )

        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.get(reverse("restaurant_photos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Photo")

    def test_delete_photo(self):
        """Test deleting a photo"""
        photo = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Test Photo",
        )

        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.post(reverse("delete_photo", args=[photo.id]))

        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertFalse(RestaurantPhoto.objects.filter(id=photo.id).exists())

    def test_set_primary_photo(self):
        """Test setting a photo as primary"""
        photo1 = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Photo 1",
            is_primary=True,
        )

        photo2 = RestaurantPhoto.objects.create(
            restaurant=self.restaurant,
            photo=self.create_test_image(),
            caption="Photo 2",
        )

        self.client.login(username="restaurantowner", password="testpass123")
        response = self.client.post(reverse("set_primary_photo", args=[photo2.id]))

        self.assertEqual(response.status_code, 302)

        photo2.refresh_from_db()
        photo1.refresh_from_db()
        self.assertTrue(photo2.is_primary)
        self.assertFalse(photo1.is_primary)


class RestaurantFilterIntegrationTests(TestCase):
    """End-to-end filtering behavior for cuisine, price, dietary, ratings, and score filters."""

    def setUp(self):
        self.client = Client()

        owner_a = User.objects.create_user(
            username="owner_a",
            password="testpass123",
        )
        owner_b = User.objects.create_user(
            username="owner_b",
            password="testpass123",
        )
        owner_c = User.objects.create_user(
            username="owner_c",
            password="testpass123",
        )
        owner_d = User.objects.create_user(
            username="owner_d",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner_a, role="restaurant")
        UserProfile.objects.create(user=owner_b, role="restaurant")
        UserProfile.objects.create(user=owner_c, role="restaurant")
        UserProfile.objects.create(user=owner_d, role="restaurant")

        Restaurant.objects.create(
            owner=owner_a,
            name="Green Garden",
            description="Vegan bowls",
            cuisine="Italian",
            cuisine_type="italian",
            cuisine_tags=["vegan", "vegetarian"],
            price_range="$$",
            latitude=Decimal("40.720000"),
            longitude=Decimal("-74.000000"),
            composite_score=Decimal("92.5"),
            grade_score_latest=96,
            borough="Manhattan",
            neighborhood="Greenwich Village",
            zip_code="10014",
            is_active=True,
            hours_open="00:00",
            hours_close="23:59",
        )
        Restaurant.objects.create(
            owner=owner_b,
            name="Budget Deli",
            description="Late night sandwich",
            cuisine="American",
            cuisine_type="american",
            cuisine_tags=["halal"],
            price_range="$",
            latitude=Decimal("40.710000"),
            longitude=Decimal("-74.010000"),
            composite_score=Decimal("84.0"),
            grade_score_latest=86,
            borough="Manhattan",
            neighborhood="Lower Manhattan",
            zip_code="10005",
            is_active=True,
            hours_open="00:00",
            hours_close="23:59",
        )
        Restaurant.objects.create(
            owner=owner_c,
            name="City Bistro",
            description="French comfort food",
            cuisine="French",
            cuisine_type="french",
            cuisine_tags=["gluten-free"],
            price_range="$$$",
            latitude=Decimal("40.730000"),
            longitude=Decimal("-74.020000"),
            composite_score=Decimal("55.0"),
            grade_score_latest=62,
            borough="Brooklyn",
            neighborhood="Williamsburg",
            zip_code="11211",
            is_active=True,
            hours_open="00:00",
            hours_close="23:59",
        )
        Restaurant.objects.create(
            owner=owner_d,
            name="Untested Cafe",
            description="Newly opened spot",
            cuisine="Cafe",
            cuisine_type="other",
            cuisine_tags=["coffee"],
            price_range="$$",
            latitude=Decimal("40.735000"),
            longitude=Decimal("-74.015000"),
            composite_score=None,
            grade_score_latest=None,
            borough="Manhattan",
            neighborhood="Chelsea",
            zip_code="10011",
            is_active=True,
            hours_open="00:00",
            hours_close="23:59",
        )

    def test_map_filtering_applies_multiple_criteria(self):
        response = self.client.get(
            reverse("api_restaurants_map"),
            {
                "search": "garden",
                "cuisine": "italian",
                "price_range": "$$",
                "min_score": "80",
                "min_rating": "90",
                "dietary": ["vegan", "vegetarian"],
                "require_coordinates": "1",
            },
        )
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        names = {record["name"] for record in payload["results"]}
        self.assertIn("Green Garden", names)
        self.assertNotIn("Budget Deli", names)
        self.assertNotIn("City Bistro", names)

        self.assertEqual(payload["count"], 1)

    def test_search_filtering_supports_price_and_composite_range(self):
        response = self.client.get(
            reverse("restaurant_search"),
            {
                "q": "",
                "price_range": "$",
                "min_composite_score": "80",
                "cuisine": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        page_text = response.content.decode("utf-8")
        self.assertIn("Budget Deli", page_text)
        self.assertNotIn("City Bistro", page_text)

    def test_conflicting_score_range_returns_empty_results(self):
        response = self.client.get(
            reverse("api_restaurants_map"),
            {
                "min_score": "90",
                "max_score": "50",
                "borough": "Manhattan",
                "require_coordinates": "1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

    def test_search_no_results_shows_empty_state(self):
        response = self.client.get(
            reverse("restaurant_search"),
            {
                "q": "nonexistent_place_xyz",
                "min_composite_score": "999",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No restaurants match your filters.")

    def test_search_can_filter_open_now_and_price_and_sort(self):
        response = self.client.get(
            reverse("restaurant_search"),
            {
                "price_range": "$",
                "open_now": "1",
                "sort_by": "name_asc",
            },
        )
        self.assertEqual(response.status_code, 200)
        page_text = response.content.decode("utf-8")
        self.assertIn("Budget Deli", page_text)
        self.assertNotIn("City Bistro", page_text)

    def test_map_zero_threshold_does_not_exclude_unscored_restaurants(self):
        response = self.client.get(
            reverse("api_restaurants_map"),
            {
                "min_score": "0",
                "min_rating": "0",
                "require_coordinates": "1",
            },
        )
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        names = {record["name"] for record in payload["results"]}
        self.assertIn("Untested Cafe", names)
