# -*- coding: utf-8 -*-
from IPython import get_ipython
get_ipython().magic('reset -sf')


from BackTestingHeader import *
from TradeData import tradeData
from PositionData import positionData
from MarketData import signalEnv
from datetime import datetime
from enum import Enum
import pickle
from os import listdir
from os.path import isfile, join
import pandas as pd

## todo, add market data (including model parameters ) object, such that the parse is safe


wkdir = 'F:\\Google Drive\\Vol_research\\volatility\\'

mypath = wkdir + 'backTesting\\CleanSignal\\'
output = wkdir + 'backTesting\\TestPnl\\'
ModelFiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

date_string = list(map(lambda g: g[7:15], ModelFiles))
dates = list(map(lambda f: datetime.strptime(f,"%Y%m%d").date(), date_string))
#date = datetime.strptime(date_string[1],"%Y%m%d")
lastday = date_string[-1]
datafile = wkdir+'\\data\\'+'VX'+lastday+".csv"
dat = pd.read_csv(datafile,index_col=0)
dat.index = pd.to_datetime(dat.index)
dat = datToSpread(dat)
trade_spread = ["f3_f1","f4_f2","f5_f3","f6_f4","f7_f5"]
dat_spread = dat[trade_spread]
#dat.describe()

#dat.head()
######### market data done
AUM1 = 100000
testPort1 = positionData(AUM=AUM1)
priority = ["f4_f2","f5_f3","f6_f4","f7_f5","f3_f1"]
strategyConfig = {'longBond' : -0.8,
                  'shortBond':1.2,
                  'longExit': 0.5,
                  'shortExit': -0.5,
                  'deadLine': 7}
Port = positionData(AUM=AUM1)
######### config done
#                
#for today in dates:
#    monthCode = contractCode(today,7)
#    priorityCode = toMonthCode(priority,monthCode)
#    modelData = getModel(mypath,'NewScan'+today.strftime('%Y%m%d')+'.csv' ,priority,monthCode)
#    mktData = getMarket(dat_spread,today,monthCode)
#    signal = getSignal(mktData,modelData)                        
#    runModel = Port.runModel(signal,priorityCode,strategyConfig,today)             
#    pnl = pd.DataFrame.from_dict(Port.getPnlReport(),orient ='index')
#    pnl.columns =['MTM','dailyPnl','move','RealizedPnl']               
#    pnl.to_csv(output + 'pnl'+ today.strftime('%Y%m%d')+'.csv')              
                  
                  
                  
                  

                  
                  
                  
today = dates[0]    
monthCode = contractCode(today,7)
priorityCode = toMonthCode(priority,monthCode)
modelData = getModel(mypath,ModelFiles[0],priority,monthCode)
mktData = getMarket(dat_spread,today,monthCode)
#signal = getSignal(mktData,modelData)
signal = signalEnv(Date = today, Market = getSignal(mktData,modelData), MonthCode = monthCode)
signal.getTimeStamp()
signal.getValue('H09_F09','close')
signal.getValue('f5_f3','close')

testPort2 = positionData(AUM=AUM1)
testPort2.getRiskReport(modelData)

t1 = tradeData(ticker='H09_F09',quantity=-10,cost=1,tradeTime=today)
trades = list()
trades.append(t1)
testPort2.addTrades(trades)
testPort2.showPotision()

unwind = ['H09_F09']
testPort2.closeTrades(unwind,signal)
testPort2.showClosePosition()
#report = testPort2.runModel(signal,priorityCode,strategyConfig,today)
#testPort2.updateMarket(mktData)
#pnl = pd.DataFrame.from_dict(testPort2.getPnlReport(),orient ='index')
#pnl.columns =['MTM','dailyPnl','move','RealizedPnl'] 
####
####### day2 let's give it a try
#today2 = dates[3]    
#monthCode2 = contractCode(today2,7)
#priorityCode2 = toMonthCode(priority,monthCode2)
#modelData2 = getModel(mypath,ModelFiles[3],priority,monthCode2)
#mktData2 = getMarket(dat_spread,today2,monthCode2)
#signal2 = getSignal(mktData2,modelData2)
#report2 = testPort2.runModel(signal2,priorityCode,strategyConfig,today2)
#testPort2.updateMarket(mktData2)
#pnl = pd.DataFrame.from_dict(testPort2.getPnlReport(),orient ='index')
#pnl.columns =['MTM','dailyPnl','move','RealizedPnl'] 