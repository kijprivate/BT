import coinex as coinex
import mxc as mxc
import kucoin as kucoin
import bkex as bkex
import bilaxy as bilaxy
import liquid as liquid
import huobi as huobi
import binance as binance
import bithumb as bithumb
import coinsuper as coinsuper
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
    if len(numbers)%2 == 1:
        return numbers[math.floor(len(numbers)/2)]
    elif len(numbers)%2 == 0:
        return (numbers[(int)(len(numbers)/2)] + numbers[(int)(len(numbers)/2) - 1]) / 2
    
if __name__ == '__main__':
    
    # get all symbols from market
    coinexSymbols = coinex.get_symbols()
    mxcSymbols = mxc.get_symbols()
    kucoinSymbols = kucoin.get_symbols()
  #  bkexSymbols = bkex.get_symbols()
    binanceSymbols = binance.get_symbols()
    #bithumbSymbols = bithumb.get_symbols()
   # bilaxySymbols = bilaxy.get_symbols()
   # liquidSymbols = liquid.get_symbols()
    
    # group as pair of values - name of market and currency pair
    initTuple = tuple_array(coinex, coinexSymbols)
    mxcTuple = tuple_array(mxc, mxcSymbols)
    kucoinTuple = tuple_array(kucoin, kucoinSymbols)
  #  bkexTuple = tuple_array(bkex, bkexSymbols)
    binanceTuple = tuple_array(binance, binanceSymbols)
    #bithumbTuple = tuple_array(bithumb, bithumbSymbols)
   # bilaxyTuple = tuple_array(bilaxy, bilaxySymbols)
   # liquidTuple = tuple_array(liquid, liquidSymbols)
    
    # add uniques to array
    initTuple = add_uniques_to_array(initTuple, mxcTuple)
    initTuple = add_uniques_to_array(initTuple, kucoinTuple)
    #initTuple = add_uniques_to_array(initTuple, bkexTuple)
    initTuple = add_uniques_to_array(initTuple, binanceTuple)
    #initTuple = add_uniques_to_array(initTuple, bithumbTuple)
    #initTuple = add_uniques_to_array(initTuple, bilaxyTuple)
   # initTuple = add_uniques_to_array(initTuple, liquidTuple)
    
    # create 3d array        
    arrays = [[initTuple[i]] for i in range(len(initTuple))]

    # add elements to arrays
    arrays = add_same_elements(arrays, initTuple)
    arrays = add_same_elements(arrays, mxcTuple)
    arrays = add_same_elements(arrays, kucoinTuple)
   # arrays = add_same_elements(arrays, bkexTuple)
    arrays = add_same_elements(arrays, binanceTuple)
    #arrays = add_same_elements(arrays, bithumbTuple)
   # arrays = add_same_elements(arrays, bilaxyTuple)
   # arrays = add_same_elements(arrays, liquidTuple)
    
    toRemove = []
    for i in range(len(arrays)):
        if(len(arrays[i]) < 2):
            toRemove.append(arrays[i])
    
    for i in range(len(toRemove)):
        arrays.remove(toRemove[i])

    lowBuy = 99999
    highSell = 0
    
    lowBuyStr = ""
    highSellStr = ""
    
    lowBuyObj = None
    highSellObj = None
    
    print(coinex.can_deposit('KSMBTC'))
    print(coinex.can_withdraw('KSMETH'))

    numbers = []
    stocks = []
    
    starttime = datetime.now()
    print(datetime.now())

    while True:
#        try:
        for i in range(len(arrays)):
            for j in range(len(arrays[i])):
                #if(len(arrays[i]) > 1):
                time.sleep(2)
                #ret = arrays[i][j][0].get_pair_sell(arrays[i][j][1])
    
                ret = (float)(arrays[i][j][0].get_pair_sell(arrays[i][j][1]))
                ret2 = (float)(arrays[i][j][0].get_pair_buy(arrays[i][j][1]))
                #if((ret-ret2)/ret > 0.05):
                #    print("duzy spread")
                #    print((ret-ret2)/ret)
                #    print(arrays[i][j][0])
                #    print(arrays[i][j][1])
                    
                numbers.append(ret)
    
                stocks.append((arrays[i][j][0]))
    
                if(ret < lowBuy):
                    lowBuy = ret
                    lowBuyStr = str(arrays[i][j][0])
                    lowBuyObj = arrays[i][j][0]
    
                #if(len(arrays[i]) > 2):
                #    numbers.append(ret)
                    
                ret2 = arrays[i][j][0].get_pair_buy(arrays[i][j][1])
                if(ret2 > highSell):
                    highSell = ret2
                    highSellStr = str(arrays[i][j][0])
                    highSellObj = arrays[i][j][0]
    
            if (len(arrays[i]) > 1) and lowBuy > 0:
                dif = highSell - lowBuy
                if(dif > 0):
                    perc = dif / lowBuy
                    perc = perc*100
    
                    if(perc > 3): #and lowBuyObj.can_deposit(arrays[i][j][1]) and lowBuyObj.can_withdraw(arrays[i][j][1]) and highSellObj.can_deposit(arrays[i][j][1]) and highSellObj.can_withdraw(arrays[i][j][1]):
                        
                        if(lowBuyObj == None or highSellObj == None):
                            continue
                        
                        ask = lowBuyObj.get_orders_asks(arrays[i][j][1], 20) #buy from
                        bid = highSellObj.get_orders_bids(arrays[i][j][1], 20) #sell at
                        
                        if lowBuyObj == mxc or lowBuyObj == binance:
                            toBuy = highSellObj.withdraw_fee(arrays[i][j][1])*100
                            toSell = highSellObj.withdraw_fee(arrays[i][j][1])*100
                        elif highSellObj == mxc or highSellObj == binance:
                            toBuy = lowBuyObj.withdraw_fee(arrays[i][j][1])*100
                            toSell = lowBuyObj.withdraw_fee(arrays[i][j][1])*100
                        else:
                            toBuy = lowBuyObj.withdraw_fee(arrays[i][j][1])*100
                            toSell = highSellObj.withdraw_fee(arrays[i][j][1])*100
                        
                        boughts = []
                        sold = []
                        boughtsAm = []
                        soldAm = []
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
                        
                            if(procent > 0.03):
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
                                print("buy from: " + lowBuyStr)
                                print("sell at: " + highSellStr)
                                print(len(arrays[i]))
                                print(datetime.now())
                                print("Realny zysk")
                                print(procent)
                                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                        else:
                            print("no bid or ask")
                            print(len(arrays[i]))
            
            if False and (len(arrays[i]) > 1):
                test = tuple_array2(numbers, stocks)
                test.sort()
                dif = (test[len(test) - 1][0] - test[0][0]) / test[len(test) - 1][0]
                if(dif > 0.04) and dif < 0.5:
                    print("Percentage difference: ")
                    print(dif)
                    print(arrays[i][j][1])
                    print("Buyu")
                    print(test[0][1])
                    print(test[0][2].can_deposit(arrays[i][j][1]))
                    print(test[0][2].can_withdraw(arrays[i][j][1]))
                    print("sell")
                    print(test[len(test) - 1][1])
                    print(test[len(test) - 1][2].can_deposit(arrays[i][j][1]))
                    print(test[len(test) - 1][2].can_withdraw(arrays[i][j][1]))
                    print(datetime.now())
    
            if(len(arrays[i]) > 2):
                test = tuple_array2(numbers, stocks)
                test.sort()
                numbers.sort()
                med = count_med(numbers)
                #val = (med - lowBuy)/med
                val = (med - numbers[0])/med
                
                if(val > 0.03):
                    print("med")
                    print(val)
                    print(arrays[i][j][1])
                    print(test[0][1])
                    print(test[0][2].can_deposit(arrays[i][j][1]))
                    print(test[0][2].can_withdraw(arrays[i][j][1]))
                    print(datetime.now())
                    
                if False and (val > 0.02) and lowBuyObj.can_deposit(arrays[i][j][1]) and lowBuyObj.can_withdraw(arrays[i][j][1]):
                    print("perc mediana")
                    print(val)
                    print(arrays[i][j][1])
                    print(lowBuyStr)
                    print(lowBuyObj.can_deposit(arrays[i][j][1]))
                    print(lowBuyObj.can_withdraw(arrays[i][j][1]))
       
                
            lowBuy = 99999
            highSell = 0
            lowBuyObj = None
            highSellObj = None
            lowBuyStr = ""
            highSellStr = ""
            numbers = []
            stocks = []
       # except:
      #      print("finish")
    
    endtime = datetime.now() - starttime
    print(datetime.now())
    print(endtime)
