import re
from collections import defaultdict
from typing import Any

import pandas as pd
from back_admin.models.upoader_fields_config import UploaderFieldsConfig
from pandas import DataFrame
from shared.models import ContainerOwner, ContainerShipmentTerms, ContainerTransferTerms, RouteType

from .errors import InvalidRouteTypeException, LoadingErrorException, PointsWithNanException
from .helpers import format_date, none_filter, price_filter
from .uploader import create_route, load_containers, load_points, load_routes, load_services


def remove_extra_spaces(value):
    if isinstance(value, str):
        return re.sub(r" {2,}", " ", value.strip())
    return value


def select_cols(processed_df: DataFrame, cols: list[str]):
    return processed_df[processed_df.columns.intersection(cols)]


def process_numeric_and_string_cols(processed_df: DataFrame, numeric_cols: set[str]):
    string_cols = {col for col in processed_df.columns if col not in numeric_cols}
    numeric_cols = {col for col in numeric_cols if col in processed_df.columns}

    if string_cols:
        string_cols_list = list(string_cols)
        processed_df[string_cols_list] = (  # noqa: ECE001
            processed_df[string_cols_list]
            .apply(lambda x: x.str.strip() if x.dtype == "str" else x)
            .apply(remove_extra_spaces)
        )

    if numeric_cols:
        numeric_cols_list = list(numeric_cols)
        processed_df[numeric_cols_list] = processed_df[numeric_cols_list].map(  # noqa: ECE001
            lambda x: (
                remove_extra_spaces(x.replace("%", "").replace("$", "")).strip()
                if isinstance(x, str) else x
            )
        )

    return processed_df


def process_points_services_effectivity(
    processed_df: DataFrame,
    warnings,
    fields_config:
    UploaderFieldsConfig,
    ws_name: str,
):
    processed_df[fields_config.service] = processed_df[fields_config.service].apply(none_filter).str.strip()

    processed_df[fields_config.start_point] = processed_df[fields_config.start_point].apply(none_filter).str.strip()
    processed_df[fields_config.end_point] = processed_df[fields_config.end_point].apply(none_filter).str.strip()
    processed_df[fields_config.terminal] = processed_df[fields_config.terminal].str.strip().str.upper()  # noqa: ECE001

    processed_df[fields_config.effective_from] = (
        processed_df[fields_config.effective_from].apply(none_filter).apply(format_date)
    )
    processed_df[fields_config.effective_to] = (
        processed_df[fields_config.effective_to].apply(none_filter).apply(format_date)
    )

    # remove rows without dates
    df_dropna_subset = [
        fields_config.effective_from,
        fields_config.effective_to,
    ]

    missing_idx = []
    for col in df_dropna_subset:
        missing_idx += processed_df[processed_df[col].isna()].index.tolist()

    if missing_idx:
        warnings.append(("UnsupportedDateFormat", tuple(row_idx for row_idx in missing_idx), ws_name))

    return processed_df.dropna(ignore_index=False, subset=df_dropna_subset)


def process_conversion_percents(processed_df: DataFrame, fields_config: UploaderFieldsConfig):
    processed_df[fields_config.conversation_percents] = (  # noqa: ECE001
        processed_df[fields_config.conversation_percents].apply(
            lambda x: (
                remove_extra_spaces(x.strip()).rstrip("%").rstrip()
                if isinstance(x, str) else
                x * 100 if isinstance(x, float) else x
            )
        )
    )
    return processed_df


def process_routes_df(processed_routes_df, route_type: RouteType, warnings, fields_config: UploaderFieldsConfig):
    processed_routes_df = select_cols(processed_routes_df, fields_config.model_dump().values())

    processed_routes_df = process_numeric_and_string_cols(
        processed_routes_df,
        {
            fields_config.sea_20dc,
            fields_config.sea_40hc,
            fields_config.rail_40hc,
            fields_config.rail_20dc24t,
            fields_config.rail_20dc28t,
            fields_config.conversation_percents,
        },
    )

    processed_routes_df = process_points_services_effectivity(
        processed_routes_df,
        warnings,
        fields_config,
        route_type.value,
    )
    processed_routes_df = process_conversion_percents(processed_routes_df, fields_config)

    processed_routes_df[fields_config.container_condition] = (
        processed_routes_df[fields_config.container_condition].apply(none_filter)
    )
    processed_routes_df[fields_config.container_transfer_terms] = (
        processed_routes_df[fields_config.container_transfer_terms].apply(none_filter)
    )
    processed_routes_df[fields_config.container_shipment_terms] = (
        processed_routes_df[fields_config.container_shipment_terms].apply(none_filter)
    )

    routes_df_dropna_subset = [
        fields_config.start_point,
        fields_config.end_point,
        fields_config.effective_from,
        fields_config.effective_to,
        fields_config.service,
    ]
    missing_info_about_id = defaultdict(list)

    for col in routes_df_dropna_subset:
        missing_idx = processed_routes_df[processed_routes_df[col].isna()].index.tolist()
        for _id in missing_idx:
            missing_info_about_id[_id].append(col)

    missing_info = tuple(
        {"row_index": row_id, "skipped_columns": columns}
        for row_id, columns in missing_info_about_id.items()
    )

    if missing_info:
        warnings.append(("MissingRoutesDataException", missing_info, route_type.value))

    processed_routes_df = processed_routes_df.dropna(subset=routes_df_dropna_subset)

    processed_routes_df[fields_config.start_point] = processed_routes_df[fields_config.start_point].str.title()
    processed_routes_df[fields_config.end_point] = processed_routes_df[fields_config.end_point].str.title()
    processed_routes_df[fields_config.terminal] = processed_routes_df[fields_config.terminal].str.upper()
    processed_routes_df[fields_config.service] = processed_routes_df[fields_config.service].str.upper()

    if route_type is RouteType.SEA:
        processed_routes_df[fields_config.sea_20dc] = (
            processed_routes_df[fields_config.sea_20dc].apply(price_filter)
        )
        processed_routes_df[fields_config.sea_40hc] = (
            processed_routes_df[fields_config.sea_40hc].apply(price_filter)
        )
    elif route_type is RouteType.RAIL:
        processed_routes_df[fields_config.rail_40hc] = (
            processed_routes_df[fields_config.rail_40hc].apply(price_filter)
        )
        processed_routes_df[fields_config.rail_20dc24t] = (
            processed_routes_df[fields_config.rail_20dc24t].apply(price_filter)
        )
        processed_routes_df[fields_config.rail_20dc28t] = (
            processed_routes_df[fields_config.rail_20dc28t].apply(price_filter)
        )
    else:
        raise InvalidRouteTypeException(route_type)

    # Default values
    processed_routes_df = processed_routes_df.astype({
        fields_config.container_condition: "str",
        fields_config.container_transfer_terms: "str",
        fields_config.container_shipment_terms: "str",
    })

    processed_routes_df.loc[
        processed_routes_df[fields_config.container_condition].isna(), fields_config.container_condition
    ] = ContainerOwner.COC.value

    processed_routes_df.loc[
        processed_routes_df[fields_config.container_transfer_terms].isna(), fields_config.container_transfer_terms
    ] = ContainerTransferTerms.FILO.value

    processed_routes_df.loc[
        processed_routes_df[fields_config.container_shipment_terms].isna(), fields_config.container_shipment_terms
    ] = ContainerShipmentTerms.FOR.value

    processed_routes_df[fields_config.route_type] = route_type

    return processed_routes_df


async def load_data(
    db_session,
    sea_routes_df: DataFrame,
    rail_routes_df: DataFrame,
    points_df: DataFrame,
    fields_config: UploaderFieldsConfig,
    load_on_warnings: bool = False,
):
    warnings: list[Any] = []
    # cleanup DF points
    points_df = points_df.apply(lambda x: x.str.strip() if x.dtype == "str" else x)
    points_df = points_df.drop_duplicates(subset=["city", "country"], ignore_index=False)

    points_rows_with_nan = [i + 2 for i in points_df[points_df.isna().any(axis=1)].index.tolist()]  # noqa: ECE001
    if points_rows_with_nan:
        raise PointsWithNanException(points_rows_with_nan)

    # process routes and setup new index for correct concatenation
    sea_routes_df = process_routes_df(sea_routes_df, RouteType.SEA, warnings, fields_config)
    sea_routes_df["Index"] = sea_routes_df.index.to_series()
    sea_routes_df = sea_routes_df.set_index([fields_config.route_type, "Index"])

    rail_routes_df = process_routes_df(rail_routes_df, RouteType.RAIL, warnings, fields_config)
    rail_routes_df["Index"] = rail_routes_df.index.to_series()
    rail_routes_df = rail_routes_df.set_index([fields_config.route_type, "Index"])

    routes_df: DataFrame = pd.concat((sea_routes_df, rail_routes_df), ignore_index=False)
    del sea_routes_df, rail_routes_df

    # Merging points with terminals
    routes_with_transit = routes_df.dropna(subset=[fields_config.terminal])[[
        fields_config.start_point,
        fields_config.end_point,
        fields_config.terminal,
    ]]

    points_df_merged_with_transit = pd.concat((
        pd.merge(
            points_df.copy(),
            routes_with_transit.loc[[RouteType.SEA]][[
                fields_config.end_point,
                fields_config.terminal,
            ]],
            left_on="city",
            right_on=fields_config.end_point,
        ),
        pd.merge(
            points_df.copy(),
            routes_with_transit.loc[[RouteType.SEA]][[
                fields_config.end_point,
                fields_config.terminal,
            ]],
            left_on="RU_city",
            right_on=fields_config.end_point,
        ),
        pd.merge(
            points_df.copy(),
            routes_with_transit.loc[[RouteType.RAIL]][[
                fields_config.start_point,
                fields_config.terminal,
            ]],
            left_on="city",
            right_on=fields_config.start_point,
        ),
        pd.merge(
            points_df.copy(),
            routes_with_transit.loc[[RouteType.RAIL]][[
                fields_config.start_point,
                fields_config.terminal,
            ]],
            left_on="RU_city",
            right_on=fields_config.start_point,
        ),
    ))

    points_df_merged_with_transit = points_df_merged_with_transit[list(
        set(points_df_merged_with_transit.columns)
        - {fields_config.start_point, fields_config.end_point}
    )].drop_duplicates()
    points_df_merged_with_transit["city"] = (
        points_df_merged_with_transit["city"]
        + " ("
        + points_df_merged_with_transit[fields_config.terminal]
        + ")"
    )

    points_df_merged_with_transit["RU_city"] = (
        points_df_merged_with_transit["RU_city"]
        + " ("
        + points_df_merged_with_transit[fields_config.terminal]
        + ")"
    )
    points_df_merged_with_transit = points_df_merged_with_transit[list(
        set(points_df_merged_with_transit.columns)
        - {fields_config.terminal}
    )]

    points_df = pd.concat((points_df, points_df_merged_with_transit)).drop_duplicates()
    del routes_with_transit, points_df_merged_with_transit

    # add terminal to the start/end point in routes
    mask = routes_df[fields_config.terminal].notna()
    mask &= routes_df[fields_config.terminal].str.strip() != ""

    sea_mask = (routes_df.index.get_level_values(fields_config.route_type) == RouteType.SEA) & mask
    routes_df.loc[sea_mask, fields_config.end_point] = (
        routes_df.loc[sea_mask, fields_config.end_point] + " (" + routes_df.loc[sea_mask, fields_config.terminal] + ")"
    )

    rail_mask = (routes_df.index.get_level_values(fields_config.route_type) == RouteType.RAIL) & mask
    routes_df.loc[rail_mask, fields_config.start_point] = (
        routes_df.loc[rail_mask, fields_config.start_point]
        + " (" + routes_df.loc[rail_mask, fields_config.terminal] + ")"
    )

    # load points
    points_data = await load_points(db_session, points_df) or []
    del points_df

    # hash points
    hashed_points = {}
    for point in points_data:
        hashed_points[point.city.lower()] = hashed_points[point.RU_city.lower()] = point
    points = hashed_points

    # load services
    services = await load_services(db_session, set(routes_df[fields_config.service].tolist()))

    # load containers
    containers = await load_containers(db_session, [
        {"size": 20, "weight_from": 0, "weight_to": 24, "type": "DC", "name": "20DC≤24t"},
        {"size": 20, "weight_from": 24, "weight_to": 28, "type": "DC", "name": "20DC 24-28t"},
        {"size": 40, "weight_from": 0, "weight_to": 28, "type": "HC", "name": "40HC≤28t"},
    ])

    # load routes
    routes_lst = []

    for index, row in routes_df.iterrows():
        route_type, i = index
        try:
            route = create_route(containers, services, points, row, fields_config, route_type)
        except (LoadingErrorException, ValueError) as e:
            warnings.append((e, i, route_type))
            continue

        if route:
            routes_lst.append(route)

    del routes_df
    if warnings and not load_on_warnings:
        return False, len(routes_lst), warnings

    await load_routes(db_session, routes_lst)
    return True, len(routes_lst), warnings
