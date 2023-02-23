import pandas as pd
import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.bardata = {}  # Initialize dictionary to store bar data

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print("The next valid order id is: ", self.nextorderId)

    def tick_df(self, reqId, contract):
        """custom function to init DataFrame and request Tick Data"""
        self.bardata[reqId] = pd.DataFrame(columns=["time", "price"])
        self.bardata[reqId].set_index("time", inplace=True)
        self.reqTickByTickData(reqId, contract, "Last", 0, True)
        return self.bardata[reqId]

    def tickByTickAllLast(
        self,
        reqId,
        tickType,
        time,
        price,
        size,
        tickAtrribLast,
        exchange,
        specialConditions,
    ):
        if tickType == 1:
            #print('tickByTickAllLast̀. time: ', time, 'time in seconds: ', pd.to_datetime(time, unit="s"))
            self.bardata[reqId].loc[pd.to_datetime(time, unit="s")] = price

    def stock_contract(
        self,
        symbol,
        secType='STK',
        exchange='SMART',
        currency='USD'
    ):
        # create a stock contract
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.exchange = exchange
        contract.currency = currency

        return contract
    

###


def run_loop():
    app.run()


def submit_order(
    contract, 
    direction, 
    qty=100, 
    ordertype="MKT", 
    transmit=True
):
    # Create order object
    order = Order()
    order.action = direction
    order.totalQuantity = qty
    order.orderType = ordertype
    order.transmit = transmit
    order.eTradeOnly = ""
    order.firmQuoteOnly = ""
    # submit order
    app.placeOrder(app.nextorderId, contract, order)
    app.nextorderId += 1


def check_for_trade(df: pd.DataFrame, contract):
    start_time = df.index[-1] - pd.Timedelta(minutes=5)
    min_value = df[start_time:].price.min()
    max_value = df[start_time:].price.max()

    if df.price.iloc[-1] < max_value * 0.95:
        submit_order(contract, "SELL")
        return True

    elif df.price.iloc[-1] > min_value * 1.05:
        submit_order(contract, "BUY")
        return True
    
    
####


app = IBapi()
app.nextorderId = None
app.connect("winhost", 7497, 123)


api_thread = threading.Thread(target=run_loop)
api_thread.start()


while True:
    if isinstance(app.nextorderId, int):
        print("connected")
        break
    else:
        print("waiting for connection")
        time.sleep(1)


goog = app.stock_contract("GOOG")
aapl = app.stock_contract("AAPL")


###


df = app.tick_df(401, goog)


time.sleep(10)
for i in range(100):
    if len(df) > 0:
        break
    time.sleep(0.3)


if i == 99:
    app.disconnect()
    raise Exception("Error with Tick data stream")




data_length = df.index[-1] - df.index[0]
if data_length.seconds < 300:
    time.sleep(300 - data_length.seconds)
    
    
while True:
    if check_for_trade(df, aapl):
        break
    time.sleep(0.1)

app.disconnect()