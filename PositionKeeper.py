# -*- coding: utf-8 -*-

class positionTracker:

     def __init__(self,**kwargs):
         self.portfolio = kwargs.get("Portfolio")
         self.closedTrades = self.portfolio.getClosedPosition()         
     
     def addTrades(self,trade,closePrice,timeStamp):
         # caluate realized pnl 
         # give it a time timeStamp
         # then archive to the closed position
         return None
         
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
         
         
