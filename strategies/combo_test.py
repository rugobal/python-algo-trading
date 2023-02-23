from datetime import datetime
from ib_insync import *
import pandas as pd
import math
import sys
from typing import List, Any, Dict, Tuple

from datetime import datetime, time


def x_round(x):
    return round(x*4)/4

# TWs 7497, IBGW 4001
ib: IB = IB().connect('winhost',  7496, clientId=123, timeout=15)

es = Future('ES', '202303', 'CME')
print(ib.qualifyContracts(es))

ib.reqMarketDataType(1)


[ticker] = ib.reqTickers(es)
# print(ticker)
#ib.sleep(5)

# spx current price
spxValue =  ticker.marketPrice() 
print('es futue value: ', spxValue)

expiration = '20230222'
trading_cls = 'E4C'


# put_contract = FuturesOption(es.symbol, expiration, 4010, 'P', 'CME', '50', 'USD', tradingClass=trading_cls)
# [put_contract] = ib.qualifyContracts(put_contract)
# [put_ticker] = ib.reqTickers(put_contract)
# print('put ticker:', put_ticker)
# print('put ticker martet price:', put_ticker.marketPrice())

# create combo
contracts = [
    FuturesOption(es.symbol, expiration, 4025, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, 4075, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, 3980, 'P', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, 3970, 'P', 'CME', '50', 'USD', tradingClass=trading_cls),]

contracts = ib.qualifyContracts(*contracts)

combo_contract = Contract(symbol=contracts[0].symbol, secType='BAG', exchange='SMART', currency='USD')
leg1 = ComboLeg(conId=contracts[0].conId, ratio=1, action='SELL', exchange=contracts[0].exchange)
leg2 = ComboLeg(conId=contracts[1].conId, ratio=1, action='BUY', exchange=contracts[1].exchange)
leg3 = ComboLeg(conId=contracts[2].conId, ratio=1, action='SELL', exchange=contracts[2].exchange)
leg4 = ComboLeg(conId=contracts[3].conId, ratio=1, action='BUY', exchange=contracts[3].exchange)
combo_contract.comboLegs = [leg1, leg2, leg3, leg4]

### IMPORTANT: use reqMktData insted of reqTickers and sleep so it has time to fill up, and then CANCEL 
### https://groups.io/g/insync/topic/7793700
### BUT!! STILL DOES NOT WORK SOMETIMES. IT IS NOT RELIABLE
combo_ticker = ib.reqMktData(combo_contract)
ib.cancelMktData(combo_contract)


ib.sleep(5)

print('')
print('combo ticker:', combo_ticker)
print('combo ticker price:', combo_ticker.marketPrice())

# # Buy at the given price
# order = LimitOrder('BUY', 1, -55)
# trade = ib.placeOrder(combo_contract, order)

# ib.sleep(1)



ib.disconnect()