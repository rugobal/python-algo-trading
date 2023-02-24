from asyncio import Future
import math
from datetime import datetime, timedelta, time
from typing import List
from cvxpy import Chain

from ib_insync import IB, FuturesOption, Ticker
from .options import get_option_chain

def get_ES_contract(ib: IB, year_mont: str) -> Future:
    es = Future('ES', '202303', 'CME')
    ib.qualifyContracts(es)
    return es

def round_2tick(x):
    return round(x*4)/4

def get_0DTE_trading_class() -> str:
    return get_DTE_trading_class(0)

def get_0DTE_expiration() -> str:
    return get_expiration(0)

def get_expiration(daysdelta: int) -> str:
    dt: datetime = datetime.today() + timedelta(days=daysdelta)
    # format the date in the format 'YYYYMMDD'
    return dt.strftime('%Y%m%d')


def get_DTE_trading_class(dte: int):
    dt: datetime = datetime.today() + timedelta(days=dte)
    
    week = __f2(dt.day)
    day = dt.weekday()
    res = 'E' + str(week)
    if day == 4:
        return 'EW' + str(week)
    else:
        return 'E' + str(week) + chr(65+day).upper()
    
    
def get_call_ticker(ib: IB, contract: Future, expiration: str, delta: float) -> Ticker:
    assert delta > 0, "the delta of a call option must be positive"
    return get_ticker(ib, contract, expiration, delta, 'C')

def get_put_ticker(ib: IB, contract: Future, expiration: str, delta: float) -> Ticker:
    assert delta < 0, "the delta of a put option must be negative"
    return get_ticker(ib, contract, expiration, delta, 'P')
    
def get_ticker(ib: IB, contract: Future, expiration: str, delta: float, write: str) -> Ticker:
    ''' Gets the ticker (snapshot) of an option with the given delta and expiration 
       contract: must be qualified
       write: C or P
       '''
    # get the contract market price first
    [ticker] = ib.reqTickers(contract)
    price = ticker.marketPrice()
    
    # parse the string to a datetime object
    exp_dt = datetime.strptime(expiration, '%Y%m%d')
    today = datetime.combine(datetime.now().date(), time.min)
    assert exp_dt >= today, "today's date must be greater or equal than  the expiration date"
    trading_cls = get_DTE_trading_class((exp_dt - today).days)
    
    chain = get_option_chain(ib, contract, trading_cls)
    
    if (write == 'C'):
        strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and price - 5 < strike < price + 90]
    else:
        strikes = [strike for strike in chain.strikes
            if strike % 5 == 0
            and price - 90 < strike < price + 5]
    
    ## Select call strike
    contracts = [FuturesOption(contract.symbol, expiration, strike, write, 'CME', '50', 'USD', tradingClass=trading_cls) for strike in strikes]
    contracts = ib.qualifyContracts(*contracts)
    tickers = ib.reqTickers(*contracts)
    tickers = list(filter(lambda t: abs(get_ticker_delta(t)) >= 0.01, tickers))

    deltas = [get_ticker_delta(t) for t in tickers]
    # print(deltas)
    return tickers[__get_delta_index(deltas, delta)]
    
    
def get_ticker_delta(t: Ticker) -> float:
    if (t.lastGreeks and t.lastGreeks.delta):
        return t.lastGreeks.delta
    elif t.askGreeks and t.bidGreeks:
        return (t.askGreeks.delta + t.bidGreeks.delta)/2.0    
    elif t.modelGreeks:
        return t.modelGreeks.delta
    else:
        print('this ticker has no greek?')
        print(t)
        return None
    
def __get_delta_index(deltas: List[float], reference: float) -> int:
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
    
    
    
def __f2(day_of_month):
    ''' gets the nth ocurrence of the given day of the month on that month'''
    actual_day = day_of_month
    counter = 0
    while actual_day > 0:
        actual_day = actual_day - 7
        counter = counter + 1
    return counter
    
# def __week_of_month(dt):
#     """ Returns the week of the month for the specified date.
#     """

#     first_day = dt.replace(day=1)

#     dom = dt.day
#     adjusted_dom = dom + first_day.weekday()
#     return int(math.ceil(adjusted_dom/7.0))