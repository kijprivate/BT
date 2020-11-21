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
        self.access_id = 'a3ed5766b24245ecb4ee5478d837f3b70e78544b'      # replace
        self.secret_key = '8764c4dd79a280bf7038d379d4592861770ad011'     # replace
        self.url = 'https://api.bibox.com'
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
        self.headers['bibox-api-key'] = self.access_id
        self.headers['bibox-timestamp'] = int(time.time()*1000)
        self.headers['bibox-api-sign'] = self.get_sign(params, self.secret_key)

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

def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/v3/mdata/pairList'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("result")
    newarr = []
    for x in var:
        symbol = x.get("pair")
        if (int)(x.get('is_hide')) == 1 or 'USD' in symbol:
            continue
        symbol = symbol.replace('_',"")
        newarr.append(symbol)

    return newarr

def get_pair_sell(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v3/mdata/depth'.format(url=request_client.url),
            params=params
    )
    ask = complex_json.loads(response.data).get("result").get("asks")[0].get('price')
    return (float)(ask)

def get_pair_buy(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v3/mdata/depth'.format(url=request_client.url),
            params=params
    )
    bid = complex_json.loads(response.data).get("result").get("bids")[0].get('price')
    return (float)(bid)

def get_orders_asks(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'pair': pair,
        'size': limit
    }
    response = request_client.request(
            'GET',
            '{url}/v3/mdata/depth'.format(url=request_client.url),
            params=params
    )
    asks = complex_json.loads(response.data).get("result").get("asks")

    arr = [[0 for i in range(2)] for i in range(limit)]
    for x in range(len(asks)):
        arr[x][0] = (float)(asks[x].get('price'))
        arr[x][1] = (float)(asks[x].get('volume'))
    return arr

def get_orders_bids(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'pair': pair,
        'size': limit
    }
    response = request_client.request(
            'GET',
            '{url}/v3/mdata/depth'.format(url=request_client.url),
            params=params
    )
    bids = complex_json.loads(response.data).get("result").get("bids")

    arr = [[0 for i in range(2)] for i in range(limit)]
    for x in range(len(bids)):
        arr[x][0] = (float)(bids[x].get('price'))
        arr[x][1] = (float)(bids[x].get('volume'))
    return arr

def has_WD_def():
    return False

def can_deposit(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'coin_symbol': pair
    }
    response = request_client.request(
            'POST',
            '{url}/v3.1/transfer/coinConfig'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var
    return (bool)(var.get('data', {}).get(pair).get('can_deposit'))

def can_withdraw(pair):
    return False

def has_fee_def():
    return False

def withdraw_fee(pair):
    return 1

