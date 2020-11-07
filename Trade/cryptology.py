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
        self.access_id = 'cfxoWsU+RO2NzdbQF6FhrA=='      # replace
        self.secret_key = 'lOX/jIcKVhIaAcpHzhdK4ydqCqOyDOHzTzNcPhv3gWU='     # replace
        self.url = 'https://api.cryptology.com'
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
        #params['Access-Key'] = self.access_id
        #params['Nonce'] = int(time.time()*1000)
        self.headers['AUTHORIZATION'] = self.get_sign(params, self.secret_key)

    def request(self, method, url, params={}, data='', json={}):
        method = method.upper()
        if method in ['GET', 'DELETE']:
            self.set_authorization(params)
            try:
                result = http.request(method, url, fields=params, headers=self.headers)
                return result
            except Exception as inst:
                print(type(inst))
                print("coinex")
            
        else:
            if data:
                json.update(complex_json.loads(data))
            self.set_authorization(json)
            encoded_data = complex_json.dumps(json).encode('utf-8')
            try:
                result = http.request(method, url, body=encoded_data, headers=self.headers)
                return result
            except Exception as inst:
                print(type(inst))
                print("coinex")
        

def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/v1/public/get-trade-pairs'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data')
    newarr = []
    for x in range(len(var)):
        sAppend = var[x].get('trade_pair')
        if("EUR" in sAppend):
            continue
        sAppend = sAppend.replace('_',"")
        newarr.append(sAppend)

    return newarr

def get_pair_sell(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'trade_pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/public/get-order-book'.format(url=request_client.url),
            params=params
    )
    print(pair)
    ask = complex_json.loads(response.data).get("data").get("asks")
    if(len(ask) > 0):
        return (float)(ask[0][0])
    else:
        return 0

def get_pair_buy(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'trade_pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/public/get-order-book'.format(url=request_client.url),
            params=params
    )
    bid = complex_json.loads(response.data).get("data").get("bids")
    if(len(bid) > 0):
        return (float)(bid[0][0])
    else:
        return 999999999

def get_orders_asks(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'trade_pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/public/get-order-book'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("data").get("asks")
    return var

def get_orders_bids(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    request_client = RequestClient()
    params = {
        'trade_pair': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/public/get-order-book'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("data").get("bids")
    return var

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

