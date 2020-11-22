import asyncio
import aiohttp
import time
import math
from datetime import datetime

import coinex as coinex
import binance as binance
import kucoin as kucoin
import bithumb as bithumb
import bitrue as bitrue
import bibox as bibox
import bkex as bkex
import mxc as mxc
import probit as probit

class TradesSimulation():
    def __init__(self, toBuy, askArray, toSell, bidArray):
        self.toBuy = toBuy
        self.askArray = askArray
        self.outOfAsk = False
        self.askIndex = 0
        self.toSell = toSell
        self.bidArray = bidArray
        self.outOfBid = False
        self.bidIndex = 0
        self.averageAskPrice = 0
        self.averageBidPrice = 0
    
    def count_Asks(self):
        boughts = []
        boughtsAm = []
        
        self.askIndex = 0
        self.outOfAsk = False
        testIndex = 0
        while(self.toBuy > 0) and testIndex < 50:
            testIndex += 1
            if(testIndex > 48):
                print("Infinite loop " + str(testIndex))
            #print("LOOP BUY")
            if self.askIndex < len(self.askArray) and (self.toBuy > (float)(self.askArray[self.askIndex][1])):
                boughts.append((float)(self.askArray[self.askIndex][0]))
                boughtsAm.append((float)(self.askArray[self.askIndex][1]))
                self.toBuy -= (float)(self.askArray[self.askIndex][1])
                self.askIndex += 1
            elif self.askIndex < len(self.askArray) and (self.toBuy < (float)(self.askArray[self.askIndex][1])):
                boughts.append((float)(self.askArray[self.askIndex][0]))
                boughtsAm.append(self.toBuy)
                self.toBuy = 0
            elif(self.askIndex >= len(self.askArray)):
                self.outOfAsk = True
                self.toBuy = 0
                
        weightedBoughts = 0
        totalBoughtsAmount = 0
        for x in range(len(boughts)):
            weightedBoughts += boughts[x]*boughtsAm[x]
            totalBoughtsAmount += boughtsAm[x]
        
        if(totalBoughtsAmount > 0):
            self.averageAskPrice = weightedBoughts / totalBoughtsAmount
        else:
            self.averageAskPrice = 0
            
    def count_Bids(self):
        sold = []
        soldAm = []
        
        self.bidIndex = 0   
        self.outOfBid = False
        testIndex = 0
        while(self.toSell > 0) and testIndex < 50:
            testIndex += 1
            if(testIndex > 48):
                print("Infinite loop " + str(testIndex))
            #print("LOOP SELL")
            if self.bidIndex < len(self.bidArray) and (self.toSell > (float)(self.bidArray[self.bidIndex][1])):
                sold.append((float)(self.bidArray[self.bidIndex][0]))
                soldAm.append((float)(self.bidArray[self.bidIndex][1]))
                self.toSell -= (float)(self.bidArray[self.bidIndex][1])
                self.bidIndex += 1
            elif self.bidIndex < len(self.bidArray) and (self.toSell < (float)(bid[self.bidIndex][1])):
                sold.append((float)(self.bidArray[self.bidIndex][0]))
                soldAm.append(self.toSell)
                self.toSell = 0
            elif self.bidIndex >= len(self.bidArray):
                self.outOfBid = True
                self.toSell = 0
        
        weightedSells = 0
        totalSellsAmount = 0
        for x in range(len(sold)):
            weightedSells += sold[x]*soldAm[x]
            totalSellsAmount += soldAm[x]
        
        if(totalSellsAmount > 0):
            self.averageBidPrice =  weightedSells / totalSellsAmount
        else:
            self.averageBidPrice = 0

    def count_Percent(self):
        substract = self.averageBidPrice - self.averageAskPrice
        return substract / self.averageAskPrice   

def count_med(numbers):
    if len(numbers) == 0:
        return 0
    elif len(numbers) == 1:
        return numbers[0]
    elif len(numbers)%2 == 1:
        return numbers[math.floor(len(numbers)/2)]
    elif len(numbers)%2 == 0:
        return (numbers[(int)(len(numbers)/2)] + numbers[(int)(len(numbers)/2) - 1]) / 2

def count_numberToTrade(obj, currentArray, currentPair):
    numberToTrade = 0
    if(obj.stock.has_fee_def()):
        numberToTrade = obj.stock.withdraw_fee(currentPair)*100
    else:
        feesArray = []
        for z in range(len(currentArray)):
            if(currentArray[z].stock.has_fee_def()):
                feesArray.append(currentArray[z].stock.withdraw_fee(currentPair))
        
        feesArray.sort()
        countedMed = count_med(feesArray)
        numberToTrade = countedMed*100
    
    return numberToTrade

class MarketPair():
    def __init__(self, stock, pair):
        self.stock = stock
        self.pair = pair
        self.bestAsk = (float)(0)
        self.bestBid = (float)(0)
        self.asks = []
        self.bids = []
class Response():
    def __init__(self, stock, response):
        self.stock = stock
        self.response = response

symbolResponses = []
arr = []
arrOfUniques = []
arrays = []
toRemoveFromArrays = []

async def fetchSymbols(session, url, stock):
    async with session.get(url) as response:
        json_response = await response.json(content_type=None)
        symbolResponses.append(Response(stock, json_response))

async def taskSymbols():
    async with aiohttp.ClientSession() as session:
        tasks = [fetchSymbols(session, coinex.getSymbolsEndpoint(), coinex)]
        tasks.append(fetchSymbols(session, binance.getSymbolsEndpoint(), binance))
        tasks.append(fetchSymbols(session, kucoin.getSymbolsEndpoint(), kucoin))
        tasks.append(fetchSymbols(session, bithumb.getSymbolsEndpoint(), bithumb))
        tasks.append(fetchSymbols(session, bitrue.getSymbolsEndpoint(), bitrue))
        tasks.append(fetchSymbols(session, bibox.getSymbolsEndpoint(), bibox))
        tasks.append(fetchSymbols(session, bkex.getSymbolsEndpoint(), bkex))
        tasks.append(fetchSymbols(session, mxc.getSymbolsEndpoint(), mxc))
        #tasks.append(fetchSymbols(session, probit.getSymbolsEndpoint(), probit))
        await asyncio.gather(*tasks)

async def fetchAsks(session, url, stock, marketPair):
    async with session.get(url) as response:
        json_response = await response.json()

        marketPair.asks = marketPair.stock.getAsksResponse(json_response)
        if(len(marketPair.asks) > 1):
            marketPair.bestAsk = (float)(marketPair.asks[0][0])
        else:
            toRemoveFromArrays.append(marketPair)
        

async def fetchBids(session, url, stock, marketPair):
    async with session.get(url) as response:
        json_response = await response.json()

        marketPair.bids = marketPair.stock.getBidsResponse(json_response)
        if(len(marketPair.bids) > 1):
            marketPair.bestBid = (float)(marketPair.bids[0][0])
        else:
            toRemoveFromArrays.append(marketPair)

async def taskPrices():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(len(arrays)):
            for j in arrays[i]:
                tasks.append(fetchAsks(session, j.stock.getPairPriceEndpoint(j.pair), j.stock, j))
                tasks.append(fetchBids(session, j.stock.getPairPriceEndpoint(j.pair), j.stock, j))
        print(len(tasks))
        await asyncio.gather(*tasks)

def test():
    print(len(arrays))

def takeAsk(elem):
    return elem.bestAsk

def takeBid(elem):
    return elem.bestBid

if __name__ == "__main__":
    startTime = time.time()
    allTime = time.time()
    asyncio.run(taskSymbols())
    print(time.time() - startTime)

    for response in symbolResponses:
        for pair in response.stock.getSymbolResponse(response.response):
            arr.append(MarketPair(response.stock, pair))

    contains = False
    for x in arr:
        for y in arrOfUniques:
            if(y.pair == x.pair):
                contains = True
                continue
        if(contains == False):
            arrOfUniques.append(x)
        contains = False

    # create 3d array        
    arrays = [[arrOfUniques[i]] for i in range(len(arrOfUniques))]
    for i in range(len(arrays)):
        for j in range(len(arr)):
            if(arrays[i][0].pair == arr[j].pair) and (arrays[i][0].stock != arr[j].stock):
                arrays[i].append(arr[j])
    toRemove = []
    for i in range(len(arrays)):
        if(len(arrays[i]) < 2):
            toRemove.append(arrays[i])

    for i in range(len(toRemove)):
        arrays.remove(toRemove[i])

    print(len(arrays))
    startTime = time.time()
    asyncio.run(taskPrices())
    print(time.time() - startTime)
    for i in range(len(arrays)):
        for j in arrays[i]:
            for z in toRemoveFromArrays:
                if j == z and arrays[i].__contains__(j):
                    arrays[i].remove(j)

    toRemove = []
    for i in range(len(arrays)):
        if(len(arrays[i]) < 2):
            toRemove.append(arrays[i])

    for i in range(len(toRemove)):
        arrays.remove(toRemove[i])
    test()
    for i in range(len(arrays)):
        currentPair = arrays[i][0].pair

        arrays[i].sort(key = takeBid, reverse = True)
        highSellObj = arrays[i][0]
        highSell = (float)(arrays[i][0].bestBid)

        arrays[i].sort(key = takeAsk)
        lowBuyObj = arrays[i][0]
        lowBuy = (float)(arrays[i][0].bestAsk)
        
        if(lowBuy == 0 or highSell == 0):
            continue

        dif = highSell - lowBuy
        perc = dif / lowBuy
        if(perc > 0.03):
            
            ask = lowBuyObj.asks #buy from
            bid = highSellObj.bids #sell at
            
            toBuy = count_numberToTrade(lowBuyObj, arrays[i], currentPair)
            toSell = count_numberToTrade(highSellObj, arrays[i], currentPair)
            toBuyFinal = toBuy #for print
            
            if toBuy == 0 or toSell == 0:
                continue
            
            tradesSim = TradesSimulation(toBuy, ask, toSell, bid)
            # print(tradesSim.averageAskPrice)
            tradesSim.count_Asks()
            # print(tradesSim.averageAskPrice)
            tradesSim.count_Bids()
            
            if(tradesSim.averageAskPrice <= 0 or tradesSim.averageBidPrice <= 0):
                continue
                
            finalPercent = tradesSim.count_Percent() 
        
            if(finalPercent > 0.03) and ((lowBuyObj.stock.has_WD_def() and highSellObj.stock.has_WD_def() and highSellObj.stock.can_deposit(currentPair) and lowBuyObj.stock.can_withdraw(currentPair)) or (lowBuyObj.stock.has_WD_def() and not(highSellObj.stock.has_WD_def()) and lowBuyObj.stock.can_withdraw(currentPair)) or (highSellObj.stock.has_WD_def() and not(lowBuyObj.stock.has_WD_def()) and highSellObj.stock.can_deposit(currentPair))):
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%\nPercentage difference: \n" + (str)(perc) + "\n" + (str)(currentPair))
                if(tradesSim.outOfBid == True):
                    print("out of bid")
                if(tradesSim.outOfAsk == True):
                    print("out of ask")
                print(tradesSim.askIndex)
                print(tradesSim.bidIndex)
                print("To buy amount: " + str(toBuyFinal) + "\nWithdraw fee: " + str(toBuyFinal/100) + "\nbuy from: " + (str)(lowBuyObj.stock))
                if(lowBuyObj.stock.has_WD_def()):
                    print(lowBuyObj.stock.can_withdraw(currentPair))
                else:
                    print("dont know if lowbuyobj can withdraw")
                print("sell at: " + (str)(highSellObj.stock))
                if(highSellObj.stock.has_WD_def()):
                    print(highSellObj.stock.can_deposit(currentPair))
                else:
                    print("dont know if highSellObj can deposit")
                print((str)(datetime.now()) + "\nRealny zysk\n" + (str)(finalPercent) + "\n%%%%%%%%%%%%%%%%%%%%%%%%%%")
    
    test()
    print(time.time() - allTime)