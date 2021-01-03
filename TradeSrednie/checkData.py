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

def checkDealsData(vp, limit, stockName, percent, percent2, minimumVolume = 0, useStopLoss = False, stopLossPercent = 0.02, periodLimited = False, lastDay = 28, lastMonth = 1, useCumulativePosition = False, cumulativePositionCount = 3):
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
                if(sells > percent) and totalVolume > minimumVolume and vp.isBought == True and vp.buyPositions < cumulativePositionCount and vp.lastBuyTime != data.get("tonce") and vp.priceBought > data.get("pairSell"):
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                    vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                    vp.setAfterBought(data)
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                if(buys > percent) and totalVolume > minimumVolume and vp.isSold == True and vp.sellPositions < cumulativePositionCount and vp.lastSellTime != data.get("tonce") and vp.priceSold < data.get("pairBuy"):
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                    vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                    vp.setAfterSold(data)
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")        

            if(sells > percent) and totalVolume > minimumVolume and vp.isBought == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if(vp.isSold):
                    vp.closeShort(data)
                    vp.resetAfterClose()

                vp.printDebug(data, vp.robot.ORDER_DIRECTION_BUY)
                vp.setAfterBought(data)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

            if(buys > percent2) and totalVolume > minimumVolume and vp.isSold == False:
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                if(vp.isBought):
                    vp.closeLong(data)
                    vp.resetAfterClose()

                vp.printDebug(data, vp.robot.ORDER_DIRECTION_SELL)
                vp.setAfterSold(data)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")

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
        self.priceSold = 0
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

    def closeShort(self, data):
        print("close " + self.pair + " short")
        #pb = data.get("pairBuy")
        pb = data.get("pairSell")
        earn = (pb - self.priceSold)/self.priceSold
        earn = -earn
        self.totalEarn += earn#*self.sellPositions
        if earn > 0:
            self.bilance += 1
        else:
            self.bilance -=1
        self.totalEarn -= 0.0003
        self.dealsAmount += 1

        self.totalEarnValues.append(self.totalEarn)
        time = str(data.get("tonce")).replace("2020","")
        self.totalEarnTimeValues.append(time)
        self.priceValues.append(float(data.get("pairSell")))

        print(earn)
        print(self.totalEarn)

    def closeLong(self, data):
        print("close " + self.pair + " long")
        #ps = data.get("pairSell")
        ps = data.get("pairBuy")
        earn = (ps - self.priceBought)/self.priceBought
        self.totalEarn += earn#*self.buyPositions
        self.totalEarn -= 0.0003
        self.dealsAmount += 1
        if earn > 0:
            self.bilance += 1
        else:
            self.bilance -=1
        self.totalEarnValues.append(self.totalEarn)
        time = str(data.get("tonce")).replace("2020","")
        self.totalEarnTimeValues.append(time)
        self.priceValues.append(float(data.get("pairSell")))

        print(earn)
        print(self.totalEarn)

    def resetAfterClose(self):
        self.isBought = False
        self.isSold = False
        self.buyPositions = 0
        self.sellPositions = 0

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

if __name__ == '__main__':
    robot = CoinexPerpetualApi()

    vpb1 = ValuePair(robot, 'BTCUSD')
    vpb2 = ValuePair(robot, 'BTCUSD')

    vpe1 = ValuePair(robot, 'ETHUSD')
    vpe2 = ValuePair(robot, 'ETHUSD')

    #checkDepthData(vpe1, 10, "coinex", 0.85, False, False)
    #checkDepthData(vpb1, 10, "coinex", 0.95, True, True) 
    #checkDepthData(vpe1, 10, "coinex", 0.95, False, False) 

    # checkDealsData(vpb1, 20, "coinex", 0.998, False, 20000, False, 30)  #20k volume, 0.996/7 best
    # checkDealsData(vpb2, 20, "coinex", 0.998, False, 1000, False, 30)

    # plt.plot(vpb1.totalEarnValues, label = "t")
    # plt.plot(vpb2.totalEarnValues, label = "n")

    # checkDealsData(vpe1, 20, "coinex", 0.993, False, 20000, False, 30)
    # checkDealsData(vpe2, 20, "coinex", 0.993, False, 1000, False, 30)

    # plt.plot(vpe1.totalEarnValues, label = "t")
    # plt.plot(vpe2.totalEarnValues, label = "n")

    # plt.xticks(rotation=90)
    # plt.legend()
    # plt.show()

    while True:
        robot.collectDepthData(vpb1, 10, "coinex")
        robot.collectDepthData(vpb1, 20, "coinex")
        robot.collectDepthData(vpe1, 10, "coinex")
        robot.collectDepthData(vpe1, 20, "coinex")







