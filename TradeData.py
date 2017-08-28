# -*- coding: utf-8 -*-
from BackTestingHeader import expiryCalc
import copy



class tradeData:
    # python don't allow constructor overload, use **kwargs
    __realizedPnl = 0
    __MTM = 0
    #__dailyPnl = 0
   
    __liveTrade = True    
    
    def __init__(self,**kwargs):
        self.ticker = kwargs.get("ticker")
        self.quantity = kwargs.get("quantity")
        self.tradeTime = kwargs.get("tradeTime")
        self.cost = kwargs.get("cost")  # price when enter the trade
        self.price = self.cost 
        #self.dailyMove = 0
        self.expiry = None
        self.closeTime = None
    
    def isAlive(self):
        return self.__liveTrade

    def getCloseTime(self):
        return self.closeTime        
        
    def getRealizedPnl(self):
        return self.__realizedPnl
     
    def getExpiry(self,today):
        self.expiry = expiryCalc(self.ticker,today)        
        return self.expiry
        
    def getMTM(self):
        return self.__MTM
    
    def getDailyPnl(self):
        return self.__dailyPnl                
            
    def updatePrice(self,signalEnv):
        newPrice = signalEnv.getValue(self.ticker,'close')
        #Move =  (newPrice - self.price)       
        #self.__dailyPnl = self.quantity *Move*1000 #assuming daily pnl tracking this should be better handled for intraday trading
        self.price = newPrice
        self.__MTM = self.quantity*(self.price - self.cost)*1000
    
    # this is a full unwind of the trade, so the function return a closed trade,
    # the self should be del after wards     
    def fullUnwind(self,signalEnv):
        self.updatePrice(signalEnv)
        self.__realizedPnl = self.__realizedPnl + self.__MTM
        self.__liveTrade = False
        self.closeTime = signalEnv.getTimeStamp()
        closedTrade = copy.deepcopy(self)
        return closedTrade    
        
    # return partial unwind trade, if the amount happen to be the full amount, do a full unwind.    
    def PartialUnWind(self,signalEnv,amount):
        self.updatePrice(signalEnv)
        if amount == self.quantity:
            closedTrade = self.fullUnwind(signalEnv)
            return closedTrade
        else:
            oldTrade = copy.deepcopy(self)
            self.quantity = self.quantity - amount
            self.updatePrice(signalEnv) #udpate MTM after unwind
            oldTrade.quantity = amount
            closedTrade = oldTrade.fullUnwind(signalEnv)
            return closedTrade
        
        
    def addTrade(self,newTrade):
        # check if the ticker is the same
        if (self.ticker is newTrade.ticker):
            #self.tradeTime = newTrade.tradeTime
            #calc new cost, quantity, reliazedPnl if closed some position
            if (self.quantity*newTrade.quantity < 0 ):
                realizedQuantity = -1*newTrade.quantity if abs(self.quantity) > abs(newTrade.quantity) else self.quantity
                self.__realizedPnl = self.__realizedPnl + realizedQuantity*1000*(newTrade.cost - self.cost)
                self.cost = self.cost if abs(self.quantity) > abs(newTrade.quantity) else newTrade.cost
                self.quantity = self.quantity + newTrade.quantity
                
            else:
                newQuantity = self.quantity + newTrade.quantity
                self.cost = (self.quantity*self.cost + newTrade.quantity*newTrade.cost)/newQuantity
                self.quantity = newQuantity
                
        else:
            print("Wrong ticker: trying to add "+str(newTrade.ticker) + " to "+ str(self.ticker))
            
    def showTrade(self):
        print(self.ticker+" "+str(self.quantity)+" @ " + str(self.cost) + " last trade " +self.tradeTime.strftime('%Y-%m-%d'))

#t1 = trade(ticker='abc',quantity=-10,cost=123,tradeTime=today)
#t2 = trade(ticker='abc',quantity=15,cost=125,tradeTime=today)
#t1.addTrade(t2)
#print(t1.getRealizedPnl())
#t1.showTrade()


        
            
        
        
        
        
if __name__ == "__main__":
    
    import datetime
    today = datetime.datetime.now()    
    t1 = tradeData(ticker='H09_F09',quantity=-10,cost=1,tradeTime=today)
    t2 = tradeData(ticker='abc',quantity=15,cost=125,tradeTime=today)
    t3 = tradeData(ticker='lol',quantity=-10,cost=11,tradeTime=today)
    t4 = tradeData(ticker='dota',quantity=15,cost=666,tradeTime=today)
    #t1.addTrade(t2)
    #print(t1.getRealizedPnl())
    t1.showTrade()
    
    closed = t1.PartialUnWind(signal,-2)
    closed.showTrade()
    closed.getMTM()
    t1.getMTM()
