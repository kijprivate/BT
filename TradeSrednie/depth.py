#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created by bu on 2018-01-17
"""
from __future__ import unicode_literals
import time
import hashlib
import json as complex_json
import urllib3
from datetime import datetime

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
        self.access_id = 'D6A3235F492F442CB61AF55F9C3A74BE'      # replace
        self.secret_key = 'AB001E9381A8478BAD65A553EB3225F7129E5D0C9C8D873A'     # replace
        self.url = 'https://api.coinex.com'
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


def get_account_balance(currency):
    request_client = RequestClient()
    response = request_client.request('GET', '{url}/v1/balance/'.format(url=request_client.url))
    print(response.status)
    var = complex_json.loads(response.data)
    if(var.get('data', {}).get(currency) != None) :
        print(var.get('data', {}).get(currency).get('available'))
        return (float)(var.get('data', {}).get(currency).get('available'))
    else:
        return 0
    
def get_pair_min(pair):
    request_client = RequestClient()
    params = {
        'market': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/market/detail'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    print (var.get('data', {}).get('min_amount'))
    return (float)(var.get('data', {}).get('min_amount'))

def order_pending(market_type):
    request_client = RequestClient()
    params = {
        'market': market_type
    }
    response = request_client.request(
            'GET',
            '{url}/v1/order/pending'.format(url=request_client.url),
            params=params
    )
    print(response.content)


def order_finished(market_type, page, limit):
    request_client = RequestClient()
    params = {
        'market': market_type,
        'page': page,
        'limit': limit
    }
    response = request_client.request(
            'GET',
            '{url}/v1/order/finished'.format(url=request_client.url),
            params=params
    )
    print (response.status)
    
def get_pair_last(pair):
    return (float)(pair.get('data', {}).get('ticker').get('last'))
    
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

def get_pair_perpetual(pair):
    request_client = RequestClient()
    params = {
        'market': pair,
        'limit': 1000
    }
    response = request_client.request(
            'GET',
            '{url}/perpetual/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_transactions(pair):
    request_client = RequestClient()
    params = {
        'market': pair,
        'limit': 100
    }
    response = request_client.request(
            'GET',
            '{url}/perpetual/v1/market/deals'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sell(pair):
    return (float)(pair.get('data', {}).get('ticker').get('sell'))

def get_pair_buy(pair):
    return (float)(pair.get('data', {}).get('ticker').get('buy'))

def get_pair_sellAmount(pair):
    return (float)(pair.get('data', {}).get('ticker').get('sell_amount'))

def get_pair_buyAmount(pair):
    return (float)(pair.get('data', {}).get('ticker').get('buy_amount'))

def get_kline(pair):
    request_client = RequestClient()
    params = {
        'market': pair,
        'type': '15min',
        'limit': 220
    }
    response = request_client.request(
            'GET',
            '{url}/v1/market/kline'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_kline_perpetual(pair):
    request_client = RequestClient()
    params = {
        'market': pair,
        'type': '15min'
    }
    response = request_client.request(
            'GET',
            '{url}/perpetual/v1/market/kline'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_price(data, index, priceType):
    normalData = data.get('data', {})
    revData = list(reversed(normalData))
    return (float)(revData[index][priceType])

def get_price_old(data, index, priceType):
    return (float)(data.get('data', {})[index][priceType])
        

def put_limit(amount, price, side, pair):
    request_client = RequestClient()
    data = {
            "amount": amount,
            "price": price,
            "type": side,
            "market": pair
        }

    response = request_client.request(
            'POST',
            '{url}/v1/order/limit'.format(url=request_client.url),
            json=data,
    )
    print(response.data)
    return complex_json.loads(response.data)


def put_market(amount, side, pair):
    request_client = RequestClient()

    data = {
            "amount": amount,
            "type": side,
            "market": pair
        }

    response = request_client.request(
            'POST',
            '{url}/v1/order/market'.format(url=request_client.url),
            json=data,
    )
    print(response.data)

def put_limit_perpetual(amount, price, side, pair):
    request_client = RequestClient()
    data = {
            'market': pair,
            'effect_type': 1,
            'side': side,
            'amount': str(amount),
            'price': str(price)
        }

    response = request_client.request(
            'POST',
            '{url}/perpetual/v1/order/put_limit'.format(url=request_client.url),
            json=data,
    )
    print(response.data)
    return complex_json.loads(response.data)

def cancel_order(id, market):
    request_client = RequestClient()
    data = {
        "id": id,
        "market": market,
    }
    print(market)

    response = request_client.request(
            'DELETE',
            '{url}/v1/order/pending'.format(url=request_client.url),
            params=data,
    )
    return response.data    
    
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
        if("USD" in x) or not("BTC" in x[-3:]) or ('CHZBTC' in x) or ('CETBTC' in x):
            continue
        newarr.append(x)

    return newarr

def open_24h(pair):
    request_client = RequestClient()
    params = { "market": pair}
    response = request_client.request(
            'GET',
            '{url}/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {}).get('ticker', {}).get('open')
    return (float)(var)

def last_24h(pair):
    request_client = RequestClient()
    params = { "market": pair}
    response = request_client.request(
            'GET',
            '{url}/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {}).get('ticker', {}).get('last')
    return (float)(var)

def takeFirst(elem):
    return elem[0]

def count_24h_change(pairArray):
    newarr = []
    for x in pairArray:
        time.sleep(1)
        spread = (get_pair_sell(get_pair(x)) - get_pair_buy(get_pair(x)))/get_pair_sell(get_pair(x))
        if spread > 0.005:
            continue
        t = (last_24h(x) - open_24h(x))/last_24h(x), x
        newarr.append(t)
        newarr.sort(key=takeFirst)
        
    #newarr.reverse()
    return newarr

def count_24h_change2(pairArray):
    newarr = []
    for x in pairArray:
        time.sleep(1)
        t = (last_24h(x[1]) - open_24h(x[1]))/last_24h(x[1]), x[1]
        newarr.append(t)
        newarr.sort(key=takeFirst)
        
    #newarr.reverse()
    return newarr
        
def new_check(vp):
    time.sleep(1)
    #print((vp.priceBought - get_pair_sell(get_pair_perpetual(vp.pair)))/vp.priceBought)
    try:
        tral = get_transactions("BTCUSD").get("data")
        sells = 0
        buys = 0
        
        for x in range(len(tral)):
            if(tral[x].get("type") == "sell"):
                sells +=1
            else:
                buys +=1
        
        if sells > 60 and sells < 70 and (vp.isBought == False) and vp.isSold == False:
            print("buy")
            print(buys)
            print(get_pair_sell(get_pair_perpetual(vp.pair)))#praw
            print(get_pair_buy(get_pair_perpetual(vp.pair)))
            print(datetime.now())
            vp.isBought = True
            vp.amountBought = vp.btcAmount/get_pair_sell(get_pair_perpetual(vp.pair))
            vp.priceBought = get_pair_sell(get_pair_perpetual(vp.pair))
            #result = put_market(vp.amountBought,'buy', vp.pair)
            #print(result)
            print(vp.amountBought)
            vp.canCutLoses = True
        elif sells > 80 and (vp.isBought == True) and vp.isSold == False:
            print("sell zysk")
            print(buys)
            print(get_pair_sell(get_pair_perpetual(vp.pair)))
            print(get_pair_buy(get_pair_perpetual(vp.pair)))# praw
            print(datetime.now())
            vp.isBought = False
            #result = put_market(vp.amountBought,'sell', vp.pair)
            #print(result)
            vp.btcAmount = vp.amountBought * get_pair_buy(get_pair_perpetual(vp.pair))
            vp.canCutLoses = False
            print(vp.btcAmount)
            zysk = (get_pair_sell(get_pair_perpetual(vp.pair)) - vp.priceBought)/vp.priceBought
            print("zarobione %")
            print(zysk)
        elif vp.canCutLoses == True and (vp.isBought == True) and vp.isSold == False and (vp.priceBought - get_pair_sell(get_pair_perpetual(vp.pair)))/vp.priceBought > 0.01:
            print("cut loses sell zysk")
            vp.canCutLoses = False
            vp.isBought = False
            zysk = (get_pair_sell(get_pair_perpetual(vp.pair)) - vp.priceBought)/vp.priceBought
            print("zarobione %")
            print(zysk)
        elif buys > 60 and buys < 70 and (vp.isBought == False) and vp.isSold == False:
            print("sell")
            print(sells)
            print(get_pair_sell(get_pair_perpetual(vp.pair)))#praw
            print(get_pair_buy(get_pair_perpetual(vp.pair)))
            print(datetime.now())
            vp.isSold = True
            vp.amountBought = vp.btcAmount/get_pair_buy(get_pair_perpetual(vp.pair))
            print(vp.amountBought)
            vp.priceSold = get_pair_buy(get_pair_perpetual(vp.pair))
            print(vp.priceSold)
            vp.canCutLoses = True
        elif buys > 80 and (vp.isBought == False) and vp.isSold == True:
            print("buy zysk")
            print(sells)
            print(get_pair_sell(get_pair_perpetual(vp.pair)))
            print(get_pair_buy(get_pair_perpetual(vp.pair)))# praw
            print(datetime.now())
            vp.isSold = False
            vp.btcAmount = vp.amountBought * get_pair_sell(get_pair_perpetual(vp.pair))
            print(vp.btcAmount)
            vp.canCutLoses = False
            zysk = (vp.priceSold - get_pair_buy(get_pair_perpetual(vp.pair)))/vp.priceSold
            print("zarobione %")
            print(zysk)
        elif vp.canCutLoses == True  and (vp.isBought == False) and vp.isSold == True and (get_pair_buy(get_pair_perpetual(vp.pair)) - vp.priceSold)/vp.priceSold > 0.01:
            print("cut loses buy zysk")
            vp.canCutLoses = False
            vp.isSold = False
            zysk = (vp.priceSold - get_pair_buy(get_pair_perpetual(vp.pair)))/vp.priceSold
            print("zarobione %")
            print(zysk)
        
    except:
        print("a=1")

    
class ValuePair():
    def __init__(self, _pair, _firstsma, _secondsma, _priceType):
        self.kline = get_kline(_pair)
        self.pair = _pair
        self.firstsma = _firstsma
        self.secondsma = _secondsma
        self.priceType = _priceType
        self.minuteBought = 3
        self.checkedFirstCandy = False
        self.cur = 0
        self.prev = count_sma(1, _firstsma, self.kline, _priceType) - count_sma(1, _secondsma,self.kline, _priceType)
        self.isBought = False
        self.isSold = False
        self.btcAmount = 0.98*get_account_balance('BTC')
        self.amountBought = 0

class BestPair():
    def __init__(self, best):
        self.cur = best
        self.btcAmount = 1
        self.amountBought = self.btcAmount/get_pair_sell(get_pair_perpetual(best))
        self.isBought = False
        self.isSold = False
        self.pair = "BTCUSD"
        self.priceBought = 1
        self.priceSold = 0
        self.canCutLoses = False
        
if __name__ == '__main__':
    #print(get_pair_perpetual("BTCUSD"))
    vp1 = BestPair("BTCUSD")
    #print(get_transactions("BTCUSD"))
    while True:
        
        new_check(vp1)
        #new_check(vp2)
        #new_check(vp3)
        #new_check(vp4)
        #new_check(vp5)
        #new_check(vp6)
        #new_check(vp7)
        #new_check(vp8)
        
        #time.sleep(10)
        #sor2 = count_24h_change2(sor)
        #if(sor2[0][1] != bp.cur) and (sor2[1][0] - sor2[0][0] > 0.01):
        #    print(sor2)
        #    print('sell')
        #    print(bp.cur)
        #    bp.btcAmount = get_pair_buy(get_pair(bp.cur))*bp.amountBought
        #    print(bp.btcAmount)
        #    bp.cur = sor2[0][1]
        #    print('buy')
        #    print(bp.cur)
        #    print(datetime.now())
        #    bp.amountBought = bp.btcAmount/get_pair_sell(get_pair(bp.cur))
            
        
        
        


