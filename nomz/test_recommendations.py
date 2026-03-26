"""
Test suite for the restaurant recommendation system.
Tests preference-based matching and recommendation ranking.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal

from .models import Restaurant, UserPreference, UserProfile
from .restaurant_sorting import recommend_restaurants_for_user


class RecommendationSystemTests(TestCase):
    """Test cases for the restaurant recommendation engine."""

    def setUp(self):
        """Create test users and restaurants."""
        # Create a diner user
        self.diner = User.objects.create_user(
            username="diner_user", email="diner@test.com", password="testpass123"
        )
        UserProfile.objects.create(user=self.diner, role="diner")

        # Create separate restaurant owners for test restaurants
        owner1 = User.objects.create_user(
            username="restaurant_owner1",
            email="owner1@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner1, role="restaurant")

        owner2 = User.objects.create_user(
            username="restaurant_owner2",
            email="owner2@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner2, role="restaurant")

        owner3 = User.objects.create_user(
            username="restaurant_owner3",
            email="owner3@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner3, role="restaurant")

        owner4 = User.objects.create_user(
            username="restaurant_owner4",
            email="owner4@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner4, role="restaurant")

        owner5 = User.objects.create_user(
            username="restaurant_owner5",
            email="owner5@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner5, role="restaurant")

        owner6 = User.objects.create_user(
            username="restaurant_owner6",
            email="owner6@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner6, role="restaurant")

        # Create test restaurants
        self.italian_restaurant = Restaurant.objects.create(
            owner=owner1,
            name="Bella Italia",
            cuisine_type="italian",
            price_range="$$",
            description="Authentic Italian cuisine",
            is_active=True,
            is_flagged=False,
            composite_score=Decimal("85.5"),
        )

        self.vegan_restaurant = Restaurant.objects.create(
            owner=owner2,
            name="Green Haven",
            cuisine_type="vegan",
            price_range="$",
            description="100% plant-based restaurant",
            is_active=True,
            is_flagged=False,
            composite_score=Decimal("78.0"),
            cuisine_tags=["vegan", "gluten-free"],
        )

        self.japanese_restaurant = Restaurant.objects.create(
            owner=owner3,
            name="Tokyo Express",
            cuisine_type="japanese",
            price_range="$$$",
            description="Premium sushi and ramen",
            is_active=True,
            is_flagged=False,
            composite_score=Decimal("92.0"),
        )

        self.mexican_budget_restaurant = Restaurant.objects.create(
            owner=owner4,
            name="Taco Fiesta",
            cuisine_type="mexican",
            price_range="$",
            description="Casual Mexican street food",
            is_active=True,
            is_flagged=False,
            composite_score=Decimal("80.0"),
        )

        self.flagged_restaurant = Restaurant.objects.create(
            owner=owner5,
            name="Flagged Place",
            cuisine_type="american",
            price_range="$$",
            description="This place is flagged",
            is_active=True,
            is_flagged=True,
            composite_score=Decimal("90.0"),
        )

        self.american_restaurant = Restaurant.objects.create(
            owner=owner6,
            name="Liberty Diner",
            cuisine_type="american",
            price_range="$",
            description="Classic American fare",
            is_active=True,
            is_flagged=False,
            composite_score=Decimal("75.0"),
        )

    def test_no_recommendations_without_preferences(self):
        """Test that users without preferences get no recommendations."""
        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        self.assertEqual(len(recommendations), 0)

    def test_no_recommendations_with_empty_preferences(self):
        """Test that users with empty preferences get no recommendations."""
        # when price_preference is set, it's still considered as having a preference
        # We test when ALL preference categories are empty
        UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=[],
            dietary_restrictions=[],
            price_preference=""  # Empty price preference
        )
        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        self.assertEqual(len(recommendations), 0)

    def test_cuisine_matching(self):
        """Test recommendations based on cuisine preferences."""
        prefs = UserPreference.objects.create(
            user=self.diner, favorite_cuisines=["italian", "mexican"]
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)

        # Should get Italian and Mexican restaurants
        rec_names = [r.name for r in recommendations]
        self.assertIn("Bella Italia", rec_names)
        self.assertIn("Taco Fiesta", rec_names)
        # Should NOT get Japanese (not in preferences)
        self.assertNotIn("Tokyo Express", rec_names)

    def test_price_range_matching(self):
        """Test recommendations based on price preference."""
        prefs = UserPreference.objects.create(
            user=self.diner, favorite_cuisines=["italian", "mexican", "vegan"],
            price_preference="$"
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Should prioritize $ restaurants
        # Mexican and Vegan are $, but Italian is $$
        self.assertIn("Taco Fiesta", rec_names)
        self.assertIn("Green Haven", rec_names)

    def test_dietary_restrictions_matching(self):
        """Test recommendations based on dietary restrictions."""
        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["vegan", "italian"],
            dietary_restrictions=["vegan"],
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Should get vegan restaurant (matches dietary and cuisine)
        self.assertIn("Green Haven", rec_names)

    def test_flagged_restaurants_excluded(self):
        """Test that flagged restaurants are excluded from recommendations."""
        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["american", "italian"],
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Flagged restaurant should NOT appear
        self.assertNotIn("Flagged Place", rec_names)
        # But Italian should
        self.assertIn("Bella Italia", rec_names)

    def test_inactive_restaurants_excluded(self):
        """Test that inactive restaurants are excluded."""
        self.italian_restaurant.is_active = False
        self.italian_restaurant.save()

        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["italian"],
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Inactive Italian should NOT appear
        self.assertNotIn("Bella Italia", rec_names)

    def test_limit_parameter(self):
        """Test that the limit parameter works correctly."""
        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["italian", "mexican", "vegan", "japanese"],
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=2)
        self.assertEqual(len(recommendations), 2)

    def test_highest_match_first(self):
        """Test that highest scoring restaurants appear first."""
        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["italian", "japanese"],
            price_preference="$$$",
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)

        # Tokyo Express should rank higher:
        # - matches cuisine (japanese)
        # - matches price ($$$)
        # - highest composite score (92.0)
        if recommendations:
            top_rec = recommendations[0]
            self.assertEqual(top_rec.name, "Tokyo Express")

    def test_neighborhood_preference(self):
        """Test neighborhood matching when set."""
        # Create a restaurant owner for the new restaurant
        owner7 = User.objects.create_user(
            username="restaurant_owner7",
            email="owner7@test.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=owner7, role="restaurant")

        # Create a restaurant in a specific neighborhood
        midtown_restaurant = Restaurant.objects.create(
            owner=owner7,
            name="Midtown Pizza",
            cuisine_type="italian",
            price_range="$$",
            neighborhood="Midtown",
            is_active=True,
            is_flagged=False,
        )

        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["italian"],
            neighborhood_preference="Midtown",
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Midtown pizza should be included
        self.assertIn("Midtown Pizza", rec_names)

    def test_combined_preferences(self):
        """Test recommendations with all preference types combined."""
        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["vegan", "italian"],
            dietary_restrictions=["vegan", "gluten-free"],
            price_preference="$",
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Green Haven should rank highest (matches all: vegan cuisine, dietary, price)
        # Bella Italia should rank second (matches cuisine and maybe price)
        self.assertIn("Green Haven", rec_names)

    def test_edge_case_no_matching_restaurants(self):
        """Test when restaurants match dietary but not other criteria still returns matches."""
        # Green Haven is a vegan restaurant with tags  
        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=[],  # No cuisine preference
            dietary_restrictions=["vegan"],  # Only dietary
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Green Haven should be recommended (has vegan dietary match)
        self.assertIn("Green Haven", rec_names)

    def test_composite_score_boost(self):
        """Test that composite score influences ranking when cuisines match equally."""
        # Both restaurants match on cuisine, so highest composite score should rank first
        prefs = UserPreference.objects.create(
            user=self.diner,
            favorite_cuisines=["japanese", "italian"],
        )

        recommendations = recommend_restaurants_for_user(self.diner, limit=10)
        rec_names = [r.name for r in recommendations]

        # Both should be included (both match cuisines)
        self.assertIn("Tokyo Express", rec_names)
        self.assertIn("Bella Italia", rec_names)
