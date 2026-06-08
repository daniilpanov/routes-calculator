from unittest.mock import AsyncMock, patch

import pytest
from backend_user.services.route_calculation import _strip_demo_fields


class TestStripDemoFields:
    def test_removes_company_from_segments(self):
        routes = [
            (
                [{"company": "CompanyA", "id": 1}, {"company": "CompanyB", "id": 2}],
                None,
                False,
                [],
            )
        ]
        _strip_demo_fields(routes)
        assert "company" not in routes[0][0][0]
        assert "company" not in routes[0][0][1]

    def test_preserves_other_fields(self):
        routes = [
            (
                [{"company": "CompanyA", "id": 1, "type": "RAIL", "prices": []}],
                None,
                False,
                [],
            )
        ]
        _strip_demo_fields(routes)
        assert "company" not in routes[0][0][0]
        assert routes[0][0][0]["id"] == 1
        assert routes[0][0][0]["type"] == "RAIL"

    def test_multiple_routes(self):
        routes = [
            ([{"company": "Co1", "id": 1}], None, False, []),
            ([{"company": "Co2", "id": 2}], None, False, []),
        ]
        _strip_demo_fields(routes)
        assert "company" not in routes[0][0][0]
        assert "company" not in routes[1][0][0]


@pytest.mark.asyncio
async def test_get_auth_context_with_demo_header(sqlite_db):
    from backend_user.dependencies.auth_context import get_auth_context

    demo_guest = AsyncMock()
    demo_guest.sea_profit = 50.0
    demo_guest.sea_profit_currency = "USD"
    demo_guest.rail_profit = 30.0
    demo_guest.rail_profit_currency = "USD"

    with (
        patch("backend_user.dependencies.auth_context.get_demo_guest_by_uid", return_value=demo_guest),
        patch("backend_user.dependencies.auth_context.get_database", return_value=sqlite_db),
    ):
        mock_request = AsyncMock()
        mock_request.headers.get = lambda key, default=None: "demo-uid-123" if key == "X-Demo-User-UID" else default

        mock_auth = AsyncMock()
        settings = AsyncMock()
        settings.DISABLE_USER_AUTH_CHECK = True

        result = await get_auth_context(
            request=mock_request,
            authorization=mock_auth,
            db=sqlite_db,
            settings=settings,
        )

    assert result.is_demo is True
    assert result.demo_uid == "demo-uid-123"
    assert result.sea_profit == 50.0
    assert result.rail_profit == 30.0


@pytest.mark.asyncio
async def test_get_auth_context_without_demo_header(sqlite_db):
    from backend_user.dependencies.auth_context import get_auth_context

    with (
        patch("backend_user.dependencies.auth_context.request_auth", return_value=None),
    ):
        mock_request = AsyncMock()
        mock_request.headers.get = lambda key, default=None: None

        mock_auth = AsyncMock()
        settings = AsyncMock()
        settings.DISABLE_USER_AUTH_CHECK = True

        result = await get_auth_context(
            request=mock_request,
            authorization=mock_auth,
            db=sqlite_db,
            settings=settings,
        )

    assert result.is_demo is False
    assert result.demo_uid is None
    assert result.sea_profit == 0.0
    assert result.rail_profit == 0.0


@pytest.mark.asyncio
async def test_get_auth_context_invalid_demo_uid(sqlite_db):
    from backend_user.dependencies.auth_context import get_auth_context

    with (
        patch("backend_user.dependencies.auth_context.get_demo_guest_by_uid", return_value=None),
        patch("backend_user.dependencies.auth_context.get_database", return_value=sqlite_db),
    ):
        mock_request = AsyncMock()
        mock_request.headers.get = lambda key, default=None: "invalid-uid" if key == "X-Demo-User-UID" else default

        mock_auth = AsyncMock()
        settings = AsyncMock()
        settings.DISABLE_USER_AUTH_CHECK = True

        result = await get_auth_context(
            request=mock_request,
            authorization=mock_auth,
            db=sqlite_db,
            settings=settings,
        )

    assert result.is_demo is False
    assert result.demo_uid is None


@pytest.mark.asyncio
async def test_strip_demo_fields_no_routes():
    from backend_user.services.route_calculation import _strip_demo_fields

    routes = []
    _strip_demo_fields(routes)
    assert routes == []


@pytest.mark.asyncio
async def test_strip_demo_fields_empty_segments_list():
    from backend_user.services.route_calculation import _strip_demo_fields

    routes = [([], None, False, [])]
    _strip_demo_fields(routes)
    assert routes[0][0] == []
