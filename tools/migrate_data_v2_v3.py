import asyncio

from dotenv import load_dotenv
from sqlalchemy import select

from src.database import database
from src.services.custom.models import RailRouteModel, SeaRouteModel
from src.services.custom.models.price import PriceTypeModel, RoutePriceModel, СurrencyModel
from src.services.custom.models.route import RouteModel

load_dotenv(".env.local") or load_dotenv("../.env.local")


async def create_currency(session, currency):
    existing = await session.execute(
        select(СurrencyModel).where(СurrencyModel.currency_name == currency)
    )
    if existing.scalar_one_or_none() is None:
        request = СurrencyModel(currency_name=currency)
        session.add(request)
        await session.flush()


async def create_type_prices(session, name, need_drop, direction):
    existing = await session.execute(
        select(PriceTypeModel).where(PriceTypeModel.name == name)
    )
    if existing.scalar_one_or_none() is None:
        new_price_types = PriceTypeModel(
            name=name,
            need_drop=need_drop,
            direction=direction,
        )
        session.add(new_price_types)
        await session.flush()


async def find_price_type_id_by_name(session, name):
    price_type = await session.execute(
        select(PriceTypeModel.id).where(PriceTypeModel.name == name)
    )
    return price_type.scalar_one_or_none()


async def find_currency_id_by_name(session, name):
    currency = await session.execute(
        select(СurrencyModel.id).where(СurrencyModel.currency_name == name)
    )
    return currency.scalar_one_or_none()


async def migrate_from_sea_routes(session):
    price_type_fifo_id = await find_price_type_id_by_name(session, "fifo")
    price_type_filo_id = await find_price_type_id_by_name(session, "filo")
    currency_id = await find_currency_id_by_name(session, "USD")

    sea_routes = (await session.execute(select(SeaRouteModel))).scalars().all()
    for sea_route in sea_routes:
        existing_route = await session.execute(
            select(RouteModel).where(
                RouteModel.company_id == sea_route.company_id,
                RouteModel.container_id == sea_route.container_id,
                RouteModel.start_point_id == sea_route.start_point_id,
                RouteModel.end_point_id == sea_route.end_point_id,
                RouteModel.effective_from == sea_route.effective_from,
                RouteModel.effective_to == sea_route.effective_to,
            )
        )
        if existing_route.scalar_one_or_none() is not None:
            continue

        new_route = RouteModel(
            company_id=sea_route.company_id,
            container_id=sea_route.container_id,
            start_point_id=sea_route.start_point_id,
            end_point_id=sea_route.end_point_id,
            effective_from=sea_route.effective_from,
            effective_to=sea_route.effective_to,
        )
        session.add(new_route)
        await session.flush()

        new_route_id = new_route.id
        if sea_route.filo is not None:
            session.add(
                RoutePriceModel(
                    route_id=new_route_id,
                    price_type_id=price_type_filo_id,
                    currency_id=currency_id,
                    value=sea_route.filo * 100,
                    conversation_percent=0,
                )
            )

        if sea_route.fifo is not None:
            session.add(
                RoutePriceModel(
                    route_id=new_route_id,
                    price_type_id=price_type_fifo_id,
                    currency_id=currency_id,
                    value=sea_route.fifo * 100,
                    conversation_percent=0,
                )
            )
    await session.flush()


async def migrate_from_rail_routes(session):
    price_type_drop_id = await find_price_type_id_by_name(session, "drop")
    price_type_fob_for_id = await find_price_type_id_by_name(session, "fob-for")
    currency_usd_id = await find_currency_id_by_name(session, "USD")
    currency_rub_id = await find_currency_id_by_name(session, "RUB")

    rail_routes = (await session.execute(select(RailRouteModel))).scalars().all()
    for rail_route in rail_routes:
        existing_route = await session.execute(
            select(RouteModel).where(
                RouteModel.company_id == rail_route.company_id,
                RouteModel.container_id == rail_route.container_id,
                RouteModel.start_point_id == rail_route.start_point_id,
                RouteModel.end_point_id == rail_route.end_point_id,
                RouteModel.effective_from == rail_route.effective_from,
                RouteModel.effective_to == rail_route.effective_to,
            )
        )
        if existing_route.scalar_one_or_none() is not None:
            continue

        new_route = RouteModel(
            company_id=rail_route.company_id,
            container_id=rail_route.container_id,
            start_point_id=rail_route.start_point_id,
            end_point_id=rail_route.end_point_id,
            effective_from=rail_route.effective_from,
            effective_to=rail_route.effective_to,
        )
        session.add(new_route)
        await session.flush()

        if rail_route.drop is not None:
            session.add(
                RoutePriceModel(
                    route_id=new_route.id,
                    price_type_id=price_type_drop_id,
                    currency_id=currency_usd_id,
                    value=rail_route.drop * 100,
                    conversation_percent=0,
                )
            )

        if rail_route.price is not None:
            session.add(
                RoutePriceModel(
                    route_id=new_route.id,
                    price_type_id=price_type_fob_for_id,
                    currency_id=currency_rub_id,
                    value=rail_route.price * 100,
                    conversation_percent=0,
                )
            )
    await session.flush()


async def migrate_data():
    async with database.session() as session:
        try:
            await create_currency(session, "RUB")
            await create_currency(session, "USD")
            await create_type_prices(session, "filo", False, 1)
            await create_type_prices(session, "fifo", False, 1)
            await create_type_prices(session, "drop", True, -1)
            await create_type_prices(session, "fob-for", True, 1)
            await migrate_from_sea_routes(session)
            await migrate_from_rail_routes(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(migrate_data())
