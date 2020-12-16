import coinex as coinex
import mxc as mxc
import kucoin as kucoin
import bkex as bkex
import binance as binance
import bithumb as bithumb
import cryptology as cryptology
import bitrue as bitrue
import bibox as bibox
import cexio as cexio
#not working
#import coinsuper as coinsuper #connection timeout? maybe easy fix
#import huobi as huobi #signature
#import okex as okex #SCAM ALERT???? #problems with signature even with api sample

#verification required
#import bilaxy as bilaxy
#import liquid as liquid

from datetime import datetime
import time
import math

def tuple_array(tupleSymbol, inputArray):
    finalArray = []
    for x in inputArray:
        v = tupleSymbol, x
        finalArray.append(v)
    return finalArray

def tuple_array2(stocks, inputArray):
    finalArray = []
    i = 0
    for x in inputArray:
        v = stocks[i], (str)(x), x 
        i+=1
        finalArray.append(v)
    return finalArray

def add_uniques_to_array(inArray, arrayToAdd):
    contain = False
    toAdd = []
    for i in range(len(arrayToAdd)):
        for j in range(len(inArray)):
            if(arrayToAdd[i][1] == inArray[j][1]):
                contain = True
                continue
        if contain == False:
            toAdd.append(arrayToAdd[i])
        contain = False

    for x in toAdd:
        inArray.append(x)
    
    return inArray

def add_same_elements(inArray, arrayToAdd):
    for i in range(len(inArray)):
        for j in range(len(arrayToAdd)):
            if(inArray[i][0][1] == arrayToAdd[j][1]) and (inArray[i][0][0] != arrayToAdd[j][0]):
                inArray[i].append(arrayToAdd[j])
    
    return inArray

def count_med(numbers):
    if len(numbers) == 0:
        return 0
    elif len(numbers) == 1:
        return numbers[0]
    elif len(numbers)%2 == 1:
        return numbers[math.floor(len(numbers)/2)]
    elif len(numbers)%2 == 0:
        return (numbers[(int)(len(numbers)/2)] + numbers[(int)(len(numbers)/2) - 1]) / 2

def get_highSellObj(currentArray, currentPair):
    highSell = 0
    highSellObj = None
    for i in range(len(currentArray)):
        val = currentArray[i][0].get_pair_buy(currentPair)
        if(val > highSell):
            highSell = val
            highSellObj = currentArray[i][0]
            
    return highSellObj

def get_lowBuyObj(currentArray, currentPair):
    lowBuy = 9999999
    lowBuyObj = None     
    for i in range(len(currentArray)):
        val = currentArray[i][0].get_pair_sell(currentPair)
        if(val < lowBuy):
            lowBuy = val
            lowBuyObj = currentArray[i][0]

    return lowBuyObj

def get_highestSpread(currentArray, currentPair):
    highSell = 0
    for i in range(len(currentArray)):
        if((currentArray[i][0].get_pair_sell(currentPair) == 0) or currentArray[i][0].get_pair_buy(currentPair) == 0):
            continue
        val = (currentArray[i][0].get_pair_sell(currentPair) - currentArray[i][0].get_pair_buy(currentPair)) / currentArray[i][0].get_pair_sell(currentPair)
        if(val > highSell):
            highSell = val
            
    return highSell

def get_lowestSpread(currentArray, currentPair):
    lowBuy = 9999999
    for i in range(len(currentArray)):
        if((currentArray[i][0].get_pair_sell(currentPair) == 0) or currentArray[i][0].get_pair_buy(currentPair) == 0):
            continue
        val = (currentArray[i][0].get_pair_sell(currentPair) - currentArray[i][0].get_pair_buy(currentPair)) / currentArray[i][0].get_pair_sell(currentPair)
        if(val < lowBuy):
            lowBuy = val
    if(lowBuy == 9999999):
        return 0
    
    return lowBuy

def count_numberToTrade(obj, currentArray, currentPair):
    numberToTrade = 0
    if(obj.has_fee_def()):
        numberToTrade = obj.withdraw_fee(currentPair)*100
    else:
        feesArray = []
        for z in range(len(currentArray)):
            if(currentArray[z][0].has_fee_def()):
                feesArray.append(currentArray[z][0].withdraw_fee(currentPair))
        
        feesArray.sort()
        countedMed = count_med(feesArray)
        numberToTrade = countedMed*100
    
    return numberToTrade

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
            self.averageBidPrice = 0;

    def count_Percent(self):
        substract = self.averageBidPrice - self.averageAskPrice
        return substract / self.averageAskPrice   
        
if __name__ == '__main__':
    startTime = time.time()
    print(cexio.get_pair("ETHBTC"))
    
    print("tu")
    #for _ in range(868):
    #    coinex.get_symbols()
    #print(time.time() - startTime)
   # print(coinex.get_orders("ETHBTC", 20))
    # get all symbols from market
    coinexSymbols = coinex.get_symbols()
    mxcSymbols = mxc.get_symbols()
    kucoinSymbols = kucoin.get_symbols()
    bkexSymbols = bkex.get_symbols()
    binanceSymbols = binance.get_symbols()
    bithumbSymbols = bithumb.get_symbols()
    bitrueSymbols = bitrue.get_symbols()
    biboxSymbols = bibox.get_symbols()
    
    # group as pair of values - name of market and currency pair
    initTuple = tuple_array(coinex, coinexSymbols)
    mxcTuple = tuple_array(mxc, mxcSymbols)
    kucoinTuple = tuple_array(kucoin, kucoinSymbols)
    bkexTuple = tuple_array(bkex, bkexSymbols)
    binanceTuple = tuple_array(binance, binanceSymbols)
    bithumbTuple = tuple_array(bithumb, bithumbSymbols)
    bitrueTuple = tuple_array(bitrue, bitrueSymbols)
    biboxTuple = tuple_array(bibox, biboxSymbols)
    
    # add uniques to array
    initTuple = add_uniques_to_array(initTuple, mxcTuple)
    initTuple = add_uniques_to_array(initTuple, kucoinTuple)
    initTuple = add_uniques_to_array(initTuple, bkexTuple)
    initTuple = add_uniques_to_array(initTuple, binanceTuple)
    initTuple = add_uniques_to_array(initTuple, bithumbTuple)
    initTuple = add_uniques_to_array(initTuple, bitrueTuple)
    initTuple = add_uniques_to_array(initTuple, biboxTuple)
    
    # create 3d array        
    arrays = [[initTuple[i]] for i in range(len(initTuple))]

    # add elements to arrays
    arrays = add_same_elements(arrays, initTuple)
    arrays = add_same_elements(arrays, mxcTuple)
    arrays = add_same_elements(arrays, kucoinTuple)
    arrays = add_same_elements(arrays, bkexTuple)
    arrays = add_same_elements(arrays, binanceTuple)
    arrays = add_same_elements(arrays, bithumbTuple)
    arrays = add_same_elements(arrays, bitrueTuple)
    arrays = add_same_elements(arrays, biboxTuple)
    
    toRemove = []
    for i in range(len(arrays)):
        if(len(arrays[i]) < 2):
            toRemove.append(arrays[i])
    
    for i in range(len(toRemove)):
        arrays.remove(toRemove[i])

    numbers = []
    stocks = []
    
    #print("START " + str(datetime.now()))

    #10,17 mins without coinex
    #TODO replace USD with smth that omit USDT
    #TODO handle '-' and '_' in 4 digit pairs (USDT), can depo/withd
    #TODO handle not active coins
    while True:
        print("START " + str(datetime.now()))
        for i in range(len(arrays)):
            currentPair = arrays[i][0][1]
            highSellObj = get_highSellObj(arrays[i], currentPair)
            if highSellObj == None:
                continue
            highSell = highSellObj.get_pair_sell(currentPair)
            lowBuyObj = get_lowBuyObj(arrays[i], currentPair)
            if lowBuyObj == None:
                continue
            lowBuy = lowBuyObj.get_pair_buy(currentPair)
            
            #if(get_highestSpread(arrays[i], currentPair) > 0.1 and get_lowestSpread(arrays[i], currentPair) < 0.02):
            #    print("Spread \n " + str(arrays[i]))
            #print("P " + str(datetime.now()))
            if (len(arrays[i]) > 1) and lowBuy > 0:
                dif = highSell - lowBuy
                perc = dif / lowBuy
                if(perc > 0.03):
                    
                    if(lowBuyObj == None or highSellObj == None):
                        continue
                    
                    ask = lowBuyObj.get_orders_asks(currentPair, 20) #buy from
                    bid = highSellObj.get_orders_bids(currentPair, 20) #sell at
                    
                    if(ask == None or bid == None):
                        continue
                    
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
                
                    if(finalPercent > 0.03) and ((lowBuyObj.has_WD_def() and highSellObj.has_WD_def() and highSellObj.can_deposit(currentPair) and lowBuyObj.can_withdraw(currentPair)) or (lowBuyObj.has_WD_def() and not(highSellObj.has_WD_def()) and lowBuyObj.can_withdraw(currentPair)) or (highSellObj.has_WD_def() and not(lowBuyObj.has_WD_def()) and highSellObj.can_deposit(currentPair))):
                        print("%%%%%%%%%%%%%%%%%%%%%%%%%%\nPercentage difference: \n" + (str)(perc) + "\n" + (str)(currentPair))
                        if(tradesSim.outOfBid == True):
                            print("out of bid")
                        if(tradesSim.outOfAsk == True):
                            print("out of ask")
                        print(tradesSim.askIndex)
                        print(tradesSim.bidIndex)
                        print("To buy amount: " + str(toBuyFinal) + "\nWithdraw fee: " + str(toBuyFinal/100) + "\nbuy from: " + (str)(lowBuyObj))
                        if(lowBuyObj.has_WD_def()):
                            print(lowBuyObj.can_withdraw(currentPair))
                        else:
                            print("dont know if lowbuyobj can withdraw")
                        print("sell at: " + (str)(highSellObj))
                        if(highSellObj.has_WD_def()):
                            print(highSellObj.can_deposit(currentPair))
                        else:
                            print("dont know if highSellObj can deposit")
                        print((str)(datetime.now()) + "\nRealny zysk\n" + (str)(finalPercent) + "\n%%%%%%%%%%%%%%%%%%%%%%%%%%")

            if False and (len(arrays[i]) > 2):
                test = tuple_array2(numbers, stocks)
                test.sort()
                numbers.sort()
                med = count_med(numbers)
                val = (med - numbers[0])/med
                
                if(val > 0.03) and val < 0.5:
                    print("med")
                    print(val)
                    print(currentPair)
                    print(test[0][1])
                    print(test[0][2].can_deposit(currentPair))
                    print(test[0][2].can_withdraw(currentPair))
                    print(datetime.now())
       
        
            numbers = []
            stocks = []
            #print("TU " + str(datetime.now()))
        print("End " + str(datetime.now()))
