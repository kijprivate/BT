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
        self.access_id = '3c318ece9342579e73742efc2c6b3e010e7531dd71ad8a1796f9af0c91c58236'      # replace
        self.secret_key = '47e472f8018e5bc04e0da9914e56904a564973612a634c23005278cfb7af4382'     # replace
        self.url = 'https://api.bkex.com'
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
    
    
def get_pair(pair):
    request_client = RequestClient()
    params = {
        'pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/q/depth'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sell(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    s = get_pair(pair).get('data', {})
    #print(pair)
    return (float)(s.get('asks')[0].get('price'))

def get_pair_buy(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    s = get_pair(pair).get('data', {})
    return (float)(s.get('bids')[0].get('price'))

def get_pair_last(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/q/ticker/price'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    s = var.get('data', {})
    return (float)(s.get('price'))

def get_orders(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'symbol': pair,
        'depth': limit
    }
    response = request_client.request(
            'GET',
            '{url}/v2/q/depth'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var.get('data', {})

def get_orders_asks(pair, limit):
    return get_orders(pair, limit).get('ask')

def get_orders_bids(pair, limit):
    return get_orders(pair, limit).get('bid')

def can_deposit(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'coin_type': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v2/common/currencys'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {})
    s = (str)(var)
    sAppend = find_between(s, 'currency\': \'' + pair + '\'', 'supportTrade')
    sAppend = find_between(sAppend, 'supportDeposit\': ', ', \'')
    return (bool)(sAppend)
    
def can_withdraw(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'coin_type': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v2/common/currencys'.format(url=request_client.url, p = pair),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {})
    s = (str)(var)
    sAppend = find_between(s, 'currency\': \'' + pair + '\'', 'withdrawFee')
    sAppend = find_between(sAppend, 'supportWithdraw\': ', ', \'')
    return (bool)(sAppend)

def withdraw_fee(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
    }
    response = request_client.request(
            'GET',
            '{url}/v2/common/currencys'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {})
    s = (str)(var)
    sAppend = find_between(s, 'currency\': \'' + pair + '\'', 'currency')
    sAppend = find_between(sAppend, 'withdrawFee\': ', '},')
    return (float)(sAppend)

def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/v1/exchangeInfo'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {}).get('pairs')
    s = (str)(var)

    array = []
    while True:
        sAppend = find_between(s, 'pair\': \'', '\', \'supportTrade')
        sAppend = sAppend.replace('_',"")
        s = s.split(":",1)[1]
        if("USD" in sAppend) or ("GRINBTC" in sAppend) or ("HOT" in sAppend) or ("ONG" in sAppend) or ("ZEL" in sAppend) or ("DOCK" in sAppend) or ("TRTL" in sAppend) or ("NRG" in sAppend) or ("XTZ" in sAppend) or (len(array) > 0 and array[-1] == sAppend):
            continue
        array.append(sAppend)
        if find_between(s, 'pair\': \'', '\', \'supportTrade') == '':
            del array[-1]
            return array

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


