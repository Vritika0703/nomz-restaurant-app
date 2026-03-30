from django.db.models import Q
from .models import Message


def unread_messages_count(request):
    """
    Returns the total number of unread messages for the logged-in user.
    Only counts messages where the user is NOT the sender.
    """
    if request.user.is_authenticated:
        count = (
            Message.objects.filter(
                Q(conversation__diner=request.user)
                | Q(conversation__restaurant__owner=request.user),
                is_read=False,
            )
            .exclude(sender=request.user)
            .distinct()
            .count()
        )
        return {"unread_messages_count": count}
    return {"unread_messages_count": 0}
