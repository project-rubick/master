# -*- coding: utf-8 -*-

from PositionData import positionData
from TradeData import tradeData


def startOfDayCheck(port, signal, priority, strConfig):
    ## exit trade by profit taking and hard deadline on expiry 
    unwindTrades = scanExit(port, signal, strConfig)
    port.closeTrades(unwindTrades)
    
    ## check risk exposure
    singleLimit= port.getSingleLimit()
    
    return None
    
def scanExit(port, signal, strConfig):
    unwindTrades = list()
    today = signal.getTimeStamp()
    
    for ticker in port.position:
        s = signal.getValue(ticker,'signal')
        expiry = port.position[ticker].getExpiry(today)
        if s > strConfig['longExit'] and port.position[ticker].quantity > 0: unwindTrades.append(ticker)
        if s < strConfig['shortExit'] and port.position[ticker].quantity < 0: unwindTrades.append(ticker)
        if expiry <= strConfig['deadLine']: unwindTrades.append(ticker)  

                
        #port.closeTrades(unwindTrades) ## Todo add close Trade func in Position
        return unwindTrades                


            