#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created by bu on 2018-01-17
"""
from __future__ import unicode_literals
import time
import hashlib
import json as complex_json
import json
import urllib3
from datetime import datetime
from lib import CoinexPerpetualApi
from lib import request_client
import asyncio

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
        self.access_id = '92D0E39AF1634EA9B7D037EDDBECD261'      # replace
        self.secret_key = 'B7B13884C89347FE86E6E34A7C9FE7DD28A43B301CB70611'     # replace
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
            #self.set_authorization(params)
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

def get_pair_perpetual(pair):
    robot = CoinexPerpetualApi(access_id, secret_key)
    response = robot.get_market_state(pair)
    #var = complex_json.loads(response.data)
    return response

    request_client = RequestClient()
    params = {
        'market': pair
    }
    response = request_client.request(
            'GET',
            '{url}/perpetual/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sell(pair):
    return (float)(pair.get('data', {}).get('ticker').get('sell'))

def get_pair_buy(pair):
    return (float)(pair.get('data', {}).get('ticker').get('buy'))

def get_kline_perpetual(pair, time, limit):
    request_client = RequestClient()
    params = {
        'market': pair,
        'type': time,
        'limit': limit
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

ORDER_DIRECTION_SELL = 1
ORDER_DIRECTION_BUY = 2

def putMarketOrder(vp, side, leverage):
    robot = CoinexPerpetualApi(access_id, secret_key)
    robot.adjust_leverage(vp.pair, 1, leverage)
    robot.adjust_leverage(vp.pair, 2, leverage)
    result = robot.put_market_order(
        vp.pair,
        side,
        vp.contractAmount
    )
    print(json.dumps(result, indent=4))
    return result

REAL_TRADE = True    

access_id = '92D0E39AF1634EA9B7D037EDDBECD261'
secret_key = 'B7B13884C89347FE86E6E34A7C9FE7DD28A43B301CB70611'

def tradeDeals(robot, vp, lim, percent):
    time.sleep(1)
    
    try:
        marketDealsData = robot.get_market_deals(vp1.pair, limit = lim).get("data")
    
        sellsAmountDeals = 0
        buysAmountDeals = 0
        for x in marketDealsData:
            if(x.get("type") == "sell"):
                sellsAmountDeals += float(x.get('amount'))
            else:
                buysAmountDeals += float(x.get('amount'))
        
        sellsPercentDeals = sellsAmountDeals/(sellsAmountDeals + buysAmountDeals)    
        buysPercentDeals = buysAmountDeals/(sellsAmountDeals + buysAmountDeals)
        
        if(sellsPercentDeals > percent) and vp.isBought == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
            print("przebicie od dołu " + vp.pair + " buy")
            print(lim)
            print(percent)
            if(vp.isSold):
                print("zamknij " + vp.pair + " od shorta")
                print(get_pair_sell(get_pair_perpetual(vp.pair)))
                pb = get_pair_buy(get_pair_perpetual(vp.pair))
                print(pb)#praw
                earn = (pb - vp.priceSold)/vp.priceSold
                earn = -earn
                vp.totalEarn += earn
                print(earn)
                print(vp.totalEarn)
                
                if(REAL_TRADE == True):
                    result = putMarketOrder(vp, ORDER_DIRECTION_BUY, vp.leverage)
                
                vp.resetAfterClose()
                
            print(get_pair_sell(get_pair_perpetual(vp.pair)))#praw
            print(get_pair_buy(get_pair_perpetual(vp.pair)))
            print(datetime.now())
            
            if(REAL_TRADE == True):
                result = putMarketOrder(vp, ORDER_DIRECTION_BUY, vp.leverage)
            
            vp.setAfterBought()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
            
        elif(buysPercentDeals > percent) and vp.isSold == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
            print("przebicie od góry " + vp.pair + " sell")
            print(lim)
            print(percent)
            if(vp.isBought):
                print("zamknij " + vp.pair + " od longa")
                ps = get_pair_sell(get_pair_perpetual(vp.pair))
                print(ps)#praw
                print(get_pair_buy(get_pair_perpetual(vp.pair)))
                earn = (ps - vp.priceBought)/vp.priceBought
                vp.totalEarn += earn
                print(earn)
                print(vp.totalEarn)
                
                if(REAL_TRADE == True):
                    result = putMarketOrder(vp, ORDER_DIRECTION_SELL, vp.leverage)
                
                vp.resetAfterClose()
                
            print(get_pair_sell(get_pair_perpetual(vp.pair)))
            print(get_pair_buy(get_pair_perpetual(vp.pair)))# praw
            print(datetime.now())
            
            if(REAL_TRADE == True):
                result = putMarketOrder(vp, ORDER_DIRECTION_SELL, vp.leverage)
            
            vp.setAfterSold()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
                                            
    except:
        print(1)
        
class ValuePair():
    def __init__(self, _pair, _priceType, _time, _limit, _contractAmount, _isBought, _priceBought):
        self.kline = None
        self.time = _time
        self.limit = _limit
        self.pair = _pair
        self.priceType = _priceType
        self.cur = 0
        self.isBought = _isBought
        self.isSold = False
        self.lowestSold = 9999
        self.highestBuy = 0
        self.priceBought = _priceBought
        self.priceSold = 0
        self.totalEarn = 0 #0.050784281 -> 0.03; 0.040850027
        self.priceBoughtTP = 0
        self.priceSoldTP = 999999999999999999999999999999999999999
        self.bestOpenOrder = 0
        self.bestStopLoss = 0
        self.minuteBought = -1
        self.minuteSold = -1
        self.minuteStopLoss = -1
        self.tp1 = False
        self.tp2 = False
        self.tp3 = False
        self.leverage = 10
        self.contractAmount = _contractAmount
        self.takeProfitStop = 0
        self.orderSellID = -1
        self.orderBuyID = -1
        self.lowest = 99999999999999999999999999999
        self.highest = 0
        self.spreadBuy = 0
        self.spreadSell = 0
        self.sellsAmount = 0
        self.buysAmount = 0

    def resetAfterClose(self):
        self.isBought = False
        self.priceBoughtTP = 0
        self.minuteBought = -1
        self.isSold = False
        self.priceSoldTP = 999999999999999999999999999999999999999
        self.minuteSold = -1
        self.tp1 = False
        self.tp2 = False
        self.tp3 = False
    
    def setAfterSold(self):
        self.isSold = True
        self.lowestSold = get_pair_buy(get_pair_perpetual(self.pair))
        self.priceSold = self.lowestSold
        self.minuteSold = datetime.now().minute
        self.tp1 = False
        self.tp2 = False
        self.tp3 = False
        self.minuteStopLoss = -1
    
    def setAfterBought(self):
        self.isBought = True
        self.highestBuy = get_pair_sell(get_pair_perpetual(self.pair))
        self.priceBought = self.highestBuy
        self.minuteBought = datetime.now().minute
        self.tp1 = False
        self.tp2 = False
        self.tp3 = False
        self.minuteStopLoss = -1
        
if __name__ == '__main__':
    firstsma = 5
    secondsma = 10
    limit = 500
    
    vp1 = ValuePair('BTCUSD', 2, "1min", limit, 1500, True, 26927.3)
    vp2 = ValuePair('ETHUSD', 2, "1min", limit, 370, False, 0)

    robot = CoinexPerpetualApi(access_id, secret_key)

    
    print(time.time())

    while True:
        tradeDeals(robot, vp1, 20, 0.997)
        tradeDeals(robot, vp2, 20, 0.995)

        
            
        
        
        


