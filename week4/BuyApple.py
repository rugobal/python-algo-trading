from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

import threading
import time

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print("The next valid order id is: ", self.nextorderId)

    def orderStatus(
        self,
        orderId,
        status,
        filled,
        remaining,
        avgFullPrice,
        permId,
        parentId,
        lastFillPrice,
        clientId,
        whyHeld,
        mktCapPrice,
    ):
        print(
            "orderStatus - orderid:",
            orderId,
            "status:",
            status,
            "filled",
            filled,
            "remaining",
            remaining,
            "lastFillPrice",
            lastFillPrice,
        )

    def openOrder(self, orderId, contract, order, orderState):
        print(
            "openOrder id:",
            orderId,
            contract.symbol,
            contract.secType,
            "@",
            contract.exchange,
            ":",
            order.action,
            order.orderType,
            order.totalQuantity,
            orderState.status,
        )

    def execDetails(self, reqId, contract, execution):
        print(
            "Order Executed: ",
            reqId,
            contract.symbol,
            contract.secType,
            contract.currency,
            execution.execId,
            execution.orderId,
            execution.shares,
            execution.lastLiquidity,
        )
    
def run_loop():
    app.run()

def stock_contract(
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

app = IBapi()
app.connect('winhost', 7497, 123)

app.nextorderId = None

api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

while True:
    if isinstance(app.nextorderId, int):
        print('connected')
        break
    else:
        print('waiting for connection')
        time.sleep(1)
        
order = Order()
order.action = "BUY"
order.totalQuantity = 10
order.orderType = "LMT"
order.lmtPrice = "130.00"

app.placeOrder(app.nextorderId, stock_contract("AAPL"), order)

# uncomment if you are sending more than one order
#app.nextorderId += 1

time.sleep(10)

# cancel the order for the demo
print('cancelling order')
app.cancelOrder(app.nextorderId, "")

time.sleep(3)
app.disconnect()