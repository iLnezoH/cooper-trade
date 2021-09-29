import traceback
import requests
import json
import time
import os

current_dir = os.path.dirname(__file__)
data_dir = os.path.abspath(os.path.join(current_dir, "../data"))

base_url = 'http://comtrade.un.org/api/get'


def _get_UN_codes():
    """get countries' code of UN from file

    Returns: countries' codes
    """

    UN_code = []

    with open(os.path.join(data_dir, 'UN-code.json'), 'r', encoding='utf8')as fp:
        UN_code = json.load(fp)['results']

    return UN_code[1:]


def _save_data(year, data):
    t = time.time()
    with open('../data/response/' + str(int(t)) + '-' + str(year) + '-world-copper-2063-trade.json', 'w') as f:
        json.dump(data, f)


def get_trade_data_by_reporter(code, year, params=None):
    """get trade data by reporter code

    Args:
        code: number | string, reporter code
        year: number | string, report year
        params?: dict, API params

    Returns: dict | None  API response data if success else None
    """

    _params = {
        "type": "C",
        'freq': 'A',
        'px': 'HS',
        'cc': 2603,
        'rg': 'all',
        'p': 'all',
        'ps': year,
        'r': code
    }

    if params is not None:
        _params = dict(_params, **params)

    r = requests.get(base_url, _params)
    if _valide_response(r):
        return r.json()['dataset']
    return None


def _valide_response(res):
    """validate API response
    Args:
        res: dict, response data
    Returns: bool, is valide
    """
    try:
        res = res.json()
        if res['validation']['status']['name'] == 'Ok':
            return True
    except Exception as e:
        print(traceback.print_exc())
        return False

    return False


def get_trade_data(year, params=None):
    """get trade data by year and save to file
    Args:
        year: list, years
        params: dict, API params
    Returns: None
    """
    _year = ','.join(year)
    trade_data = []
    to_iter_cods = _get_UN_codes()
    failed_req = []
    try:
        for item in to_iter_cods:
            res = get_trade_data_by_reporter(item['id'], _year, params)
            if res is None:
                print('failed: ', item['id'])
                failed_req.append(item)
            else:
                print('success: ', item['id'])
                trade_data.append(res)

    except Exception as e:
        print(traceback.print_exc())
        _save_data(_year, trade_data)
    else:
        _save_data(_year, trade_data)


def _merge_data(dir):
    merged_data = []
    for name in os.listdir(dir):
        if os.path.splitext(name)[1] == ".json":
            with open(os.path.join(dir, name), 'r') as f:
                # with open('../data/2017,2018,2020-world-copper-2063-trade.json', 'r') as f:
                data = json.load(f)
                merged_data += data

    with open(os.path.join(dir, 'merged_data.json'), 'w') as f:
        json.dump(data, f)


def split_data_by_year(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    years = set([log['yr'] for logs in data for log in logs])

    for year in years:
        year_data = [[log for log in logs if log['yr'] == year]
                     for logs in data]
        with open(os.path.join(data_dir, 'year_origin_data', str(year) + '.json'), 'w') as f:
            json.dump(year_data, f)


def format_data(file, to):
    with open(file, 'r') as f:
        data = json.load(f)
        data = [{
            **log,
            'Reporter Code': log['rtCode'],
            'Reporter': log['rtTitle'],
            'Partner Code': log['ptCode'],
            'Partner': log['ptTitle'],
            'Trade Flow': log['rgDesc'],
            'Trade Value (US$)': log['TradeValue']
        } for logs in data for log in logs]
    with open(to, 'w') as f:
        json.dump(data, f)

###########################################


for year in ['2011', '2012', '2013', '2014', '2015']:
    format_data(os.path.join(data_dir, 'year_origin_data', year+'.json'),
                os.path.join(data_dir, year+'-world-copper-2063-trade.json'))
