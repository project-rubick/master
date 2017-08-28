# -*- coding: utf-8 -*-
from math import floor
from TradeData import tradeData
import copy

#a collection of trades
class positionData:
    __tickerList = list()
    __MTM = 0
    __dailyPnl = 0
    __closedPosition = list()
    
    def __init__(self,**kwargs):
        self.newTrades = kwargs.get("trades")
        self.AUM = kwargs.get("AUM")
        self.position = dict()
        if self.newTrades is not None:
            for trade in self.newTrades:
                self.position[trade.ticker] = trade
    #remove this
    def closeTrades(self, unwindTrades,signalEnv):
        if unwindTrades is not None:
            for ticker in unwindTrades:
                closedTrade = self.position[ticker].fullUnwind(signalEnv)
                key = closedTrade.ticker + " " + closedTrade.getCloseTime().strftime('%Y%m%d')
                self.__closedPosition[key] = closedTrade
                del self.position[ticker]
    
    def getClosedPosition(self):
        return self.__closedPosition
        
    def showPotision(self):
        for ticker in self.position: 
            self.position[ticker].showTrade()
            
    def addToExistTrade(self,newTrade):
        currentPosition = self.position[newTrade.ticker]
        currentAmount = currentPosition.quantity
        newAmount = newTrade.quantity
        if (currentAmount * newAmount >0):
            #add more exposure
            currentPosition.addTrade(newTrade)
        else:
            #reduce exposure
            closedTrade = copy.deepcopy(currentPosition)                
            closedTrade.price = newTrade.cost
            closedTrade.closeTime = newTrade.tradeTime
            if (abs(newAmount) > abs(currentAmount)):
                self.__closedPosition.append(closedTrade)
                
            else:
                #partial reduce
                closedTrade.quantity = -1 * newAmount
                self.__closedPosition.append(closedTrade)
            
            # update current holding
            currentPosition.quantity = newAmount + currentAmount
            
            # if Position closed 
            if (currentPosition.quantity == 0): del self.position[newTrade.ticker] 
            
            
    def addTrades(self,tradeList):
        
        for trade in tradeList:
            if trade.ticker in self.position:
                self.addToExistTrade(trade)
            else:
                self.position[trade.ticker] = trade
            
    def updateMarket(self,marketData):
        for ticker in self.position:
            self.position[ticker].updatePrice(marketData)
    
        
    def getMTM(self):
        return self.__MTM
        

    
  


        
if __name__ == "__main__":
    
    import datetime
    today = datetime.datetime.now()    
    t1 = tradeData(ticker='abc',quantity=-10,cost=123,tradeTime=today)
    t2 = tradeData(ticker='abc',quantity=15,cost=125,tradeTime=today)
    t3 = tradeData(ticker='lol',quantity=-10,cost=11,tradeTime=today)
    t4 = tradeData(ticker='dota',quantity=15,cost=666,tradeTime=today)
    t1.addTrade(t2)
    print(t1.getRealizedPnl())
    t1.showTrade()

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
    
    



