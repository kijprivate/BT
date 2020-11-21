from __future__ import unicode_literals
import time
import hashlib
import json as complex_json
import urllib3
import re
import coinex as coinex

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
        self.access_id = 'mx0ivWxFZE2Bxg3y9y'      # replace
        self.secret_key = 'b54ab2e4f96f49069b36f9d4143ae6bb'     # replace
        self.url = 'https://www.mxc.co'
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
            '{url}/open/api/v2/market/symbols'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    s = (str)(var.get('data', {}))

    array = []
    while True:
        sAppend = find_between(s, 'symbol\': \'', '\', \'state')
        sAppend = sAppend.replace('_',"")
        s = s.split("state",1)[1]
        if("USD" in sAppend) or ("DOT" in sAppend) or ("HOT" in sAppend) or ("TRTL" in sAppend) or ("GRIN" in sAppend) or ("NRG" in sAppend) or ("QKC" in sAppend) or ("HOT" in sAppend):
            continue
        array.append(sAppend)
        if find_between(s, 'symbol\': \'', '\', \'state') == '':
            return array
        
def get_pair(pair):
    request_client = RequestClient()
    params = {
        'symbol': pair
    }
    response = request_client.request(
            'GET',
            '{url}/open/api/v2/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sell(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    s = (str)(get_pair(pair).get('data', {}))
    result = re.search('ask\': \'(.*)\', \'open', s)
    return (float)(result.group(1))

def get_pair_buy(pair):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    s = (str)(get_pair(pair).get('data', {}))
    result = re.search('bid\': \'(.*)\', \'ask', s)
    return (float)(result.group(1))

def get_orders(pair, limit):
    request_client = RequestClient()
    params = {
        'symbol': pair,
        'depth': limit
    }
    response = request_client.request(
            'GET',
            '{url}/open/api/v2/market/depth'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var.get('data', {})

def get_orders_asks(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    arr = [[0 for i in range(2)] for i in range(limit)]
    asks = get_orders(pair, limit).get('asks')
    for x in range(len(asks)):
        arr[x][0] = asks[x].get('price')
        arr[x][1] = asks[x].get('quantity')

    return arr

def get_orders_bids(pair, limit):
    end = pair[-3:]
    start = pair[:-3]
    pair = start + "_" + end
    arr = [[0 for i in range(2)] for i in range(limit)]
    asks = get_orders(pair, limit).get('bids')
    for x in range(len(asks)):
        arr[x][0] = asks[x].get('price')
        arr[x][1] = asks[x].get('quantity')

    return arr

def has_WD_def():
    return False

def can_deposit(pair):
    #print("no def")
    return True
    
def can_withdraw(pair):
    #print("no def")
    return True

def has_fee_def():
    return False

def withdraw_fee(pair):
    return coinex.withdraw_fee(pair)

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
    pair = start + "_" + end
    s = (str)(get_pair(pair).get('data', {}))
    result = re.search('last\': \'(.*)\', \'time', s)
    return (float)(result.group(1))


