import io

import pandas as pd
import numpy as np
from fastapi import APIRouter, UploadFile, HTTPException
from sqlalchemy import select, update

from back_admin.api.data_import.loading_data_to_db import validate_route_data, extract_data, create_independent_models, \
    group_containers_from_db, create_routes, write_independent_data, write_routes, parse_date
from back_admin.database import database
from back_admin.models import RailRouteModel, SeaRouteModel, ContainerModel
from back_admin.models.route import BatchModel

router = APIRouter(prefix="/data", tags=["data-admin"])


@router.post("/import")
async def dataImport(file: UploadFile,
                     route_type: str,
                     type_data: str | None = None,
                     company_col: str | None = None,
                     company_name: str | None = None,
                     dates_col: str | None = None,
                     dates: str | None = None):
    async def process_dataframe(_df: pd.DataFrame, _company_col, _dates_col):
        validate_route_data(_df, _company_col, _dates_col)

        services, points, containers = extract_data(_df, _company_col)
        services, points, containers, typed_containers = create_independent_models(
            services, points, containers
        )

        async with database.session() as session:
            db_containers = (await session.execute(select(ContainerModel))).scalars().all()

        db_containers, db_typed_containers = group_containers_from_db(db_containers)
        containers = {**containers, **db_containers}
        typed_containers = {**typed_containers, **db_typed_containers}

        _additional_data = None
        if route_type != "sea" and type_data:
            _additional_data = type_data.split(";")
            if _additional_data[0] == "column":  # todo: finalize 5th item
                route_type_col = "ROUTE TYPE" if _additional_data[1] == "" else _additional_data[1]

        if route_type == "rail":
            prices = {"Price, RUB": "price", "Guard": "guard"}
            if not _additional_data:
                _additional_data = ["drop", "Drop, $"]
                _df[_additional_data[1]] = 0

            if _additional_data:
                if _additional_data[0] == "drop":  # Drop = Drop, $
                    prices[_additional_data[1]] = "drop"

                if _additional_data[0] == "only drop":  # todo: make into point check
                    prices = {_additional_data[2]: "drop"}

            routes = create_routes(
                _df,
                RailRouteModel,
                prices,
                ["Price, RUB"],
                services,
                points,
                containers,
                typed_containers,
                _company_col if _company_col else None,
                _dates_col if _dates_col else None,
            )

        elif route_type == "sea":
            routes = create_routes(
                _df,
                SeaRouteModel,
                {"FILO": "filo", "FIFO": "fifo"},
                ["FIFO", "FILO"],
                services,
                points,
                containers,
                typed_containers,
                _company_col if _company_col else None,
                _dates_col if _dates_col else None,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown route type '{route_type}'"
            )

        async with database.session() as session:
            count_points = await write_independent_data(services, points, containers, session)
            await write_routes(routes, session)
            await session.commit()

        return len(routes), count_points

    def combine_excel_sheets(excel_file: pd.ExcelFile,
                             dates_col: str | None = None,
                             dates: str | None = None,
                             company_col: str | None = None,
                             company_name: str | None = None,
                             route_type: str = "sea") -> pd.DataFrame:
        all_sheets_data = []
        processed_sheets_info = []

        date_from = None
        date_to = None
        if dates_col:
            date_from, date_to = dates_col.split(";")

        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(
                    excel_file,
                    sheet_name=sheet_name,
                    converters={date_from: parse_date, date_to: parse_date} if dates_col else None,
                )

                df.columns = df.columns.str.strip()

                required_columns = {
                    "POL COUNTRY", "POL FULL NAME", "POD COUNTRY",
                    "POD FULL NAME", "CONTAINER TYPE", "CONTAINER SIZE",
                    "Container weight limit",
                }

                if company_col:
                    required_columns.add(company_col)
                if dates_col:
                    required_columns.add(date_from)
                    required_columns.add(date_to)

                if "Container weight limit" not in df.columns:
                    df["Container weight limit"] = np.nan

                if 'CONTAINER TYPE' in df.columns:
                    df['CONTAINER TYPE'] = df['CONTAINER TYPE'].str[:2]

                if dates and date_from and date_to:
                    date_from_val, date_to_val = dates.split(" - ")
                    df[date_from] = parse_date(date_from_val)
                    df[date_to] = parse_date(date_to_val)

                if company_name and company_col:
                    df[company_col] = company_name

                data_columns = set(df.columns)

                if not all(col in data_columns for col in required_columns):
                    print(f"Sheet {sheet_name} doesn't contain {required_columns - data_columns}. Skipping.")
                    processed_sheets_info.append({
                        "sheet": sheet_name,
                        "rows": len(df),
                        "status": "skipped",
                        "reason": f"Missing columns: {required_columns - data_columns}"
                    })
                    continue

                if route_type == "sea":
                    filo_col = next((col for col in df.columns if isinstance(col, str) and 'FILO' in col.upper()), None)
                    if filo_col and filo_col != 'FILO':
                        df = df.rename(columns={filo_col: 'FILO'})

                df['_source_sheet'] = sheet_name

                all_sheets_data.append(df)
                processed_sheets_info.append({
                    "sheet": sheet_name,
                    "rows": len(df),
                    "status": "processed"
                })

            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                processed_sheets_info.append({
                    "sheet": sheet_name,
                    "error": str(e),
                    "status": "failed"
                })

        if not all_sheets_data:
            raise HTTPException(
                status_code=400,
                detail="No valid sheets found in Excel file"
            )

        combined_df = pd.concat(all_sheets_data, ignore_index=True)

        return combined_df, processed_sheets_info

    file_extension = file.filename.rsplit('.', maxsplit=1)[-1].lower()
    contents = await file.read()

    if dates:
        dates_col = "EFFECTIVE FROM;EFFECTIVE TO"

    date_from, date_to = None, None
    if dates_col:
        date_from, date_to = dates_col.split(";")

    if company_name:
        company_col = "Service"

    if file_extension == "csv" or file_extension == "txt":
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')),
            index_col=None,
            delimiter=";",
            converters={date_from: parse_date, date_to: parse_date} if dates_col else None,
        )

        if dates:
            date_from_val, date_to_val = dates.split(" - ")
            df[date_from] = parse_date(date_from_val)
            df[date_to] = parse_date(date_to_val)

        if company_name:
            df[company_col] = company_name

        count_new_routes, count_new_points = await process_dataframe(df, company_col, dates_col)
        processed_sheets = [{"sheet": "main", "rows": len(df)}]

    elif file_extension == "xlsx":
        excel_file = pd.ExcelFile(io.BytesIO(contents))

        combined_df, processed_sheets = combine_excel_sheets(
            excel_file,
            dates_col=dates_col,
            dates=dates,
            company_col=company_col,
            company_name=company_name,
            route_type=route_type
        )

        count_new_routes, count_new_points = await process_dataframe(combined_df, company_col, dates_col)

        for sheet_info in processed_sheets:
            if sheet_info["status"] == "processed":
                sheet_info["processed_routes"] = count_new_routes

    else:
        raise HTTPException(
            status_code=400,
            detail="Wrong file extension. Allowed only CSV (TXT), XLSX"
        )

    return {
        "status": "OK",
        "count_new_routes": count_new_routes,
        "count_new_points": count_new_points,
        "processed_sheets": processed_sheets,
        "file": file.filename,
    }


@router.patch("/save")
async def saveData(batch_id: int):
    async with database.session() as session:
        new_vals = {"batch_id": None}
        rail_q = await session.execute(
            update(
                RailRouteModel,
            ).where(
                RailRouteModel.batch_id == batch_id,
            ).values(
                **new_vals
            )
        )

        sea_q = await session.execute(
            update(
                SeaRouteModel,
            ).where(
                SeaRouteModel.batch_id == batch_id,
                ).values(
                **new_vals
            )
        )

        rail_count = rail_q.rowcount
        sea_count = sea_q.rowcount

    return {
        "status": "OK",
        "rail_count": rail_count,
        "sea_count": sea_count,
    }


@router.post("/batches")
async def getBatches():
    async with database.session() as session:
        temp = await session.execute(
            select(
                BatchModel,
            )
        )
        batches = temp.scalars().all()

    return {
        "status": "OK",
        "batches": batches,
    }
