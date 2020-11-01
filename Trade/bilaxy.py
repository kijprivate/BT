from __future__ import unicode_literals
import time
import hashlib
import json as complex_json
import urllib3
import re

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
        self.access_id = 'a8abdce19b26d4608837311c869bbdf08'      # replace
        self.secret_key = '0d8c31a497c69b282395e590faf504b4'     # replace
        self.url = 'https://newapi.bilaxy.com'
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
        params['api_key'] = self.access_id
        params['req_time'] = int(time.time()*1000)
        #self.headers['AUTHORIZATION'] = self.get_sign(params, self.secret_key)

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
            result = http.request(method, url, body=encoded_data, headers=self.headers)
        return result
    
def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/v1/pairs'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    s = (str)(var)

    array = []
    while True:
        sAppend = find_between(s, '\'', '\': {')
        sAppend = sAppend.replace('_',"")
        s = s.split("closed\': ",1)[1]
        if("USD" in sAppend) or ("HOT" in sAppend) or ("ONG" in sAppend) or ("GRINBTC" in sAppend) or ("COMP" in sAppend) or ("HOT" in sAppend):
            continue
        array.append(sAppend)
        if find_between(s, '\'', '\': {') == '':
            return array
        
def get_pair(pair):
    request_client = RequestClient()
    params = {
        'pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/orderbook'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sell(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    s = get_pair(pair)
    if len(s.get('asks')) > 0:
        return (float)(s.get('asks')[0][0])
    else:
        return 9999999999999

def get_pair_buy(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    s = get_pair(pair)
    if len(s.get('bids')) > 0:
        return (float)(s.get('bids')[0][0])
    else:
        return 0

def get_orders(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/orderbook'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_orders_asks(pair, limit):
    return get_orders(pair, limit).get('asks')

def get_orders_bids(pair, limit):
    return get_orders(pair, limit).get('bids')

def has_WD_def():
    return True

def can_deposit(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'currency': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/currencies'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return (bool)(var.get(pair).get('deposit_enabled'))

def can_withdraw(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'currency': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/currencies'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return (bool)(var.get(pair).get('withdraw_enabled'))

def has_fee_def():
    return True

def withdraw_fee(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'currency': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/currencies'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return (float)(var.get(pair).get('fixed_withdraw_fee'))



def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


