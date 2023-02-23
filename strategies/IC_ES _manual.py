from datetime import datetime
from ib_insync import *
import pandas as pd
import math
from typing import List, Any
import copy

from datetime import datetime, time
import sys


def f2(day_of_month):
    ''' gets the nth ocurrence of the given day of the month on that month'''
    actual_day = day_of_month
    counter = 0
    while actual_day > 0:
        actual_day = actual_day - 7
        counter = counter + 1
    return counter

# def week_of_month(dt):
#     """ Returns the week of the month for the specified date.
#     """

#     first_day = dt.replace(day=1)

#     dom = dt.day
#     adjusted_dom = dom + first_day.weekday()

#     return int(math.ceil(adjusted_dom/7.0))

def x_round(x):
    return round(x*4)/4

def get_trading_class(dt: datetime):
    week = f2(dt.day)
    day = dt.weekday()
    res = 'E' + str(week)
    if day == 4:
        return 'EW' + str(week)
    else:
        return 'E' + str(week) + chr(65+day).upper()
    
    
def create_ic(contracts: List[Contract]) -> Contract:
    
    # contract = Contract(symbol=und_contract.symbol, secType=und_contract.secType, exchange=und_contract.exchange, currency=und_contract.currency)
    # contract = copy.copy(und_contract)
    # contract.secType = 'BAG'
    # contract.conId=28812380
    # contract =Future('BAG', '202303', 'CME', localSymbol='ESH3', multiplier='50', currency='USD')
    contract = Contract(symbol=contracts[0].symbol, secType='BAG', exchange='SMART', currency='USD')
    # print('bag contract:', contract)
    
    leg1 = ComboLeg(conId=contracts[0].conId, ratio=1, action='SELL', exchange=contracts[0].exchange)
    leg2 = ComboLeg(conId=contracts[1].conId, ratio=1, action='BUY', exchange=contracts[1].exchange)
    leg3 = ComboLeg(conId=contracts[2].conId, ratio=1, action='SELL', exchange=contracts[2].exchange)
    leg4 = ComboLeg(conId=contracts[3].conId, ratio=1, action='BUY', exchange=contracts[3].exchange)
    
    contract.comboLegs = [leg1, leg2, leg3, leg4]

    return contract
        
        
# def in_between(now, start=time(9,30), end=time(16)):
#     if start <= now < end:
#         return 1
#     else:
#         return 2


# timeZ_Ny = pytz.timezone('America/New_York')
# data_type = in_between(datetime.now(timeZ_Ny).time())


# TWs 7497, IBGW 4001
ib: IB = IB().connect('winhost',  7496, clientId=123, timeout=15)

es = Future('ES', '202303', 'CME')
# print('conId:', es.conId)
print(ib.qualifyContracts(es))

ib.reqMarketDataType(1)


[ticker] = ib.reqTickers(es)

# spx current price
spxValue =  ticker.marketPrice() 
print('es futue value: ', spxValue)

chains = ib.reqSecDefOptParams(es.symbol, 'CME', es.secType, es.conId)

# chainsDf = util.df(chains)
# print(chainsDf.to_string(max_colwidth=10))
# chainsDf = chainsDf[(chains.exchange == 'SMART') & (chains.tradingClass == 'SPXW')]

trading_cls = get_trading_class(datetime.now())
print('trading class:', trading_cls)
chain = next(c for c in chains if c.tradingClass == trading_cls and c.exchange == 'CME')
expiration = chain.expirations[0]

print('expiration:',expiration)

##############################################
#### STRIKES AND PRICE #######################

call_strike = 4025
call_width = 50

put_strike = 3990
put_width = call_width

price = -55.75

##############################################
##############################################


contracts = [
    FuturesOption(es.symbol, expiration, call_strike, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, call_strike+call_width, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike, 'P', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike-put_width, 'P', 'CME', '50', 'USD', tradingClass=trading_cls)]


contracts = ib.qualifyContracts(*contracts)
ic_contract = create_ic(contracts)
### IMPORTANT: use reqMktData instea of reqTickers and sleep so it has time to fill up
#### https://groups.io/g/insync/topic/7793700
ic_ticker = ib.reqMktData(ic_contract) 
ib.sleep(5)

print('')
print('ic_ticker', ic_ticker)
# target = .25
# stop = .60
# price = x_round(ic_ticker.marketPrice()) - 1
# limit = x_round(price * (1-target))
# stop = x_round(price * (1+stop))
# print('IC last price:', ic_ticker.marketPrice())

# print('price:', price)
# print('limit:', limit)
# print('stop:', stop)


# Buy at the given price
# order = LimitOrder('BUY', 1, price)
# trade = ib.placeOrder(ic_contract, order)

# ib.sleep(1)

# Next, try a bracket order.
# bracket_order = ib.bracketOrder('BUY', 1, price, limit, stop)
# for o in bracket_order:
#     bracket_trade = ib.placeOrder(ic_contract, o)
#     print(bracket_trade)


ib.disconnect()