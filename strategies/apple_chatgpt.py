from ib_insync import *
import pandas as pd
import datetime as dt

# Connect to TWS or IB Gateway
ib = IB()
ib.connect('winhost', 7496, clientId=1, timeout=15)

# Define the contract for Apple stock
contract = Stock('AAPL', 'SMART', 'USD')

# Check if the market is open
now = dt.datetime.now().strftime("%Y%m%d %H:%M:%S")
market_open = ib.reqMarketDataType(4)
market_opened = False
while not market_opened:
    if ib.reqMarketDataType(4) == 1:
        print(f"The market is open at {now}")
        market_opened = True
    else:
        print(f"The market is closed at {now}. Waiting for it to open...")
        ib.sleep(60) # Wait for 60 seconds before checking again

# Get the high price of Apple stock for the previous day
prev_day = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='1 D', barSizeSetting='1 day',
    whatToShow='TRADES', useRTH=True, formatDate=1)
df: pd.DataFrame = util.df(prev_day)
prev_high = df['high'].max()

# Get the opening price of Apple stock for the current day
ticker = ib.reqMktData(contract, snapshot=True)
open_price = ticker.last

position = False

# Place a stop limit order for 100 shares of Apple at the previous day's high price
if open_price <= prev_high:
    order = StopLimitOrder('BUY', 100, prev_high * 1.01, prev_high)
    trade = ib.placeOrder(contract, order)
    
else:
    order = MarketOrder('BUY', 100)
    trade = ib.placeOrder(contract, order)
    

# Define a function to handle the orderStatus event
def handle_order_status(trade, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
    global position # Use the global keyword to update the position variable
    if status == 'Filled' and trade.order.action == 'BUY': # If the order has been filled and it was a long or BUY trade, set the position variable to True
        position = True
        print(f"Order {trade.order.orderId} has been filled at price {avgFillPrice}")
    elif status == 'Filled' and trade.order.action == 'SELL': # If the order has been filled and it was a short or SELL trade, set the position variable to False
        position = False
        print(f"Order {trade.order.orderId} has been filled at price {avgFillPrice}")

# Register the handle_order_status function with the orderStatus event
ib.pendingOrdersEvent += handle_order_status

# Monitor the price of Apple throughout the day and check if the position is profitable
while True:
    ib.sleep(60) # Wait for 60 seconds
    ticker = ib.reqMktData(contract)
    price = ticker.last
    
    # Check if the market is about to close and close the position if there is one
    if ib.reqMarketDataType(4) == 3 and position:
        print("The market is about to close. Closing the position...")
        order = MarketOrder('SELL', 100)
        ib.placeOrder(contract, order)
        position = False
    
    if position and price >= trade.price * 1.02: # If we're in a position and the price has risen by 2% or more, sell the position
        order = MarketOrder('SELL', 100)
        ib.placeOrder(contract, order)
        position = False
        break
    elif position and price <= trade.price * 0.99: # If we're in a position and the price has fallen by 1% or more, sell the position to limit the loss
        order = MarketOrder('SELL', 100)
        ib.placeOrder(contract, order)
        position = False
        break

# Disconnect from TWS or IB Gateway
ib.disconnect()

"""
In this code, we first connect to TWS or IB Gateway using the IB() function from the ib_insync library. We then define the contract for Apple stock using the Stock() function, which specifies the ticker symbol, exchange, and currency.

We then use the reqHistoricalData() method to get the high price of Apple stock for the previous day. This method returns a list of BarData objects, which we convert to a Pandas DataFrame using the util.df() function. We then use the max() method to get the highest price of the previous day.

We then place a buy order for 100 shares of Apple at the previous day's high price using the LimitOrder() function and placeOrder() method. The LimitOrder() function specifies the order type, quantity, and limit price.

We then initialize the position variable to True, because we are starting the day with an open position.

We then define the handle_order_status() function, which updates the position variable to True when the buy order is filled, and to False when the order is cancelled or rejected.

We then register the handle_order_status() function with the pendingOrdersEvent event.

We then use a while loop to monitor the price of Apple using the reqMktData() method, which returns a Ticker object that contains the latest price information. We check if we are in a position and the price has risen by 2% or fallen by 1% from the price at which we bought the position. If either condition is met, we place a sell order to close the position using the MarketOrder() function and placeOrder() method. When the order is filled, the handle_order_status() function updates the position variable to False, and the while loop terminates.

Finally, we disconnect from TWS or IB Gateway using the disconnect() method.

"""