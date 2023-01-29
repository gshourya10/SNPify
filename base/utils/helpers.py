import os.path

import openpyxl as xl
import requests
import re
import logging

from logging.handlers import RotatingFileHandler
from ..api.utils.data_params import valid_data_fields


def parse_file(filename):
    data = []
    if len(re.findall('.xls', str(filename))) > 0:
        wb = xl.load_workbook(filename, read_only=True)
        ws = wb.worksheets[0]
        for row in ws.iter_rows():
            row_data = []
            for col in row:
                row_data.append(col.value)
            data.append(tuple(row_data))
        wb.close()
    elif len(re.findall('.csv', str(filename))) > 0:
        csv_data = filename.readlines()
        index = 0
        for i in range(len(csv_data)):
            row = csv_data[i]
            if i != len(csv_data) - 1:
                row = row[:-2]
            temp = str(row, 'UTF-8')
            row_data = temp.split(',')
            data.append(tuple(row_data))
            index += 1
    return get_formatted_data(data)


def get_formatted_data(data):
    if len(data) == 0:
        return []

    keys = data[0]
    formatted_data = []
    for row in range(1, len(data)):
        obj = {}
        for col in range(len(data[row])):
            if data[row][col]:
                if keys[col] == 'location':
                    obj[keys[col]] = int(data[row][col])
                else:
                    obj[keys[col]] = data[row][col]
        formatted_data.append(obj)

    return formatted_data


def download_file_from_url(url):
    response = requests.get(url)
    with open('temp.zip', 'wb') as f:
        f.write(response.content)


def dict_has_keys(obj: dict, required_keys: list):
    for key in required_keys:
        if key not in obj.keys():
            return False
    return True


def sanitize_data(tool, parsed_data):
    required_fields = valid_data_fields[tool]
    sanitized_data = []
    for obj in parsed_data:
        if dict_has_keys(obj, required_fields):
            sanitized_data.append(obj)

    return sanitized_data


def combine_data(data):
    new_data = {}
    for obj in data:
        if new_data.get(obj.get('uniprot_id')):
            new_data[obj.get('uniprot_id')].append({
                'wild_type': obj.get('wild_type'),
                'location': obj.get('location'),
                'mutant': obj.get('mutant')
            })
        else:
            new_data[obj.get('uniprot_id')] = [{
                'wild_type': obj.get('wild_type'),
                'location': obj.get('location'),
                'mutant': obj.get('mutant')
            }]

    combined_data = []
    for key, value in new_data.items():
        combined_data.append({
            'uniprot_id': key,
            'mutations': value
        })

    return combined_data


def log_error(tool_fn):
    def wrapper_function(*args, **kwargs):
        try:
            tool_fn(*args, **kwargs)
        except Exception as ex:
            HOME_DIR = os.path.expanduser('~')
            file_dir = os.path.join(HOME_DIR, 'SNP Results')
            log_filename = os.path.join(file_dir, 'error.log')
            formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s:%(message)s')
            handler = RotatingFileHandler(log_filename)
            handler.setFormatter(formatter)
            log = logging.getLogger('SNPAnalyses')
            log.addHandler(handler)
            log.setLevel(logging.DEBUG)
            log.error(f'Error at fetching results for {args[0]}')

    return wrapper_function


def retry_thrice(tool_fn):
    def wrapper_function(*args, **kwargs):
        trials = 3
        while trials:
            try:
                tool_fn(*args, **kwargs)
                return
            except Exception as ex:
                print(ex)
                trials -= 1

        raise Exception

    return wrapper_function
