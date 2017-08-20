# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from IPython import get_ipython
get_ipython().magic('reset -sf')

from BackTestingHeader import *
from TradeData import tradeData
from PositionData import positionData
from datetime import datetime
from enum import Enum
import pickle
from os import listdir
from os.path import isfile, join
import pandas as pd

wkdir = 'F:\\Google Drive\\Vol_research\\volatility\\'

mypath = wkdir + 'backTesting\\'
output = mypath + 'CleanSignal\\'

ModelFiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
file_old = pd.read_csv(mypath + ModelFiles[0],index_col =0)
#file_old.loc['f2_f1']
#file_old.index
for f in ModelFiles:
    file = pd.read_csv(mypath + f,index_col =0)
    for ticker in file.index:
        if file.loc[ticker]['mean'] == 0: file.loc[ticker]['mean'] = file_old.loc[ticker]['mean']
        if file.loc[ticker]['sigma.eq'] == 0: file.loc[ticker]['sigma.eq'] = file_old.loc[ticker]['sigma.eq']
    file.to_csv(output + f)
    file_old = file
    
