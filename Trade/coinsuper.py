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
        self.access_id = '46e0400e-83cb-4d4a-a381-ddac28d4e7f8'      # replace
        self.secret_key = '74c89359-6bde-4db0-9db8-0cadf11a2c63'     # replace
        self.url = 'https://api.coinsuper.info'
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
        params['accesskey'] = self.access_id
        params['secretkey'] = self.secret_key
        params['timestamp'] = int(time.time()*1000)
        self.headers['sign'] = self.get_sign(params, self.secret_key)

    def request(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method in ['GET', 'DELETE']:
            self.set_authorization(params)
            result = http.request(method, url, fields=params, headers=self.headers)
        else:
            if data:
                json.update(complex_json.loads(data))
            self.set_authorization(json)
            encoded_data = complex_json.dumps(json).encode('utf-8')
            print(encoded_data)
            print(self.headers)
            result = http.request(method, url, body=encoded_data, headers=self.headers)
        return result
    
def get_pair(pair):
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v3/ticker/bookTicker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_orders(pair, limit):
    request_client = RequestClient()
    params = {
        'symbol': pair,
        'limit': limit
    }
    response = request_client.request(
            'GET',
            '{url}/api/v3/depth'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_orders_asks(pair, limit):
    return get_orders(pair, limit).get('asks')

def get_orders_bids(pair, limit):
    return get_orders(pair, limit).get('bids')

def can_deposit(pair):
    return True

def can_withdraw(pair):
    return True

def withdraw_fee(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
    }
    response = request_client.request(
            'GET',
            '{url}/v1/common/asset/config'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return (float)(var.get('data', {}).get(pair).get('withdraw_tx_fee'))

#not set
def get_amount(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
    }
    response = request_client.request(
            'GET',
            '{url}/v1/balance/info'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    p = var.get('data', {}).get(pair)
    if p is None:
        return 0 
    else:
        return (float)(p.get('available'))

def get_pair_sell(pair):
    return (float)(get_pair(pair).get('askPrice'))

def get_pair_buy(pair):
    return (float)(get_pair(pair).get('bidPrice'))

#not set
def get_pair_last(pair):
    return (float)(get_pair(pair).get('last'))

def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'POST',
            '{url}/api/v1/market/symbolList'.format(url=request_client.url)
    )
    var = complex_json.loads(response.data)
    return var
    newarr = []
    for x in range(len(var)):
        if("USDT" in var[x].get("symbol")) or ("BNB" in var[x].get("symbol")) or ("EUR" in var[x].get("symbol")) or ("USD" in var[x].get("symbol")) or ("GRINBTC" in var[x].get("symbol")) or ("HOT" in var[x].get("symbol")) or ("NRG" in var[x].get("symbol")):
            continue
        newarr.append(var[x].get("symbol"))

    return newarr

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


