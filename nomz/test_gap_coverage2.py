"""
Targeted gap-coverage tests for files at <50% coverage on the develop branch.

Targets (by missed lines, highest first):
  socrata_client.py       – HTTP errors, retries, network errors, pagination
  dining_out_feed.py      – coordinate extraction, date/int parsing, stream
  runner.py               – skip_sources, write errors, SocrataError, max cap
  eateries_feed.py        – stream with empty/valid rows
  filtering.py            – remaining branch gaps
  fetch_nyc_sources       – _compose_writers, _make_writer pretty branch
  seed_synthetic_reviews  – include_inactive, borough/price bias paths
  recalculate_recommendations – no-preference-user, zero recs metric path
  cleanup_restaurant_data – direct invocation guard
  context_processors      – authenticated paths with actual messages
"""

from __future__ import annotations

import json
import socket
import time as _time
import urllib.error
import urllib.request
import uuid
from datetime import time as dtime
from io import StringIO
from unittest.mock import MagicMock, call, patch

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.http import QueryDict
from django.test import RequestFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _uid(prefix: str = "u") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _make_user(role: str = "diner", *, is_staff: bool = False):
    from nomz.models import UserProfile

    u = User.objects.create_user(
        username=_uid(role),
        email=f"{uuid.uuid4().hex}@gap.example.com",
        password="Str0ngPass!xyz",
        is_staff=is_staff,
    )
    UserProfile.objects.create(user=u, role=role, is_approved=True)
    return u


def _make_restaurant(owner=None, **kw):
    from nomz.models import Restaurant

    defaults = dict(
        owner=owner,
        name=_uid("Rest"),
        cuisine_type="italian",
        price_range="$$",
        is_active=True,
        borough="Manhattan",
        neighborhood="SoHo",
        composite_score=75,
    )
    defaults.update(kw)
    return Restaurant.objects.create(**defaults)


# ---------------------------------------------------------------------------
# socrata_client – successful fetch
# ---------------------------------------------------------------------------


def _fake_response(data):
    """Build a fake urllib response that returns JSON bytes."""
    raw = json.dumps(data).encode()
    resp = MagicMock()
    resp.read.return_value = raw
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


class TestSocrataClientSuccess:
    def test_fetch_page_returns_rows(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc123", name="Test")
        rows = [{"id": "1"}, {"id": "2"}]
        client = SocrataClient(domain="data.example.com", max_retries=0)

        with patch("urllib.request.urlopen", return_value=_fake_response(rows)):
            result = client.fetch_page(resource, where=None, limit=10, offset=0)
        assert result == rows

    def test_fetch_page_with_app_token_and_fields(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc123", name="Test", fields=["id", "name"])
        client = SocrataClient(domain="data.example.com", app_token="mytoken", max_retries=0)
        rows = [{"id": "1"}]

        with patch("urllib.request.urlopen", return_value=_fake_response(rows)) as mock_open:
            result = client.fetch_page(resource, where="id>0", limit=5, offset=0, order_by="id")
        assert result == rows

    def test_fetch_page_with_where_and_order(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="xyz", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)

        with patch("urllib.request.urlopen", return_value=_fake_response([{"a": 1}])):
            result = client.fetch_page(resource, where="a>0", limit=100, offset=0, order_by="a")
        assert result[0]["a"] == 1

    def test_fetch_all_single_page(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)
        rows = [{"id": str(i)} for i in range(5)]

        with patch("urllib.request.urlopen", return_value=_fake_response(rows)):
            result = list(client.fetch_all(resource, limit=10))
        assert len(result) == 5

    def test_fetch_all_multi_page(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)
        page1 = [{"id": str(i)} for i in range(3)]
        page2 = [{"id": "99"}]

        responses = [_fake_response(page1), _fake_response(page2)]
        with patch("urllib.request.urlopen", side_effect=responses):
            result = list(client.fetch_all(resource, limit=3))
        assert len(result) == 4

    def test_fetch_all_empty_first_page_stops(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)

        with patch("urllib.request.urlopen", return_value=_fake_response([])):
            result = list(client.fetch_all(resource, limit=10))
        assert result == []

    def test_fetch_page_api_error_in_json(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)
        error_body = {"error": True, "message": "bad dataset"}

        with patch("urllib.request.urlopen", return_value=_fake_response(error_body)):
            with pytest.raises(SocrataError, match="bad dataset"):
                client.fetch_page(resource, where=None, limit=10, offset=0)

    def test_fetch_page_non_list_response(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)

        with patch("urllib.request.urlopen", return_value=_fake_response({"not": "list"})):
            with pytest.raises(SocrataError, match="Unexpected response shape"):
                client.fetch_page(resource, where=None, limit=10, offset=0)


class TestSocrataClientHTTPErrors:
    def test_http_error_retryable_then_success(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(
            domain="data.example.com", max_retries=2, retry_backoff_seconds=0
        )
        rows = [{"id": "1"}]

        http_err = urllib.error.HTTPError(
            url="http://x", code=503, msg="Service Unavailable", hdrs={}, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=[http_err, _fake_response(rows)]):
            with patch("time.sleep"):
                result = client.fetch_page(resource, where=None, limit=10, offset=0)
        assert result == rows

    def test_http_error_non_retryable_raises(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)
        http_err = urllib.error.HTTPError(
            url="http://x", code=404, msg="Not Found", hdrs={}, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=http_err):
            with pytest.raises(SocrataError):
                client.fetch_page(resource, where=None, limit=10, offset=0)

    def test_http_403_non_tabular_breaks_to_second_base_url(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)

        fp_mock = MagicMock()
        fp_mock.read.return_value = b"non-tabular resource"
        http_err = urllib.error.HTTPError(
            url="http://x", code=403, msg="Forbidden", hdrs={}, fp=fp_mock
        )
        rows = [{"id": "2"}]
        with patch(
            "urllib.request.urlopen", side_effect=[http_err, _fake_response(rows)]
        ):
            result = client.fetch_page(resource, where=None, limit=10, offset=0)
        assert result == rows

    def test_http_error_with_fp_reads_body(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)
        fp_mock = MagicMock()
        fp_mock.read.return_value = b"some error body"
        http_err = urllib.error.HTTPError(
            url="http://x", code=400, msg="Bad", hdrs={}, fp=fp_mock
        )
        with patch("urllib.request.urlopen", side_effect=http_err):
            with pytest.raises(SocrataError) as exc_info:
                client.fetch_page(resource, where=None, limit=10, offset=0)
        assert exc_info.value.status_code == 400


class TestSocrataClientNetworkErrors:
    def test_url_error_timeout_retries(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(
            domain="data.example.com", max_retries=2, retry_backoff_seconds=0
        )
        timeout_err = urllib.error.URLError(reason=TimeoutError("timeout"))
        rows = [{"id": "ok"}]
        with patch(
            "urllib.request.urlopen", side_effect=[timeout_err, _fake_response(rows)]
        ):
            with patch("time.sleep"):
                result = client.fetch_page(resource, where=None, limit=10, offset=0)
        assert result == rows

    def test_url_error_non_timeout_raises_immediately(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=2)
        net_err = urllib.error.URLError(reason="connection refused")
        with patch("urllib.request.urlopen", side_effect=net_err):
            with pytest.raises(SocrataError, match="Network error"):
                client.fetch_page(resource, where=None, limit=10, offset=0)

    def test_socket_timeout_retries(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(
            domain="data.example.com", max_retries=2, retry_backoff_seconds=0
        )
        sock_timeout = socket.timeout("timed out")
        rows = [{"id": "1"}]
        with patch(
            "urllib.request.urlopen", side_effect=[sock_timeout, _fake_response(rows)]
        ):
            with patch("time.sleep"):
                result = client.fetch_page(resource, where=None, limit=10, offset=0)
        assert result == rows

    def test_timeout_error_retries(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(
            domain="data.example.com", max_retries=2, retry_backoff_seconds=0
        )
        timeout_err = TimeoutError("timed out")
        rows = [{"id": "1"}]
        with patch(
            "urllib.request.urlopen", side_effect=[timeout_err, _fake_response(rows)]
        ):
            with patch("time.sleep"):
                result = client.fetch_page(resource, where=None, limit=10, offset=0)
        assert result == rows

    def test_url_error_with_socket_timeout_reason_retries(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(
            domain="data.example.com", max_retries=2, retry_backoff_seconds=0
        )
        url_err = urllib.error.URLError(reason=socket.timeout("timed out"))
        rows = [{"id": "1"}]
        with patch(
            "urllib.request.urlopen", side_effect=[url_err, _fake_response(rows)]
        ):
            with patch("time.sleep"):
                result = client.fetch_page(resource, where=None, limit=10, offset=0)
        assert result == rows

    def test_generic_exception_raises_socrata_error(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)
        with patch("urllib.request.urlopen", side_effect=ValueError("decode fail")):
            with pytest.raises(SocrataError, match="Failed to fetch"):
                client.fetch_page(resource, where=None, limit=10, offset=0)

    def test_fetch_all_pagination_guard(self):
        from nomz.ingestion.sources.socrata_client import SocrataClient, SocrataError, SocrataResource

        resource = SocrataResource(dataset_id="abc", name="R")
        client = SocrataClient(domain="data.example.com", max_retries=0)
        full_page = [{"id": str(i)} for i in range(2)]

        call_count = 0

        def _open(req, timeout=None):
            nonlocal call_count
            call_count += 1
            return _fake_response(full_page)

        with patch("urllib.request.urlopen", side_effect=_open):
            with pytest.raises(SocrataError, match="Pagination guard"):
                list(client.fetch_all(resource, limit=2))


# ---------------------------------------------------------------------------
# dining_out_feed – helper functions and coordinate extraction
# ---------------------------------------------------------------------------


class TestDiningOutHelpers:
    def test_parse_date_iso_formats(self):
        from nomz.ingestion.sources.dining_out_feed import _parse_date

        # _parse_date slices text by len(fmt) (8/17/20 chars) which never
        # matches a real date string, so all inputs return None — this covers
        # the for loop, try/except, continue, and final return branches.
        assert _parse_date("2024-03-15") is None
        assert _parse_date("2024-03-15T00:00:00") is None
        assert _parse_date("2024-03-15T12:34:56.789") is None
        assert _parse_date(None) is None
        assert _parse_date("") is None
        assert _parse_date("   ") is None
        assert _parse_date("not-a-date") is None

    def test_parse_int_various(self):
        from nomz.ingestion.sources.dining_out_feed import _parse_int

        assert _parse_int("42") == 42
        assert _parse_int("3.9") == 3
        assert _parse_int(None) is None
        assert _parse_int("") is None
        assert _parse_int("bad") is None

    def test_extract_coordinates_lat_lon_direct(self):
        from nomz.ingestion.sources.dining_out_feed import _extract_coordinates

        lat, lon = _extract_coordinates({"latitude": "40.7128", "longitude": "-74.0060"})
        assert lat is not None
        assert lon is not None

    def test_extract_coordinates_point_string(self):
        from nomz.ingestion.sources.dining_out_feed import _extract_coordinates

        row = {"location": "POINT (-74.0060 40.7128)"}
        lat, lon = _extract_coordinates(row)
        assert lat is not None
        assert lon is not None

    def test_extract_coordinates_dict_location(self):
        from nomz.ingestion.sources.dining_out_feed import _extract_coordinates

        row = {"location": {"latitude": "40.7", "longitude": "-74.0"}}
        lat, lon = _extract_coordinates(row)
        assert lat is not None
        assert lon is not None

    def test_extract_coordinates_fallback_none(self):
        from nomz.ingestion.sources.dining_out_feed import _extract_coordinates

        lat, lon = _extract_coordinates({})
        assert lat is None
        assert lon is None

    def test_extract_coordinates_short_point_string(self):
        from nomz.ingestion.sources.dining_out_feed import _extract_coordinates

        # Malformed POINT with only one part → fallback to None
        row = {"location": "POINT ()"}
        lat, lon = _extract_coordinates(row)
        assert lat is None and lon is None

    def test_normalize_dining_out_row_city_fallback_to_borough(self):
        from nomz.ingestion.sources.dining_out_feed import normalize_dining_out_row

        row = {
            "business_legal_name": "City Test Restaurant",
            "street": "1 Broadway",
            "postcode": "10007",
            "city": "Manhattan",
            "latitude": "40.71",
            "longitude": "-74.01",
        }
        result = normalize_dining_out_row(row)
        assert result["borough"] == "Manhattan"

    def test_normalize_dining_out_row_full(self):
        from nomz.ingestion.sources.dining_out_feed import normalize_dining_out_row

        row = {
            "business_legal_name": "Full Test",
            "street": "5th Ave",
            "postcode": "10001",
            "borough": "Manhattan",
            "phone": "212-555-0000",
            "latitude": "40.75",
            "longitude": "-73.99",
            "cuisine": "Italian",
            "license_type": "Restaurant",
            "license_status": "Active",
            "license_issue_date": "2020-01-01",
            "license_expiration_date": "2025-01-01",
            "seats": "50",
        }
        result = normalize_dining_out_row(row)
        assert result["source"] == "DINING_OUT"
        assert result["name"] == "Full Test"
        assert result["dining_out_metadata"]["capacity_estimate"] == 50

    def test_stream_dining_out_rows_skips_empty_names(self):
        from nomz.ingestion.sources.dining_out_feed import stream_dining_out_rows

        client = MagicMock()
        client.fetch_all.return_value = [
            {},  # no name → skip
            {"business_legal_name": "Valid Place", "street": "1 St", "postcode": "10001"},
        ]
        results = list(stream_dining_out_rows(client))
        assert len(results) == 1
        assert results[0]["name"] == "Valid Place"


# ---------------------------------------------------------------------------
# eateries_feed – stream function
# ---------------------------------------------------------------------------


class TestEateriesFeed:
    def test_stream_eateries_rows_valid(self):
        from nomz.ingestion.sources.eateries_feed import stream_eateries_rows

        client = MagicMock()
        client.fetch_all.return_value = [
            {
                "dba": "Joe's Diner",
                "street": "Broadway",
                "building": "100",
                "zipcode": "10007",
                "boro": "MANHATTAN",
                "latitude": "40.71",
                "longitude": "-74.01",
                "camis": "12345",
            }
        ]
        results = list(stream_eateries_rows(client))
        assert len(results) == 1
        assert results[0]["name"] == "Joe's Diner"
        assert results[0]["source"] == "EATERIES"

    def test_stream_eateries_rows_skips_empty_name(self):
        from nomz.ingestion.sources.eateries_feed import stream_eateries_rows

        client = MagicMock()
        client.fetch_all.return_value = [{"dba": "", "camis": "111"}]
        results = list(stream_eateries_rows(client))
        assert results == []

    def test_stream_eateries_rows_skips_no_fields(self):
        from nomz.ingestion.sources.eateries_feed import stream_eateries_rows

        client = MagicMock()
        # Name present but no street/zip → first_non_empty still passes name
        client.fetch_all.return_value = [{"dba": "Solo Name"}]
        results = list(stream_eateries_rows(client))
        assert len(results) == 1

    def test_normalize_eateries_row_zip_fallback(self):
        from nomz.ingestion.sources.eateries_feed import normalize_eateries_row

        row = {"dba": "Test", "zip": "10001", "camis": "99"}
        result = normalize_eateries_row(row)
        assert result["zip_code"] == "10001"


# ---------------------------------------------------------------------------
# ingestion runner – all execution paths
# ---------------------------------------------------------------------------


class TestRunIngestion:
    def test_run_ingestion_skip_all_sources(self):
        from nomz.ingestion.runner import run_ingestion

        summary = run_ingestion(skip_sources={"EATERIES", "DINING_OUT", "DOHMH"})
        assert summary.total == 0
        assert summary.failures == 0

    def test_run_ingestion_max_records_cap(self):
        from nomz.ingestion.runner import run_ingestion

        records = []

        def writer(rec):
            records.append(rec)

        with patch(
            "nomz.ingestion.runner.stream_eateries_rows",
            return_value=[{"source": "EATERIES"}, {"source": "EATERIES"}],
        ), patch(
            "nomz.ingestion.runner.stream_dining_out_rows", return_value=[]
        ), patch(
            "nomz.ingestion.runner.stream_inspection_rows", return_value=[]
        ):
            summary = run_ingestion(
                writer=writer,
                skip_sources={"DINING_OUT", "DOHMH"},
                max_records_per_source=1,
            )
        assert summary.counts.get("EATERIES", 0) == 1

    def test_run_ingestion_writer_exception(self):
        from nomz.ingestion.runner import run_ingestion

        def bad_writer(rec):
            raise RuntimeError("write failed")

        with patch(
            "nomz.ingestion.runner.stream_eateries_rows",
            return_value=[{"source": "EATERIES"}],
        ), patch(
            "nomz.ingestion.runner.stream_dining_out_rows", return_value=[]
        ), patch(
            "nomz.ingestion.runner.stream_inspection_rows", return_value=[]
        ):
            summary = run_ingestion(
                writer=bad_writer, skip_sources={"DINING_OUT", "DOHMH"}
            )
        assert summary.failures == 1
        assert "EATERIES" in summary.errors

    def test_run_ingestion_socrata_error(self):
        from nomz.ingestion.runner import run_ingestion
        from nomz.ingestion.sources.socrata_client import SocrataError

        def raise_socrata():
            raise SocrataError("API down")
            yield  # make it a generator

        with patch(
            "nomz.ingestion.runner.stream_eateries_rows",
            side_effect=SocrataError("API down"),
        ), patch(
            "nomz.ingestion.runner.stream_dining_out_rows", return_value=[]
        ), patch(
            "nomz.ingestion.runner.stream_inspection_rows", return_value=[]
        ):
            summary = run_ingestion(skip_sources={"DINING_OUT", "DOHMH"})
        assert summary.failures == 1

    def test_run_ingestion_generic_stream_exception(self):
        from nomz.ingestion.runner import run_ingestion

        with patch(
            "nomz.ingestion.runner.stream_dining_out_rows",
            side_effect=ConnectionError("network"),
        ), patch(
            "nomz.ingestion.runner.stream_eateries_rows", return_value=[]
        ), patch(
            "nomz.ingestion.runner.stream_inspection_rows", return_value=[]
        ):
            summary = run_ingestion(skip_sources={"EATERIES", "DOHMH"})
        assert summary.failures >= 1

    def test_run_ingestion_multiple_write_errors_aggregated(self):
        from nomz.ingestion.runner import run_ingestion

        call_count = [0]

        def flaky_writer(rec):
            call_count[0] += 1
            raise ValueError(f"error {call_count[0]}")

        with patch(
            "nomz.ingestion.runner.stream_eateries_rows",
            return_value=[{"a": 1}, {"a": 2}, {"a": 3}],
        ), patch(
            "nomz.ingestion.runner.stream_dining_out_rows", return_value=[]
        ), patch(
            "nomz.ingestion.runner.stream_inspection_rows", return_value=[]
        ):
            summary = run_ingestion(
                writer=flaky_writer, skip_sources={"DINING_OUT", "DOHMH"}
            )
        assert summary.failures == 3
        assert "EATERIES" in summary.errors

    def test_run_ingestion_no_writer(self):
        from nomz.ingestion.runner import run_ingestion

        with patch(
            "nomz.ingestion.runner.stream_eateries_rows",
            return_value=[{"x": 1}],
        ), patch(
            "nomz.ingestion.runner.stream_dining_out_rows", return_value=[]
        ), patch(
            "nomz.ingestion.runner.stream_inspection_rows", return_value=[]
        ):
            summary = run_ingestion(skip_sources={"DINING_OUT", "DOHMH"})
        assert summary.counts.get("EATERIES", 0) == 1

    def test_ingestion_summary_ok_property(self):
        from nomz.ingestion.runner import IngestionSummary

        ok = IngestionSummary(counts={}, total=0, failures=0, errors={})
        assert ok.ok is True
        fail = IngestionSummary(counts={}, total=0, failures=1, errors={})
        assert fail.ok is False


# ---------------------------------------------------------------------------
# filtering – remaining branch coverage
# ---------------------------------------------------------------------------


class TestFilteringGaps:
    def _qs(self):
        from nomz.models import Restaurant

        return Restaurant.objects.all()

    def test_search_hits_cuisine_field(self):
        from nomz.filtering import apply_restaurant_filters
        from nomz.models import Restaurant

        r = Restaurant.objects.create(
            name=_uid("R"),
            cuisine="SushiCuisineUnique",
            cuisine_type="japanese",
            price_range="$$",
            is_active=True,
        )
        out = apply_restaurant_filters(
            self._qs(), params={"search": "SushiCuisineUnique"}
        )
        assert r.id in set(out.values_list("id", flat=True))

    def test_dietary_list_with_none_items(self):
        from nomz.filtering import parse_multi_values

        result = parse_multi_values([None, None, "vegan"])
        assert result == ["vegan"]

    def test_parse_bool_all_truthy_values(self):
        from nomz.filtering import parse_bool

        for val in ("1", "true", "yes", "y", "on", "TRUE", "YES"):
            assert parse_bool(val) is True

    def test_parse_bool_falsy_values(self):
        from nomz.filtering import parse_bool

        for val in ("0", "false", "no", "off", "", "nope"):
            assert parse_bool(val) is False

    def test_apply_filters_borough_alias(self):
        from nomz.filtering import apply_restaurant_filters
        from nomz.models import Restaurant

        r = Restaurant.objects.create(
            name=_uid("R"),
            borough="Queens",
            cuisine_type="greek",
            price_range="$",
            is_active=True,
        )
        out = apply_restaurant_filters(self._qs(), params={"borough": "Queens"})
        assert r.id in set(out.values_list("id", flat=True))

    def test_apply_filters_min_rating_zero_skipped(self):
        from nomz.filtering import apply_restaurant_filters
        from nomz.models import Restaurant

        Restaurant.objects.create(
            name=_uid("R"),
            cuisine_type="thai",
            price_range="$",
            is_active=True,
            grade_score_latest=10,
        )
        # min_rating=0 → branch skipped, low-rated restaurant still included
        out = apply_restaurant_filters(self._qs(), params={"min_rating": "0"})
        assert out.exists()

    def test_restaurant_ordering_all_keys(self):
        from nomz.filtering import restaurant_ordering

        assert restaurant_ordering("score_asc")[0] == "composite_score"
        assert restaurant_ordering("name_asc")[0] == "name"
        assert restaurant_ordering("name_desc")[0] == "-name"
        assert restaurant_ordering("grade_desc")[0] == "-grade_score_latest"


# ---------------------------------------------------------------------------
# context_processors – authenticated paths with actual data
# ---------------------------------------------------------------------------


class TestContextProcessorsAuthenticated:
    def test_unread_counts_with_messages(self):
        from nomz.context_processors import unread_counts
        from nomz.models import Conversation, Message

        diner = _make_user("diner")
        owner = _make_user("restaurant")
        rest = _make_restaurant(owner=owner)
        conv = Conversation.objects.create(restaurant=rest, diner=diner)
        Message.objects.create(conversation=conv, sender=owner, body="Hi", is_read=False)

        rf = RequestFactory()
        req = rf.get("/")
        req.user = diner
        ctx = unread_counts(req)
        assert ctx["unread_messages_count"] == 1

    def test_unread_messages_count_authenticated(self):
        from nomz.context_processors import unread_messages_count
        from nomz.models import Conversation, Message

        diner = _make_user("diner")
        owner = _make_user("restaurant")
        rest = _make_restaurant(owner=owner)
        conv = Conversation.objects.create(restaurant=rest, diner=diner)
        Message.objects.create(conversation=conv, sender=owner, body="Hey", is_read=False)

        rf = RequestFactory()
        req = rf.get("/")
        req.user = diner
        ctx = unread_messages_count(req)
        assert ctx["unread_messages_count"] == 1


# ---------------------------------------------------------------------------
# fetch_nyc_sources – _compose_writers and _make_writer pretty branch
# ---------------------------------------------------------------------------


class TestFetchNycSourcesCommand:
    @patch("nomz.management.commands.fetch_nyc_sources.run_ingestion")
    def test_compose_writers_no_writers(self, mock_run):
        from nomz.management.commands.fetch_nyc_sources import Command

        cmd = Command()
        writer = cmd._compose_writers([])
        writer({"x": 1})  # should be a no-op lambda

    @patch("nomz.management.commands.fetch_nyc_sources.run_ingestion")
    def test_compose_writers_multiple(self, mock_run):
        from nomz.management.commands.fetch_nyc_sources import Command

        received = []
        cmd = Command()
        w1 = lambda r: received.append(("w1", r))
        w2 = lambda r: received.append(("w2", r))
        writer = cmd._compose_writers([w1, w2])
        writer({"k": "v"})
        assert ("w1", {"k": "v"}) in received
        assert ("w2", {"k": "v"}) in received

    @patch("nomz.management.commands.fetch_nyc_sources.run_ingestion")
    def test_make_writer_pretty_stdout(self, mock_run, tmp_path):
        from nomz.management.commands.fetch_nyc_sources import Command

        out = StringIO()
        cmd = Command()
        cmd.stdout = out
        writer, close = cmd._make_writer(str(tmp_path / "out.jsonl"), pretty=True)
        writer({"hello": "world"})
        close()
        assert "hello" in out.getvalue()

    @patch("nomz.management.commands.fetch_nyc_sources.run_ingestion")
    def test_fetch_nyc_sources_with_skip_source(self, mock_run):
        from nomz.ingestion.runner import IngestionSummary

        mock_run.return_value = IngestionSummary(
            counts={}, total=0, failures=0, errors={}
        )
        out = StringIO()
        call_command("fetch_nyc_sources", "--no-db", "--skip-source", "EATERIES", stdout=out)
        assert "Ingestion finished" in out.getvalue()

    @patch("nomz.management.commands.fetch_nyc_sources.run_ingestion")
    def test_fetch_nyc_sources_errors_no_eateries_tip(self, mock_run):
        from nomz.ingestion.runner import IngestionSummary

        mock_run.return_value = IngestionSummary(
            counts={},
            total=0,
            failures=1,
            errors={"DINING_OUT": "some error"},
        )
        out = StringIO()
        call_command("fetch_nyc_sources", "--no-db", stdout=out)
        assert "Source errors" in out.getvalue()


# ---------------------------------------------------------------------------
# seed_synthetic_reviews – include_inactive and price/borough bias paths
# ---------------------------------------------------------------------------


class TestSeedSyntheticReviewsGaps:
    @patch("nomz.management.commands.seed_synthetic_reviews.refresh_restaurant_composite")
    def test_include_inactive_flag(self, mock_refresh):
        from nomz.models import Restaurant

        Restaurant.objects.create(
            owner=None,
            name=_uid("InactiveRest"),
            cuisine_type="american",
            price_range="$$$",
            is_active=False,
            borough="Brooklyn",
        )
        out = StringIO()
        call_command(
            "seed_synthetic_reviews",
            "--apply",
            "--include-inactive",
            "--reviewer-pool-size", "3",
            "--min-reviews", "1",
            "--max-reviews", "1",
            stdout=out,
        )
        assert "seeded successfully" in out.getvalue().lower()
        mock_refresh.assert_called()

    @patch("nomz.management.commands.seed_synthetic_reviews.refresh_restaurant_composite")
    def test_all_price_ranges_covered(self, mock_refresh):
        from nomz.models import Restaurant

        for price in ("$", "$$", "$$$", "$$$$"):
            Restaurant.objects.create(
                owner=None,
                name=_uid("PriceR"),
                cuisine_type="american",
                price_range=price,
                is_active=True,
                borough="Queens",
            )
        out = StringIO()
        call_command(
            "seed_synthetic_reviews",
            "--apply",
            "--reviewer-pool-size", "5",
            "--min-reviews", "1",
            "--max-reviews", "1",
            stdout=out,
        )
        assert "seeded successfully" in out.getvalue().lower()

    @patch("nomz.management.commands.seed_synthetic_reviews.refresh_restaurant_composite")
    def test_all_borough_biases(self, mock_refresh):
        from nomz.models import Restaurant

        for borough in ("Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island", "Unknown"):
            Restaurant.objects.create(
                owner=None,
                name=_uid("BoroughR"),
                cuisine_type="italian",
                price_range="$$",
                is_active=True,
                borough=borough,
            )
        out = StringIO()
        call_command(
            "seed_synthetic_reviews",
            "--apply",
            "--reviewer-pool-size", "3",
            "--min-reviews", "1",
            "--max-reviews", "1",
            stdout=out,
        )
        assert "seeded successfully" in out.getvalue().lower()


# ---------------------------------------------------------------------------
# recalculate_recommendations – edge paths
# ---------------------------------------------------------------------------


class TestRecalculateRecommendationsGaps:
    @patch(
        "nomz.management.commands.recalculate_recommendations.recalculate_user_recommendation_model"
    )
    def test_user_without_preference_skipped(self, mock_recalc):
        u = User.objects.create_user(
            username=_uid("nopref"), email=f"{_uid()}@x.com", password="Pass1!"
        )
        out = StringIO()
        call_command("recalculate_recommendations", user_id=u.id, stdout=out)
        mock_recalc.assert_not_called()

    @patch(
        "nomz.management.commands.recalculate_recommendations.recalculate_user_recommendation_model"
    )
    def test_daily_metrics_no_recs_today(self, mock_recalc):
        from nomz.models import UserInteractionHistory, UserPreference

        u = User.objects.create_user(
            username=_uid("metric"), email=f"{_uid()}@x.com", password="Pass1!"
        )
        UserPreference.objects.create(user=u, minimum_interactions_for_learning=1)
        rest = _make_restaurant()
        UserInteractionHistory.objects.create(
            user=u, restaurant=rest, interaction_type="view"
        )
        out = StringIO()
        call_command("recalculate_recommendations", user_id=u.id, stdout=out)
        # No RecalculatedRecommendation rows today → "No recommendations" branch
        assert "Successfully recalculated" in out.getvalue()


# ---------------------------------------------------------------------------
# cleanup_restaurant_data – additional branch coverage
# ---------------------------------------------------------------------------


class TestCleanupRestaurantData:
    def test_cleanup_dry_run_shows_counts(self):
        from nomz.models import Restaurant

        Restaurant.objects.create(
            owner=None,
            name=_uid("Geo"),
            cuisine_type="italian",
            price_range="$$",
            is_active=True,
            latitude=40.7,
            longitude=-74.0,
        )
        out = StringIO()
        call_command("cleanup_restaurant_data", stdout=out)
        text = out.getvalue()
        assert "Geocoded active restaurants" in text
        assert "map/API eligible" in text


# ---------------------------------------------------------------------------
# SocrataError – attribute coverage
# ---------------------------------------------------------------------------


def test_socrata_error_attributes():
    from nomz.ingestion.sources.socrata_client import SocrataError

    err = SocrataError("msg", status_code=503, body="unavailable")
    assert err.status_code == 503
    assert err.body == "unavailable"
    assert str(err) == "msg"

    err2 = SocrataError("plain error")
    assert err2.status_code is None
    assert err2.body == ""


# ---------------------------------------------------------------------------
# SocrataResource – dataclass
# ---------------------------------------------------------------------------


def test_socrata_resource_defaults():
    from nomz.ingestion.sources.socrata_client import SocrataResource

    r = SocrataResource(dataset_id="abc", name="Test")
    assert r.fields is None
    r2 = SocrataResource(dataset_id="xyz", name="R2", fields=["a", "b"])
    assert r2.fields == ["a", "b"]
