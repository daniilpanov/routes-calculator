import asyncio
import json

import aiohttp
import click

from .auth import ensure_token, make_cookie_header
from .config import get_cli_settings

VALID_RESOURCES = [
    "companies",
    "points",
    "containers",
    "route-segments",
    "services",
    "drop-off",
]


def _make_url(path: str) -> str:
    base = get_cli_settings().ADMIN_API_BASE_URL
    return f"{base}/db/{path.lstrip('/')}"


async def _api_get(path: str) -> tuple[int, dict | list]:
    token = ensure_token()
    async with aiohttp.ClientSession(headers=make_cookie_header(token)) as session:
        async with session.get(_make_url(path)) as resp:
            body = await resp.json()
            return resp.status, body


async def _api_post(path: str, data: dict) -> tuple[int, dict | list]:
    token = ensure_token()
    async with aiohttp.ClientSession(headers=make_cookie_header(token)) as session:
        async with session.post(_make_url(path), json=data) as resp:
            body = await resp.json() if resp.content_length != 0 else {}
            return resp.status, body


async def _api_put(path: str, data: dict) -> tuple[int, dict | list]:
    token = ensure_token()
    async with aiohttp.ClientSession(headers=make_cookie_header(token)) as session:
        async with session.put(_make_url(path), json=data) as resp:
            body = await resp.json() if resp.content_length != 0 else {}
            return resp.status, body


async def _api_patch(path: str, data: dict) -> tuple[int, dict | list]:
    token = ensure_token()
    async with aiohttp.ClientSession(headers=make_cookie_header(token)) as session:
        async with session.patch(_make_url(path), json=data) as resp:
            body = await resp.json() if resp.content_length != 0 else {}
            return resp.status, body


async def _api_delete(path: str) -> int:
    token = ensure_token()
    async with aiohttp.ClientSession(headers=make_cookie_header(token)) as session:
        async with session.delete(_make_url(path)) as resp:
            return resp.status


@click.group()
def db():
    """Query and manage database resources via Admin API."""


@db.command("list")
@click.argument("resource", type=click.Choice(VALID_RESOURCES))
@click.option("--filter", "filters", multiple=True, nargs=2, help="Filter params (key value)")
def list_resources(resource: str, filters: list[tuple[str, str]]):
    """List resources (companies, points, containers, ...)."""
    params = "&".join(f"{k}={v}" for k, v in filters)

    async def _run():
        status, body = await _api_get(f"{resource}?{params}" if params else resource)
        click.echo(json.dumps(body, indent=2, ensure_ascii=False))
        if status != 200:
            click.echo(f"HTTP {status}", err=True)

    asyncio.run(_run())


@db.command()
@click.argument("resource_id", type=str)
def get(resource_id: str):
    """Get a single resource by ID. Use format: <resource>/<id> (e.g. companies/5)."""
    async def _run():
        status, body = await _api_get(resource_id)
        click.echo(json.dumps(body, indent=2, ensure_ascii=False))
        if status != 200:
            click.echo(f"HTTP {status}", err=True)

    asyncio.run(_run())


@db.command()
@click.argument("resource", type=click.Choice(VALID_RESOURCES))
@click.option("--data", "-d", required=True, help="JSON payload")
def create(resource: str, data: str):
    """Create a new resource."""
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON: {e}", err=True)
        raise click.Abort from e

    async def _run():
        status, body = await _api_post(resource, payload)
        click.echo(json.dumps(body, indent=2, ensure_ascii=False))
        if status not in (200, 201):
            click.echo(f"HTTP {status}", err=True)

    asyncio.run(_run())


@db.command()
@click.argument("resource_id", type=str)
@click.option("--data", "-d", required=True, help="JSON payload")
def update(resource_id: str, data: str):
    """Full update (PUT) a resource by ID. Format: <resource>/<id>."""
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON: {e}", err=True)
        raise click.Abort from e

    async def _run():
        status, body = await _api_put(resource_id, payload)
        click.echo(json.dumps(body, indent=2, ensure_ascii=False))
        if status != 200:
            click.echo(f"HTTP {status}", err=True)

    asyncio.run(_run())


@db.command()
@click.argument("resource_id", type=str)
@click.option("--data", "-d", required=True, help="JSON payload")
def patch(resource_id: str, data: str):
    """Partial update (PATCH) a resource by ID. Format: <resource>/<id>."""
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON: {e}", err=True)
        raise click.Abort from e

    async def _run():
        status, body = await _api_patch(resource_id, payload)
        click.echo(json.dumps(body, indent=2, ensure_ascii=False))
        if status != 200:
            click.echo(f"HTTP {status}", err=True)

    asyncio.run(_run())


@db.command()
@click.argument("resource_id", type=str)
def delete(resource_id: str):
    """Delete a resource by ID. Format: <resource>/<id>."""
    async def _run():
        status = await _api_delete(resource_id)
        if status == 204:
            click.echo("Deleted")
        else:
            click.echo(f"HTTP {status}", err=True)

    asyncio.run(_run())


@db.group("stats")
def stats():
    """Show database statistics."""


@stats.command("route-segments")
def stats_route_segments():
    """Show route segments statistics (totals, distribution, top companies)."""
    async def _run():
        status, body = await _api_get("route-segments/stats")
        if status != 200:
            click.echo(f"HTTP {status}", err=True)
            click.echo(json.dumps(body, indent=2, ensure_ascii=False))
            return

        data: dict = body  # type: ignore[assignment]
        click.echo(f"Total segments:       {data['total_segments']}")
        click.echo(f"By type:              {data['by_type']}")
        click.echo(f"By is_through:        {data['by_is_through']}")
        click.echo(f"By container_owner:   {data['by_container_owner']}")
        click.echo("\nTop companies:")
        for c in data["top_companies"]:
            click.echo(f"  #{c['company_id']:>4} {c['name']:<30} {c['count']} segments")

    asyncio.run(_run())
