import os
import pandas as pd
from pandas_datareader import data as web
from datetime import datetime, date, timedelta
from yahoo_finance import Share
from threading import Timer
import time
import csv
from collections import deque
import datetime


def update_stock_data():
    stock_info = pd.DataFrame.from_csv('stocklist.csv',header=0,index_col=0)
    path = "C:\\Users\\ajhau\\Desktop\\Sector_data"
    glpath = "C:\\Users\\ajhau\\Desktop\\Finance Program\\finance5\\program\\Gainer_loser\\gainer_loser.csv"
    #path = "C:\\Users\\ajhau\\Desktop\\testing\\testing\\csv"
    sectors = list(set(stock_info['Sector']))
    sectors = sorted(sectors[1:])
    clear_gl = open(glpath,'w+')
    clear_gl.close()

    ydate = datetime.date.today()
    todays_data = {}
    n = 0
    for files in os.listdir(path):
        sector = sectors[n]
        with open(path+'\\'+files) as f:
            reader = csv.reader(f)
            sec_symbols = next(reader)
            sec_symbols = sorted(list(set(sec_symbols[1:])))
            lastdate = deque(csv.reader(f), 1)[-1][0]
            lastdate = pd.to_datetime(lastdate).date()
        if lastdate < ydate:
            updated_dict = {}
            x = 0 
            for symbol in sec_symbols:
                try:
                    updated_data = web.DataReader(str(symbol),'google',lastdate)
                    mrkcap = Share(str(symbol)).get_market_cap()
                    if mrkcap is None:
                        mrkcap = 0.0
                        updated_data['Mrk Cap'] = mrkcap
                    elif 'M' in mrkcap:
                        mrkcap = float(mrkcap[:-1])*1000000
                        updated_data['Mrk Cap'] = mrkcap
                    elif 'B' in mrkcap:
                        mrkcap = float(mrkcap[:-1])*1000000000
                        updated_data['Mrk Cap'] = mrkcap
                    updated_data['Change'] = updated_data['Close'].diff()
                    updated_data['% Change'] = updated_data['Close'].pct_change()
                    updated_dict[symbol] = updated_data    
                    todays_data[sector+':'+symbol] = updated_data[['% Change','Change','Close','Mrk Cap','Volume']].tail(1)
                    print sector+' ['+symbol+']'+': '+str((round(float(x)/float(len(sec_symbols)),2))*100)+'%', str((round(float(x)/float(4942),4))*100)+'%'
                    x += 1
                except:
                    pass
            reform = {(outk, ink): values for outk, ind in updated_dict.iteritems() 
                for ink, values in ind.iteritems()}
            updated_data = pd.DataFrame(reform)
            updated_data.index = pd.to_datetime(updated_data.index)
            updated_data = updated_data[1:] #only keep new data
            with open(path+'\\'+files,'a') as file_upd:
                updated_data.to_csv(file_upd, header = False)
        else:
            print "No update"
        n += 1

    reform = {(outk, ink): values for outk, ind in todays_data.iteritems() 
        for ink, values in ind.iteritems()}
    todays_data = pd.DataFrame(reform)
    todays_data.index = pd.to_datetime(todays_data.index)
    todays_data.to_csv(glpath)
    print updated_data
    print todays_data

def time_it():
    start_time = time.time()
    update_stock_data()
    end_time = time.time()
    print 'Time:', end_time - start_time

time_it()