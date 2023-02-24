from typing import List
from cvxpy import Chain
from ib_insync import util

from ib_insync import IB, ComboLeg, Contract


def get_option_chain(ib: IB, contract: Contract, trading_class: str) -> Chain:
    ''' gets the option chain for a given qualified contract and trading class '''
    chains = ib.reqSecDefOptParams(contract.symbol, contract.exchange, contract.secType, contract.conId)
    # chainsDf = util.df(chains)
    # print(chainsDf.to_string(max_colwidth=20))
    # chainsDf = chainsDf[(chainsDf.exchange == 'CME') & (chainsDf.tradingClass == 'E3C')]
    return next(c for c in chains if c.tradingClass == trading_class and c.exchange == contract.exchange)


def create_ic(ib: IB, contracts: List[Contract]) -> Contract:
    
    # contract = Contract(symbol=und_contract.symbol, secType=und_contract.secType, exchange=und_contract.exchange, currency=und_contract.currency)
    # contract = copy.copy(und_contract)
    # contract.secType = 'BAG'
    # contract.conId=28812380
    # contract =Future('BAG', '202303', 'CME', localSymbol='ESH3', multiplier='50', currency='USD')
    ib.qualifyContracts(*contracts)
    contract = Contract(symbol=contracts[0].symbol, secType='BAG', exchange='SMART', currency='USD')
    # print('bag contract:', contract)
    
    leg1 = ComboLeg(conId=contracts[0].conId, ratio=1, action='SELL', exchange=contracts[0].exchange)
    leg2 = ComboLeg(conId=contracts[1].conId, ratio=1, action='BUY', exchange=contracts[1].exchange)
    leg3 = ComboLeg(conId=contracts[2].conId, ratio=1, action='SELL', exchange=contracts[2].exchange)
    leg4 = ComboLeg(conId=contracts[3].conId, ratio=1, action='BUY', exchange=contracts[3].exchange)
    
    contract.comboLegs = [leg1, leg2, leg3, leg4]

    return contract

def create_double_cal(ib: IB, contracts: List[Contract]) -> Contract:
    
    ib.qualifyContracts(*contracts)
    contract = Contract(symbol=contracts[0].symbol, secType='BAG', exchange='SMART', currency='USD')
    
    leg1 = ComboLeg(conId=contracts[0].conId, ratio=1, action='SELL', exchange=contracts[0].exchange)
    leg2 = ComboLeg(conId=contracts[1].conId, ratio=1, action='BUY', exchange=contracts[1].exchange)
    leg3 = ComboLeg(conId=contracts[2].conId, ratio=1, action='SELL', exchange=contracts[2].exchange)
    leg4 = ComboLeg(conId=contracts[3].conId, ratio=1, action='BUY', exchange=contracts[3].exchange)
    
    contract.comboLegs = [leg1, leg2, leg3, leg4]

    return contract


def create_ici(ib: IB, contracts: List[Contract]) -> Contract:
    
    ib.qualifyContracts(*contracts)
    contract = Contract(symbol=contracts[0].symbol, secType='BAG', exchange='SMART', currency='USD')
    
    leg1 = ComboLeg(conId=contracts[0].conId, ratio=1, action='BUY', exchange=contracts[0].exchange)
    leg2 = ComboLeg(conId=contracts[1].conId, ratio=1, action='SELL', exchange=contracts[1].exchange)
    leg3 = ComboLeg(conId=contracts[2].conId, ratio=1, action='BUY', exchange=contracts[2].exchange)
    leg4 = ComboLeg(conId=contracts[3].conId, ratio=1, action='SELL', exchange=contracts[3].exchange)
    
    contract.comboLegs = [leg1, leg2, leg3, leg4]

    return contract