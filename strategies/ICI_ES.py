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

# TWs 7497, IBGW 4001
ib: IB = IB().connect('winhost',  7496, clientId=123, timeout=15)

es = Future('ES', '202303', 'CME')
print(ib.qualifyContracts(es))

ib.reqMarketDataType(1)

trading_cls = esUtils.get_0DTE_trading_class()
expiration = esUtils.get_0DTE_expiration()
print('expiration: ', expiration)

call_ticker = esUtils.get_call_ticker(ib, es, expiration, 0.45)
print('call strike selected:', call_ticker.contract.strike, 'delta:', call_ticker.lastGreeks.delta)

put_ticker = esUtils.get_put_ticker(ib, es, expiration, -0.40)
print('put strike selected:', put_ticker.contract.strike, 'delta:', put_ticker.lastGreeks.delta)

##############################################
#### STRIKES AND PRICE #######################

call_strike = call_ticker.contract.strike 
call_width = +30

put_strike = put_ticker.contract.strike 
put_width = -40

target = 4
stop = 8

##############################################
##############################################

contracts = [
    FuturesOption(es.symbol, expiration, call_strike, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, call_strike+call_width, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike, 'P', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, put_strike+put_width, 'P', 'CME', '50', 'USD', tradingClass=trading_cls)]

ici_contract = optionUtils.create_ici(ib, contracts)
ici_ticker = bagUtils.get_ticker(ib, ici_contract)

# print('ic_ticker', ticker)

print('ICI market price:', ici_ticker.marketPrice())
price = esUtils.round_2tick(ici_ticker.marketPrice()) - 0.5
limit = esUtils.round_2tick(price + target)
stop = esUtils.round_2tick(price - stop)

print('price:', price)
print('limit:', limit)
print('stop:', stop)

# Next, try a bracket order.
bracket_order = ib.bracketOrder('BUY', 3, price, limit, stop)
mainOrder: Trade = ib.placeOrder(ici_contract, bracket_order[0])
takeProfitOrder = ib.placeOrder(ici_contract, bracket_order[1])
stopLossOrder = ib.placeOrder(ici_contract, bracket_order[2])

print('order sent')

# define a function to handle the order status event
def onOrderStatus(trade, order, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld):
    # check if the take profit or stop loss order has been filled
    if order.orderId == takeProfitOrder.order.orderId or order.orderId == stopLossOrder.order.orderId:
        print(f"The {order.action} order has been filled.")
        # disconnect from TWS/IB Gateway
        ib.disconnect()
    


# register the order status event handler
ib.orderStatusEvent += onOrderStatus

# wait for the orders to fill
util.run()

ib.disconnect()

