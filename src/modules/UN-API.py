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


def _save_data(name, data, path=None):
    if path is None:
        path = os.path.join(data_dir, 'response/')
    with open(path + name + '.json', 'w') as f:
        json.dump(data, f)


def get_trade_data_by_reporter(code, year, params=None):
    """get trade data by reporter code

    Args:
        code: string, reporter code(s): 1,2
        year: string, report year(s): 2011,2012
        params?: dict, API params

    Returns: dict | None  API response data if success else None
    """

    _params = {
        "type": "C",
        'freq': 'A',
        'px': 'HS',
        'cc': 2603,
        'rg': '1,2',  # 1: Import, 2: export, all: all
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


def get_trade_data(year, codes, params=None):
    """get trade data by year and save to file
    Args:
        year: list, years
        params: dict, API params
    Returns: None
    """
    _year = ','.join(year)
    trade_data = []
    failed_req = []
    save_name = _year + \
        '(' + str(codes[0]['id']) + '-' + str(codes[-1]['id']) + ')'
    try:
        for i in range(0, len(codes), 5):
            code = ','.join([item['id'] for item in codes[i:i+5]])
            res = get_trade_data_by_reporter(code, _year, params)
            if res is None:
                print('failed: ', code, '. API request times: ' + str(i))
                failed_req.append(code)
            else:
                print('success: ', code, '. API request times: ' + str(i))
                trade_data.append(res)

    except Exception as e:
        print(traceback.print_exc())
        _save_data(save_name, trade_data)
    else:
        _save_data(save_name, trade_data)


def _merge_data(dir):
    merged_data = []
    for name in os.listdir(dir):
        if os.path.splitext(name)[1] == ".json":
            print('merging ' + name + "...")
            with open(os.path.join(dir, name), 'r') as f:
                # with open('../data/2017,2018,2020-world-copper-2063-trade.json', 'r') as f:
                data = json.load(f)
                merged_data += data
                print('appden data length: ' + str(len(data)))
                print('merged data length: ' + str(len(merged_data)))

    with open(os.path.join(dir, 'merged_data/merged_data.json'), 'w') as f:
        json.dump(merged_data, f)


def split_data_by_year(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    years = set([log['yr'] for logs in data for log in logs])
    print("data years: ", years)

    for year in years:
        year_data = [log for logs in data for log in logs if log['yr'] == year]

        with open(os.path.join(data_dir, 'year_origin_data', str(year) + '.json'), 'w') as f:
            json.dump(year_data, f)


def format_data(file, to):
    with open(file, 'r') as f:
        data = json.load(f)
        print('forming ' + file + '... data length: ' + str(len(data)))
        data = [{
            # **log,
            'Reporter Code': log['rtCode'],
            'Reporter': log['rtTitle'],
            'Partner Code': log['ptCode'],
            'Partner': log['ptTitle'],
            'Trade Flow': log['rgDesc'],
            'Trade Value (US$)': log['TradeValue'],
            'Trade Quantity': log['TradeQuantity'],
            'NetWeight': log['NetWeight'],
        } for log in data]
    with open(to, 'w') as f:
        json.dump(data, f)

###########################################


years = ['2011', '2012', '2013', '2014', '2015',
         '2016', '2017', '2018', '2019', '2020']

for year in years[5:]:
    format_data(os.path.join(data_dir, 'year_origin_data', year + '.json'),
                os.path.join(data_dir, 'format-' + year + '-world-copper-2063-trade.json'))

# _merge_data(os.path.join(data_dir, 'tmp'))
# split_data_by_year(os.path.join(data_dir, 'tmp/merged_data/merged_data.json'))
# split_data_by_year(os.path.join(data_dir, 'response/2011,2012,2013,2014,2015(4-975).json'))
# split_data_by_year(os.path.join(
#    data_dir, 'response/2016,2017,2018,2019,2020(4-975).json'))

# get_trade_data(['2011', '2012', '2013', '2014', '2015'], _get_UN_codes())
# get_trade_data(['2016', '2017', '2018', '2019', '2020'], _get_UN_codes())
