from __future__ import unicode_literals
import time
import hashlib
import json
from datetime import datetime
from lib import CoinexPerpetualApi
from lib import BinancePerpetualApi
import csv
import matplotlib.pyplot as plt

def checkDepthData(vp, limit, stockName, percent, useStopLoss, useTakeProfit, periodLimited = False):
    fileName = "depthData_" + vp.pair + "_" + str(limit) + "_" + stockName + ".csv"

    with open(fileName, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            r = row[0]
            r = r.replace("\'", "\"")
            data = json.loads(r)
            buys = float(data.get("buysPercent"))
            sells = float(data.get("sellsPercent"))

            if(periodLimited == True):
                day = int(data.get("tonce")[0] + data.get("tonce")[1])
                if(day < 28):
                    continue

            if(useStopLoss == True):
                if(vp.isBought):
                    cur = float(data.get("pairSell"))
                    diff2 = (cur - vp.priceBought)/vp.priceBought
                    if(diff2 < -0.02):
                        vp.closeLong(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("stop loss " + vp.pair + " long")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

                if(vp.isSold):
                    cur = float(data.get("pairBuy"))
                    diff2 = (cur - vp.priceSold)/vp.priceSold
                    if(diff2 > 0.02):
                        vp.closeShort(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("stop loss " + vp.pair + " short")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

            if(useTakeProfit == True):
                if(vp.isBought):
                    cur = float(data.get("pairSell"))
                    diff2 = (cur - vp.priceBought)/vp.priceBought
                    if(diff2 > 0.05):
                        vp.closeLong(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("stop loss " + vp.pair + " long")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

                if(vp.isSold):
                    cur = float(data.get("pairBuy"))
                    diff2 = (cur - vp.priceSold)/vp.priceSold
                    if(diff2 < -0.05):
                        vp.closeShort(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("stop loss " + vp.pair + " short")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

            if(sells > percent) and vp.isBought == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if(vp.isSold):
                    vp.closeShort(data)
                    vp.resetAfterClose()

                vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                vp.setAfterBought(data)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

            if(buys > percent) and vp.isSold == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if(vp.isBought):
                    vp.closeLong(data)
                    vp.resetAfterClose()

                vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                vp.setAfterSold(data)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")

    print(vp.dealsAmount)
    print(vp.totalEarn)

def checkDealsData(vp, limit, stockName, percent, percent2, minimumVolume = 0, maximumVolume = 99999999999999999999999999999999999999999999, useStopLoss = False, stopLossPercent = 0.02, useTakeProfit = False, takeProfitPercent = 0.02, periodLimited = False, lastDay = 28, lastMonth = 1, useCumulativePosition = False, cumulativePositionCount = 3):
    fileName = "depthData_" + vp.pair + "_" + str(limit) + "_" + stockName + ".csv"

    with open(fileName, 'r') as csv_file:
        #csv_reader = csv.reader(csv_file)
        rowList = list(csv.reader(csv_file))

        for row in rowList:
            r = row[0]
            r = r.replace("\'", "\"")
            data = json.loads(r)
            buys = float(data.get("buysPercentDeals"))
            sells = float(data.get("sellsPercentDeals"))

            if(data.get("buysAmountDeals") != None):
                totalVolume = float(data.get("buysAmountDeals")) + float(data.get("sellsAmountDeals"))
            else:
                totalVolume = 999999999999999999999999999

            if(periodLimited == True):
                if data.get("tonce")[1] == ".":
                    day = int(data.get("tonce")[0])
                else:
                    day = int(data.get("tonce")[0] + data.get("tonce")[1])

                if data.get("tonce")[5] == ".": #12.12.2020
                    month = int(data.get("tonce")[3] + data.get("tonce")[4])
                elif data.get("tonce")[3] == ".": #1.1.2020
                    month = int(data.get("tonce")[2])
                elif data.get("tonce")[1] == "." and data.get("tonce")[4] == ".": #1.12.2020 
                    month = int(data.get("tonce")[2] + data.get("tonce")[3])
                elif data.get("tonce")[2] == "." and data.get("tonce")[4] == ".": #12.1.2020
                    month = int(data.get("tonce")[3])
                
                if(day < lastDay) or month != lastMonth:
                    continue

            if(useStopLoss == True):
                if(vp.isBought):
                    cur = float(data.get("pairSell"))
                    diff2 = (cur - vp.priceBought)/vp.priceBought
                    if(diff2 < -stopLossPercent):
                        vp.closeLong(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("stop loss " + vp.pair + " long")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

                if(vp.isSold):
                    cur = float(data.get("pairBuy"))
                    diff2 = (cur - vp.priceSold)/vp.priceSold
                    if(diff2 > stopLossPercent):
                        vp.closeShort(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("stop loss " + vp.pair + " short")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

            if(useCumulativePosition):
                if(sells > percent) and totalVolume > minimumVolume and totalVolume < maximumVolume and vp.isBought == True and vp.buyPositions < cumulativePositionCount and vp.lastBuyTime != data.get("tonce") and vp.priceBought > data.get("pairSell"):
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                    vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                    vp.setAfterBought(data)
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                if(buys > percent) and totalVolume > minimumVolume and totalVolume < maximumVolume and vp.isSold == True and vp.sellPositions < cumulativePositionCount and vp.lastSellTime != data.get("tonce") and vp.priceSold < data.get("pairBuy"):
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                    vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                    vp.setAfterSold(data)
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")        

            if(sells > percent) and totalVolume > minimumVolume and totalVolume < maximumVolume  and vp.isBought == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if(vp.isSold):
                    vp.closeShort(data)
                    vp.resetAfterClose()

                vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                vp.setAfterBought(data)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

            if(buys > percent2) and totalVolume > minimumVolume and totalVolume < maximumVolume and vp.isSold == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if(vp.isBought):
                    vp.closeLong(data)
                    vp.resetAfterClose()

                vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                vp.setAfterSold(data)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")

            if(useTakeProfit == True):
                if(vp.isBought):
                    cur = float(data.get("pairSell"))
                    diff2 = (cur - vp.priceBought)/vp.priceBought
                    if(diff2 > takeProfitPercent):
                        vp.closeLong(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("takeProfit " + vp.pair + " long")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

                if(vp.isSold):
                    cur = float(data.get("pairBuy"))
                    diff2 = (cur - vp.priceSold)/vp.priceSold
                    if(diff2 < -takeProfitPercent):
                        vp.closeShort(data)
                        vp.resetAfterClose()

                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                        print("takeProfit " + vp.pair + " short")
                        vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

    print(vp.totalEarn)
    print(vp.dealsAmount)
    print(vp.bilance)
    return vp.totalEarn

class ValuePair():
    def __init__(self, _robot, _stockName, _pair):
        self.robot = _robot
        self.stockName = _stockName
        self.pair = _pair
        self.isBought = False
        self.isSold = False
        self.priceBought = 0
        self.priceSold = 99999999999
        self.buyPositions = 0
        self.sellPositions = 0
        self.lastBuyTime = ""
        self.lastSellTime = ""
        self.totalEarn = 0
        self.leverage = 10
        self.dealsAmount = 0
        self.totalEarnValues = []
        self.totalEarnTimeValues = []
        self.priceValues = []
        self.bilance = 0
        self.contractAmount = 100

    def closeShort(self, data):
        print("close " + self.pair + " short")
        priceSell = data.get("pairSell")
        earn = (self.contractAmount*self.sellPositions)/(self.leverage*priceSell) - (self.contractAmount*self.sellPositions)/(self.leverage*self.priceSold)
        fee = 0.0005*((self.contractAmount*self.sellPositions)/(self.leverage*self.priceSold))
        self.totalEarn += earn
        self.totalEarn -= fee

        if earn > 0:
            self.bilance += 1
        else:
            self.bilance -=1

        self.dealsAmount += 1

        self.totalEarnValues.append(self.totalEarn)
        time = str(data.get("tonce")).replace("2020","")
        self.totalEarnTimeValues.append(time)
        self.priceValues.append(float(data.get("pairSell")))

        print(priceSell - self.priceSold)
        print(earn)
        print(self.totalEarn)

    def closeLong(self, data):
        print("close " + self.pair + " long")
        pairBuy = data.get("pairBuy")
        earn = (self.contractAmount*self.buyPositions)/(self.leverage*pairBuy) - (self.contractAmount*self.buyPositions)/(self.leverage*self.priceBought)
        fee = 0.0005*((self.contractAmount*self.buyPositions)/(self.leverage*self.priceBought))
        earn = -earn
        self.totalEarn += earn
        self.totalEarn -= fee

        self.dealsAmount += 1
        if earn > 0:
            self.bilance += 1
        else:
            self.bilance -=1
            
        self.totalEarnValues.append(self.totalEarn)
        time = str(data.get("tonce")).replace("2020","")
        self.totalEarnTimeValues.append(time)
        self.priceValues.append(float(data.get("pairSell")))

        print(pairBuy - self.priceBought)
        print(earn)
        print(self.totalEarn)

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
            self.priceSold = (self.priceSold + float(data.get("pairBuy")))/2
        else:
            self.priceSold = float(data.get("pairBuy"))

    def setAfterBought(self, data):
        self.isBought = True
        self.buyPositions += 1
        self.lastBuyTime = data.get("tonce")
        if self.buyPositions > 1:
            self.priceBought = (self.priceBought + float(data.get("pairSell")))/2
        else:
            self.priceBought = float(data.get("pairSell"))

    def printDebug(self, data, orderDirection):
        if(orderDirection == 1):
            print(self.pair + " sell")
        else:
            print(self.pair + " buy")
        print(data.get("pairSell"))
        print(data.get("pairBuy"))
        print(data.get("tonce"))
        print(data.get("sellsAmountDeals"))
        print(data.get("buysAmountDeals"))

if __name__ == '__main__':
    collectData = False
    
    coinexRobot = CoinexPerpetualApi()
   # binanceRobot = BinancePerpetualApi()

    coinexBTCTrade = ValuePair(coinexRobot, "coinexTrade", 'BTCUSD')
    coinexBTC = ValuePair(coinexRobot, "coinex", 'BTCUSD')
    coinexETH = ValuePair(coinexRobot, "coinex", 'ETHUSD')

    #binanceBTC = ValuePair(binanceRobot, "binance", 'BTCUSD_PERP')
    
    if(collectData == False):
        coinexBTC2 = ValuePair(coinexRobot, "coinex", 'BTCUSD')
    
        #checkDepthData(coinexETH, 10, "coinex", 0.85, False, False)
        #checkDepthData(coinexBTC, 10, "coinex", 0.95, False, False) 
        #checkDepthData(coinexETH, 10, "coinex", 0.95, False, False) 
    
        checkDealsData(coinexBTC, 20, "coinex", 0.95, 0.95, minimumVolume=20000, useStopLoss=False, stopLossPercent=0.02, useTakeProfit=False, takeProfitPercent = 0.02, periodLimited=True, lastDay=8, lastMonth=1, useCumulativePosition=True, cumulativePositionCount=10)  #20k volume, 0.996/7 best -> 998
        checkDealsData(coinexBTC2, 20, "coinex", 0.95, 0.95, minimumVolume=20000, useStopLoss=False, stopLossPercent=0.015, useTakeProfit=False, takeProfitPercent = 0.02, periodLimited=True, lastDay=8, lastMonth=1, useCumulativePosition=True, cumulativePositionCount=15)
    
        plt.plot(coinexBTC.totalEarnValues, label = "1")
        plt.plot(coinexBTC2.totalEarnValues, label = "2")
    
        # checkDealsData(coinexETH, 20, "coinex", 0.95, 0.95, minimumVolume = 20000, periodLimited=True, lastDay=7, lastMonth=1, useCumulativePosition=True, cumulativePositionCount=15) #20k 0.993
        # checkDealsData(coinexETH2, 20, "coinex", 0.935, 0.935, minimumVolume = 0, periodLimited=True, lastDay=7, lastMonth=1, useCumulativePosition=True, cumulativePositionCount=15)
    
        # plt.plot(coinexETH.totalEarnValues, label = "1")
        # plt.plot(coinexETH2.totalEarnValues, label = "2")
    
        plt.xticks(rotation=90)
        plt.legend()
        plt.show()
    else:
        while True:
            coinexRobot.collectDepthData(coinexBTCTrade, 20)
            coinexRobot.collectDepthData(coinexBTC, 20)
            coinexRobot.collectDepthData(coinexETH, 10)
            coinexRobot.collectDepthData(coinexETH, 20)
        #     coinexRobot.collectKlineData(coinexBTC, 1)
        #     coinexRobot.collectKlineData(coinexBTC, 5)
        #     coinexRobot.collectKlineData(coinexBTC, 15)
    
        #     binanceRobot.collectDepthData(binanceBTC, 10)
        #     binanceRobot.collectDepthData(binanceBTC, 20)
    
        #     binanceRobot.collectKlineData(binanceBTC, 1)
        #     binanceRobot.collectKlineData(binanceBTC, 5)
        #     binanceRobot.collectKlineData(binanceBTC, 15)







