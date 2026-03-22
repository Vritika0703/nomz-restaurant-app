from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Restaurant, RestaurantOwnershipClaim

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'neighborhood', 'cuisine')
    search_fields = ('name', 'neighborhood')


@admin.register(RestaurantOwnershipClaim)
class RestaurantOwnershipClaimAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'restaurant',
        'claimant',
        'status',
        'created_at',
        'reviewed_at',
    )
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = (
        'restaurant__name',
        'restaurant__address',
        'claimant__username',
        'claimant__email',
        'business_email',
    )
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')
    actions = ('approve_selected_claims', 'reject_selected_claims')

    @admin.action(description='Approve selected pending claims')
    def approve_selected_claims(self, request, queryset):
        approved_count = 0
        for claim in queryset.select_related('restaurant', 'claimant'):
            if claim.status != RestaurantOwnershipClaim.STATUS_PENDING:
                continue
            try:
                claim.approve(reviewer=request.user)
                approved_count += 1
            except ValidationError as exc:
                self.message_user(
                    request,
                    f'Could not approve claim #{claim.id}: {exc}',
                    level=messages.ERROR,
                )
        self.message_user(request, f'Approved {approved_count} claim(s).')

    @admin.action(description='Reject selected pending claims')
    def reject_selected_claims(self, request, queryset):
        rejected_count = 0
        for claim in queryset:
            if claim.status != RestaurantOwnershipClaim.STATUS_PENDING:
                continue
            claim.reject(reviewer=request.user, notes='Rejected via admin bulk action.')
            rejected_count += 1
        self.message_user(request, f'Rejected {rejected_count} claim(s).')
