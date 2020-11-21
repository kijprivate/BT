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
        self.access_id = '18f29c48d3e8dee07b10c3a54b431993'      # replace
        self.secret_key = '648641d9fdb98cc64a3f351befbf6ae325c5fd232445562cfe4838abf984b757'     # replace
        self.url = 'https://global-openapi.bithumb.pro/openapi/v1'
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
            '{url}/spot/config'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("data").get("spotConfig")

    newarr = []
    for x in range(len(var)):
        if ("BNB" in var[x].get("symbol")) or ("EUR" in var[x].get("symbol")) or ("USD" in var[x].get("symbol")) or ("GRINBTC" in var[x].get("symbol")) or ("HOT" in var[x].get("symbol")) or ("NRG" in var[x].get("symbol")):
            continue
        p = var[x].get("symbol")
        p = p.replace('-',"")
        newarr.append(p)

    return newarr

def getSymbolsEndpoint():
    return 'https://global-openapi.bithumb.pro/openapi/v1/spot/config'

def getSymbolResponse(response):
    newArr = []
    for pair in response.get("data").get("spotConfig"):
        if ("USD" in pair.get("symbol")):
            continue
        toAdd = pair.get("symbol")
        toAdd = toAdd.replace('-',"")
        newArr.append(toAdd)
    return newArr

def getPairPriceEndpoint(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "-" + end
    return '{url}/spot/orderBook?symbol={p}'.format(url='https://global-openapi.bithumb.pro/openapi/v1', p = pair)

def getAsksResponse(response):
    return response.get("data").get("s")

def getBidsResponse(response):
    return response.get("data").get("b")

def get_pair_sell(pair):
    return (float)(get_orders_asks(pair, 10)[0][0])

def get_pair_buy(pair):
    return (float)(get_orders_bids(pair, 10)[0][0])

def get_orders(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "-" + end
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/spot/orderBook'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var.get('data', {})

def get_orders_asks(pair, limit):
    orders = get_orders(pair, limit)
    if(orders != None):
        return orders.get('s')
    return None

def get_orders_bids(pair, limit):
    orders = get_orders(pair, limit)
    if(orders != None):
        return orders.get('b')
    return None

def has_WD_def():
    return True

def can_deposit(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/spot/config'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("data").get("coinConfig")
    for x in range(len(var)):
        if var[x].get("name") == pair:
            if (int)(var[x].get("depositStatus")) == 0:
                return False
            else:
                return True

def can_withdraw(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/spot/config'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("data").get("coinConfig")
    for x in range(len(var)):
        if var[x].get("name") == pair:
            if (int)(var[x].get("withdrawStatus")) == 0:
                return False
            else:
                return True

def has_fee_def():
    return True

def withdraw_fee(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/spot/config'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get("data").get("coinConfig")
    for x in range(len(var)):
        if var[x].get("name") == pair:
            return (float)(var[x].get("withdrawFee"))





def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


