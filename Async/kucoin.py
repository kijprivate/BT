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
        self.access_id = '5e1e20211e35490009223642'      # replace
        self.secret_key = 'b0f23012-8123-40f5-9f5e-59db4df7c8f1'     # replace
        self.url = 'https://api.kucoin.com'
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
        params['KC-API-KEY'] = self.access_id
        params['KC-API-TIMESTAMP'] = int(time.time()*1000)
        #self.headers['KC-API-SIGN'] = self.get_sign(params, self.secret_key)

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
            '{url}/api/v1/symbols'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    s = (str)(var.get('data', {}))
    array = []
    while True:
        sAppend = find_between(s, 'symbol\': \'', '\', \'name')
        sAppend = sAppend.replace('-',"")
        s = s.split(":",1)[1]
        if("USD" in sAppend) or ("DGTX" in sAppend) or ("COTI" in sAppend) or ("AMBBTC" in sAppend) or ("QKC" in sAppend) or ("GRINBTC" in sAppend) or ("HOT" in sAppend) or ("TRTL" in sAppend) or ("NRG" in sAppend) or (sAppend in array):
            continue
        
        array.append(sAppend)
        if find_between(s, 'symbol\': \'', '\', \'name') == '':
            del array[-1]
            return array

def getSymbolsEndpoint():
    return "https://api.kucoin.com/api/v1/symbols"

def getSymbolResponse(response):
    newArr = []
    for pair in response.get("data"):
        if pair.get("enableTrading") == False or ("USD" in pair.get("symbol")):
            continue
        toAdd = pair.get("symbol")
        toAdd = toAdd.replace('-',"")
        newArr.append(toAdd)
    return newArr

def getPairPriceEndpoint(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "-" + end
    return '{url}/api/v1/market/orderbook/level2_20?symbol={p}'.format(url='https://api.kucoin.com', p = pair)

def getAsksResponse(response):
    return response.get("data").get("asks")

def getBidsResponse(response):
    return response.get("data").get("bids")

def get_pair(pair):
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/market/orderbook/level1'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sell(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "-" + end

    s = (str)(get_pair(pair))
    result = re.search('bestAsk\': \'(.*)\', \'bestAskSize', s)
    return (float)(result.group(1))

def get_pair_buy(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "-" + end

    s = (str)(get_pair(pair).get('data', {}))
    result = re.search('bestBid\': \'(.*)\', \'bestBidSize', s)
    return (float)(result.group(1))

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
            '{url}/api/v1/market/orderbook/level2_20'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var.get('data', {})

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
        'coin_type': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/currencies/{p}'.format(url=request_client.url, p = pair),
            params=params
    )
    var = complex_json.loads(response.data)
    return (bool)(var.get('data', {}).get('isDepositEnabled'))
    
def can_withdraw(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'coin_type': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/currencies/{p}'.format(url=request_client.url, p = pair),
            params=params
    )
    var = complex_json.loads(response.data)
    return (bool)(var.get('data', {}).get('isWithdrawEnabled'))

def has_fee_def():
    return True

def withdraw_fee(pair):
    request_client = RequestClient()
    pair = pair[:-3]
    params = {
        'coin_type': pair
    }
    response = request_client.request(
            'GET',
            '{url}/api/v1/currencies/{p}'.format(url=request_client.url, p = pair),
            params=params
    )
    var = complex_json.loads(response.data)
    return (float)(var.get('data', {}).get('withdrawalMinFee'))

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""





def get_pair_last(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "-" + end

    s = (str)(get_pair(pair).get('data', {}))
    result = re.search('price\': \'(.*)\', \'size', s)
    return (float)(result.group(1))
