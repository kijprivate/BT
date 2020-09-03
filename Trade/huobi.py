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
        self.access_id = '2a5a1244-xa2b53ggfc-9f77da81-f7e49'      # replace
        self.secret_key = '0d6dc85d-7113521f-febe2f77-b2753'     # replace
        self.url = 'https://api.huobi.pro'
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
        params['AccessKeyId'] = self.access_id
        params['Timestamp'] = int(time.time()*1000)
        params['SignatureMethod'] = "HmacSHA256"
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

def get_pair_sell(pair):
    return (float)(get_pair(pair).get('data', {}).get('ticker').get('sell'))

def get_pair_buy(pair):
    return (float)(get_pair(pair).get('data', {}).get('ticker').get('buy'))

def get_pair_last(pair):
    return (float)(get_pair(pair).get('data', {}).get('ticker').get('last'))

def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/v1/common/symbols'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {})
    return var
    newarr = []
    for x in var:
        if("USDT" in x) or ("HOT" in x) or ("NRG" in x):
            continue
        newarr.append(x)

    return newarr

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


