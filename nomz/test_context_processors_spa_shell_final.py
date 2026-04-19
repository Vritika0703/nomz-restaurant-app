"""
Tests for nomz.context_processors.unread_counts and nomz.spa_shell_views.spa_index (?next=).
"""

import uuid

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory
from django.urls import reverse

from nomz.context_processors import unread_counts
from nomz.models import (
    Conversation,
    FriendConversation,
    FriendMessage,
    Message,
    Restaurant,
)


def _req(user):
    request = RequestFactory().get("/")
    request.user = user
    return request


def test_unread_counts_anonymous_user():
    ctx = unread_counts(_req(AnonymousUser()))
    assert ctx == {
        "unread_messages_count": 0,
        "unread_friends_count": 0,
    }


@pytest.mark.django_db
def test_unread_counts_authenticated_counts_restaurant_and_friend_unread():
    suffix = uuid.uuid4().hex[:8]
    owner = User.objects.create_user(username=f"o_{suffix}", password="x")
    diner = User.objects.create_user(username=f"d_{suffix}", password="x")
    pal = User.objects.create_user(username=f"p_{suffix}", password="x")

    restaurant = Restaurant.objects.create(
        name=f"RUnread_{suffix}",
        owner=owner,
    )
    conv = Conversation.objects.create(restaurant=restaurant, diner=diner)
    Message.objects.create(
        conversation=conv,
        sender=owner,
        body="Hello from owner",
        is_read=False,
    )
    Message.objects.create(
        conversation=conv,
        sender=diner,
        body="Reply from diner",
        is_read=False,
    )

    fchat = FriendConversation.objects.create(is_group=False)
    fchat.participants.add(diner, pal)
    FriendMessage.objects.create(
        conversation=fchat,
        sender=pal,
        body="yo",
        is_read=False,
    )
    FriendMessage.objects.create(
        conversation=fchat,
        sender=diner,
        body="me",
        is_read=False,
    )

    ctx_diner = unread_counts(_req(diner))
    assert ctx_diner["unread_messages_count"] == 1
    assert ctx_diner["unread_friends_count"] == 1

    ctx_owner = unread_counts(_req(owner))
    assert ctx_owner["unread_messages_count"] == 1
    assert ctx_owner["unread_friends_count"] == 0


def test_spa_index_without_next_returns_shell_get():
    client = Client()
    resp = client.get(reverse("landing"))
    assert resp.status_code == 200
    assert "text/html" in resp["Content-Type"]


def test_spa_index_empty_next_returns_shell_get():
    client = Client()
    resp = client.get(reverse("landing"), {"next": ""})
    assert resp.status_code == 200


def test_spa_index_whitespace_next_returns_shell_get():
    client = Client()
    resp = client.get(reverse("landing"), {"next": "   \t  "})
    assert resp.status_code == 200


def test_spa_index_safe_relative_next_redirects():
    client = Client()
    resp = client.get(reverse("landing"), {"next": "/search/"})
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/search/"


def test_spa_index_safe_absolute_same_host_redirects():
    client = Client()
    resp = client.get(reverse("landing"), {"next": "http://testserver/profile/"})
    assert resp.status_code == 302
    assert resp.headers["Location"] == "http://testserver/profile/"


def test_spa_index_external_next_rejected_no_redirect():
    client = Client()
    resp = client.get(
        reverse("landing"), {"next": "https://evil.example.com/steal-cookies"}
    )
    assert resp.status_code == 200
    assert resp.headers.get("Location") is None


def test_spa_index_protocol_relative_next_rejected():
    client = Client()
    resp = client.get(reverse("landing"), {"next": "//evil.example.com/x"})
    assert resp.status_code == 200


def test_spa_index_javascript_next_rejected():
    client = Client()
    resp = client.get(reverse("landing"), {"next": "javascript:alert(1)"})
    assert resp.status_code == 200
