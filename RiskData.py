# -*- coding: utf-8 -*-


class riskReport:
     __riskExposure = 0
     __singleRiskLimit = 0.3
    
     def __init__(self,**kwargs):
         self.portfolio = kwargs.get("Portfolio") # is this passed by reference?
         self.valueEnv = kwargs.get("ValuationEnv")
         
     
     def getTotalRisk(self):
         return self.__riskExposure
         
     def getTradeRisk(self,ticker):
         if ticker in self.portfolio.position:
             trade = self.portfolio.position[ticker]
             risk = abs(trade.quantity)*self.valueEnv.getValue(ticker,'vol')*1000
         else:
             risk = 0
         return risk
     
     def getRiskReport(self):
         report = dict()
         self.__riskExposure = 0
         for ticker in self.portfolio.position:
             risk = self.getTradeRisk(ticker)
             self.__riskExposure = self.__riskExposure + risk
             report[ticker] = [self.portfolio.position[ticker].quantity, risk]
             
         return report