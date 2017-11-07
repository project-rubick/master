# -*- coding: utf-8 -*-


class riskReport:
     __riskExposure = 0
     __riskBuffer = 0
     __riskReport = dict()
     # risk action
     # 1. total risk less than AUM * ratio
     # 2. single position risk less than AUM * single limit
     # 3. 
    
     def __init__(self,**kwargs):
         self.portfolio = kwargs.get("Portfolio") 
         self.valueEnv = kwargs.get("ValuationEnv")
         self.singleRiskLimit = kwargs.get("SingleRiskLimit")
         self.capitalRiskRatio = kwargs.get("CapitalRiskRatio")
         self.updateRisk()
         
     
     def getTotalRisk(self):
         return self.__riskExposure
         
     def getRiskReport(self):
         return self.__riskReport
     
     def getRiskBuffer(self):
         return self.__riskBuffer
         
         
     def getTradeRisk(self,ticker):
         if ticker in self.portfolio.position:
             trade = self.portfolio.position[ticker]
             risk = abs(trade.quantity)*self.valueEnv.getValue(ticker,'sigma.eq')*1000
         else:
             risk = 0
         return risk
             
     
     def updateRisk(self):
         self.__riskReport = dict()
         self.__riskExposure = 0
         for ticker in self.portfolio.position:
             risk = self.getTradeRisk(ticker)
             self.__riskExposure = self.__riskExposure + risk
             self.__riskReport[ticker] = [self.portfolio.position[ticker].quantity, risk]
         self.__riskBuffer = self.portfolio.AUM * self.capitalRiskRatio - self.__riskExposure
         
         
         