def get_pair_min(pair):
    request_client = RequestClient()
    params = {
        'market': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/market/detail'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    print (var.get('data', {}).get('min_amount'))
    return (float)(var.get('data', {}).get('min_amount'))

def order_pending(market_type):
    request_client = RequestClient()
    params = {
        'market': market_type
    }
    response = request_client.request(
            'GET',
            '{url}/v1/order/pending'.format(url=request_client.url),
            params=params
    )
    print(response.content)


def order_finished(market_type, page, limit):
    request_client = RequestClient()
    params = {
        'market': market_type,
        'page': page,
        'limit': limit
    }
    response = request_client.request(
            'GET',
            '{url}/v1/order/finished'.format(url=request_client.url),
            params=params
    )
    print (response.status)
    
def get_pair_last(pair):
    return (float)(pair.get('data', {}).get('ticker').get('last'))
    
def get_pair(pair):
    request_client = RequestClient()
    params = {
        'market': pair
    }
    response = request_client.request(
            'GET',
            '{url}/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def get_pair_sellAmount(pair):
    return (float)(pair.get('data', {}).get('ticker').get('sell_amount'))

def get_pair_buyAmount(pair):
    return (float)(pair.get('data', {}).get('ticker').get('buy_amount'))

def get_kline(pair):
    request_client = RequestClient()
    params = {
        'market': pair,
        'type': '5min',
        'limit': 500
    }
    response = request_client.request(
            'GET',
            '{url}/v1/market/kline'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data)
    return var

def count_sma(offset, period, data, priceType):
    index = offset
    endIndex = index + period
    priceSum = 0
    while index < endIndex:
        priceSum += get_price(data, index, priceType)
        index += 1
        
    return priceSum / period

def count_pK(offset, period, data):
    index = offset
    endIndex = index + period
    lowArr = []
    highArr = []
    while index < endIndex:
        highArr.append(get_price(data, index, 3))
        lowArr.append(get_price(data, index, 4))
        index += 1
        
    lowArr.sort()
    highArr.sort()
    highArr.reverse()
    lowest = lowArr[0]
    highest = highArr[0]
    lastClose = get_price(data, offset, 2)

    return (lastClose - lowest) / (highest - lowest)

def count_pD(data):
    one = (get_price(data, 1, 2) - get_price(data, 1, 4)) / (get_price(data, 1, 3) - get_price(data, 1, 4))
    two = (get_price(data, 2, 2) - get_price(data, 2, 4)) / (get_price(data, 2, 3) - get_price(data, 2, 4))
    three = (get_price(data, 3, 2) - get_price(data, 3, 4)) / (get_price(data, 3, 3) - get_price(data, 3, 4))
    print(one)
    print(two)
    print(three)
    return (one + two + three) / 3
        

def put_limit(amount, price, side, pair):
    request_client = RequestClient()
    data = {
            "amount": amount,
            "price": price,
            "type": side,
            "market": pair
        }

    response = request_client.request(
            'POST',
            '{url}/v1/order/limit'.format(url=request_client.url),
            json=data,
    )
    print(response.data)
    return complex_json.loads(response.data)


def put_market(market, amount, side):
    request_client = RequestClient()

    data = {
            "market": market,
            "amount": str(amount),
            "side": str(side)
            #"use_cet": 1
        }

    response = request_client.request(
            'POST',
            '{url}/perpetual/v1/order/put_market'.format(url=request_client.url),
            json=data,
    )
    print(response.data)

def put_limit_perpetual(amount, price, side, pair):
    request_client = RequestClient()
    data = {
            'market': pair,
            'effect_type': 1,
            'side': side,
            'amount': str(amount),
            'price': str(price)
        }

    response = request_client.request(
            'POST',
            '{url}/perpetual/v1/order/put_limit'.format(url=request_client.url),
            json=data,
    )
    print(response.data)
    return complex_json.loads(response.data)

def cancel_order(id, market):
    request_client = RequestClient()
    data = {
        "id": id,
        "market": market,
    }
    print(market)

    response = request_client.request(
            'DELETE',
            '{url}/v1/order/pending'.format(url=request_client.url),
            params=data,
    )
    return response.data    
    
def get_symbols():
    request_client = RequestClient()
    params = {}
    response = request_client.request(
            'GET',
            '{url}/v1/market/list'.format(url=request_client.url),
            params=params
    )
    var = []
    var = complex_json.loads(response.data).get('data', {})
    newarr = []
    for x in var:
        if("USD" in x) or not("BTC" in x[-3:]) or ('CHZBTC' in x) or ('CETBTC' in x):
            continue
        newarr.append(x)

    return newarr

def open_24h(pair):
    request_client = RequestClient()
    params = { "market": pair}
    response = request_client.request(
            'GET',
            '{url}/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {}).get('ticker', {}).get('open')
    return (float)(var)

def last_24h(pair):
    request_client = RequestClient()
    params = { "market": pair}
    response = request_client.request(
            'GET',
            '{url}/v1/market/ticker'.format(url=request_client.url),
            params=params
    )
    var = complex_json.loads(response.data).get('data', {}).get('ticker', {}).get('last')
    return (float)(var)

def takeFirst(elem):
    return elem[0]

def count_24h_change(pairArray):
    newarr = []
    for x in pairArray:
        time.sleep(1)
        spread = (get_pair_sell(get_pair(x)) - get_pair_buy(get_pair(x)))/get_pair_sell(get_pair(x))
        if spread > 0.005:
            continue
        t = (last_24h(x) - open_24h(x))/last_24h(x), x
        newarr.append(t)
        newarr.sort(key=takeFirst)
        
    #newarr.reverse()
    return newarr

def count_24h_change2(pairArray):
    newarr = []
    for x in pairArray:
        time.sleep(1)
        t = (last_24h(x[1]) - open_24h(x[1]))/last_24h(x[1]), x[1]
        newarr.append(t)
        newarr.sort(key=takeFirst)
        
    #newarr.reverse()
    return newarr


def change_vsBTC(pair):
    p = (last_24h(pair) - open_24h(pair))/last_24h(pair)

    if(p > 0.02):
        return True
    elif(p < 0.02):
        return False

def check(vp, worst):
    time.sleep(1)
    try:
        if worst == False:
            vp.kline = get_kline(vp.pair)
            vp.cur = count_sma(1, vp.firstsma, vp.kline, vp.priceType) - count_sma(1,vp.secondsma, vp.kline, vp.priceType)
            change = change_vsBTC(vp.pair)
            #print(count_sma(1, 200, vp.kline, vp.priceType))
            if(vp.prev < 0) and (vp.cur > 0) and (vp.isBought == False):
                print(vp.prev)
                print(vp.cur)
                print("przebicie od dołu " + vp.pair + " buy")
                print(get_pair_sell(get_pair(vp.pair)))#praw
                print(get_pair_buy(get_pair(vp.pair)))
                print(datetime.now())
                vp.isBought = True
                vp.minuteBought = datetime.now().minute
            elif(vp.prev > 0) and (vp.cur < 0) and (vp.isBought == True):
                print(vp.prev)
                print(vp.cur)
                print("przebicie od góry " + vp.pair + " sell")
                print(get_pair_sell(get_pair(vp.pair)))
                print(get_pair_buy(get_pair(vp.pair)))# praw
                print(datetime.now())
                vp.minuteBought = 3
                vp.checkedFirstCandy = False
                vp.isBought = False
    
            if vp.checkedFirstCandy == False and vp.isBought == True:
                currentMinute = datetime.now().minute
                if(currentMinute == 30 or currentMinute == 0):
                    if(currentMinute != vp.minuteBought):
                        vp.checkedFirstCandy = True
                        diff = get_price(vp.kline,1,2) - get_price(vp.kline,1,1)
                        if(diff < 0) and (diff/get_price(vp.kline,1,2) > 0.005):
                            print("close position cut loses")
                            print(vp.pair)
                            print(get_pair_sell(get_pair(vp.pair)))
                            print(get_pair_buy(get_pair(vp.pair)))# praw
                            print(datetime.now())
                            vp.minuteBought = 3
                            vp.checkedFirstCandy = False
                            vp.isBought = False
        
            vp.prev = vp.cur
        elif worst == True:
            vp.kline = get_kline(vp.pair)
            vp.cur = count_sma(1, vp.firstsma, vp.kline, vp.priceType) - count_sma(1,vp.secondsma, vp.kline, vp.priceType)
            #change = change_vsBTC(vp.pair)
        
            if(vp.prev < 0) and (vp.cur > 0) and (vp.isBought == False):
                print(vp.prev)
                print(vp.cur)
                print("przebicie od dołu worst" + vp.pair + " buy")
                print(get_pair_sell(get_pair(vp.pair)))#praw
                print(get_pair_buy(get_pair(vp.pair)))
                print(datetime.now())
                vp.isBought = True
                vp.minuteBought = datetime.now().minute
            elif(vp.prev > 0) and (vp.cur < 0) and (vp.isBought == True):
                print(vp.prev)
                print(vp.cur)
                print("przebicie od góry worst" + vp.pair + " sell")
                print(get_pair_sell(get_pair(vp.pair)))
                print(get_pair_buy(get_pair(vp.pair)))# praw
                print(datetime.now())
                vp.minuteBought = 3
                vp.checkedFirstCandy = False
                vp.isBought = False
    
            if vp.checkedFirstCandy == False and vp.isBought == True:
                currentMinute = datetime.now().minute
                if(currentMinute == 30 or currentMinute == 0):
                    if(currentMinute != vp.minuteBought):
                        vp.checkedFirstCandy = True
                        diff = get_price(vp.kline,1,2) - get_price(vp.kline,1,1)
                        if(diff < 0) and (diff/get_price(vp.kline,1,2) > 0.005):
                            print("close position cut loses worst")
                            print(vp.pair)
                            print(get_pair_sell(get_pair(vp.pair)))
                            print(get_pair_buy(get_pair(vp.pair)))# praw
                            print(datetime.now())
                            vp.minuteBought = 3
                            vp.checkedFirstCandy = False
                            vp.isBought = False
        
            vp.prev = vp.cur
    except:
        a=1
        
def new_check(vp):
    time.sleep(1)
    try:
        vp.kline = get_kline_perpetual(vp.pair)
        
        sr = count_sma(0, 10, vp.kline, vp.priceType)
        last = count_sma(0, 1, vp.kline, vp.priceType)
        
        diff = abs((last - sr)/sr)
        
        if(last > sr) and vp.sideChosen == False:
            vp.side = 1
            vp.sideChosen = True
        elif(last < sr) and vp.sideChosen == False:
            vp.side = 0
            vp.sideChosen = True
            
        if(last > sr) and (diff > 0.002) and (vp.isBought == False) and vp.sideChosen and vp.side == 0:
            print("przebicie od dołu " + vp.pair + " buy")
            print(get_pair_sell(get_pair_perpetual(vp.pair)))#praw
            print(get_pair_buy(get_pair_perpetual(vp.pair)))
            print(datetime.now())
            vp.isBought = True
            vp.isSold = False
            vp.highestBuy = get_pair_sell(get_pair_perpetual(vp.pair))
         #   vp.amountBought = vp.btcAmount/get_pair_sell(get_pair(vp.pair))
           # result = put_market(vp.amountBought,'buy', vp.pair)
           # print(result)
          #  print(vp.amountBought)
        elif(last < sr) and (diff > 0.002) and (vp.isSold == False) and vp.sideChosen and vp.side == 1:
            print("przebicie od góry " + vp.pair + " sell")
            print(get_pair_sell(get_pair_perpetual(vp.pair)))
            print(get_pair_buy(get_pair_perpetual(vp.pair)))# praw
            print(datetime.now())
            vp.isBought = False
            vp.isSold = True
            vp.lowestSold = get_pair_buy(get_pair_perpetual(vp.pair))
          #  result = put_market(vp.amountBought,'sell', vp.pair)
          #  print(result)
          #  vp.btcAmount = get_account_balance('BTC')
          #  print(vp.btcAmount)
        
        #set highest
        if(vp.isBought) and last > vp.highestBuy:
            vp.highestBuy = last
        elif(vp.isSold) and last < vp.lowestSold:
            vp.lowestSold = last
            
        #stoploss
        if(vp.isBought):
            diff2 = abs((last - vp.highestBuy)/vp.highestBuy)
            if(diff2 > 0.007):
                print("stop loss " + vp.pair + " od longa")
                print(get_pair_sell(get_pair_perpetual(vp.pair)))#praw
                print(get_pair_buy(get_pair_perpetual(vp.pair)))
                print(datetime.now())
                print(vp.highestBuy)
                vp.isBought = False
                vp.sideChosen = False
                
        if(vp.isSold):
            diff2 = abs((last - vp.lowestSold)/vp.lowestSold)
            if(diff2 > 0.007):
                print("stop loss " + vp.pair + " od shorta")
                print(get_pair_sell(get_pair_perpetual(vp.pair)))
                print(get_pair_buy(get_pair_perpetual(vp.pair)))#praw
                print(datetime.now())
                print(vp.lowestSold)
                vp.isSold = False
                vp.sideChosen = False
    
    
    except:
        print(1)