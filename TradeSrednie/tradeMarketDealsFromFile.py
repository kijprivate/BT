from __future__ import unicode_literals
import time
import json
from datetime import datetime
from lib import CoinexPerpetualApi
import csv
#from lib import request_client_coinex

def tradeDeals(robot, vp, lim, percent, minVolume):    
    try:
        sellsPercentDeals = vp.getPercentDeals(lim, "sell")    
        buysPercentDeals = vp.getPercentDeals(lim, "buy")
        totalVolume = vp.getAmountDeals(lim)

        if(sellsPercentDeals > percent) and totalVolume > minVolume and vp.isBought == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isSold):
                vp.closeShort()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage)
                vp.resetAfterClose()

            vp.printDebug(robot.ORDER_DIRECTION_BUY)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage)
            vp.setAfterBought()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            
        elif(buysPercentDeals > percent) and totalVolume > minVolume and vp.isSold == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isBought):
                vp.closeLong()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage)
                vp.resetAfterClose()
            
            vp.printDebug(robot.ORDER_DIRECTION_SELL)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage)
            vp.setAfterSold()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                                            
    except:
        print(1)

def tradeDealsFromFile(robot, vp, lim, percent, minVolume):    
    try:
        fileName = "depthData_" + vp.pair + "_" + str(lim) + "_" + vp.stockName + ".csv"

        with open(fileName, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            csv_reader = reversed(list(csv_reader))
            for row in csv_reader:
                r = row[0]
                r = r.replace("\'", "\"")
                data = json.loads(r)
                tonce = data.get("tonce")
                buysPercentDeals = float(data.get("buysPercent"))
                sellsPercentDeals = float(data.get("sellsPercent"))
                buysAmount = float(data.get("buysAmountDeals"))
                sellsAmount = float(data.get("sellsAmountDeals"))
                break

        totalVolume = buysAmount + sellsAmount

        if(sellsPercentDeals > percent) and totalVolume > minVolume and vp.isBought == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isSold):
                vp.closeShort()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage)
                vp.resetAfterClose()

            vp.printDebug(robot.ORDER_DIRECTION_BUY)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage)
            vp.setAfterBought()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            
        elif(buysPercentDeals > percent) and totalVolume > minVolume and vp.isSold == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isBought):
                vp.closeLong()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage)
                vp.resetAfterClose()
            
            vp.printDebug(robot.ORDER_DIRECTION_SELL)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage)
            vp.setAfterSold()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                                            
    except:
        print(1)

class ValuePair():
    def __init__(self, _robot, _stockName, _pair, _contractAmount, _isBought = False, _priceBought = 0, _isSold = False, _priceSold = 0):
        self.robot = _robot
        self.stockName = _stockName
        self.realTrade = False
        self.pair = _pair
        self.isBought = _isBought
        self.isSold = _isSold
        self.priceBought = _priceBought
        self.priceSold = _priceSold
        self.totalEarn = 0 
        self.leverage = 10
        self.contractAmount = _contractAmount

    def closeShort(self):
        print("close " + self.pair + " short")
        pairBuy = self.robot.get_pair_buy(self.pair)
        earn = (pairBuy - self.priceSold)/self.priceSold
        earn = -earn
        self.totalEarn += earn
        self.totalEarn -= 0.0003
        print(earn)
        print(self.totalEarn)

    def closeLong(self):
        print("close " + self.pair + " long")
        priceSell = self.robot.get_pair_sell(self.pair)
        earn = (priceSell - self.priceBought)/self.priceBought
        self.totalEarn += earn
        self.totalEarn -= 0.0003
        print(earn)
        print(self.totalEarn)

    def resetAfterClose(self):
        self.isBought = False
        self.isSold = False
    
    def setAfterSold(self):
        self.isSold = True
        self.priceSold = self.robot.get_pair_buy(self.pair)
    
    def setAfterBought(self):
        self.isBought = True
        self.priceBought = self.robot.get_pair_sell(self.pair)

    def getPercentDeals(self, lim, dealsType):
        marketDealsData = self.robot.get_market_deals(self.pair, limit = lim).get("data")
    
        sellsAmountDeals = 0
        buysAmountDeals = 0
        for x in marketDealsData:
            if(x.get("type") == "sell"):
                sellsAmountDeals += float(x.get('amount'))
            else:
                buysAmountDeals += float(x.get('amount'))
        
        if(dealsType == "sell"):
            return sellsAmountDeals/(sellsAmountDeals + buysAmountDeals) 
        else:
            return buysAmountDeals/(sellsAmountDeals + buysAmountDeals)

    def getAmountDeals(self, lim):
        marketDealsData = self.robot.get_market_deals(self.pair, limit = lim).get("data")
    
        sellsAmountDeals = 0
        buysAmountDeals = 0
        for x in marketDealsData:
            if(x.get("type") == "sell"):
                sellsAmountDeals += float(x.get('amount'))
            else:
                buysAmountDeals += float(x.get('amount'))

        return sellsAmountDeals + buysAmountDeals

    def printDebug(self, orderDirection):
        if(orderDirection == 1):
            print(self.pair + " sell")
        else:
            print(self.pair + " buy")
        print(self.robot.get_pair_sell(self.pair))
        print(self.robot.get_pair_buy(self.pair))
        print(datetime.now())
        
if __name__ == '__main__':
    robot = CoinexPerpetualApi()

    vp1 = ValuePair(robot, "coinex", 'BTCUSD', 500)
    vp2 = ValuePair(robot, "coinex", 'ETHUSD', 100)
    
    print(time.time())


    while True:
        tradeDealsFromFile(robot, vp1, 20, 0.998, 20000)
        tradeDealsFromFile(robot, vp2, 20, 0.995, 20000)

        
            
        
        
        


