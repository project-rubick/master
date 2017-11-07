# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from IPython import get_ipython
get_ipython().magic('reset -sf')

#%load_ext autoreload
#%autoreload 2

from BackTestingHeader import *
from TradingScript import strategy
from TradeData import tradeData
from PositionData import positionData
from PositionKeeper import positionTracker
from RiskData import riskReport
from MarketData import valueEnv
from datetime import datetime
from enum import Enum
import pickle
from os import listdir
from os.path import isfile, join
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import copy

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
                  'shortBond':99.2,
                  'longExit': 0.5,
                  'shortExit': -0.5,
                  'deadLine': 7}
Port = positionData(AUM=AUM1)
######### config done
acumPnl = list()
totalDf = pd.DataFrame()          
TotaltradesList = list()
   
for today in dates:
    monthCode = contractCode(today,7)
    priorityCode = toMonthCode(priority,monthCode)
    Str  = strategy(Priority = priorityCode, Config = strategyConfig)
    modelData = getModel(mypath,'NewScan'+today.strftime('%Y%m%d')+'.csv' ,priority,monthCode)
    mktData = getMarket(dat_spread,today,monthCode)
    signal = valueEnv(Date = today, Market = getSignal(mktData,modelData), MonthCode = monthCode)
    risk = riskReport(Portfolio = Port, ValuationEnv = signal, SingleRiskLimit = 0.3, CapitalRiskRatio = 1)
    tradeListToday = list()
    
    #1. scan exit trade    
    exitTrades = Str.scanExit(Port,signal)
    Port.addTrades(exitTrades)
    risk.updateRisk()
    #make a copy of trades for reporting
    tradeListToday.extend(copy.deepcopy(exitTrades))

    #2. reduce risk
    reduceRiskTrades = Str.reduceRiskExposure(Port,signal,risk)
    Port.addTrades(reduceRiskTrades)
    risk.updateRisk()
    tradeListToday.extend(copy.deepcopy(reduceRiskTrades))
                                
    #3. scan new Trade
    newTrades = Str.scanNewSignal(Port,signal,risk)
    Port.addTrades(newTrades)
    risk.updateRisk()
    Port.updateMarket(signal)
    tradeListToday.extend(copy.deepcopy(newTrades))    
    
    #4.pnl report
    keeper = positionTracker(Portfolio = Port)
    pnl_realized = keeper.getTotalRealizedPnl()
    pnl_mtm      = Port.getMTM()
    pnl_today  = pnl_realized + pnl_mtm
    acumPnl.append(pnl_today)
    
    if pnl_realized > 100000*np.sqrt(255):
        Port.AUM = pnl_realized/np.sqrt(255)
    else:
        Port.AUM = 100000
    
    TotaltradesList.extend(tradeListToday)    
    # append total data    
    df1 = signal.dataFrame
    df1['date'] = pd.Series([today]*5,index = df1.index)
    totalDf = totalDf.append(df1)
    
    
    #write Position
    keeper.writePosition(output,today)
    keeper.writeClosedPosition(output,today)
    
    #write New Trade
    outputList =list()    
    outputDf = pd.DataFrame()
    for trade in tradeListToday:
        outputList.append([trade.ticker, trade.quantity, trade.cost])
           
    outputDf = pd.DataFrame(outputList, columns = ['ticker','quantity','price'])
    outputDf.to_csv(output+"\\Trade"+str(today)+".csv")
  
                      
keeper = positionTracker(Portfolio = Port)                  
pnls = keeper.pnlReport()                  



time_plt = np.array(dates)
pnl_plt = np.array(acumPnl)

plt.plot(time_plt,pnl_plt)

len(acumPnl)
math.pow(1.27,10)
x=acumPnl[2161]/np.sqrt(255)/100000
math.pow(x,0.1)


TotalTradeOutPutList =list()    
outputDf = pd.DataFrame()
for trade in TotaltradesList:
    TotalTradeOutPutList.append([trade.tradeTime, trade.ticker, trade.quantity, trade.cost])
           
outputDf = pd.DataFrame(TotalTradeOutPutList, columns = ['date','ticker','quantity','price'])
outputDf.to_csv(wkdir+"\\AllTrades.csv")

# TODO: put the plot into function then run the plot for every spread.
spread_list = np.unique(totalDf.index)
for spread in spread_list:
    sampleTrades = tradesFilter(TotaltradesList,spread)
    sample = totalDf.loc[spread]
    sample_plot=pd.merge(sampleTrades,sample, how= 'outer',left_on="date" , right_on="date")
    sample_plot=sample_plot.fillna(0)
    time_plt = np.array(sample_plot['date'])
    pnl_plt = np.array(sample_plot['close'])
    trade_plt = np.array(sample_plot['quantity'])
    size = abs(trade_plt)+10
    #%matplotlib qt
    fig = plt.figure()
    plt.scatter(time_plt,pnl_plt,c=trade_plt,s=size)
    #plt.colorbar()
    fig.savefig(output + '\\plot\\'+ spread + '.png')
    #plt.plot(time_plt,pnl_plt,'-o')







