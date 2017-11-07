# -*- coding: utf-8 -*-
from IPython import get_ipython
get_ipython().magic('reset -sf')


from TradeData import tradeData
from PositionData import positionData
from PositionKeeper import positionTracker
import datetime

today = datetime.datetime.now()    
t1 = tradeData(ticker='abc',quantity=-10,cost=123,tradeTime=today)
t2 = tradeData(ticker='abc',quantity=15,cost=125,tradeTime=today)
t3 = tradeData(ticker='lol',quantity=-10,cost=11,tradeTime=today)
t4 = tradeData(ticker='dota',quantity=15,cost=666,tradeTime=today)
trades_list = list()
trades_list.append(t1)
trades_list.append(t3)
trades_list.append(t4)
p1 = positionData()
p1 = positionData(trades = trades_list)
p1.showPotision()      

newlist = list()
t5 = tradeData(ticker='dota',quantity=-10,cost=566,tradeTime=today)
newlist.append(t5)
p1.addTrades(newlist)

p1.showPotision()    

tracker1 = positionTracker(Portfolio = p1)
report =  tracker1.pnlReport()    