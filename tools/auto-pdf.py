# REQUIREMENTS: ghostscript, pillow, camelot, pandas, numpy

import camelot
import typing
import csv

import requests

if typing.TYPE_CHECKING:
    from pandas import Series


def parse_pdf(service, path, transfer_type, output_suffix=''):
    parsed_path = path.rsplit('-', maxsplit=3)
    updated_mark = parsed_path[-2].endswith('_upd')
    start_date = parsed_path[-2 - updated_mark]
    end_date = parsed_path[-1 - updated_mark][:-4]
    print(start_date, '-', end_date)
    output_path = service + '.' + transfer_type + '.' + output_suffix + '.' + start_date + '-' + end_date + '.csv'

    with open(output_path, 'w') as output_file:
        writer = csv.writer(output_file, delimiter=';')
        doc = camelot.read_pdf(path, pages='all')
        writer.writerow([
            'Service',
            'Destination Country', 'Destination',
            'Departure Country', 'Departure',
            'Start date', 'End date',
            'Container size', 'Container type', 'Container weight',
            'Transfer type', 'Price', 'FIFO', 'FILO',
        ])

        for page in doc:
            df = page.df
            header = list(map(lambda l: l.strip(), df.loc[0][0].splitlines()))
            if not header[0].startswith('Port of Discharge: '):
                print('ERROR!', df)
                continue
            discharge = header[0].split(':')[1].strip()
            container_types = header[2], header[3]
            print(discharge, *container_types)
            body = df.loc[1:]
            for index, row in body.iterrows():
                row: Series
                if len(row) < 3:
                    parsed_row = row[0].splitlines()
                else:
                    parsed_row = row.tolist()
                *_, depot, dc20, dc_hc40 = parsed_row
                depot = depot.strip()
                new_row = [service, 'Russia', discharge, 'Russia', depot, start_date, end_date, None, None, None, transfer_type, None]
                for _size, _type, _price in ((20, 'DC', dc20), (40, 'DC', dc_hc40), (40, 'HC', dc_hc40)):
                    _price = _price.strip()
                    if _price[0] == '-' or _price[-1] == '*':
                        continue
                    parsed_price = int(_price.replace('USD', '').replace(' ', ''))
                    if parsed_price <= 0:
                        continue
                    new_row[7] = _size
                    new_row[8] = _type
                    new_row[11] = parsed_price
                    writer.writerow(new_row)


def parse_from_net(service, urls, transfer_type, output_suffix=''):
    files = []
    with requests.Session() as session:
        for url in urls:
            f_name = url.rsplit('/', maxsplit=1)[-1]
            res = session.get(url)
            res.raise_for_status()
            with open(f_name, 'wb') as f:
                f.write(res.content)
            files.append(f_name)

    for f_name in files:
        parse_pdf(service, f_name, transfer_type, output_suffix)


parse_from_net('HUB', [
    'https://hub-shipping.com/wp-content/uploads/2025/04/HUB-Shipping_Drop-Off-Tariffs_ENG-16.04.2025-30.04.2025_upd-210425.pdf',
    'https://hub-shipping.com/wp-content/uploads/2025/04/HUB-Shipping_Drop-Off-Tariffs_ENG-01.04.2025-15.04.2025.pdf',
    'https://hub-shipping.com/wp-content/uploads/2025/04/HUB-Shipping_Drop-Off-Tariffs_ENG-16.03.2025-31.03.2025.pdf',
    'https://hub-shipping.com/wp-content/uploads/2025/02/HUB-Shipping_Drop-Off-Tariffs_ENG-16.02.2025-15.03.2025.pdf',
    'https://hub-shipping.com/wp-content/uploads/2024/12/HUB-Shipping_Drop-Off-Tariffs_ENG-16.01.2025-15.02.2025.pdf',
    'https://hub-shipping.com/wp-content/uploads/2024/12/HUB-Shipping_Drop-Off-Tariffs_ENG-16.12.2024-15.01.2025.pdf',
], 'TRAIN')
