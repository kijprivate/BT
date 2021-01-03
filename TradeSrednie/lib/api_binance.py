import logging
from .request_client_binance import RequestClient
import csv
import time

class BinancePerpetualApi(object):
    ORDER_DIRECTION_SELL = 1
    ORDER_DIRECTION_BUY = 2

    MARGIN_ADJUST_TYPE_INCRESE = 1
    MARGIN_ADJUST_TYPE_DECREASE = 2

    POSITION_TYPE_ISOLATED = 1
    POSITION_TYPE_CROSS_MARGIN = 2

    access_id = '92D0E39AF1634EA9B7D037EDDBECD261'
    secret_key = 'B7B13884C89347FE86E6E34A7C9FE7DD28A43B301CB70611' 

    def __init__(self, logger=None):
        self.request_client = RequestClient(self.access_id, self.secret_key, logger)

    #My API
    def collectDepthData(self, vp, limit):
        #try:
        depthData = self.depth(vp.pair, limit = limit)

        sellsAmount = 0
        buysAmount = 0
        for x in range(len(depthData.get('asks'))):
            sellsAmount += float(depthData.get('asks')[x][1])
        
        for x in range(len(depthData.get('bids'))):
            buysAmount += float(depthData.get('bids')[x][1])
        
        sellsPercent = sellsAmount/(sellsAmount + buysAmount)    
        buysPercent = buysAmount/(sellsAmount + buysAmount) 

        marketDealsData = self.get_market_deals(vp.pair, limit = limit)

        sellsAmountDeals = 0
        buysAmountDeals = 0
        for x in marketDealsData:
            if(x.get("isBuyerMaker") == "true"):
                sellsAmountDeals += float(x.get('baseQty'))
            else:
                buysAmountDeals += float(x.get('baseQty'))
        
        sellsPercentDeals = sellsAmountDeals/(sellsAmountDeals + buysAmountDeals)    
        buysPercentDeals = buysAmountDeals/(sellsAmountDeals + buysAmountDeals) 

        currTime = time.gmtime(time.time())
        realTime = (str)(currTime[2]) + "." + (str)(currTime[1]) + "." + (str)(currTime[0]) + " " + (str)(currTime[3] + 1) + ":" + (str)(currTime[4])
        
        data = [{
            "time": realTime,
            "sellsPercent": sellsPercent,
            "buysPercent": buysPercent,
            "sellsPercentDeals": sellsPercentDeals,
            "buysPercentDeals": buysPercentDeals,
            "pairSell": self.get_pair_sell(vp.pair),
            "pairBuy": self.get_pair_buy(vp.pair),
            "sellsAmountDeals": sellsAmountDeals,
            "buysAmountDeals": buysAmountDeals
        }]  
        
        fileName = "depthData_" + vp.pair + "_" + str(limit) + "_" + vp.stockName + ".csv"
        with open(fileName, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(data)
        #except:
        #    print(1)

    def collectKlineData(self, vp, typeInMinutes):
        try:
            klineData = self.kline(vp.pair, str(typeInMinutes) + "m", 1)

            data = [{
                "tonce": klineData[0][0],
                "open": klineData[0][1],
                "close": klineData[0][4],
                "highest": klineData[0][2],
                "lowest": klineData[0][3],
                "volume": klineData[0][5],
                "amount": klineData[0][7],
                "pairSell": self.get_pair_sell(vp.pair),
                "pairBuy": self.get_pair_buy(vp.pair)
            }]
            
            fileName = "klineData_" + vp.pair + "_" + str(typeInMinutes) + "min" + "_" + vp.stockName + ".csv"
            with open(fileName, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',')
                csv_writer.writerow(data)
                
        except:
            print(1)
        
    # Market API
    def get_market_info(self):
        path = '/v1/market/list'
        return self.request_client.get(path, sign=False)

    def get_market_state(self, market):
        path = '/v1/market/ticker'
        params = {
            'market': market
        }
        return self.request_client.get(path, params, sign=False)

    def get_market_deals(self, market, limit):
        path = '/dapi/v1/trades'
        params = {
            'symbol': market,
            'limit': limit
        }
        return self.request_client.get(path, params, sign=False)

    def tickers(self):
        path = '/v1/market/ticker/all'
        return self.request_client.get(path, sign=False)

    def depth(self, market, merge=0, limit=50):
        path = '/dapi/v1/depth'
        params = {
            'symbol': market,
            'limit': limit
        }
        return self.request_client.get(path, params, sign=False)

    def kline(self, market, kline_type, limit):
        path = '/dapi/v1/klines'
        params = {
            'symbol': market,
            'interval': kline_type,
            'limit': limit
        }
        return self.request_client.get(path, params, sign=False)

    def get_pair_sell(self, pair):
        dep = self.depth(pair)
        return (float)(dep.get('asks')[0][0])

    def get_pair_buy(self, pair):
        dep = self.depth(pair)
        return (float)(dep.get('bids')[0][0])
    
    # Account API
    def query_account(self):
        path = '/v1/asset/query'
        return self.request_client.get(path)

    # Trading API
    def putMarketOrder(self, vp, side, leverage):
        if(vp.realTrade == False):
            return "Trading disabled"

        self.adjust_leverage(vp.pair, 1, leverage)
        self.adjust_leverage(vp.pair, 2, leverage)
        result = self.put_market_order(
            vp.pair,
            side,
            vp.contractAmount
        )
        print(result)
        return result

    def put_limit_order(self, market, side, amount, price, effect_type=1):
        path = '/v1/order/put_limit'
        data = {
            'market': market,
            'effect_type': effect_type,
            'side': side,
            'amount': str(amount),
            'price': str(price),
            'use_cet': 1
        }
        return self.request_client.post(path, data)

    def put_market_order(self, market, side, amount):
        path = '/v1/order/put_market'
        data = {
            'market': market,
            'amount': str(amount),
            'side': side,
            'use_cet': 1
        }
        return self.request_client.post(path, data)

    def close_limit(self, market, position_id, amount, price, effect_type=None):
        path = '/v1/order/close_limit'
        data = {
            'market': market,
            'position_id': position_id,
            'amount': str(amount),
            'price': str(price)
        }
        if effect_type:
            data['effect_type'] = effect_type

        return self.request_client.post(path, data)

    def close_market(self, market, position_id):
        path = '/v1/order/close_market'
        data = {
            'market': market,
            'position_id': position_id
        }
        return self.request_client.post(path, data)

    def cancel_order(self, market, order_id):
        path = '/v1/order/cancel'
        params = {
            'market': market,
            'order_id': order_id
        }
        return self.request_client.post(path, params)

    def cancel_all_order(self, market):
        path = '/v1/order/cancel_all'
        params = {
            'market': market
        }
        return self.request_client.post(path, params)

    def query_order_pending(self, market, side, offset, limit=100):
        path = '/v1/order/pending'
        params = {
            'market': market,
            'side': side,
            'offset': offset,
            'limit': limit
        }
        return self.request_client.get(path, params)

    def query_stop_pending(self, market, side, offset, limit=100):
        path = '/v1/order/stop_pending'
        params = {
            'market': market,
            'side': side,
            'offset': offset,
            'limit': limit
        }
        return self.request_client.get(path, params)

    def query_position_pending(self, market=''):
        path = '/v1/position/pending'
        params = {}
        if market:
            params['market'] = market

        return self.request_client.get(path, params)

    def query_order_finished(self, market, side, offset, limit=100):
        path = '/v1/order/finished'
        params = {
            'market': market,
            'side': side,
            'offset': offset,
            'limit': limit
        }
        return self.request_client.get(path, params)

    def query_order_status(self, market, order_id):
        path = '/v1/order/status'
        params = {
            'market': market,
            'order_id': order_id
        }
        return self.request_client.get(path, params)

    def query_user_deals(self, market, offset, limit=100, side=0):
        path = '/v1/market/user_deals'
        params = {
            'market': market,
            'side': side,
            'offset': offset,
            'limit': limit,
        }
        return self.request_client.get(path, params)

    def adjust_margin(self, market, amount, adjust_type):
        path = '/v1/position/adjust_margin'
        data = {
            'market': market,
            'amount': amount,
            'type': adjust_type
        }
        return self.request_client.post(path, data)

    def adjust_leverage(self, market, position_type, leverage):
        path = '/v1/market/adjust_leverage'
        data = {
            'market': market,
            'position_type': position_type,
            'leverage': leverage
        }
        return self.request_client.post(path, data)
