from datetime import datetime as dt
from ib_insync import *
import pandas as pd
import math
import sys
from typing import List, Any, Dict, Tuple

import os
import yaml


import util.bag as bagUtils
import util.es_future as esUtils
import util.options as optionUtils
import util.config as config
import util.ib as ibUtils

# Read config
config: Dict[str, Any] = config.get_config("ici_es")
print(config)
    
# TWs 7497, IBGW 4001
ib: IB = IB().connect('winhost',  7497, clientId=123, timeout=15)

es = Future('ES', '202303', 'CME')
ib.qualifyContracts(es)

ib.reqMarketDataType(1)

expiration = esUtils.get_0DTE_expiration()
trading_cls = esUtils.get_0DTE_trading_class()
print('expiration:', expiration)
print('trading_class:', trading_cls)

## Define the strikes
call_ticker = esUtils.get_call_ticker(ib, es, expiration, config['call_delta'])
print('call strike selected:', call_ticker.contract.strike, 'delta:', call_ticker.lastGreeks.delta)

put_ticker = esUtils.get_put_ticker(ib, es, expiration, config['put_delta'])
print('put strike selected:', put_ticker.contract.strike, 'delta:', put_ticker.lastGreeks.delta)

buy_call_strike = call_ticker.contract.strike 
sell_call_strike = buy_call_strike + config['call_wing_width']
buy_put_strike = put_ticker.contract.strike
sell_put_strike = buy_put_strike - config['put_wing_width']

## Create the ticker
contracts = [
    FuturesOption(es.symbol, expiration, buy_call_strike, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, sell_call_strike, 'C', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, buy_put_strike, 'P', 'CME', '50', 'USD', tradingClass=trading_cls),
    FuturesOption(es.symbol, expiration, sell_put_strike, 'P', 'CME', '50', 'USD', tradingClass=trading_cls)]

ici_contract = optionUtils.create_ici(ib, contracts)
ici_ticker = bagUtils.get_ticker(ib, ici_contract)

# Define prices for orders
print('ICI market price:', ici_ticker.marketPrice())
price = esUtils.round_2tick(ici_ticker.marketPrice()) - 0.25
limit = esUtils.round_2tick(price + config['target'])
stop = esUtils.round_2tick(price - config['stop'])

print('price:', price)
print('limit:', limit)
print('stop:', stop)

# Enter the orders
bracket_order = ib.bracketOrder('BUY', 1, price, limit, stop)
mainOrder: Trade = ib.placeOrder(ici_contract, bracket_order[0])
takeProfitOrder = ib.placeOrder(ici_contract, bracket_order[1])
stopLossOrder = ib.placeOrder(ici_contract, bracket_order[2])
print(f'mainOrder id: {mainOrder.order.orderId}')
print(f'takeProfitOrder id: {takeProfitOrder.order.orderId}')
print(f'stopLossOrder id: {stopLossOrder.order.orderId}')

print('Order sent')

# exit after take profit or stop loss
ibUtils.disconnect_after_tp_or_sl(ib, takeProfitOrder, stopLossOrder)

# wait for the orders to fill
util.run()
