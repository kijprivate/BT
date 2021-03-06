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
        contractAmount
    )
    print(json.dumps(result, indent=4))
    return result

def handleResultAfterClose(vp, result):
    if(result.get("code") == 0):
        vp.resetAfterClose()
    else:
        print("FAIL")

def handleResultAfterSold(vp, result):
    if(result.get("code") == 0):
        vp.setAfterSold()
    else:
        print("FAIL")
        
def handleResultAfterBought(vp, result):
    if(result.get("code") == 0):
        vp.setAfterBought()
    else:
        print("FAIL")

REAL_TRADE = False     
openOrder = 10
stopLoss = 8
takeProfit1 = 10
takeProfitStop1 = 5
takeProfit2 = 25
takeProfitStop2 = 10
takeProfit3 = 50
takeProfitStop3 = 20
takeProfitNOW = 100
contractAmount = 100
access_id = '92D0E39AF1634EA9B7D037EDDBECD261'
secret_key = 'B7B13884C89347FE86E6E34A7C9FE7DD28A43B301CB70611'

def new_check2(vp):
    time.sleep(1)
    
    try:
        robot = CoinexPerpetualApi(access_id, secret_key)
        vp.kline = robot.kline(vp.pair, vp.time, vp.limit)
        
        sr1 = get_price(vp.kline, 0, vp.priceType)
        sr2 = get_price(vp.kline, 0, 1)
        last1 = get_price(vp.kline, 1, vp.priceType)
        #last2 = get_price(vp.kline, 1, 1)
        openOrder = 0.00125*sr1
        stopLoss = 0.00125*sr1
        takeProfit1 = 0.002*sr1
        takeProfitStop1 = 0.001*sr1
        takeProfit2 = 0.004*sr1
        takeProfitStop2 = 0.002*sr1
        takeProfit3 = 0.007*sr1
        takeProfitStop3 = 0.0035*sr1
        oc1 = abs(sr1-sr2)/sr2

        #oc2 = abs(last1-last2)
        diff = (last1 - sr1)#/sr
        spread = abs(get_pair_buy(get_pair_perpetual(vp.pair)) - get_pair_sell(get_pair_perpetual(vp.pair)))
        
        #stoploss
        if(vp.isBought) and spread < 4 and vp.minuteBought != datetime.now().minute:
            cur = get_price(vp.kline, 0, vp.priceType)
            diff2 = (cur - vp.priceBought)#/vp.priceBought
            if(diff2 > takeProfit3):
                vp.priceBoughtTP = cur
                vp.tp3 = True
            elif(diff2 > takeProfit2):
                vp.priceBoughtTP = cur
                vp.tp2 = True
            elif(diff2 > takeProfit1):
                vp.priceBoughtTP = cur
                vp.tp1 = True
                
            if(vp.priceBoughtTP != 0) and vp.tp3 == True:
                diff3 = (cur - vp.priceBoughtTP)#/vp.priceBoughtTP
                if(diff3 < -takeProfitStop3):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("TP " + vp.pair + " od longa")
                    print(datetime.now())
                    ps = get_pair_sell(get_pair_perpetual(vp.pair))
                    print(ps)#praw
                    print(get_pair_buy(get_pair_perpetual(vp.pair)))
                    earn = (ps - vp.priceBought)/vp.priceBought
                    vp.totalEarn += earn
                    print(earn)
                    print(vp.totalEarn)
                    
                    if(REAL_TRADE == True):
                        result = putMarketOrder(vp, ORDER_DIRECTION_SELL, vp.leverage)
                        handleResultAfterClose(vp, result)
                    else:
                        vp.resetAfterClose()
                    
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            elif(vp.priceBoughtTP != 0) and vp.tp2 == True:
                diff3 = (cur - vp.priceBoughtTP)#/vp.priceBoughtTP
                if(diff3 < -takeProfitStop2):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("TP " + vp.pair + " od longa")
                    print(datetime.now())
                    ps = get_pair_sell(get_pair_perpetual(vp.pair))
                    print(ps)#praw
                    print(get_pair_buy(get_pair_perpetual(vp.pair)))
                    earn = (ps - vp.priceBought)/vp.priceBought
                    vp.totalEarn += earn
                    print(earn)
                    print(vp.totalEarn)
                    
                    if(REAL_TRADE == True):
                        result = putMarketOrder(vp, ORDER_DIRECTION_SELL, vp.leverage)
                        handleResultAfterClose(vp, result)
                    else:
                        vp.resetAfterClose()
                    
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            elif(vp.priceBoughtTP != 0) and vp.tp1 == True:
                diff3 = (cur - vp.priceBoughtTP)#/vp.priceBoughtTP
                if(diff3 < -takeProfitStop1):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("TP " + vp.pair + " od longa")
                    print(datetime.now())
                    ps = get_pair_sell(get_pair_perpetual(vp.pair))
                    print(ps)#praw
                    print(get_pair_buy(get_pair_perpetual(vp.pair)))
                    earn = (ps - vp.priceBought)/vp.priceBought
                    vp.totalEarn += earn
                    print(earn)
                    print(vp.totalEarn)
                    
                    if(REAL_TRADE == True):
                        result = putMarketOrder(vp, ORDER_DIRECTION_SELL, vp.leverage)
                        handleResultAfterClose(vp, result)
                    else:
                        vp.resetAfterClose()
                    
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                
            if(diff2 < -stopLoss):
                print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                print("stop loss " + vp.pair + " od longa")
                print(datetime.now())
                ps = get_pair_sell(get_pair_perpetual(vp.pair))
                print(ps)#praw
                print(get_pair_buy(get_pair_perpetual(vp.pair)))
                earn = (ps - vp.priceBought)/vp.priceBought
                vp.totalEarn += earn
                print(earn)
                print(vp.totalEarn)
                
                if(REAL_TRADE == True):
                    result = putMarketOrder(vp, ORDER_DIRECTION_SELL, vp.leverage)
                    handleResultAfterClose(vp, result)
                else:
                    vp.resetAfterClose()
                
                print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                
        if(vp.isSold) and spread < 4 and vp.minuteSold != datetime.now().minute:
            cur = get_price(vp.kline, 0, vp.priceType)
            diff2 = (cur - vp.priceSold)#/vp.priceSold
            if(diff2 < -takeProfit3):
                vp.priceSoldTP = cur
                vp.tp3 = True
            elif(diff2 < -takeProfit2):
                vp.priceSoldTP = cur
                vp.tp2 = True
            elif(diff2 < -takeProfit1):
                vp.priceSoldTP = cur
                vp.tp1 = True
                
            if(vp.priceSoldTP != 0) and vp.tp3 == True:
                diff3 = (cur - vp.priceSoldTP)#/vp.priceSoldTP
                if(diff3 > takeProfitStop3):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("TP " + vp.pair + " od shorta")
                    print(datetime.now())
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
                        handleResultAfterClose(vp, result)
                    else:
                        vp.resetAfterClose()
                    
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            if(vp.priceSoldTP != 0) and vp.tp2 == True:
                diff3 = (cur - vp.priceSoldTP)#/vp.priceSoldTP
                if(diff3 > takeProfitStop2):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("TP " + vp.pair + " od shorta")
                    print(datetime.now())
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
                        handleResultAfterClose(vp, result)
                    else:
                        vp.resetAfterClose()
                    
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            if(vp.priceSoldTP != 0) and vp.tp1 == True:
                diff3 = (cur - vp.priceSoldTP)#/vp.priceSoldTP
                if(diff3 > takeProfitStop1):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("TP " + vp.pair + " od shorta")
                    print(datetime.now())
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
                        handleResultAfterClose(vp, result)
                    else:
                        vp.resetAfterClose()
                    
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    
            if(diff2 > stopLoss):
                print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                print("stop loss " + vp.pair + " od shorta")
                print(datetime.now())
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
                    handleResultAfterClose(vp, result)
                else:
                    vp.resetAfterClose()
                
                print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        
        if oc1 > 0.0015: #(datetime.now().second < 3) and 
            if(diff < -openOrder) and vp.isBought == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
                print("przebicie od dołu " + vp.pair + " buy")
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
                        handleResultAfterClose(vp, result)
                    else:
                        vp.resetAfterClose()
                    
                print(get_pair_sell(get_pair_perpetual(vp.pair)))#praw
                print(get_pair_buy(get_pair_perpetual(vp.pair)))
                print(datetime.now())
                
                if(REAL_TRADE == True):
                    result = putMarketOrder(vp, ORDER_DIRECTION_BUY, vp.leverage)
                    handleResultAfterBought(vp, result)
                else:
                    vp.setAfterBought()
                
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
                
            elif(diff > openOrder) and vp.isSold == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
                print("przebicie od góry " + vp.pair + " sell")
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
                        handleResultAfterClose(vp, result) 
                    else:
                        vp.resetAfterClose()
                    
                print(get_pair_sell(get_pair_perpetual(vp.pair)))
                print(get_pair_buy(get_pair_perpetual(vp.pair)))# praw
                print(datetime.now())
                
                if(REAL_TRADE == True):
                    result = putMarketOrder(vp, ORDER_DIRECTION_SELL, vp.leverage)
                    handleResultAfterClose(vp, result)
                else:
                    vp.setAfterSold()
                
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
        
    except:
        print(1)

def checkAll(vp, candleRange, debug):
    #time.sleep(1)
    #vp.kline = get_kline_perpetual(vp.pair)
    vp.totalEarn = 0
    for x in range(candleRange):
        sr = get_price_old(vp.kline, x, vp.priceType)
        last = get_price_old(vp.kline, x-1, vp.priceType)
    
        diff = (last - sr)#/sr
            
        if(diff < -vp.openOrder) and vp.isBought == False: #and vp.isSold == False:
            if(debug == True):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
            if(vp.isSold):
                pb = get_price_old(vp.kline, x, vp.priceType)
                earn = (pb - vp.priceSold)/vp.priceSold
                earn = -earn
                vp.totalEarn += earn
                vp.isSold = False
                if(debug == True):
                    print("zamknij " + vp.pair + " od shorta")
                    print(pb)#praw
                    print(vp.priceSold)
                    print(earn)

            currTime = time.gmtime(get_price_old(vp1.kline, x, 0))
            if(debug == True):
                print("przebicie od dołu " + vp.pair + " buy")
                print(get_price_old(vp.kline, x, vp.priceType))#praw
                print((str)(currTime[2]) + "." + (str)(currTime[1]) + "." + (str)(currTime[0]) + " " + (str)(currTime[3] + 1) + ":" + (str)(currTime[4]))
            vp.isBought = True
            vp.highestBuy = get_price_old(vp.kline, x, vp.priceType)
            vp.priceBought = vp.highestBuy
            if(debug == True):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")

        elif(diff > vp.openOrder) and vp.isSold == False: #and vp.isBought == False:
            if(debug == True):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
            if(vp.isBought):
                ps = get_price_old(vp.kline, x, vp.priceType)
                earn = (ps - vp.priceBought)/vp.priceBought
                vp.totalEarn += earn
                vp.isBought = False 
                
                if(debug == True):
                    print("zamknij " + vp.pair + " od longa")
                    print(ps)#praw
                    print(vp.priceBought)
                    print(earn)
                
            
            currTime = time.gmtime(get_price_old(vp1.kline, x, 0))
            if(debug == True):
                print("przebicie od góry " + vp.pair + " sell")
                print(get_price_old(vp.kline, x, vp.priceType))
                print((str)(currTime[2]) + "." + (str)(currTime[1]) + "." + (str)(currTime[0]) + " " + (str)(currTime[3] + 1) + ":" + (str)(currTime[4]))
            vp.isSold = True
            vp.lowestSold = get_price_old(vp.kline, x, vp.priceType)
            vp.priceSold = vp.lowestSold
            if(debug == True):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
         
        curek = get_price_old(vp.kline, x, vp.priceType)
        if(vp.isBought) and curek > vp.highestBuy:
            vp.highestBuy = curek
        elif(vp.isSold) and curek < vp.lowestSold:
            vp.lowestSold = curek
            
        #stoploss
        if(vp.isBought):
            cur = get_price_old(vp.kline, x, vp.priceType)
            diff2 = (cur - vp.priceBought)#/vp.priceBought
            if(diff2 < -vp.stopLoss):
                currTime = time.gmtime(get_price_old(vp1.kline, x, 0))
                ps = get_price_old(vp.kline, x, vp.priceType)
                earn = (ps - vp.priceBought)/vp.priceBought
                vp.totalEarn += earn
                vp.isBought = False
                
                if(debug == True):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("stop loss " + vp.pair + " od longa")
                    print((str)(currTime[2]) + "." + (str)(currTime[1]) + "." + (str)(currTime[0]) + " " + (str)(currTime[3] + 1) + ":" + (str)(currTime[4]))
                    print(ps)#praw
                    print(earn)
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                
            if(diff2 > takeProfit1):
                vp.priceBoughtTP = cur
            if(vp.priceBoughtTP != 0):
                diff3 = (cur - vp.priceBoughtTP)#/vp.priceBoughtTP
                if(diff3 < -takeProfitStop1):
                    currTime = time.gmtime(get_price_old(vp1.kline, x, 0))
                    ps = get_price_old(vp.kline, x, vp.priceType)
                    earn = (ps - vp.priceBought)/vp.priceBought
                    vp.totalEarn += earn
                    vp.isBought = False
                    vp.priceBoughtTP = 0
                    
                    if(debug == True):
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("TP " + vp.pair + " od longa")
                        print((str)(currTime[2]) + "." + (str)(currTime[1]) + "." + (str)(currTime[0]) + " " + (str)(currTime[3] + 1) + ":" + (str)(currTime[4]))
                        print(ps)#praw
                        print(earn)
                        print(vp.totalEarn)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                
        if(vp.isSold):
            cur = get_price_old(vp.kline, x, vp.priceType)
            diff2 = (cur - vp.priceSold)#/vp.priceSold
            if(diff2 > vp.stopLoss):
                currTime = time.gmtime(get_price_old(vp1.kline, x, 0))
                pb = get_price_old(vp.kline, x, vp.priceType)
                earn = (pb - vp.priceSold)/vp.priceSold
                earn = -earn
                vp.totalEarn += earn
                vp.isSold = False
                
                if(debug == True):
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                    print("stop loss " + vp.pair + " od shorta")
                    print((str)(currTime[2]) + "." + (str)(currTime[1]) + "." + (str)(currTime[0]) + " " + (str)(currTime[3] + 1) + ":" + (str)(currTime[4]))
                    print(pb)#praw
                    print(earn)
                    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                
            if(diff2 < -takeProfit1):
                vp.priceSoldTP = cur
            if(vp.priceSoldTP != 0):
                diff3 = (cur - vp.priceSoldTP)#/vp.priceSoldTP
                if(diff3 > takeProfitStop1):
                    currTime = time.gmtime(get_price_old(vp1.kline, x, 0))
                    pb = get_price_old(vp.kline, x, vp.priceType)
                    earn = (pb - vp.priceSold)/vp.priceSold
                    earn = -earn
                    vp.totalEarn += earn
                    vp.isSold = False
                    vp.priceSoldTP = 0
                    
                    if(debug == True):
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("TP " + vp.pair + " od shorta")
                        print((str)(currTime[2]) + "." + (str)(currTime[1]) + "." + (str)(currTime[0]) + " " + (str)(currTime[3] + 1) + ":" + (str)(currTime[4]))
                        print(pb)#praw
                        print(earn)
                        print(vp.totalEarn)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    
    #if(vp.totalEarn > 0.01):
    #print(openOrder)
    #print(stopLoss)
    #print(vp.totalEarn)
    return vp.totalEarn

def checkSpread(vp):
    #time.sleep(1)
    robot = CoinexPerpetualApi(access_id, secret_key)
    robot.adjust_leverage(vp.pair, 2, 3)
    
    buy = get_pair_buy(get_pair_perpetual(vp.pair))
    sell = get_pair_sell(get_pair_perpetual(vp.pair))
    
    dataPosition = robot.query_position_pending(vp1.pair)
    dataPosition = dataPosition.get("data")
    print(len(dataPosition))
    if(len(dataPosition) > 0):
        print("TUUUUUUUUUUU")
        if(dataPosition[0].get("side") == 1):
            idPos = dataPosition[0].get("position_id")
            amount = (dataPosition[0].get("close_left"))
            if(vp.orderSellIDClose == -1):
                res = robot.close_limit(vp.pair, idPos, amount, buy + 0.1)
                vp.orderSellIDClose = res.get("data").get("order_id")
                print("TRASDASd")
                print(res)
            if(vp.orderSellIDClose != -1):
                res2 = robot.query_order_status(vp.pair, vp.orderSellIDClose)
                if(float(res2.get("data").get("price")) < buy + 0.1):
                    robot.cancel_order(vp.pair, vp.orderSellIDClose)
                    vp.orderSellIDClose = -1
    if(len(dataPosition) > 1):
        print("WTF")
        
    getOrderSell = robot.query_order_status(vp.pair, vp.orderSellID)
    if(getOrderSell.get("data") != None):
        if(float(getOrderSell.get("data").get("price")) > sell - 1):
            robot.cancel_order(vp.pair, vp.orderSellID)
            vp.orderSellID = -1
    else:
        vp.orderSellID = -1
        print("no order sell")
    
    getOrderBuy = robot.query_order_status(vp.pair, vp.orderBuyID)
    if(getOrderBuy.get("data") != None):
        if(float(getOrderBuy.get("data").get("price")) < buy + 1):
            robot.cancel_order(vp.pair, vp.orderBuyID)
            vp.orderBuyID = -1
            #print(getOrderBuy.get("data"))
    else:
        vp.orderBuyID = -1
        #print("noorderbuy")
    
    spread = (sell - buy)/sell
    
    if(spread > 0.0005) and len(dataPosition) < 1:
        print(spread)
        print(vp.pair)
        print(buy)
        print(sell)
        if(vp.orderSellID == -1):
            resultSell = robot.put_limit_order(vp.pair, ORDER_DIRECTION_SELL, 10, sell - 1)
            print(resultSell)
            if(resultSell.get("code") == 0):
                vp.orderSellID = resultSell.get("data").get("order_id")
        
        #if(vp.orderBuyID == -1):
        #    resultBuy = robot.put_limit_order(vp.pair, ORDER_DIRECTION_BUY, 10, buy + 1)
        #    print(resultBuy)
        #    if(resultBuy.get("code") == 0):
        #        vp.orderBuyID = resultBuy.get("data").get("order_id")
        
        
    #else:
    #    robot.cancel_all_order(vp.pair)
    
def hujl():
    vp1.openOrder = 3  
    vp1.stopLoss = 3
    print(checkAll(vp1, limit, False))
    time.sleep(10)

    vp1.bestEarn = -10
    for x in range(30):
        vp1.isBought = False
        vp1.isSold = False
        vp1.lowestSold = 9999
        vp1.highestBuy = 0
        vp1.priceBought = 0
        vp1.priceSold = 0
        vp1.priceBoughtTP = 0
        vp1.priceSoldTP = 0
        vp1.totalEarn = 0
        vp1.openOrder = x
        s = 0
        for y in range(30):
            vp1.isBought = False
            vp1.isSold = False
            vp1.lowestSold = 9999
            vp1.highestBuy = 0
            vp1.priceBought = 0
            vp1.priceSold = 0
            vp1.priceBoughtTP = 0
            vp1.priceSoldTP = 0
            vp1.totalEarn = 0
            vp1.stopLoss = y
            s = checkAll(vp1, limit, False)
            if s > vp1.bestEarn:
                vp1.bestEarn = s
                print(x)
                print(y)
                vp1.bestOpenOrder = x
                vp1.bestStopLoss = y     
                
class ValuePair():
    def __init__(self, _pair, _priceType, _time, _limit):
        self.kline = None
        self.time = _time
        self.limit = _limit
        self.pair = _pair
        self.priceType = _priceType
        self.cur = 0
        self.isBought = False
        self.isSold = False
        self.lowestSold = 9999
        self.highestBuy = 0
        self.priceBought = 0
        self.priceSold = 0
        self.totalEarn = 0 #0.050784281 -> 0.03; 0.040850027
        self.priceBoughtTP = 0
        self.priceSoldTP = 0
        self.bestOpenOrder = 0
        self.bestStopLoss = 0
        self.minuteBought = -1
        self.minuteSold = -1
        self.tp1 = False
        self.tp2 = False
        self.tp3 = False
        self.leverage = 10

    def resetAfterClose(self):
        self.isBought = False
        self.priceBoughtTP = 0
        self.minuteBought = -1
        self.isSold = False
        self.priceSoldTP = 0
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
    
    def setAfterBought(self):
        self.isBought = True
        self.highestBuy = get_pair_sell(get_pair_perpetual(self.pair))
        self.priceBought = self.highestBuy
        self.minuteBought = datetime.now().minute
        self.tp1 = False
        self.tp2 = False
        self.tp3 = False
        
if __name__ == '__main__':
    firstsma = 5
    secondsma = 10
    limit = 1000
    #print(put_limit_perpetual(1, get_pair_sell(get_pair_perpetual('BTCUSD')), 2, 'BTCUSD'))
    
   # vp2 = ValuePair('LTCBTC', firstsma, secondsma, 2)
   # vp3 = ValuePair('EOSBTC', firstsma, secondsma, 2)
   # vp4 = ValuePair('BCHBTC', firstsma, secondsma, 2)
   # vp5 = ValuePair('XRPBTC', firstsma, secondsma, 2)
   # vp6 = ValuePair('BSVBTC', firstsma, secondsma, 2)
   # vp7 = ValuePair('ETCBTC', firstsma, secondsma, 2)
   # vp8 = ValuePair('TRXBTC', firstsma, secondsma, 2)
    
    vp1 = ValuePair('BTCUSD', 2, "1min", limit)
    #vp2 = ValuePair('ETHUSD', firstsma, secondsma, 2)
    #vp3 = ValuePair('BCHUSD', firstsma, secondsma, 2)
    #vp4 = ValuePair('LTCUSD', firstsma, secondsma, 2)
    #vp5 = ValuePair('BSVUSD', firstsma, secondsma, 2)
    #vp6 = ValuePair('XRPUSD', firstsma, secondsma, 2)
    #vp7 = ValuePair('EOSUSD', firstsma, secondsma, 2)

    #1 open
    #2 close
    print(time.time())
    #sr2 = get_price(vp1.kline, 0, 2)        
    #print(sr2)
    while True:
        new_check2(vp1)
        #new_check(vp2)
        #new_check(vp3)
        #new_check(vp4)
        #new_check(vp5)
        #new_check(vp6)
        #new_check(vp7)
        
            
        
        
        


