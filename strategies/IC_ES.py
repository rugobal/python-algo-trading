from datetime import datetime
from ib_insync import *
import pandas as pd
import math
import sys
from typing import List, Any, Dict, Tuple

from datetime import datetime, time

import util.bag as bagUtils
import util.es_future as esUtils
import util.options as optionUtils


# def in_between(now, start=time(9,30), end=time(16)):
#     if start <= now < end:
#         return 1
#     else:
#         return 2


    
def get_delta_index(deltas: List[float], reference: float) -> int:
    ''' reference: the reference delta
        returns the index of the closest element to the reference delta
    '''
    _deltas = sorted(deltas)
    # print(_deltas)
    above_delta = next(d for d in _deltas if d > reference)
    below_delta = next(d for d in reversed(_deltas) if d < reference)
    
    # print('up_delta', above_delta)
    # print('down_delta', below_delta)
    if abs(above_delta - reference) <= abs(below_delta - reference):
        return deltas.index(above_delta)
    else: 
        return deltas.index(below_delta)

    
    


def x_round(x):
    return round(x*4)/4
        


# timeZ_Ny = pytz.timezone('America/New_York')
# data_type = in_between(datetime.now(timeZ_Ny).time())

# print(ord('A'))
# print(ord('B'))
# print(ord('C'))
# print(ord('D'))
# sys.exit(0)


# TWs 7497, IBGW 4001
ib: IB = IB().connect('winhost',  7496, clientId=123, timeout=15)

es = Future('ES', '202303', 'CME')
print(ib.qualifyContracts(es))

ib.reqMarketDataType(1)

trading_cls = esUtils.get_0DTE_trading_class()
expiration = esUtils.get_0DTE_expiration()
print('expiration: ', expiration)

call_ticker = esUtils.get_call_ticker(ib, es, expiration, 0.25)
print('call strike selected:', call_ticker.contract.strike, 'delta:', call_ticker.lastGreeks.delta)

put_ticker = esUtils.get_put_ticker(ib, es, expiration, -0.25)
print('put strike selected:', put_ticker.contract.strike, 'delta:', put_ticker.lastGreeks.delta)

##############################################
#### STRIKES AND PRICE #######################

call_strike = call_ticker.contract.strike # 4105
call_width = 50

put_strike = put_ticker.contract.strike # 4030
put_width = -call_width

# price = -55.75

target = .25
stop = .60

##############################################
##############################################

contracts = [
    FuturesOption(es.symbol, expiration, call_strike, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, call_strike+call_width, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike, 'P', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike+put_width, 'P', 'CME', '50', 'USD', tradingClass=trading_cls)]

ic_contract = optionUtils.create_ic(ib, contracts)

ic_ticker = bagUtils.get_ticker(ib, ic_contract)

# print('ic_ticker', ticker)

print('IC market price:', ic_ticker.marketPrice())
price = x_round(ic_ticker.marketPrice()) - 0
limit = x_round(price * (1-target))
stop = x_round(price * (1+stop))

print('price:', price)
print('limit:', limit)
print('stop:', stop)

# Next, try a bracket order.
bracket_order = ib.bracketOrder('BUY', 3, price, limit, stop)
for o in bracket_order:
    bracket_trade = ib.placeOrder(ic_contract, o)
    # print(bracket_trade)
    
print('order sent')

ib.disconnect()

sys.exit(0)


[ticker] = ib.reqTickers(es)
# print(ticker)
#ib.sleep(5)

# spx current price
spxValue =  ticker.marketPrice() 
print('es futue value: ', spxValue)

chains = ib.reqSecDefOptParams(es.symbol, 'CME', es.secType, es.conId)

# chainsDf = util.df(chains)
# print(chainsDf.to_string(max_colwidth=20))
# chainsDf = chainsDf[(chainsDf.exchange == 'CME') & (chainsDf.tradingClass == 'E3C')]

trading_cls = esUtils.get_0DTE_trading_class()
print('trading class:', trading_cls)
chain = next(c for c in chains if c.tradingClass == trading_cls and c.exchange == 'CME')
expiration = chain.expirations[0]

print('expiration:',expiration)

call_strikes = [strike for strike in chain.strikes
        if strike % 5 == 0
        and spxValue < strike < spxValue + 30]

put_strikes = [strike for strike in chain.strikes
        if strike % 5 == 0
        and spxValue - 30 < strike < spxValue]
rights = ['P', 'C']

#print(call_strikes)

## Select call strike
contracts = [FuturesOption(es.symbol, expiration, strike, 'C', 'CME', '50', 'USD', tradingClass=trading_cls) for strike in call_strikes]
contracts = ib.qualifyContracts(*contracts)
tickers = ib.reqTickers(*contracts)
tickers = list(filter(lambda t: abs(t.lastGreeks.delta) >= 0.01, tickers))

deltas = [t.lastGreeks.delta for t in tickers]
call_ticker = tickers[get_delta_index(deltas, 0.25)]
print('call strike selected:', call_ticker.contract.strike, 'delta:', call_ticker.lastGreeks.delta)

# for ticker in tickers:
#     print('call strike', ticker.contract.strike, 'bid:', ticker.bid, 'ask:', ticker.ask, 'delta:', ticker.lastGreeks.delta)

## Select put strike
contracts = [FuturesOption(es.symbol, expiration, strike, 'P', 'CME', '50', 'USD', tradingClass=trading_cls) for strike in put_strikes]
contracts = ib.qualifyContracts(*contracts)
tickers = ib.reqTickers(*contracts)
tickers = list(filter(lambda t: abs(t.lastGreeks.delta) >= 0.01, tickers))

deltas = [t.lastGreeks.delta for t in tickers]
put_ticker = tickers[get_delta_index(deltas, -0.25)]
print('put strike selected:', put_ticker.contract.strike, 'delta:', put_ticker.lastGreeks.delta)

# for ticker in tickers:
#     print('put strike', ticker.contract.strike, 'bid:', ticker.bid, 'ask:', ticker.ask, 'delta:', ticker.lastGreeks.delta)


# print(tickers[0])


##############################################
#### STRIKES AND PRICE #######################

call_strike = call_ticker.contract.strike # 4105
call_width = 50

put_strike = put_ticker.contract.strike # 4030
put_width = call_width

# price = -55.75

##############################################
##############################################


contracts = [
    FuturesOption(es.symbol, expiration, call_strike, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, call_strike+call_width, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike, 'P', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike-put_width, 'P', 'CME', '50', 'USD', tradingClass=trading_cls)]

ic_contract = optionUtils.create_ic(ib, contracts)

# print('contract 0:', contracts[0])
# print('ic_contract', ic_contract)

ic_ticker = bagUtils.get_ticker(ib, ic_contract)

# print('ic_ticker', ticker)
target = .25
stop = .60
print('IC market price:', ic_ticker.marketPrice())
price = x_round(ic_ticker.marketPrice()) - 2
limit = x_round(price * (1-target))
stop = x_round(price * (1+stop))

print('price:', price)
print('limit:', limit)
print('stop:', stop)


# Buy at the given price
# order = LimitOrder('BUY', 1, price)
# trade = ib.placeOrder(ic_contract, order)

# ib.sleep(1)

# Next, try a bracket order.
# bracket_order = ib.bracketOrder('BUY', 1, price, limit, stop)
# for o in bracket_order:
#     bracket_trade = ib.placeOrder(ic_contract, o)
#     # print(bracket_trade)
    
# print('order sent')


ib.disconnect()