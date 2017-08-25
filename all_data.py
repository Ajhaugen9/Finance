import pandas as pd
import numpy as np
from pandas_datareader import data as web
import datetime
import sys
from yahoo_finance import Share
import os
import csv
import sqlite3


start = datetime.date(2000,1,1)
end = datetime.date.today()

stocklist = pd.read_csv('stocklist.csv',header=0)

conn = sqlite3.connect('Finance Project.db')
c = conn.cursor()
#c.execute("CREATE TABLE Stockdata (Name TEXT, Symbol TEXT, Date TEXT, Year TEXT, Month TEXT, Day TEXT, Open INTEGER, High INTEGER, Low INTEGER, Close INTEGER, Change INTEGER, PChange INTEGER, Volume INTEGER)")

for s in range(len(stocklist['Symbol'])):
    try:
        symbol = stocklist['Symbol'][s]

        sym_data = web.DataReader(symbol,'google',start)
        sym_data = sym_data.reset_index()
        sym_data['Name'] = list(stocklist.loc[stocklist['Symbol']==symbol,'Name'])[0]
        sym_data['Symbol'] = symbol
        sym_data['Date'] = [sym_data['Date'][x].date() for x in range(len(sym_data.index))]
        sym_data['Year'] = [str(sym_data['Date'][x].year) for x in range(len(sym_data['Date']))]
        sym_data['Month'] = [str(sym_data['Date'][x].month) for x in range(len(sym_data['Date']))]
        sym_data['Day'] = [str(sym_data['Date'][x].day) for x in range(len(sym_data['Date']))]
        sym_data['Date'] = [str(sym_data['Date'][x]) for x in range(len(sym_data['Date']))]
        sym_data['Change'] = sym_data['Close'].diff()
        sym_data['PChange'] = sym_data['Close'].pct_change()
        sym_data = sym_data[['Name','Symbol','Date','Year','Month','Day','Open','High','Low','Close','Change','PChange','Volume']]
        sym_data.to_sql('Stockdata',conn,if_exists='append')
        print symbol, round(float(s)/float(len(stocklist['Symbol']))*100,3)

    except:
        print 'ERROR', symbol



