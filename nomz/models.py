from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    # The available roles
    ROLE_CHOICES = [
        ('diner', 'Diner'),
        ('restaurant', 'Restaurant'),
    ]

    # Links this profile to the built-in Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='diner')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True)
    name_normalized = models.CharField(max_length=255, db_index=True)
    building = models.CharField(max_length=64, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    borough = models.CharField(max_length=80, blank=True, null=True)
    zip_code = models.CharField(max_length=10, db_index=True, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, null=True)
    cuisine_tags = models.JSONField(default=list, blank=True)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )

    composite_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade_latest = models.CharField(max_length=16, blank=True, null=True)
    grade_score_latest = models.IntegerField(blank=True, null=True)
    last_inspection_date = models.DateField(blank=True, null=True)
    composite_score_calculated_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name_normalized", "zip_code"]),
            models.Index(fields=["borough", "zip_code"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["latitude", "longitude"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.zip_code})"


class RestaurantSourceRecord(models.Model):
    SOURCE_EATERIES = "EATERIES"
    SOURCE_DINING_OUT = "DINING_OUT"
    SOURCE_DOHMH = "DOHMH"

    SOURCE_CHOICES = [
        (SOURCE_EATERIES, "Directory of Eateries"),
        (SOURCE_DINING_OUT, "Dining Out NYC Locations"),
        (SOURCE_DOHMH, "DOHMH Inspection Results"),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="sources",
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    external_id = models.CharField(max_length=200)
    external_name = models.CharField(max_length=255)
    external_address = models.CharField(max_length=255, blank=True, null=True)
    raw_payload = models.JSONField(blank=True, null=True)
    confidence = models.DecimalField(max_digits=4, decimal_places=3, default=0.0)
    source_url = models.URLField(max_length=500, blank=True, null=True)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["source", "external_id"]]
        indexes = [
            models.Index(fields=["source", "external_id"]),
            models.Index(fields=["restaurant", "source"]),
        ]

    def __str__(self):
        return f"{self.source} {self.external_id}"


class InspectionRecord(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="inspections",
    )
    inspection_date = models.DateField()
    inspection_key = models.CharField(max_length=200)
    grade = models.CharField(max_length=12, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    critical_violations = models.IntegerField(default=0)
    noncritical_violations = models.IntegerField(default=0)
    violation_count = models.IntegerField(default=0)
    inspection_type = models.CharField(max_length=128, blank=True, null=True)
    action = models.CharField(max_length=255, blank=True, null=True)
    violations = models.JSONField(default=list, blank=True)
    camis = models.CharField(max_length=80, blank=True, null=True)
    boro = models.CharField(max_length=80, blank=True, null=True)
    raw_payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["restaurant", "inspection_key"]]
        indexes = [
            models.Index(fields=["restaurant", "inspection_date"]),
            models.Index(fields=["grade"]),
        ]
        ordering = ["-inspection_date"]

    def __str__(self):
        return f"{self.restaurant_id}:{self.inspection_key}"


class DataIngestionRun(models.Model):
    STATUS_CHOICES = [
        ("running", "Running"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    dataset = models.CharField(max_length=64)
    status = models.CharField(max_length=20, default="running", choices=STATUS_CHOICES)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    records_fetched = models.IntegerField(default=0)
    records_processed = models.IntegerField(default=0)
    records_created = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    records_matched = models.IntegerField(default=0)
    records_skipped = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    error_log = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.dataset} | {self.status} | {self.started_at:%Y-%m-%d %H:%M}"
