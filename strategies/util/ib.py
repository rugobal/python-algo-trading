from ib_insync import IB, Trade
from ib_insync import util as ibUtil
import sys
import datetime as dt
import time as t


def disconnect_after_tp_or_sl(ib: IB, tp: Trade, sl: Trade) -> None:
    
    # def onExecDetails(trade: Trade,fill): 
    #     # print(f'The trade {trade.order.orderId} has been filled with executio: {fill.execution}')
    #     print('trade:', trade)
    #     print('fill:', fill)
    
    def onOrderStatus(trade):
        # check if the take profit or stop loss order has been filled
        if trade.orderStatus.status == 'Filled' and \
            (trade.order.orderId == tp.order.orderId or trade.order.orderId == sl.order.orderId):
                
            print(f"The {trade.order.action} order has been filled. order id: {trade.order.orderId}")
            # disconnect from TWS/IB Gateway
            ib.disconnect()
            ibUtil.getLoop().stop()
            

    

    # ib.execDetailsEvent += onExecDetails 
    
    # register the order status event handler
    ib.orderStatusEvent += onOrderStatus
    
    
def wait_until(time_str: str, ib:IB = None): 
    ''' target_time_str: in format hh:mm'''
    target_time = dt.datetime.strptime(time_str, '%H:%M').time()
    while True:
        now = dt.datetime.now().time()
        if now >= target_time:
            return
        else:
            remaining_time = dt.datetime.combine(dt.datetime.today(), target_time) - dt.datetime.combine(dt.datetime.today(), now)
            remaining_seconds = remaining_time.total_seconds()
            print(f"Waiting {dt.timedelta(seconds=remaining_seconds)} until {target_time.strftime('%H:%M')}...")
            if (ib):
                ib.sleep(30)
            else:
                t.sleep(30)