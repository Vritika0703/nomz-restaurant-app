from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    UserProfile,
    Restaurant,
    RestaurantPhoto,
    UserPreference,
    Review,
    ModerationReport,
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
            # Restaurant accounts start as NOT approved pending admin review (Issue #53)
            is_approved = self.cleaned_data["role"] != "restaurant"
            UserProfile.objects.create(
                user=user, role=self.cleaned_data["role"], is_approved=is_approved
            )
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
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        security_code = self.cleaned_data.get("security_code")

        # Hardcoded admin username, but the password is a secure hash so it is safe for GitHub
        HARDCODED_USER = "admin"
        HARDCODED_PASS_HASH = "pbkdf2_sha256$600000$NvKgdMfTjHfGXwLuieCtCo$r3maZLapzui28vRpgClLYsUaBjSjBsyyBunVvCEoVNc="

        self.user_cache = None

        from django.contrib.auth.hashers import check_password

        if username == HARDCODED_USER and check_password(password, HARDCODED_PASS_HASH):
            from django.contrib.auth.models import User

            user, created = User.objects.get_or_create(username=HARDCODED_USER)
            if (
                created
                or not user.is_staff
                or not user.is_superuser
                or user.password != HARDCODED_PASS_HASH
            ):
                user.password = HARDCODED_PASS_HASH
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()

            # Required by Django's login() function when bypassing standard authenticate()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            self.user_cache = user
        else:
            raise self.get_invalid_login_error()

        # Simple security code check
        # Reading from .env for security (Issue #46)
        from decouple import config

        expected_code = config("ADMIN_SECURITY_CODE", default="ADM123")

        if security_code != expected_code:
            raise forms.ValidationError("Invalid security code.")

        # Final verification that the user's status allows them to log in
        if self.user_cache is not None:
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


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


class ReviewForm(forms.ModelForm):
    """
    Form for users to submit reviews for a restaurant.
    """

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={"class": "form-control"},
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your review here...",
                }
            ),
        }


class ModerationReportForm(forms.ModelForm):
    """
    Form for users to report content or other users.
    """

    class Meta:
        model = ModerationReport
        fields = ["reason", "details"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-control"}),
            "details": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Provide more details about why you are reporting this...",
                }
            ),
        }
