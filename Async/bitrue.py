from __future__ import unicode_literals
import time
import hashlib
import json as complex_json
import urllib3

from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)
http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1, read=2))

class RequestClient(object):
    __headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    }

    def __init__(self, headers={}):
        self.access_id = '672675a32fb5186250ec33a77be6bafc6c274cfc7c4950dd53e1d5fa3ccbab37'      # replace
        self.secret_key = 'e585b9b3594597550cf80e7dda8997de6c369da7913110228b21e0f22b93ecb1'     # replace
        self.url = 'https://www.bitrue.com'
        self.headers = self.__headers
        self.headers.update(headers)

    @staticmethod
    def get_sign(params, secret_key):
        sort_params = sorted(params)
        data = []
        for item in sort_params:
            data.append(item + '=' + str(params[item]))
        str_params = "{0}&secret_key={1}".format('&'.join(data), secret_key)
        token = hashlib.md5(str_params.encode('utf-8')).hexdigest().upper()
        return token

    def set_authorization(self, params):
        params['access_id'] = self.access_id
        params['tonce'] = int(time.time()*1000)
        self.headers['AUTHORIZATION'] = self.get_sign(params, self.secret_key)

    def request(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method in ['GET', 'DELETE']:
            self.set_authorization(params)
            result = http.request(method, url, fields=params, headers=self.headers)
            return result
        

def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/api/v1/exchangeInfo'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("symbols")
    newarr = []
    for x in var:
        symbol = x.get("symbol")
        if x.get('status') != 'TRADING':
            continue
        newarr.append(symbol)

    return newarr

def get_pair_sell(pair):
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/depth'.format(url=request_client.url),
            params=params
    )
    ask = complex_json.loads(response.data).get("asks")
    
    if(len(ask) > 0):
        return (float)(ask[0][0])
    else:
        return 0

def get_pair_buy(pair):
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/depth'.format(url=request_client.url),
            params=params
    )
    bid = complex_json.loads(response.data).get("bids")
    
    if(len(bid) > 0):
        return (float)(bid[0][0])
    else:
        return 999999999

def get_orders_asks(pair, limit):
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/depth'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("asks")
    return var

def get_orders_bids(pair, limit):
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/depth'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("bids")
    return var

def has_WD_def():
    return False

def can_deposit(pair):
    return False

def can_withdraw(pair):
    return False

def has_fee_def():
    return False

def withdraw_fee(pair):
    return 1

