from datetime import datetime
from ib_insync import *
import pandas as pd
import pytz

from datetime import datetime, time


def in_between(now, start=time(9,30), end=time(16)):
    if start <= now < end:
        return 1
    else:
        return 2


timeZ_Ny = pytz.timezone('America/New_York')
data_type = in_between(datetime.now(timeZ_Ny).time())


# TWs 7497, IBGW 4001
ib = IB().connect('winhost',  7497, clientId=123, timeout=15)

spx = Index('SPX', 'CBOE')
print(ib.qualifyContracts(spx))

# To avoid issues with market data permissions, we'll use delayed data:
ib.reqMarketDataType(4)

[ticker] = ib.reqTickers(spx)
print(ticker)
#ib.sleep(5)

# spx current price
spxValue =  ticker.marketPrice() #4065.75 
print('spxValue: ', spxValue)

chains = ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)

# chainsDf = util.df(chains)
# chainsDf = chainsDf[(chains.exchange == 'SMART') & (chains.tradingClass == 'SPXW')]

chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
expiration = chain.expirations[0]

print('')
print(expiration)

strikes = [strike for strike in chain.strikes
        if strike % 5 == 0
        and spxValue - 20 < strike < spxValue + 20]
rights = ['P', 'C']


contracts = [Option('SPX', expiration, strikes[int(len(strikes)/2)], 'C', 'SMART', tradingClass='SPXW')]

contracts = ib.qualifyContracts(*contracts)

print(contracts[0])

tickers = ib.reqTickers(*contracts)

print(tickers[0])
#print('greeks: ', tickers[0].modelGreeks)
print('lastGreeks delta: ', tickers[0].lastGreeks.delta)



def get_individual(ticker,exp,strike,kind):
    ib.reqMarketDataType(data_type)
    contract = Option(ticker, exp, strike, kind, "SMART", currency="USD")
    snapshot = ib.reqMktData(contract, "", True, False)
    while util.isNan(snapshot.bid):
        ib.sleep()
    return {'strike': strike, 'kind': kind, 'close': snapshot.close, 'last': snapshot.last, 'bid': snapshot.bid, 'ask': snapshot.ask, 'volume': snapshot.volume}



ib.disconnect()