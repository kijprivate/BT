import coinex as coinex
import mxc as mxc
import kucoin as kucoin
import bkex as bkex
import bilaxy as bilaxy
import liquid as liquid
import binance as binance
import bithumb as bithumb

#not working
#import coinsuper as coinsuper #connection timeout? maybe easy fix
#import huobi as huobi #signature
#import okex as okex #problems with signature even with api sample

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
    
if __name__ == '__main__':
    # get all symbols from market
    coinexSymbols = coinex.get_symbols()
    mxcSymbols = mxc.get_symbols()
    kucoinSymbols = kucoin.get_symbols()
    bkexSymbols = bkex.get_symbols()
    binanceSymbols = binance.get_symbols()
    bithumbSymbols = bithumb.get_symbols()
    bilaxySymbols = bilaxy.get_symbols()
    liquidSymbols = liquid.get_symbols()
    
    # group as pair of values - name of market and currency pair
    initTuple = tuple_array(coinex, coinexSymbols)
    mxcTuple = tuple_array(mxc, mxcSymbols)
    kucoinTuple = tuple_array(kucoin, kucoinSymbols)
    bkexTuple = tuple_array(bkex, bkexSymbols)
    binanceTuple = tuple_array(binance, binanceSymbols)
    bithumbTuple = tuple_array(bithumb, bithumbSymbols)
    bilaxyTuple = tuple_array(bilaxy, bilaxySymbols)
    liquidTuple = tuple_array(liquid, liquidSymbols)
    
    # add uniques to array
    initTuple = add_uniques_to_array(initTuple, mxcTuple)
    initTuple = add_uniques_to_array(initTuple, kucoinTuple)
    initTuple = add_uniques_to_array(initTuple, bkexTuple)
    initTuple = add_uniques_to_array(initTuple, binanceTuple)
    initTuple = add_uniques_to_array(initTuple, bithumbTuple)
    initTuple = add_uniques_to_array(initTuple, bilaxyTuple)
    initTuple = add_uniques_to_array(initTuple, liquidTuple)
    
    # create 3d array        
    arrays = [[initTuple[i]] for i in range(len(initTuple))]

    # add elements to arrays
    arrays = add_same_elements(arrays, initTuple)
    arrays = add_same_elements(arrays, mxcTuple)
    arrays = add_same_elements(arrays, kucoinTuple)
    arrays = add_same_elements(arrays, bkexTuple)
    arrays = add_same_elements(arrays, binanceTuple)
    arrays = add_same_elements(arrays, bithumbTuple)
    arrays = add_same_elements(arrays, bilaxyTuple)
    arrays = add_same_elements(arrays, liquidTuple)
    
    toRemove = []
    for i in range(len(arrays)):
        if(len(arrays[i]) < 2):
            toRemove.append(arrays[i])
    
    for i in range(len(toRemove)):
        arrays.remove(toRemove[i])

    lowBuy = 99999
    highSell = 0
    
    lowBuyObj = None
    highSellObj = None

    numbers = []
    stocks = []
    
    print("START " + str(datetime.now()))
    #TODO spread?
    #TODO handle can deposit/withdraw
    #TODO handle not active coins
    while True:
        for i in range(len(arrays)):
            for j in range(len(arrays[i])):

                time.sleep(0.2)
                ret = (float)(arrays[i][j][0].get_pair_sell(arrays[i][j][1]))
                ret2 = (float)(arrays[i][j][0].get_pair_buy(arrays[i][j][1]))
                    
                numbers.append(ret)
                stocks.append((arrays[i][j][0]))
    
                if(ret < lowBuy):
                    lowBuy = ret
                    lowBuyObj = arrays[i][j][0]
                    
                if(ret2 > highSell):
                    highSell = ret2
                    highSellObj = arrays[i][j][0]
    
            if (len(arrays[i]) > 1) and lowBuy > 0:
                dif = highSell - lowBuy
                if(dif > 0):
                    perc = dif / lowBuy
                    perc = perc*100
    
                    if(perc > 3):
                        
                        if(lowBuyObj == None or highSellObj == None):
                            continue
                        
                        ask = lowBuyObj.get_orders_asks(arrays[i][j][1], 20) #buy from
                        bid = highSellObj.get_orders_bids(arrays[i][j][1], 20) #sell at
                        
                        if(ask == None or bid == None):
                            continue
                        
                        if(lowBuyObj.has_fee_def()):
                            toBuy = lowBuyObj.withdraw_fee(arrays[i][j][1])*100
                        else:
                            stocksArray = []
                            for z in range(len(arrays[i])):
                                if(arrays[i][z][0].has_fee_def()):
                                    stocksArray.append(arrays[i][z][0].withdraw_fee(arrays[i][z][1]))
                                
                            countedMed = count_med(stocksArray)
                            toBuy = countedMed*100

                        if(highSellObj.has_fee_def()):
                            toSell = highSellObj.withdraw_fee(arrays[i][j][1])*100
                        else:
                            stocksArray = []
                            for z in range(len(arrays[i])):
                                if(arrays[i][z][0].has_fee_def()):
                                    stocksArray.append(arrays[i][z][0].withdraw_fee(arrays[i][z][1]))
                                
                            countedMed = count_med(stocksArray)
                            toSell = countedMed*100
                            
                        
                        if toBuy == 0 or toSell == 0:
                            continue
                        
                        boughts = []
                        sold = []
                        boughtsAm = []
                        soldAm = []
                        toBuyFinal = toBuy
                        l = 0
                        outOfAsk = False
                        while(toBuy > 0):
                            if l < len(ask) and (toBuy > (float)(ask[l][1])):
                                boughts.append((float)(ask[l][0]))
                                boughtsAm.append((float)(ask[l][1]))
                                toBuy -= (float)(ask[l][1])
                                l += 1
                            elif l < len(ask) and (toBuy < (float)(ask[l][1])):
                                boughts.append((float)(ask[l][0]))
                                boughtsAm.append(toBuy)
                                toBuy = 0
                            elif( l >= len(ask)):
                                outOfAsk = True
                                toBuy = 0
                        k = 0   
                        outOfBid = False
                        while(toSell > 0):
                            if k < len(bid) and (toSell > (float)(bid[k][1])):
                                sold.append((float)(bid[k][0]))
                                soldAm.append((float)(bid[k][1]))
                                toSell -= (float)(bid[k][1])
                                k += 1
                            elif k < len(bid) and (toSell < (float)(bid[k][1])):
                                sold.append((float)(bid[k][0]))
                                soldAm.append(toSell)
                                toSell = 0
                            elif k >= len(bid):
                                outOfBid = True
                                toSell = 0
                        
                        wb = 0
                        srb = 0
                        for x in range(len(boughts)):
                            wb += boughts[x]*boughtsAm[x]
                            srb += boughtsAm[x]
                        
                        ws = 0
                        srs = 0
                        for x in range(len(sold)):
                            ws += sold[x]*soldAm[x]
                            srs += soldAm[x]
                          
                        if(srs > 0) and (srb > 0):
                            sredniacenakupna = wb / srb
                            sredniacenasprzedazy = ws / srs
                            roznica = sredniacenasprzedazy - sredniacenakupna
                            procent = roznica / sredniacenakupna
                        
                            if(procent > 0.03) and ((lowBuyObj.has_WD_def() and highSellObj.has_WD_def() and highSellObj.can_deposit(arrays[i][j][1]) and lowBuyObj.can_withdraw(arrays[i][j][1])) or (lowBuyObj.has_WD_def() and not(highSellObj.has_WD_def()) and lowBuyObj.can_withdraw(arrays[i][j][1])) or (highSellObj.has_WD_def() and not(lowBuyObj.has_WD_def()) and highSellObj.can_deposit(arrays[i][j][1]))):
                                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                                print("Percentage difference: ")
                                print(perc)
                                print(arrays[i][j][1])
                                if(outOfBid == True):
                                    print("out of bid")
                                if(outOfAsk == True):
                                    print("out of ask")
                                print(l)
                                print(k)
                                print("To buy amount: " + str(toBuyFinal))
                                print("Withdraw fee: " + str(toBuyFinal/100))
                                print("buy from: " + (str)(lowBuyObj))
                                if(lowBuyObj.has_WD_def()):
                                    print(lowBuyObj.can_withdraw(arrays[i][j][1]))
                                else:
                                    print("dont know if lowbuyobj can withdraw")
                                print("sell at: " + (str)(highSellObj))
                                if(highSellObj.has_WD_def()):
                                    print(highSellObj.can_deposit(arrays[i][j][1]))
                                else:
                                    print("dont know if highSellObj can deposit")
                                print(datetime.now())
                                print("Realny zysk")
                                print(procent)
                                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        else:
                            print("no bid or ask")
                            print(len(arrays[i]))
    
            if False and (len(arrays[i]) > 2):
                test = tuple_array2(numbers, stocks)
                test.sort()
                numbers.sort()
                med = count_med(numbers)
                val = (med - numbers[0])/med
                
                if(val > 0.03) and val < 0.5:
                    print("med")
                    print(val)
                    print(arrays[i][j][1])
                    print(test[0][1])
                    print(test[0][2].can_deposit(arrays[i][j][1]))
                    print(test[0][2].can_withdraw(arrays[i][j][1]))
                    print(datetime.now())
       
                
            lowBuy = 99999
            highSell = 0
            lowBuyObj = None
            highSellObj = None
            numbers = []
            stocks = []
    
