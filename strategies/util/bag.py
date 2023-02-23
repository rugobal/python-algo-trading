from typing import List
from ib_insync import IB, Contract, Ticker
import math

def get_price_leg_by_leg(ib: IB, bag: Contract) -> float:
    ''' Gets the list of a BAG contract by calculating the price leg by leg'''
    tickers: List[Ticker] = ib.reqTickers(*[Contract(conId=l.conId, exchange=l.exchange) for l in bag.comboLegs])
    # return sum(list(map(lambda t, l: t.marketPrice()*l.ratio if l.action=='BUY' else -1*t.marketPrice()*l.ratio, tickers, bag.comboLegs)))
    
    # Calculate the market price for the BAG contract using the bid/ask prices from the market depth
    price = 0
    for i, leg in enumerate(bag.comboLegs):
        if leg.action == 'BUY':
            price += tickers[i].marketPrice() * leg.ratio
        else:
            price -= tickers[i].marketPrice() * leg.ratio

    return price

def get_ticker(ib: IB, bag: Contract) -> Ticker:
    ### IMPORTANT: use reqMktData insted of reqTickers and sleep so it has time to fill up, and then CANCEL 
    ### https://groups.io/g/insync/topic/7793700
    ### BUT!! STILL DOES NOT WORK SOMETIMES. IT IS NOT RELIABLE, that's why we foll back to the 
    count = 0
    max_retries = 2
    while (count < max_retries):
        ic_ticker = ib.reqMktData(bag)
        ib.sleep(2)
        ib.cancelMktData(bag)
        if not math.isnan(ic_ticker.marketPrice()):
            print('combo ticker retrieved correctly')
            return ic_ticker
        else :
            print('combo ticker has no data. attempt {0}. retrying...', count)
            count = count+1
            if count == max_retries:
                print('calculating price leg by leg')
                ic_ticker.last = get_price_leg_by_leg(ib, bag)
                # print('price leg by leg:', ic_ticker.last)
                return ic_ticker
