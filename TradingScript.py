# -*- coding: utf-8 -*-

from PositionData import positionData
from TradeData import tradeData
from BackTestingHeader import expiryCalc
#from RiskData import riskReport
from math import floor


class strategy:
    
    def __init__(self,**kwargs):
        self.priority = kwargs.get("Priority")
        self.config = kwargs.get("Config")
        
    def startOfDayCheck(port, signal, priority, strConfig):
        ## exit trade by profit taking and hard deadline on expiry 
        unwindTrades = scanExit(port, signal, strConfig)
        
        ## check risk exposure
        singleLimit= port.getSingleLimit()
    
        return None
    
    def scanNewSignal(self, port, valueEnv,riskReport):
        newTrades = list()
        riskBuffer = riskReport.getRiskBuffer()
        
        today = valueEnv.getTimeStamp()
        #the single trade limit is used here, TODO, add to risk reduce?
        
    
        for ticker in self.priority:
            
            if riskBuffer > 5000: # hard code 5k for now
                tradeLimit = riskReport.singleRiskLimit * port.AUM - riskReport.getTradeRisk(ticker)
                s = valueEnv.getValue(ticker,'signal')
                vol = valueEnv.getValue(ticker,'sigma.eq')
                expiry = expiryCalc(ticker,today)
                amount = 0
                if expiry > self.config['deadLine']:
                    if s > self.config['shortBond']: amount = -1*floor(min(riskBuffer,tradeLimit)/vol/1000)
                    if s < self.config['longBond']:  amount = floor(min(riskBuffer,tradeLimit)/vol/1000)
                if amount != 0:
                    px = valueEnv.getValue(ticker,'close')
                    newTrade = tradeData(ticker = ticker, quantity = amount, cost = px, tradeTime =today)
                    newTrades.append(newTrade)
                    riskBuffer = riskBuffer - abs(newTrade.quantity) * vol * 1000
         
        return newTrades           
        
        
    def scanExit(self, port, valueEnv):
        #scan position at begining of a cycle exit if rules are met
    
        unwindTrades = list()
        today = valueEnv.getTimeStamp()
    
        for ticker in port.position:
            s = valueEnv.getValue(ticker,'signal')
            expiry = port.position[ticker].getExpiry(today)
            if s > self.config['longExit'] and port.position[ticker].quantity > 0: 
                unwindTrades.append(port.position[ticker].getUnwindTrade(valueEnv))
            if s < self.config['shortExit'] and port.position[ticker].quantity < 0: 
                unwindTrades.append(port.position[ticker].getUnwindTrade(valueEnv))
            if expiry <= self.config['deadLine']:
                unwindTrades.append(port.position[ticker].getUnwindTrade(valueEnv))
                           

        return unwindTrades                


    def reduceRiskExposure(self,port,valueEnv,riskReport):
        # reduce risk if risk limitation is exceeded.
    
        unwindTrades = list()

        riskBuffer = riskReport.getRiskBuffer()
        
        #the priority of reduce risk can be enhanced, current order is the reverse order of enter new trade.
        for ticker in reversed(self.priority):
            if ticker in port.position and riskBuffer < 0:
                trade = port.position[ticker]
                currentAmount = trade.quantity
                vol = valueEnv.getValue(ticker,"sigma.eq")

                currentRisk = abs(currentAmount) * vol *  1000
                # if risk deficit larger than currentrisk, close this position                
                if currentRisk < abs(riskBuffer):
                    newTrade = trade.getUnwindTrade(valueEnv)
                # else close partial    
                else:
                    amount = floor(riskBuffer/vol/1000)
                    newTrade = trade.getUnwindTrade(valueEnv,abs(amount))
                unwindTrades.append(newTrade)
                riskBuffer = riskBuffer + abs(newTrade.quantity) * vol * 1000
                
                
        return unwindTrades