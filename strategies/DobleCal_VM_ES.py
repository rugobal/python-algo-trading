import datetime as dt
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

assert dt.datetime.today().weekday() == 4, "Today is not Friday!!"

# Read config
config: Dict[str, Any] = config.get_config("doble_cal_VM_es")
print(config)

ibUtils.wait_until('18:00')
    
# TWs 7497, IBGW 4001
ib: IB = IB().connect('winhost',  7496, clientId=123, timeout=15)

es = Future('ES', '202303', 'CME')
ib.qualifyContracts(es)

ib.reqMarketDataType(1)

close_expiration = esUtils.get_expiration(5)
close_trading_cls = esUtils.get_DTE_trading_class(5)
long_expiration = esUtils.get_expiration(7)
long_trading_cls = esUtils.get_DTE_trading_class(7)
print('close expiration:', close_expiration, 'trading_class:', close_trading_cls)
print('long expiration:', long_expiration, 'trading_class:', long_trading_cls)

## Define the strikes
call_ticker = esUtils.get_call_ticker(ib, es, close_expiration, config['call_delta'])
print('call strike selected:', call_ticker.contract.strike, 'delta:', esUtils.get_ticker_delta(call_ticker))

put_ticker = esUtils.get_put_ticker(ib, es, close_expiration, config['put_delta'])
print('put strike selected:', put_ticker.contract.strike, 'delta:', esUtils.get_ticker_delta(put_ticker))

buy_call_strike = call_ticker.contract.strike 
sell_call_strike = buy_call_strike
buy_put_strike = put_ticker.contract.strike
sell_put_strike = buy_put_strike

## Create the ticker
contracts = [
    FuturesOption(es.symbol, close_expiration, buy_call_strike, 'C', 'CME', '50', 'USD', tradingClass=close_trading_cls),
    FuturesOption(es.symbol, long_expiration, sell_call_strike, 'C', 'CME', '50', 'USD', tradingClass=long_trading_cls),
    FuturesOption(es.symbol, close_expiration, buy_put_strike, 'P', 'CME', '50', 'USD', tradingClass=close_trading_cls),
    FuturesOption(es.symbol, long_expiration, sell_put_strike, 'P', 'CME', '50', 'USD', tradingClass=long_trading_cls)]

bag_contract = optionUtils.create_ic(ib, contracts)
bag_ticker = bagUtils.get_ticker(ib, bag_contract)

# Define prices for orders
print('Double calendar market price:', bag_ticker.marketPrice())
price = esUtils.round_2tick(bag_ticker.marketPrice()) - 0.25
limit = esUtils.round_2tick(price * (1-config['target']))
stop = esUtils.round_2tick(price * (1+config['stop']))

print('price:', price)
print('limit:', limit)
print('stop:', stop)

# Enter the orders
params = {'tif': 'GTC'}
bracket_order = ib.bracketOrder('BUY', 2, price, limit, stop, **params)
mainOrder: Trade = ib.placeOrder(bag_contract, bracket_order[0])
takeProfitOrder = ib.placeOrder(bag_contract, bracket_order[1])
stopLossOrder = ib.placeOrder(bag_contract, bracket_order[2])
print(f'mainOrder id: {mainOrder.order.orderId}')
print(f'takeProfitOrder id: {takeProfitOrder.order.orderId}')
print(f'stopLossOrder id: {stopLossOrder.order.orderId}')

print('Order sent')


ib.sleep(5)




    
