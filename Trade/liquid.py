from __future__ import unicode_literals
import time
import hashlib
import json as complex_json
import coinex as coinex
import mxc as mxc
import kucoin as kucoin
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
        self.access_id = '1505421'      # replace
        self.secret_key = 'LAWIee2faHNciXRrqVAe6IvG5ogggrli+3IE5VM00wrxoacPzylPHMzV+SlPnMjkQD3xMY6rjiv5Xw0aKnYQcQ=='     # replace
        self.url = 'https://api.liquid.com'
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
    

def get_id(pair):
    request_client = RequestClient()
    params = {

    }
    response = request_client.request(
            'GET',
            '{url}/products'.format(url=request_client.url),
            params=params
    )
    
    var = (str)(complex_json.loads(response.data))
    while True:
        sAppend = find_between(var, '\'id\': \'', '\', \'symbol')
        var = var.split("symbol",1)[1]
        if(pair in sAppend):
            pid = find_between(sAppend, '', '\',')
            return pid

def can_deposit(pair):
    print("no def")
    return True
    
def can_withdraw(pair):
    print("no def")
    return True

def get_pair_sell(pair):
    pid = get_id(pair)
    request_client = RequestClient()
    params = {

    }
    response = request_client.request(
            'GET',
            '{url}/products/{i}'.format(url=request_client.url, i = pid),
            params=params
    )
    
    var = complex_json.loads(response.data)
    #print(pair)
    return (float)(var.get('market_ask'))

def get_pair_buy(pair):
    pid = get_id(pair)
    request_client = RequestClient()
    params = {

    }
    response = request_client.request(
            'GET',
            '{url}/products/{i}'.format(url=request_client.url, i = pid),
            params=params
    )
    
    var = complex_json.loads(response.data)
    return (float)(var.get('market_bid'))

def get_pair_last(pair):
    pid = get_id(pair)
    request_client = RequestClient()
    params = {

    }
    response = request_client.request(
            'GET',
            '{url}/products/{i}'.format(url=request_client.url, i = pid),
            params=params
    )
    
    var = complex_json.loads(response.data)
    return (float)(var.get('last_traded_price'))

def get_orders(pair, limit):
    pid = get_id(pair)
    request_client = RequestClient()
    params = {

    }
    response = request_client.request(
            'GET',
            '{url}/products/{i}/price_levels'.format(url=request_client.url, i = pid),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_orders_asks(pair, limit):
    return get_orders(pair, limit).get('sell_price_levels')

def get_orders_bids(pair, limit):
    return get_orders(pair, limit).get('buy_price_levels')

def get_pair_volume(pair):
    pid = get_id(pair)
    request_client = RequestClient()
    params = {

    }
    response = request_client.request(
            'GET',
            '{url}/products/{i}'.format(url=request_client.url, i = pid),
            params=params
    )
    
    var = complex_json.loads(response.data)
    return (float)(var.get('volume_24h'))

def withdraw_fee(pair):
    if(coinex.withdraw_fee(pair) != None):
        return coinex.withdraw_fee(pair)
    elif(mxc.withdraw_fee(pair) != None):
        return mxc.withdraw_fee(pair)
    else:
        return kucoin.withdraw_fee(pair)

def get_symbols():
    request_client = RequestClient()
    params = {

    }
    response = request_client.request(
            'GET',
            '{url}/products'.format(url=request_client.url),
            params=params
    )
    
    var = (str)(complex_json.loads(response.data))
    #return var
    newarr = []
    while True:
        sAppend = find_between(var, '\'currency_pair_code\': \'', '\', \'symbol')
        disabled = find_between(var, '\'disabled\': ', ', \'margin_enabled')
        #print(disabled)
        #print(sAppend)
        var = var.split(disabled,1)[1]
        d = (str)(disabled)
        a = str_to_bool(d)
        #print(a)
        if a == True or ("USD" in sAppend) or ("WIN" in sAppend) or ("MTC" in sAppend) or ("HOT" in sAppend) or ("TRTL" in sAppend) or ("QKC" in sAppend) or ("SNXETH" in sAppend) or ("XMR" in sAppend) or ("HOT" in sAppend) or ("FTT" in sAppend) or ("HYDRO" in sAppend) or ("ONG" in sAppend):
            continue
        newarr.append(sAppend)
        #print(sAppend)
        #print(d)
        if find_between(var, '\'currency_pair_code\': \'', '\', \'symbol') == '' or find_between(var, '\'disabled\': ', ', \'margin_enabled') == '':
            newarr2 = []
            for x in newarr:
                if(not(x in newarr2)):
                    newarr2.append(x)
                    
            return newarr2
        
   
def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError
         
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


