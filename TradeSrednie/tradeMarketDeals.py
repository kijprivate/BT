from __future__ import unicode_literals
import time
import json
from datetime import datetime
from lib import CoinexPerpetualApi
#from lib import request_client_coinex

def tradeDeals(robot, vp, lim, percent, minVolume = 0, useCumulativePosition = False, cumulativePositionCount = 3):    
    time.sleep(5)
    try:
        sellsPercentDeals = vp.getPercentDeals(lim, "sell")    
        buysPercentDeals = vp.getPercentDeals(lim, "buy")
        totalVolume = vp.getAmountDeals(lim)

        if(useCumulativePosition == True):
            if(sellsPercentDeals > percent) and totalVolume > minVolume and vp.isBought == True and vp.buyPositions < cumulativePositionCount and time.time() - vp.lastBuyTime > 20 and vp.priceBought > vp.robot.get_pair_sell(vp.pair):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                vp.printDebug(robot.ORDER_DIRECTION_BUY)
                
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage, vp.contractAmount)
                vp.setAfterBought()
                
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                
            elif(buysPercentDeals > percent) and totalVolume > minVolume and vp.isSold == True and vp.sellPositions < cumulativePositionCount and time.time() - vp.lastSellTime > 20 and vp.priceSold < vp.robot.get_pair_buy(vp.pair):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                vp.printDebug(robot.ORDER_DIRECTION_SELL)
                
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage, vp.contractAmount)
                vp.setAfterSold()
                
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        if(sellsPercentDeals > percent) and totalVolume > minVolume and vp.isBought == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isSold):
                vp.closeShort()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage, vp.contractAmount*vp.sellPositions)
                vp.resetAfterClose()

            vp.printDebug(robot.ORDER_DIRECTION_BUY)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_BUY, vp.leverage, vp.contractAmount)
            vp.setAfterBought()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            
        elif(buysPercentDeals > percent) and totalVolume > minVolume and vp.isSold == False:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            if(vp.isBought):
                vp.closeLong()
                robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage, vp.contractAmount*vp.buyPositions)
                vp.resetAfterClose()
            
            vp.printDebug(robot.ORDER_DIRECTION_SELL)
            
            robot.putMarketOrder(vp, robot.ORDER_DIRECTION_SELL, vp.leverage, vp.contractAmount)
            vp.setAfterSold()
            
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                                            
    except:
        print(1)
        
class ValuePair():
    def __init__(self, _robot, _pair, _contractAmount, _isBought = False, _priceBought = 0, _buyPositions = 0, _isSold = False, _priceSold = 0, _sellPositions = 0, _totalEarn = 0):
        self.robot = _robot
        self.realTrade = True
        self.pair = _pair
        self.isBought = _isBought
        self.isSold = _isSold
        self.priceBought = _priceBought
        self.priceSold = _priceSold
        self.buyPositions = 0
        self.sellPositions = 0
        self.lastBuyTime = time.time()
        self.lastSellTime = time.time()
        self.totalEarn = _totalEarn 
        self.realTotalEarn = 0
        self.realTotalEarnWithFee = 0
        self.leverage = 10
        self.contractAmount = _contractAmount

    def closeShort(self):
        print("close " + self.pair + " short")
        pairBuy = self.robot.get_pair_buy(self.pair)
        earn = (self.contractAmount*self.sellPositions)/(self.leverage*pairBuy) - (self.contractAmount*self.sellPositions)/(self.leverage*self.priceSold)
        fee = 0.0005*((self.contractAmount*self.sellPositions)/(self.leverage*self.priceSold))
        #earn = (pairBuy - self.priceSold)/self.priceSold
        #earn = -earn
        self.totalEarn += earn#*self.sellPositions
        self.totalEarn -= fee
        print(earn)
        print(fee)
        print(self.totalEarn)
        print(self.realTotalEarn)
        print(self.realTotalEarnWithFee)

    def closeLong(self):
        print("close " + self.pair + " long")
        priceSell = self.robot.get_pair_sell(self.pair)
        earn = (self.contractAmount*self.buyPositions)/(self.leverage*priceSell) - (self.contractAmount*self.buyPositions)/(self.leverage*self.priceBought)
        fee = 0.0005*((self.contractAmount*self.buyPositions)/(self.leverage*self.priceBought))
        #earn = (priceSell - self.priceBought)/self.priceBought
        earn = -earn
        self.totalEarn += earn#*self.buyPositions
        self.totalEarn -= fee
        print(earn)
        print(fee)
        print(self.totalEarn)
        print(self.realTotalEarn)
        print(self.realTotalEarnWithFee)

    def resetAfterClose(self):
        self.isBought = False
        self.isSold = False
        self.buyPositions = 0
        self.sellPositions = 0
    
    def setAfterSold(self):
        self.isSold = True
        self.sellPositions += 1
        self.lastSellTime = time.time()
        if self.sellPositions > 1:
            self.priceSold = (self.priceSold + self.robot.get_pair_buy(self.pair))/2
        else:
            self.priceSold = self.robot.get_pair_buy(self.pair)
    
    def setAfterBought(self):
        self.isBought = True
        self.buyPositions += 1
        self.lastBuyTime = time.time()
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

    vp1 = ValuePair(robot, 'BTCUSD', 30)
    vp2 = ValuePair(robot, 'ETHUSD', 20)

    print(time.time())

    while True:
        tradeDeals(robot, vp1, 20, 0.95, minVolume=20000, useCumulativePosition=True, cumulativePositionCount=15)
        #tradeDeals(robot, vp2, 20, 0.935, minVolume=5000, useCumulativePosition=True, cumulativePositionCount=10)

        
            
        
        
        


