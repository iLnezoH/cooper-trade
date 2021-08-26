import traceback
import requests
import json
import time

UN_code = []
with open('../data/UN-code.json', 'r', encoding='utf8')as fp:
    UN_code = json.load(fp)['results']


base_url = 'http://comtrade.un.org/api/get'


def save_data(year, data):
    t = time.time()
    with open('../data/' + str(int(t)) + '-' + str(year) + '-world-copper-2063-trade.json', 'w') as f:
        json.dump(data, f)


def get_cooper_trade_data(year):
    _year = ','.join(year)
    copper_trade_data = []
    to_iter_cods = UN_code[181:]
    failed_req = []
    try:
        # while True:
        for item in to_iter_cods:
            res = get_cooper_trade_data_by_reporter(
                code=item['id'], year=_year)
            if res is None:
                print('failed: ', item['id'])
                failed_req.append(item)
            else:
                print('success: ', item['id'])
                copper_trade_data.append(res)

        # to_iter_cods = failed_req
        # failed_req = []

            # if len(failed_req) == 0: break
    except Exception as e:
        print(traceback.print_exc())
        save_data(_year, copper_trade_data)
    else:
        save_data(_year, copper_trade_data)


def get_cooper_trade_data_by_reporter(code, year):
    params = {"type": "C", 'freq': 'A', 'px': 'HS', 'cc': 2603,
              'rg': 'all', 'p': 'all', 'ps': year, 'r': code}
    r = requests.get(base_url, params)
    if valide_response(r):
        return r.json()['dataset']
    return None


def valide_response(res):
    try:
        res = res.json()
        if res['validation']['status']['name'] == 'Ok':
            return True
    except Exception as e:
        print(traceback.print_exc())
        return False

    return False


def split_data():
    with open('../data/2017,2018,2020-world-copper-2063-trade.json', 'r') as f:
        data = json.load(f)
    data_2017 = [[log for log in logs if log['yr'] == 2017] for logs in data]
    data_2018 = [[log for log in logs if log['yr'] == 2018] for logs in data]
    data_2020 = [[log for log in logs if log['yr'] == 2020] for logs in data]

    with open('../data/2017-world-copper-2063-trade.json', 'w') as f:
        json.dump(data_2017, f)
    with open('../data/2018-world-copper-2063-trade.json', 'w') as f:
        json.dump(data_2018, f)
    with open('../data/2020-world-copper-2063-trade.json', 'w') as f:
        json.dump(data_2020, f)


def format_data(path):
    with open('../data/' + path, 'r') as f:
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
    with open('../data/format-' + path, 'w') as f:
        json.dump(data, f)


format_data('2016-world-copper-2063-trade.json')
format_data('2017-world-copper-2063-trade.json')
format_data('2018-world-copper-2063-trade.json')
format_data('2020-world-copper-2063-trade.json')

# split_data()

# get_cooper_trade_data(['2017','2018','2020'])
