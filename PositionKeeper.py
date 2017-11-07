# -*- coding: utf-8 -*-
import pandas as pd

class positionTracker: 
    
     
     def __init__(self,**kwargs):
         self.portfolio = kwargs.get("Portfolio")
         self.closedTrades = self.portfolio.getClosedPosition()         
     
     def addTrades(self,trade,closePrice,timeStamp):
         # caluate realized pnl 
         # give it a time timeStamp
         # then archive to the closed position
         return None
     
     def writePosition(self, path, time):
         output = list()
         outputDf = pd.DataFrame()
         for ticker in self.portfolio.position:
             trade = self.portfolio.position[ticker]
             output.append([trade.ticker, trade.quantity, trade.cost, trade.price, trade.getMTM()])
           
         outputDf = pd.DataFrame(output, columns = ['ticker','quantity','cost','price','PnL'])

         filename = path + "\\" + "Position" + str(time) +".csv"
         
         outputDf.to_csv(filename)
            
     def writeClosedPosition(self,path,time):
         output = list()
         outputDf = pd.DataFrame()
         for trade in self.closedTrades:
             
             output.append([trade.closeTime,trade.ticker, trade.quantity, trade.cost, trade.price, trade.getMTM()])
           
         outputDf = pd.DataFrame(output, columns = ['closedate','ticker','quantity','cost','price','PnL'])

         filename = path + "\\" + "ClosedPosition" + str(time) +".csv"
         
         outputDf.to_csv(filename)
         
     def pnlReport(self):
         # do a realized pnl report by trade, todo, by time, by risk
         report = dict()
         
         for trade in self.closedTrades:
             ticker = trade.ticker
             realizedPnl = trade.quantity * (trade.price - trade.cost) * 1000
             if ticker in report:
                 report[ticker] = report[ticker] + realizedPnl
             else: 
                 report[ticker] = realizedPnl
                 
         return report   
         
     def getTotalRealizedPnl(self):
         total = 0
         report = self.pnlReport()
         for ticker in report:
             total = total + report[ticker]
              
         return total    
