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
        self.access_id = '5f8a5ac1-cfe3-4ee4-8e55-13015d05787a'      # replace
        self.secret_key = 'NDIzOTcxZjY4ZWJlYTA1MzBkODM4YzNjYmUzZTRjMzE2YjRmY2UxYjc3OGFiNWZjMDRlYzg1Zjk0Mzg1MjQ0ZQ=='     # replace
        self.url = 'https://www.cointiger.com/exchange/api'
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
            #self.set_authorization(params)
            result = http.request(method, url, fields=params, headers=self.headers)
            return result
            
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
            '{url}/v1/market/list'.format(url=request_client.url),
            params=params
    )
    var = []
    var = complex_json.loads(response.data).get('data', {})
    newarr = []
    for x in var:
        if("GRINBTC" in x) or ("HOT" in x) or ("NRG" in x):
            continue
        newarr.append(x)

    return newarr

def getSymbolsEndpoint():
    return "https://www.cointiger.com/exchange/api/public/market/detail"

def getSymbolResponse(response):
    resp = list(response.keys())
    return resp

def getPairPriceEndpoint(pair):
    pair = pair.lower()
    return '{url}/depth?api_key=5f8a5ac1-cfe3-4ee4-8e55-13015d05787a&symbol={p}&type=step0'.format(url='https://api.cointiger.com/exchange/trading/api/market', p = pair)

def getAsksResponse(response):
    if(response.get("data") == None):
        arr = [[0 for i in range(2)] for i in range(20)]
        for x in range(20):
            arr[x][0] = 0
            arr[x][1] = 0
        return arr
    #print(response.get("data"))
    return response.get("data").get("depth_data").get("tick").get("asks")

def getBidsResponse(response):
    if(response.get("data") == None):
        arr = [[0 for i in range(2)] for i in range(20)]
        for x in range(20):
            arr[x][0] = 0
            arr[x][1] = 0
        return arr
    #print(response.get("data"))
    return response.get("data").get("depth_data").get("tick").get("buys")

def get_pair(pair):
    request_client = RequestClient()
    params = {
        'market': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sell(pair):
    return (float)(get_pair(pair).get('data', {}).get('ticker').get('sell'))

def get_pair_buy(pair):
    return (float)(get_pair(pair).get('data', {}).get('ticker').get('buy'))

def get_orders(pair, limit):
    request_client = RequestClient()
    params = {
        'market': pair,
        'merge': 0,
        'limit': limit
    }
    response = request_client.request(
            'GET',
            '{url}/v1/market/depth'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var.get('data', {})

def get_orders_asks(pair, limit):
    return get_orders(pair, limit).get('asks')

def get_orders_bids(pair, limit):
    return get_orders(pair, limit).get('bids')

def has_WD_def():
    return False

def can_deposit(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'coin_type': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/common/asset/config'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return (bool)(var.get('data', {}).get(pair).get('can_deposit'))

def can_withdraw(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'coin_type': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/common/asset/config'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return (bool)(var.get('data', {}).get(pair).get('can_withdraw'))

def has_fee_def():
    return False

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
    try:
        var = complex_json.loads(response.data)
        return (float)(var.get('data', {}).get(pair).get('withdraw_tx_fee'))
    except:
        return 0


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""




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
    
def get_pair_last(pair):
    return (float)(get_pair(pair).get('data', {}).get('ticker').get('last'))
