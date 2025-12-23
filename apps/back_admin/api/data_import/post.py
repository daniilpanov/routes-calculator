import io
from datetime import datetime

import pandas as pd
import numpy as np
from fastapi import APIRouter, UploadFile, HTTPException
from pandas import DataFrame
from sqlalchemy import select, update, delete

from back_admin.api.data_import.loading_data_to_db import validate_route_data, extract_data, create_independent_models, \
    group_containers_from_db, create_routes, write_independent_data, write_routes, parse_date
from back_admin.database import database
from back_admin.models import RailRouteModel, SeaRouteModel, ContainerModel, PointModel
from back_admin.models.route import BatchModel

router = APIRouter(prefix="/data", tags=["data-admin"])


@router.post("/load_points")
async def load_points_by_file(file: UploadFile):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents), sep=";")
    load_count: int = 0

    async with database.session() as session:
        for _, point in df.iterrows():
            try:
                new_point = PointModel(
                    city=point["city"].strip().upper(),
                    country=point["country"].strip(),
                    RU_city=point["RU_city"].strip(),
                    RU_country=point["RU_country"].strip(),
                )

                await session.merge(new_point)
                load_count += 1
            except Exception as e:
                return HTTPException(
                    status_code=500,
                    detail=str(e),
                )
            await session.flush()
        await session.commit()

    return {
        "status": "OK",
        "input": len(df),
        "load": load_count,
    }


async def parse_pattern_file(input_df: pd.DataFrame, route_type: str, sea_price='FILO') -> pd.DataFrame:
    df = input_df.copy()
    
    port_countries = {
        'BUENOS AIRES': 'Argentina', 'ITAJAI': 'Brazil', 'PARANAGUA': 'Brazil',
        'RIO GRANDE': 'Brazil', 'SANTOS': 'Brazil', 'VITORIA': 'Brazil',
        'ASUNCION': 'Paraguay', 'MONTEVIDEO': 'Uruguay', 'BAHRAIN': 'Bahrain',
        'CHITTAGONG': 'Bangladesh', 'CHENNAI': 'India', 'COCHIN': 'India',
        'KANDLA': 'India', 'KATTUPALLI': 'India', 'KOLKATA': 'India',
        'Nhava Sheva': 'India', 'TUTICORIN': 'India', 'VISAKHAPATNAM': 'India',
        'UMM QASR (NORTH PORT)': 'Iraq', 'SHUWAIKH': 'Kuwait', 'SOHAR': 'Oman',
        'DOHA (HAMAD)': 'Qatar', 'DAMMAM': 'Saudi Arabia', 'JEDDAH': 'Saudi Arabia',
        'COLOMBO': 'Sri Lanka', 'JEBEL ALI': 'UAE', 'KHALIFA': 'UAE',
        'DAMIETTA': 'Egypt', 'SAFIPORT': 'Egypt', 'MERSIN': 'Turkey',
        'SINGAPORE': 'Singapore', 'HO CHI MINH': 'Vietnam', 'BUSAN': 'Korea', 'BANGKOK': 'Thailand',
        'LAEM CHABANG': 'Thailand', 'JAKARTA': 'Indonesia', 'SURABAYA': 'Indonesia', 'SEMARANG': 'Indonesia',
        'BELAWAN': 'Indonesia', 'PORT KLANG': 'Malaysia', 'YANGON': 'Myanma', 'INCHEON': 'Korea',
        'MUNDRA': 'India', 'KARACHI': 'Pakistan', 'PENANG': 'Malaysia', 'HAIPHONG': 'Vietnam',
        'TOKYO': 'Japan', 'YOKOHAMA': 'Japan', 'NAGOYA': 'Japan', 'HAKATA': 'Japan', 'MOJI': 'Japan', 'OSAKA': 'Japan',
        'KOBE': 'Japan',
    }
    
    russian_ports = [
        'MOSCOW', 'SAINT-PETERSBURG', 'INYA-VOSTOCHNAYA', 'YEKATERINBURG-TOVARNY', 'YEKATERINBURG',
        'IRKUTSK', 'NOVOSIBIRSK', 'OMSK', 'CHELYABINSK', 'PERM', 'KRASNOYARSK', 'NIZHNEKAMSK', 'ULYANOVSK',
        'TOLYATTI', 'ROSTOV-ON-DON', 'SAMARA', 'KRASNODARH', 'KAZAN', 'NIZHNY NOVGOROD', 'PENZA', 'VOSTOCHNY',
        'BALTIYSK-KALININGRAD', 'NOVOROSSIYSK',
    ]

    chinese_ports = [
        'BAJIANG', 'BEIHAI', 'BEIJIAO', 'CHANGSHU', 'CHANGSHA', 'CHONGQING', 'CHANGZHOU',
        'DAFENG', 'DONGGUAN', 'DAMAIYU', 'FANGCHENG', 'FULING', 'GAOLAN', 'GAOMING',
        'WAIHAI/GAOSHA', 'HONGWAN', 'HAIKOU', 'HAIMEN', 'HUANGPU', 'HESHAN', 'JIANGYIN',
        'JIANGYIN, JIANGSU', 'JIUJIANG', 'JIAO XIN', 'KAIPING', 'LANSHAN', 'LELIU',
        'LUZHOU', 'LIANYUNGANG', 'MAWEI', 'NANCHANG', 'NANJING', 'NANTONG', 'QINZHOU',
        'QUANZHOU', 'RONGQI', 'RIZHAO', 'SANSHAN', 'SHEKOU', 'QINHUANGDAO', 'SANSHUI (NEW PORT)',
        'SANRONG/GAOYAO', 'SHANTOU', 'TAICANG', 'TAIZHOU', 'TAISHAN', 'WEIHAI', 'WUHU',
        'WENZHOU', 'WUHAN', 'WANZHOU', 'XINHUI', 'XIYU', 'YANTAI', 'YANGZHOU', 'YIBIN',
        'YICHANG', 'YANTIAN', 'YUNFU', 'YUEYANG', 'ZHANJIANG', 'ZHENJIANG', 'ZHANGJIAGANG',
        'ZHAPU', 'ZHONGSHAN', 'HEFEI', 'WEIFANG', 'XIAOLAN', 'YANGPU', 'DALIAN', 'HONG KONG', 'QINGDAO',
        'SHANGHAI', 'NINGBO', 'XIAMEN', 'NANSHA', 'KEELUNG', 'TAICHUNG', 'KAOHSIUNG'
    ]

    def get_upper(port: str):
        return port.upper().strip()

    df['POD FULL NAME'] = df['Пункт прибытия'].apply(get_upper)
    df['POL FULL NAME'] = df['Пункт отправления'].apply(get_upper)

    for port in chinese_ports:
        port_countries[port] = 'China'
        
    for port in russian_ports:
        port_countries[port] = 'Russia'

    def get_country(port_name):
        port_name = str(port_name)
        if port_name in port_countries:
            return port_countries[port_name].strip()

        return 'Unknown'


    is_rail: bool = route_type == 'rail'
    price_field, other_price = '', ''
    if not is_rail:
        price_field = sea_price
        if sea_price == 'FILO':
            other_price = 'FIFO'
        else:
            other_price = 'FILO'
    else:
        price_field = 'Price, RUB'

    df['POL COUNTRY'] = df['Пункт отправления'].apply(get_country)
    df['POD COUNTRY'] = df['Пункт прибытия'].apply(get_country)
    df['Service'] = df['Линия']
    if not is_rail:
        df[sea_price] = np.nan

    def format_date(date_str):
        try:
            if isinstance(date_str, str):
                month_replacements = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }

                for eng_month, num_month in month_replacements.items():
                    if eng_month in date_str:
                        date_str = date_str.replace(eng_month, num_month)

                for fmt in ['%d.%m.%Y', '%d-%m-%Y', '%d %m %Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(date_str.strip(), fmt).strftime('%d.%m.%Y')
                    except ValueError:
                        continue
            return date_str
        except:
            return date_str

    date_columns = ['EFFECTIVE FROM', 'EFFECTIVE TO', 'Валидность (Начало)', 'Валидность (Конец)']
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(format_date)

    result_rows = []

    for _, row in df.iterrows():
        base_data = {
            'POL FULL NAME': row['POL FULL NAME'],
            'POL COUNTRY': row['POL COUNTRY'],
            'POD FULL NAME': row['POD FULL NAME'],
            'POD COUNTRY': row['POD COUNTRY'],
            'Service': row['Service'],
            'EFFECTIVE FROM': row.get('EFFECTIVE FROM') or row.get('Валидность (Начало)'),
            'EFFECTIVE TO': row.get('EFFECTIVE TO') or row.get('Валидность (Конец)')
        }

        # 20dv<24т
        container_20dv_24 = str(row.get('20dv<24т', '')).strip()
        if container_20dv_24 and container_20dv_24 != 'nan' and container_20dv_24 != '':
            result_rows.append({
                **base_data,
                'CONTAINER SIZE': '20',
                'CONTAINER TYPE': 'DC',
                'Container weight limit': '24',
                price_field: float(container_20dv_24.replace(',', '.').replace(' ', '')),
            })

        # 20dv<28т
        container_20dv_28 = str(row.get('20dv<28т', '')).strip()
        if container_20dv_28 and container_20dv_28 != 'nan' and container_20dv_28 != '':
            result_rows.append({
                **base_data,
                'CONTAINER SIZE': '20',
                'CONTAINER TYPE': 'DC',
                'Container weight limit': '28',
                price_field: float(container_20dv_28.replace(',', '.').replace(' ', '')),
            })

        # 40hc
        container_40hc = str(row.get('40hc', '')).strip()
        if container_40hc and container_40hc != 'nan' and container_40hc != '':
            result_rows.append({
                **base_data,
                'CONTAINER SIZE': '40',
                'CONTAINER TYPE': 'HC',
                'Container weight limit': '28',
                price_field: float(container_40hc.replace(',', '.').replace(' ', '')),
            })

        # Guard
        if is_rail:
            guard_20dv_24 = str(row.get('Охрана 20dv<24т', 0)).strip()
            guard_20dv_28 = str(row.get('Охрана 20dv<28т', 0)).strip()
            guard_40hc = str(row.get('Охрана 40hc', 0)).strip()

            result_rows[0]['Guard'] = float(guard_20dv_24.replace(',', '.').replace(' ', '')) if guard_20dv_24 and guard_20dv_24 != 'nan' else 0
            result_rows[1]['Guard'] = float(guard_20dv_28.replace(',', '.').replace(' ', '')) if guard_20dv_28 and guard_20dv_28 != 'nan' else 0
            result_rows[2]['Guard'] = float(guard_40hc.replace(',', '.').replace(' ', '')) if guard_40hc and guard_40hc != 'nan' else 0

    result_df = pd.DataFrame(result_rows)

    column_order = [
        'POL FULL NAME', 'POL COUNTRY', 'POD FULL NAME', 'POD COUNTRY',
        'Service', 'CONTAINER SIZE', 'CONTAINER TYPE', 'Container weight limit',
        price_field, 'EFFECTIVE FROM', 'EFFECTIVE TO'
    ]

    if other_price == '':
        column_order.append('Guard')
    else:
        column_order.append(other_price)


    result_df = result_df.reindex(columns=column_order)

    return result_df


async def process_dataframe(_df: pd.DataFrame, _company_col, _dates_col, _r_type, _type_data):
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
    if _r_type != "sea" and _type_data:
        _additional_data = _type_data.split(";")
        if _additional_data[0] == "column":  # todo: finalize 5th item
            route_type_col = "ROUTE TYPE" if _additional_data[1] == "" else _additional_data[1]

    if _r_type == "rail":
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

    elif _r_type == "sea":
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
            detail=f"Unknown route type '{_r_type}'"
        )

    this_batch_id = 0

    async with database.session() as session:
        count_points = await write_independent_data(services, points, containers, session)
        this_batch_id = await write_routes(routes, session)
        await session.commit()

    return len(routes), count_points, this_batch_id


@router.post("/import")
async def dataImport(file: UploadFile,
                     route_type: str,
                     type_data: str | None = None,
                     company_col: str | None = None,
                     company_name: str | None = None,
                     dates_col: str | None = None,
                     dates: str | None = None):


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

    pattern_check = type_data.split(';')
    if pattern_check[0] == 'pattern':
        params = (pd.read_excel(io.BytesIO(contents)), route_type,)
        if pattern_check[1][0] == 'F':
            temp = (pattern_check[1],)
            params += temp

        df: DataFrame = await parse_pattern_file(*params)

        count_new_routes, count_new_points, import_batch_id = await process_dataframe(df, company_col, dates_col, route_type, type_data)
        processed_sheets = [{"sheet": "Main", "rows": len(df)}]

    elif file_extension == "csv" or file_extension == "txt":
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

        count_new_routes, count_new_points, import_batch_id = await process_dataframe(df, company_col, dates_col, route_type, type_data)
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

        count_new_routes, count_new_points, import_batch_id = await process_dataframe(combined_df, company_col, dates_col, route_type, type_data)

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
        "batch_id": import_batch_id,
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
        await session.execute(delete(
            BatchModel,
        ).where(
            BatchModel.id == batch_id,
        ))

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