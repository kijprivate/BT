from __future__ import unicode_literals
import time
import json
from datetime import datetime
from lib import CoinexPerpetualApi
from lib import BinancePerpetualApi
import csv


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

def tradeDealsFromFile(robot, vp, lim, percent, minVolume = 0, useCumulativePosition = False, cumulativePositionCount = 3):    
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
                buysPercentDeals = float(data.get("buysPercentDeals"))
                sellsPercentDeals = float(data.get("sellsPercentDeals"))
                buysAmount = float(data.get("buysAmountDeals"))
                sellsAmount = float(data.get("sellsAmountDeals"))
                break

        totalVolume = buysAmount + sellsAmount

        if(useCumulativePosition == True):
            if(sellsPercentDeals > percent) and totalVolume > minVolume and vp.isBought == True and vp.buyPositions < cumulativePositionCount and vp.lastBuyTime != tonce and vp.priceBought > data.get("pairSell"):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                vp.printDebug(robot.ORDER_DIRECTION_BUY)
                
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage, vp.contractAmount)
                vp.setAfterBought(data)
                
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                
            elif(buysPercentDeals > percent) and totalVolume > minVolume and vp.isSold == True and vp.sellPositions < cumulativePositionCount and vp.lastSellTime != tonce and vp.priceSold < data.get("pairBuy"):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                vp.printDebug(robot.ORDER_DIRECTION_SELL)
                
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage, vp.contractAmount)
                vp.setAfterSold(data)
                
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        if(sellsPercentDeals > percent) and totalVolume > minVolume and vp.isBought == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isSold):
                vp.closeShort()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage, vp.contractAmount*vp.sellPositions)
                vp.resetAfterClose()

            vp.printDebug(robot.ORDER_DIRECTION_BUY)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage, vp.contractAmount)
            vp.setAfterBought(data)
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            
        elif(buysPercentDeals > percent) and totalVolume > minVolume and vp.isSold == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isBought):
                vp.closeLong()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage, vp.contractAmount*vp.buyPositions)
                vp.resetAfterClose()
            
            vp.printDebug(robot.ORDER_DIRECTION_SELL)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage, vp.contractAmount)
            vp.setAfterSold(data)
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                                                
    except:
        print(1)

class ValuePair():
    def __init__(self, _robot, _stockName, _pair, _contractAmount, _isBought = False, _priceBought = 0, _isSold = False, _priceSold = 999999999):
        self.robot = _robot
        self.stockName = _stockName
        self.realTrade = True
        self.pair = _pair
        self.isBought = _isBought
        self.isSold = _isSold
        self.priceBought = _priceBought
        self.priceSold = _priceSold
        self.buyPositions = 0
        self.sellPositions = 0
        self.lastBuyTime = ""
        self.lastSellTime = ""
        self.totalEarn = 0 
        self.realTotalEarn = 0
        self.realTotalEarnWithFee = 0
        self.leverage = 10
        self.contractAmount = _contractAmount

    def closeShort(self):
        print("close " + self.pair + " short")
        priceSell = self.robot.get_pair_sell(self.pair)
        earn = (self.contractAmount*self.sellPositions)/(priceSell) - (self.contractAmount*self.sellPositions)/(self.priceSold)
        fee = 2*0.00035*((self.contractAmount*self.sellPositions)/(self.priceSold))
        self.totalEarn += earn
        self.totalEarn -= fee
        print("earn " + str(earn))
        print("totalEarn " + str(self.totalEarn))

    def closeLong(self):
        print("close " + self.pair + " long")
        pairBuy = self.robot.get_pair_buy(self.pair)
        earn = (self.contractAmount*self.buyPositions)/(self.priceBought) - (self.contractAmount*self.buyPositions)/(pairBuy)
        fee = 2*0.00035*((self.contractAmount*self.buyPositions)/(self.priceBought))
        self.totalEarn += earn
        self.totalEarn -= fee
        print("earn " + str(earn))
        print("totalEarn " + str(self.totalEarn))

    def resetAfterClose(self):
        self.isBought = False
        self.isSold = False
        self.buyPositions = 0
        self.sellPositions = 0
        self.priceBought = 0
        self.priceSold = 999999999
    
    def setAfterSold(self, data):
        self.isSold = True
        self.sellPositions += 1
        self.lastSellTime = data.get("tonce")
        if self.sellPositions > 1:
            self.priceSold = (self.priceSold + self.robot.get_pair_buy(self.pair))/2
        else:
            self.priceSold = self.robot.get_pair_buy(self.pair)
    
    def setAfterBought(self, data):
        self.isBought = True
        self.buyPositions += 1
        self.lastBuyTime = data.get("tonce")
        if self.buyPositions > 1:
            self.priceBought = (self.priceBought + self.robot.get_pair_sell(self.pair))/2
        else:
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
    binanceRobot = BinancePerpetualApi()

    vp1 = ValuePair(robot, "coinexTrade", 'BTCUSD', 20)
    
    binanceBTC = ValuePair(binanceRobot, "coinexTrade", 'BTCUSD', 1)

    print(time.time())
    while True:
        tradeDealsFromFile(robot, vp1, 20, 0.95, minVolume=20000, useCumulativePosition=True, cumulativePositionCount=15)
        tradeDealsFromFile(binanceRobot, binanceBTC, 20, 0.95, minVolume=20000, useCumulativePosition=True, cumulativePositionCount=15)

        
            
        
        
        


