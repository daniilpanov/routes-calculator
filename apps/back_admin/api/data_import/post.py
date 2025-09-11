import io

import pandas as pd
from fastapi import APIRouter, UploadFile, HTTPException
from sqlalchemy import select

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
    async def process_dataframe(_df: pd.DataFrame) -> int:
        # company_col = Service
        # dates_col = EFFECTIVE FROM;EFFECTIVE TO

        validate_route_data(_df, company_col, dates_col)

        if company_col:
            services, points, containers = extract_data(_df, company_col)

        else:
            points, containers = extract_data(_df)
            services = [company_name]

        services, points, containers, typed_containers = create_independent_models(
            services, points, containers
        )

        async with database.session() as session:
            db_containers = (await session.execute(select(ContainerModel))).scalars().all()

        db_containers, db_typed_containers = group_containers_from_db(db_containers)
        containers = {**containers, **db_containers}
        typed_containers = {**typed_containers, **db_typed_containers}

        _additional_data = [""]
        if route_type != "sea":
            _additional_data = type_data.split(";")
            if _additional_data[0] == "column":  # todo: finalize 5th item
                column_type = "ROUTE TYPE" if _additional_data[1] == "" else _additional_data[1]

        if route_type == "rail":
            prices = {"Price, RUB": "price", "Guard": "guard"}
            if _additional_data[0] == "drop":
                drop_col = "Drop, $" if _additional_data[1] == "" else _additional_data[1]
                prices[drop_col] = "drop"
            if _additional_data[0] == "only drop":  # todo: make into point check
                prices = {"Drop, $": "drop"}

            routes = create_routes(
                _df,
                RailRouteModel,
                prices,
                ["Price, RUB"],
                services if company_col else services[company_name],
                points,
                containers,
                typed_containers,
                company_col if company_col else None,
                dates_col if dates_col else None,
                dates if dates else None,
            )

        elif route_type == "sea":
            routes = create_routes(
                _df,
                SeaRouteModel,
                {"FILO": "filo", "FIFO": "fifo"},
                ["FIFO", "FILO"],
                services if company_col else services[company_name],
                points,
                containers,
                typed_containers,
                company_col if company_col else None,
                dates_col if dates_col else None,
                dates if dates else None,
            )

        elif route_type == "column":
            ...

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown route type '{route_type}'"
            )

        async with database.session() as session:
            await write_independent_data(services, points, containers, session)
            await write_routes(routes, session)
            await session.commit()

        return len(routes)

    file_extension = file.filename.rsplit('.', maxsplit=1)[-1].lower()
    contents = await file.read()

    if dates_col:
        date_from, date_to = dates_col.split(";")

    if file_extension == "csv" or file_extension == "txt":
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')),
            index_col=None,
            delimiter=";",
            converters={date_from: parse_date, date_to: parse_date} if dates_col else None,
        )
        total_count = await process_dataframe(df)
        processed_sheets = [{"sheet": "main", "rows": len(df)}]

    elif file_extension == "xlsx":
        processed_sheets = []
        total_count = 0

        excel_file = pd.ExcelFile(io.BytesIO(contents))

        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(
                    io.BytesIO(contents),
                    sheet_name=sheet_name,
                    converters={date_from: parse_date, date_to: parse_date} if dates_col else None,
                )

                required_columns = [
                    "POL COUNTRY", "POL FULL NAME", "POD COUNTRY",
                    "POD FULL NAME", "CONTAINER TYPE", "CONTAINER SIZE",
                    "Container weight limit",
                ]

                if company_col:
                    required_columns += [company_col]
                if dates_col:
                    required_columns += [date_from, date_to]

                if not all(col in df.columns for col in required_columns):
                    print(f"Sheet {sheet_name} doesn't contain required columns. Skipping.")
                    continue

                df_for_processing = df.copy()

                sheet_count = await process_dataframe(df_for_processing)
                total_count += sheet_count
                processed_sheets.append({
                    "sheet": sheet_name,
                    "rows": len(df),
                    "processed_routes": sheet_count
                })

            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                processed_sheets.append({
                    "sheet": sheet_name,
                    "error": str(e),
                    "status": "failed"
                })

    else:
        raise HTTPException(
            status_code=400,
            detail="Wrong file extension. Allowed only CSV (TXT), XLSX"
        )

    return {
        "status": "OK",
        "total_count": total_count,
        "processed_sheets": processed_sheets,
        "file": file.filename,
    }


@router.post("/batches")
async def getBatches():
    batch_stmt = select(
        BatchModel,
    )

    async with database.session() as session:
        temp = await session.execute(batch_stmt)
        batches = temp.scalars().all()

    return {
        "status": "OK",
        "batches": batches,
    }
