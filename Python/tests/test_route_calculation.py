import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from backend_user.dependencies.auth_context import AuthContext
from backend_user.schemas.form_requests import CalculateFormRequest
from backend_user.services.route_calculation import calculate_routes
from module_shared.models.route import ContainerItem, PriceItem, RouteResult, RouteSegment


def _make_segment(company: str = "CompanyA", **overrides) -> RouteSegment:
    kwargs = dict(  # noqa: C408
        id=1,
        company=company,
        type="RAIL",
        effectiveFrom="2024-01-01",
        effectiveTo="2025-12-31",
        startPointCountry="Россия",
        startPointName="Москва",
        endPointCountry="Россия",
        endPointName="Владивосток",
        comment=None,
        timetable=None,
        container_transfer_terms="FIFO",
        container_shipment_terms="FOB",
        container_owner="COC",
        prices=[
            PriceItem(
                container=ContainerItem(
                    id=1, size=20, type="DC", weight_from=0, weight_to=28000, name="20DC"
                ),
                value=1000.0,
                currency="USD",
                conversation_percents=0,
            )
        ],
    )
    kwargs.update(overrides)
    return RouteSegment(**kwargs)


def _make_full_route(company: str = "CompanyA", segments_count: int = 1, **segment_overrides) -> RouteResult:
    segment = _make_segment(company=company, **segment_overrides)
    segments = [segment]
    if segments_count > 1:
        segments.append(_make_segment(company=company, id=2, type="SEA"))
    return RouteResult(segments=segments)


def _make_request(
    dispatch_date: datetime.date | None = None,
    dep_internal: list[int] | None = None,
    dest_internal: list[int] | None = None,
    dep_external: list[str] | None = None,
    dest_external: list[str] | None = None,
    weight: float = 20000,
    container_type: int = 20,
) -> CalculateFormRequest:
    return CalculateFormRequest(
        dispatchDate=dispatch_date or datetime.date(2024, 6, 15),
        departureInternalIds=dep_internal or [1],
        destinationInternalIds=dest_internal or [2],
        departureExternalIds=dep_external or [],
        destinationExternalIds=dest_external or [],
        cargoWeight=weight,
        containerType=container_type,
    )


@pytest.mark.asyncio
async def test_rail_only_internal():
    route = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert len(result["errors"]) == 0
    route_data = result["routes"][0]
    segments = route_data[0]
    assert len(segments) == 1
    assert segments[0].company == "CompanyA"
    assert segments[0].type == "RAIL"


@pytest.mark.asyncio
async def test_sea_only_internal():
    route = _make_full_route(company="SeaLine", type="SEA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    segments = result["routes"][0][0]
    assert segments[0].type == "SEA"


@pytest.mark.asyncio
async def test_no_routes_found():
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 0


@pytest.mark.asyncio
async def test_no_matching_containers():
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[])
        mock_agg.search_container_ids = lambda containers, weight, size: []
        mock_agg.find_all_paths = AsyncMock(return_value=[])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 0


@pytest.mark.asyncio
async def test_multiple_internal_pairs():
    route_a = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route_a])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request(dep_internal=[1, 3], dest_internal=[2, 4])
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) >= 1


@pytest.mark.asyncio
async def test_fesco_external_source():
    route = _make_full_route(company="FESCO")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[])
        mock_agg.search_container_ids = lambda containers, weight, size: []
        mock_agg.find_all_paths = AsyncMock(return_value=[])
        fesco_container = {"id": "f1", "size": 20, "weight_from": 0, "weight_to": 28000}
        mock_fesco.get_containers = AsyncMock(return_value=[fesco_container])
        mock_fesco.search_container_ids = lambda containers, weight, size: ["f1"]
        mock_fesco.find_all_paths = AsyncMock(return_value=[route])

        request = _make_request(dep_external=["EXT1"], dest_external=["EXT2"])
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert result["routes"][0][0][0].company == "FESCO"


@pytest.mark.asyncio
async def test_mixed_internal_and_external():
    route_int = _make_full_route(company="CompanyA")
    route_ext = _make_full_route(company="FESCO")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route_int])
        fesco_container = {"id": "f1", "size": 20, "weight_from": 0, "weight_to": 28000}
        mock_fesco.get_containers = AsyncMock(return_value=[fesco_container])
        mock_fesco.search_container_ids = lambda containers, weight, size: ["f1"]
        mock_fesco.find_all_paths = AsyncMock(return_value=[route_ext])

        request = _make_request(dep_internal=[1], dest_internal=[2], dep_external=["EXT1"], dest_external=["EXT2"])
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 2
    companies = {seg.company for route_res in result["routes"] for seg in route_res[0]}
    assert "CompanyA" in companies
    assert "FESCO" in companies


@pytest.mark.asyncio
async def test_fesco_api_error_does_not_break_all():
    route_int = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route_int])
        mock_fesco.get_containers = AsyncMock(side_effect=Exception("FESCO timeout"))
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(side_effect=Exception("FESCO timeout"))

        request = _make_request(dep_internal=[1], dest_internal=[2], dep_external=["EXT1"], dest_external=["EXT2"])
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert result["routes"][0][0][0].company == "CompanyA"
    assert len(result["errors"]) == 1


@pytest.mark.asyncio
async def test_demo_auth_strips_company_field():
    route = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext(is_demo=True)
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert result["routes"][0][0][0].company is None


@pytest.mark.asyncio
async def test_demo_auth_with_profit():
    route = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
        patch("backend_user.services.profit.get_rates", return_value={"RUB": 1, "USD": 90, "EUR": 100}),
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext(is_demo=True, sea_profit=100.0, sea_profit_currency="USD")
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert result["routes"][0][0][0].company is None


@pytest.mark.asyncio
async def test_single_segment_rail_route_preserves_structure():
    route = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    route_data = result["routes"][0]
    segments, drop, may_be_invalid, services = route_data
    assert isinstance(segments, list)
    assert len(segments) == 1
    segment = segments[0]
    assert isinstance(segment.id, int)
    assert segment.company == "CompanyA"
    assert segment.type == "RAIL"
    assert isinstance(segment.prices, list)
    assert segment.prices[0].value == 1000.0
    assert segment.prices[0].currency == "USD"


@pytest.mark.asyncio
async def test_external_only_without_internal():
    route = _make_full_route(company="FESCO")
    fesco_container = {"id": "f1", "size": 20, "weight_from": 0, "weight_to": 28000}
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[])
        mock_agg.search_container_ids = lambda containers, weight, size: []
        mock_agg.find_all_paths = AsyncMock(return_value=[])
        mock_fesco.get_containers = AsyncMock(return_value=[fesco_container])
        mock_fesco.search_container_ids = lambda containers, weight, size: ["f1"]
        mock_fesco.find_all_paths = AsyncMock(return_value=[route])

        request = _make_request(dep_internal=[], dest_internal=[], dep_external=["EXT1"], dest_external=["EXT2"])
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert result["errors"] == []


@pytest.mark.asyncio
async def test_empty_ids_lists_returns_empty():
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[])
        mock_agg.search_container_ids = lambda containers, weight, size: []
        mock_agg.find_all_paths = AsyncMock(return_value=[])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request(dep_internal=[], dest_internal=[], dep_external=[], dest_external=[])
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert result == {"errors": [], "routes": []}


@pytest.mark.asyncio
async def test_container_fetch_fails_gracefully():
    route = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(side_effect=Exception("DB timeout"))
        mock_agg.search_container_ids = Mock()
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext()
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 0
    assert len(result["errors"]) == 1


@pytest.mark.asyncio
async def test_demo_auth_with_profit_and_rail():
    route = _make_full_route(company="CompanyA", type="RAIL")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
        patch("backend_user.services.profit.get_rates", return_value={"RUB": 1, "USD": 90, "EUR": 100}),
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext(is_demo=True, rail_profit=50.0, rail_profit_currency="USD")
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert result["routes"][0][0][0].company is None


@pytest.mark.asyncio
async def test_non_demo_does_not_strip_company():
    route = _make_full_route(company="CompanyA")
    with (
        patch("backend_user.services.route_calculation.aggregators") as mock_agg,
        patch("backend_user.services.route_calculation.api_client") as mock_fesco,
    ):
        mock_agg.get_containers = AsyncMock(return_value=[{"id": 1, "size": 20, "weight_from": 0, "weight_to": 28000}])
        mock_agg.search_container_ids = lambda containers, weight, size: [1]
        mock_agg.find_all_paths = AsyncMock(return_value=[route])
        mock_fesco.get_containers = AsyncMock(return_value=[])
        mock_fesco.search_container_ids = lambda containers, weight, size: []
        mock_fesco.find_all_paths = AsyncMock(return_value=[])

        request = _make_request()
        auth = AuthContext(is_demo=False)
        result = await calculate_routes(request, auth)

    assert len(result["routes"]) == 1
    assert result["routes"][0][0][0].company == "CompanyA"


def test_strip_demo_fields_empty_segments():
    from backend_user.services.route_calculation import _strip_demo_fields

    routes = [([], None, False, [])]
    _strip_demo_fields(routes)
    assert routes[0][0] == []
