# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from math import floor
from TradeData import tradeData

#a collection of trades
class positionData:
    __tickerList = list()
    __realizedPnl = 0
    __MTM = 0
    __dailyPnl = 0
    __riskExposure = 0
    __singleRiskLimit = 0.3 # any single position can't exceed 30% of total Risklimit
    __closedPosition = dict() #key is ticker+exit time, realized pnl only calc for closed position
    
    def __init__(self,**kwargs):
        self.newTrades = kwargs.get("trades")
        self.AUM = kwargs.get("AUM")
        self.position = dict()
        if self.newTrades is not None:
            for trade in self.newTrades:
                self.position[trade.ticker] = trade
    
    def closeTrades(self, unwindTrades,signalEnv):
        if unwindTrades is not None:
            for ticker in unwindTrades:
                closedTrade = self.position[ticker].fullUnwind(signalEnv)
                key = closedTrade.ticker + " " + closedTrade.getCloseTime().strftime('%Y%m%d')
                self.__closedPosition[key] = closedTrade
                del self.position[ticker]
                
    def getClosedPosition(self):
        return self.__closedPosition
        
    # move to risk data        
    def getSingleLimit(self):
        return self.__singleRiskLimit * self.AUM
    
    # move to position tracker     
    def showClosePosition(self):
        for ticker in self.__closedPosition:
            trade = self.__closedPosition[ticker]
            print (ticker + " " + str(trade.getRealizedPnl()))
        
    def showPotision(self):
        for ticker in self.position: 
            self.position[ticker].showTrade()
            
            
    def addTrades(self,trades):

        for trade in trades:
            if trade.ticker in self.position:
                self.position[trade.ticker].addTrade(trade)
            else:
                self.position[trade.ticker] = trade
            
    def updateMarket(self,marketData):
        for ticker in self.position:
            self.position[ticker].updatePrice(marketData)
    
    # move to record keeping        
    def getRealizedPnl(self):
        return self.__realizedPnl
        
    def getMTM(self):
        return self.__MTM
        
    # move risk data    
    def getTotalRisk(self):
        return self.__riskExposure
        
    # move to record keeping
    def getPnlReport(self):
        report = dict()
        for ticker in self.position:
            trade = self.position[ticker]
            pnls = [trade.getMTM(), trade.getDailyPnl(), trade.dailyMove, trade.getRealizedPnl()]
            report[ticker] = pnls
            
        return report
        
    # move risk data    
    def getRiskTrade(self,ticker,signal):
        if ticker in self.position:
            trade = self.position[ticker]
            risk = abs(trade.quantity)*signal.loc[ticker]['sigma.eq']*1000
        else:
            risk = 0
        return risk
    # move risk data    
    def getRiskReport(self,model):
        report = dict()
        self.__riskExposure = 0
        for ticker in self.position:
            trade = self.position[ticker]
            if trade.quantity == 0 : 
                risk = 0
            else:
                risk = abs(trade.quantity)*model.loc[ticker]['sigma.eq']*1000
            self.__riskExposure = self.__riskExposure + risk
            report[ticker] = [trade.quantity, risk]
        return report
     
    # to be moved to TradingScript 
    def reduceExposure(self,priority,riskdeficit,signal,today):
        newTradesList = list()
        for ticker in reversed(priority):
            if ticker in self.position and riskdeficit < 0:
                trade = self.position[ticker]
                currentAmount = trade.quantity
                vol = signal.loc[ticker]['sigma.eq']
                px = signal.loc[ticker]['close']
                currentRisk = abs(currentAmount) * vol * 1000
                if currentRisk < abs(riskdeficit): 
                    newTradeAmount = -1*currentAmount
                else:
                    newTradeAmount = floor(riskdeficit/(currentRisk/currentAmount))
                
                newTrade = tradeData(ticker=ticker,quantity=newTradeAmount,cost=px,tradeTime=today)
                newTradesList.append(newTrade)
                riskdeficit = riskdeficit + abs(newTradeAmount)*vol*1000
                
        return newTradesList
        
    # to be moved to TradingScript    
    def positionExist(self,signal,strConfig,today):
        self.newTrades = list()
        for ticker in self.position:
            if self.position[ticker].quantity != 0 :
                s = signal.loc[ticker]['signal']
                expiry = self.position[ticker].getExpiry(today)
                amount = 0
                if s > strConfig['longExit'] and self.position[ticker].quantity > 0: amount = -1* self.position[ticker].quantity
                if s < strConfig['shortExit'] and self.position[ticker].quantity < 0: amount = -1* self.position[ticker].quantity
                if expiry <= strConfig['deadLine']: amount = -1* self.position[ticker].quantity    
                if amount !=0:
                    px = signal.loc[ticker]['close']
                    newTrade = tradeData(ticker=ticker,quantity=amount,cost=px,tradeTime=today)
                    self.newTrades.append(newTrade)
                
        self.addTrades(self.newTrades)
        return None   
    
    # to be moved to TradingScript     
    def runModel(self,signal,priority,strConfig,today):
        # step 1 check exist positions, any position we can close
        self.positionExist(signal,strConfig,today)

        # step 2 check risk after exit
        singleLimit = self.__singleRiskLimit * self.AUM
        currentRisk = self.getRiskReport(signal)
        riskBuffer = self.AUM - self.__riskExposure
        self.newTrades = list()

        
        # step 3 check risk limit, if we exceed limit, reduce exposure
        if riskBuffer < -0.2*self.AUM:
            #need to reduce exposure
            newTrade = self.reduceExposure(priority,riskBuffer,signal,today)
            self.newTrades.extend(newTrade)
            
        # step 4 if we still have some buffer and signals, add more position    
        elif riskBuffer > 0:
            # add exposure
           
            for ticker in priority:
                s = signal.loc[ticker]['signal']
                vol = signal.loc[ticker]['sigma.eq']
                amount = 0
                tradeLimit = singleLimit - self.getRiskTrade(ticker,signal)
                if s < strConfig['longBond']: amount  = floor(min(riskBuffer,tradeLimit)/vol/1000)
                if s > strConfig['shortBond']: amount = -1*floor(min(riskBuffer,tradeLimit)/vol/1000) 
                if amount != 0:
                    px = signal.loc[ticker]['close']
                    newTrade = tradeData(ticker=ticker,quantity=amount,cost=px,tradeTime=today)
                    self.newTrades.append(newTrade)
                    riskBuffer = riskBuffer - abs(amount)*vol*1000
        
        if len(self.newTrades) > 0 : self.addTrades(self.newTrades)
        newRisk = self.getRiskReport(signal)
        
        output = {'oldRisk':currentRisk, 'newRisk':newRisk}
        
        self.updateMarket(signal)
        
        return output


        
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
    pnl = p1.getPnlReport()
