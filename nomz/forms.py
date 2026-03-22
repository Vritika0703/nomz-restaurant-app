from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from decouple import config
from .models import (
    UserProfile,
    Restaurant,
    RestaurantPhoto,
    RestaurantOwnershipClaim,
    UserPreference,
)


class UserRegisterForm(UserCreationForm):
    """
    Custom user registration form that extends Django's UserCreationForm.
    Adds email field and improves styling.
    """

    # Add the Role selection field
    ROLE_CHOICES = [
        ("diner", "I am a Diner"),
        ("restaurant", "I am a Restaurant Owner"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, widget=forms.Select(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email address"}
        ),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm password"}
        ),
    )

    class Meta:
        model = User
        fields = ["email", "username", "role", "password1", "password2"]

    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        """Save user with email AND create their UserProfile"""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # This is where the backend permanently stores the role!
            UserProfile.objects.create(user=user, role=self.cleaned_data["role"])
        return user


class UserLoginForm(AuthenticationForm):
    """
    Custom login form that extends Django's AuthenticationForm.
    Adds Bootstrap styling for better UI.
    """

    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username or Email"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )


class AdminLoginForm(UserLoginForm):
    """
    Login form for administrators with an extra security code field.
    """

    security_code = forms.CharField(
        max_length=20,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Security Code"}
        ),
        help_text="Enter the administrative security code.",
    )

    def clean(self):
        cleaned_data = super().clean()
        security_code = cleaned_data.get("security_code")
        expected_code = config("ADMIN_SECURITY_CODE", default="ADM123")

        if security_code != expected_code:
            raise forms.ValidationError("Invalid security code.")

        user = self.get_user()
        if user and not (user.is_staff or user.is_superuser):
            raise forms.ValidationError("This login is restricted to administrators.")

        return cleaned_data


class RestaurantProfileForm(forms.ModelForm):
    """
    Form for restaurant owners to create and edit their restaurant profile.
    Handles description, hours, cuisine type, and price range.
    """

    class Meta:
        model = Restaurant
        fields = [
            "name",
            "description",
            "cuisine_type",
            "price_range",
            "hours_open",
            "hours_close",
            "address",
            "phone",
            "website",
            "email",
        ]
        labels = {
            "name": "Restaurant Name",
            "description": "Description & Ambiance",
            "cuisine_type": "Cuisine Type",
            "price_range": "Price Range",
            "hours_open": "Opening Time",
            "hours_close": "Closing Time",
            "address": "Address",
            "phone": "Phone Number",
            "website": "Website",
            "email": "Contact Email",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'e.g., "The Italian Corner"',
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe your restaurant, cuisine style, and special offerings...",
                }
            ),
            "cuisine_type": forms.Select(attrs={"class": "form-control"}),
            "price_range": forms.Select(attrs={"class": "form-control"}),
            "hours_open": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "hours_close": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'e.g., "123 Main St, New York, NY 10001"',
                }
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "(123) 456-7890"}
            ),
            "website": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.example.com",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "contact@restaurant.com"}
            ),
        }


class RestaurantAvailabilityForm(forms.ModelForm):
    """
    Form for restaurant owners to mark temporary unavailability.
    """

    class Meta:
        model = Restaurant
        fields = [
            "is_temporarily_unavailable",
            "unavailable_reason",
            "unavailable_until",
        ]
        labels = {
            "is_temporarily_unavailable": "Mark as Temporarily Unavailable",
            "unavailable_reason": "Reason for Unavailability",
            "unavailable_until": "Available Again On",
        }
        widgets = {
            "is_temporarily_unavailable": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "unavailable_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "e.g., Renovations, Special Event, Staffing Issues...",
                }
            ),
            "unavailable_until": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }


class RestaurantActivationForm(forms.ModelForm):
    """
    Form for restaurant owners to activate/deactivate their profile.
    """

    class Meta:
        model = Restaurant
        fields = ["is_active"]
        labels = {
            "is_active": "Profile Active & Visible to Customers",
        }
        widgets = {
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class RestaurantPhotoForm(forms.ModelForm):
    """
    Form for uploading restaurant photos.
    """

    class Meta:
        model = RestaurantPhoto
        fields = ["photo", "caption", "is_primary"]
        labels = {
            "photo": "Photo",
            "caption": "Photo Caption",
            "is_primary": "Set as Main Photo",
        }
        widgets = {
            "photo": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "caption": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": 'e.g., "Dining Area", "Signature Dish"',
                }
            ),
            "is_primary": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class UserPreferenceForm(forms.ModelForm):
    # Defining choices manually or pulling from Restaurant.CUISINE_CHOICES
    CUISINE_OPTIONS = Restaurant.CUISINE_CHOICES
    DIETARY_CHOICES = [
        ("Vegan", "Vegan"),
        ("Vegetarian", "Vegetarian"),
        ("Non-vegetarian", "Non-vegetarian"),
        ("Gluten-Free", "Gluten-Free"),
        ("Halal", "Halal"),
        ("Kosher", "Kosher"),
    ]

    favorite_cuisines = forms.MultipleChoiceField(
        choices=CUISINE_OPTIONS, widget=forms.CheckboxSelectMultiple, required=False
    )
    dietary_restrictions = forms.MultipleChoiceField(
        choices=DIETARY_CHOICES, widget=forms.CheckboxSelectMultiple, required=False
    )

    class Meta:
        model = UserPreference
        fields = [
            "favorite_cuisines",
            "dietary_restrictions",
            "price_preference",
            "neighborhood_preference",
        ]


class RestaurantOwnershipClaimForm(forms.ModelForm):
    restaurant = forms.ModelChoiceField(
        queryset=Restaurant.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Pick your restaurant from the existing database records.",
    )

    class Meta:
        model = RestaurantOwnershipClaim
        fields = ["restaurant", "business_email", "contact_phone", "proof_details"]
        labels = {
            "business_email": "Business Email",
            "contact_phone": "Business Phone",
            "proof_details": "Verification Details",
        }
        widgets = {
            "business_email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "owner@restaurant.com"}
            ),
            "contact_phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 212-555-1234"}
            ),
            "proof_details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Share proof like website manager email match, business license number, menu system access, or public listing links.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        search_query = (kwargs.pop("search_query", "") or "").strip()
        super().__init__(*args, **kwargs)

        queryset = Restaurant.objects.filter(owner__isnull=True)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(address__icontains=search_query)
                | Q(zip_code__icontains=search_query)
            )

        self.fields["restaurant"].queryset = queryset.order_by("name")[:100]

        selected_restaurant_id = self.data.get("restaurant") or self.initial.get(
            "restaurant"
        )
        if selected_restaurant_id:
            self.fields["restaurant"].queryset = Restaurant.objects.filter(
                Q(owner__isnull=True) | Q(pk=selected_restaurant_id)
            ).order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        restaurant = cleaned_data.get("restaurant")
        if not self.user or not restaurant:
            return cleaned_data

        if Restaurant.objects.filter(owner=self.user).exists():
            raise forms.ValidationError("You already own a restaurant profile.")

        if restaurant.owner and restaurant.owner != self.user:
            raise forms.ValidationError(
                "This restaurant is already owned by another user."
            )

        existing_claim = RestaurantOwnershipClaim.objects.filter(
            claimant=self.user,
            restaurant=restaurant,
            status=RestaurantOwnershipClaim.STATUS_PENDING,
        ).exists()
        if existing_claim:
            raise forms.ValidationError(
                "You already submitted a pending claim for this restaurant."
            )

        other_pending = RestaurantOwnershipClaim.objects.filter(
            claimant=self.user,
            status=RestaurantOwnershipClaim.STATUS_PENDING,
        ).exists()
        if other_pending:
            raise forms.ValidationError(
                "You already have another pending ownership claim."
            )

        restaurant_pending = RestaurantOwnershipClaim.objects.filter(
            restaurant=restaurant,
            status=RestaurantOwnershipClaim.STATUS_PENDING,
        ).exists()
        if restaurant_pending:
            raise forms.ValidationError(
                "This restaurant already has a pending claim under review."
            )

        return cleaned_data

    def save(self, commit=True):
        claim = super().save(commit=False)
        claim.claimant = self.user
        if commit:
            claim.save()
        return claim
