# -*- coding: utf-8 -*-

class valueEnv:
    
     def __init__(self,**kwargs):
         self.date = kwargs.get("Date")
         self.dataFrame = kwargs.get("Market") #include esitmated model and market data
         self.tickerMap = kwargs.get("MonthCode")
     
     def checkTicker(self, ticker):
         if ticker in self.tickerMap:
             return self.tickerMap[ticker]
         else:
             return ticker
     
     def getValue(self,ticker,field):
         ticker = self.checkTicker(ticker)
         value = self.dataFrame.loc[ticker][field]
         return value

     def getTimeStamp(self):
         return self.date
         
     def getReverseTicker(self):
         reverseMap = dict()
         for ticker in self.tickerMap:
             code = self.tickerMap[ticker]
             reverseMap[code] = ticker
            
         return reverseMap
         
#if __name__ == "__main__":
    
