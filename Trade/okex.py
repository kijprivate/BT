from __future__ import unicode_literals
import time
import hashlib
import hmac
import json as complex_json
import urllib3
import base64

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
        self.access_id = '18293940-b2d8-494b-80ec-136554706ca9'      # replace
        self.secret_key = '311FEEAE5C99C6590FD9ED03C8A45D63'     # replace
        self.url = 'https://www.okex.com/'
        self.headers = self.__headers
        self.headers.update(headers)

    @staticmethod
    def get_sign(params, secret_key):
        request_path = '/api/account/v3/currencies'
        body = ''
        message = str(params) + str.upper('GET') + request_path + str(body)
        mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d)
    
        str_params = params + 'GET' + '/users/self/verify/orders?before=2&limit=3' 

        print(str_params)
        signature = base64.b64encode(hmac.new(bytes(secret_key, encoding = 'utf-8'), msg=bytes(str_params, encoding = 'utf-8'), digestmod='sha256').digest())
        print((str)(signature))
        #token = hashlib.sha256(str_params.encode('utf-8')).hexdigest().upper()
       # t = base64.b64encode(signature)
       # print(t)
        return (str)(signature)

    def set_authorization(self, params):
        #params['tonce'] = get_server_time()
        test = get_server_time()
        self.headers['OK-ACCESS-KEY'] = self.access_id
        self.headers['OK-ACCESS-TIMESTAMP'] = test
        self.headers['OK-ACCESS-PASSPHRASE'] = 'passphrase'
        self.headers['OK-ACCESS-SIGN'] = self.get_sign(test, self.secret_key)

    def request(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method in ['GET', 'DELETE']:
            self.set_authorization(params)
            result = http.request(method, url, fields=params, headers=self.headers)
            return result
            
        else:
            if data:
                json.update(complex_json.loads(data))
            self.set_authorization(json)
            encoded_data = complex_json.dumps(json).encode('utf-8')
            result = http.request(method, url, body=encoded_data, headers=self.headers)
            return result
    def request2(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method in ['GET', 'DELETE']:
            result = http.request(method, url, fields=params, headers=self.headers)
            return result
        
def get_server_time():
    request_client = RequestClient()
    params = {}
    response = request_client.request2(
            'GET',
            '{url}api/general/v3/time'.format(url=request_client.url),
            params=params
    )
    print(complex_json.loads(response.data).get('epoch'))
    return complex_json.loads(response.data).get('epoch')

def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}api/account/v3/wallet'.format(url=request_client.url),
            params=params
    )
    return response.data
    var = []
    var = complex_json.loads(response.data).get('data', {})
    newarr = []
    for x in var:
        if("USDT" in x) or ("GRINBTC" in x) or ("HOT" in x) or ("NRG" in x):
            continue
        newarr.append(x)

    return newarr
    
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