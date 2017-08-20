# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 11:20:31 2017

@author: Heng
"""

import calendar
from datetime import timedelta


import pandas as pd    
from enum import Enum


def toMonthCode(ticker,monthCode):
    tickerCode = list()
    for t in ticker:
        code = monthCode[t]
        tickerCode.append(code)

    return tickerCode
        
        
#def generateTrade(signal_list,mktData,risk_limit,long_bond,short_bond,today):
#    raw_trades = list()
#    #t1 = trade("X08",10,1.25,today)
#    for key in list(signal_list.index):
#        s = signal_list.loc[key]['signal']
#        amount = 10 if s<long_bond else -10 #this is wrong
#        t1 = tradeData(ticker = key,
#                   quantity = amount,
#                   cost = mktData.loc[key]['close'],
#                   tradeTime = today)
#                    
#        raw_trades.append(t1)
#        
#    return raw_trades
        
        
def getMarket(histData,today,monthCode):
    todayData = histData.loc[today]
    mktData = dict()
    for ticker in todayData.index:
        code = monthCode[ticker]
        mktData[code] = todayData[ticker]
    dfMktData = pd.DataFrame.from_dict(mktData,orient='index')
    dfMktData.columns =['close']    
    return dfMktData
    
    
def getModel(filepath,filename,priority,monthCode):
    model_file = pd.read_csv(filepath+filename,index_col=0).loc[priority]
    tickerMonth = list()
    for t in list(model_file.index):
        code = monthCode[t]
        tickerMonth.append(code)
    
    model_file.index = tickerMonth
    
    return model_file
  
def getSignal(data,model):
    tickers = list(model.index)
    signals = dict()
    for t in tickers:
        model_t = model.loc[t]
        signal_t = (data.loc[t]['close']-model_t["mean"])/model_t["sigma.eq"]
        signals[t] = signal_t
    dfSignals = pd.DataFrame.from_dict(signals,orient='index')
    dfSignals.columns =['signal'] 
    output = model.join(dfSignals, how='outer')
    output = output.join(data,how='outer')
    return output

def datToSpread(dat):
    tenors = list(dat)
    spread_names = list()
    for i in range(0,len(tenors)-1):
        for j in range(i+1,len(tenors)):
            spread = dat[tenors[j]] - dat[tenors[i]]
            name = tenors[j]+"_"+tenors[i]
            spread_names.append(name)
            dat[name] = spread
            
    return dat

def next_third_Wednesday(d):
    """ Given a third friday find next third friday"""
    d += timedelta(weeks=4)
    return d if d.day >= 15 else d + timedelta(weeks=1)
    
def contractDate(d,n):
    Maturity = list()
    
    Exp_thisMonth = calendar.Calendar(2).monthdatescalendar(d.year, d.month)[3][0]
    if Exp_thisMonth >= d:
        Maturity.append(Exp_thisMonth)
    else:
        Maturity.append(next_third_Wednesday(Exp_thisMonth))
    
    for i in range(n-1):
        Maturity.append(next_third_Wednesday(Maturity[i]))
    
    return Maturity

def expiryCalc(ticker,today):
    dates = contractDate(today,7)
    monthMap = {"F":1, "G":2, "H":3,"J":4,"K":5, "M":6, "N":7,"Q":8,"U":9, "V":10, "X":11,"Z":12}
    code = ticker.split("_")   
    month = monthMap[code[1][0]]
    for date in dates:
        if month == date.month : expiry = date - today
    
    return expiry.days



    
def contractCode(d,n):
    monthcode = {1:"F", 2:"G", 3:"H",4:"J",5:"K", 6:"M", 7:"N",8:"Q",9:"U", 10:"V", 11:"X",12:"Z"}
    dates = contractDate(d,n)
    code_list = list(map(lambda aday: monthcode[aday.month] + str(aday.year)[2:],dates))
    code = dict()
    contract_list = ['f1','f2','f3','f4','f5','f6','f7']
    for i in range(len(code_list)):
        code[contract_list[i]] = code_list[i]

    for i in range(0,len(code_list)-1):
        for j in range(i+1,len(code_list)):
            futName = contract_list[j]+"_"+contract_list[i]
            monName = code[contract_list[j]]+"_"+code[contract_list[i]]
            code[futName] = monName
    
    return code

def tradeFilter(tradeList, priority, monthCodeMap):
    priority_code = list()

    for ticker in priority:
        priority_code.append(monthCodeMap[ticker])
    priorityMap = dict()
    TopOrder = 100  # this looks stupid, is there a better to get Top priority trade
    TopOrderTrade = None
    for trade in tradeList:
        ticker = trade.ticker
        order = priority_code.index(ticker)
        priorityMap[ticker] = order
        if TopOrder > order:
            TopOrder = order
            TopOrderTrade = trade
    tradeList = list()
    tradeList.append(TopOrderTrade)    
    return tradeList





    



