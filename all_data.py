import pandas as pd
import numpy as np
from pandas_datareader import data as web
import datetime
import sys
from yahoo_finance import Share
import os
import csv

def pull_stock_data():
    start = datetime.date(2000,1,1)
    end = datetime.date.today()
    stock_info = pd.DataFrame.from_csv('stocklist.csv',header=0,index_col=0)
    #path = "C:\\Users\\ajhau\\Desktop\\Finance Program\\finance5\\program\\Sector_data"
    path = "C:\\Users\\ajhau\\Desktop\\Sector_data"

    #makes sure the files are empty and get all the file names
    file_names = []
    for files in os.listdir(path):
       if files.endswith(".csv"):
            file_names.append(str(files))
            f = open(path+'\\'+files,'w+')
            f.close()

    sectors = list(set(stock_info['Sector']))
    sectors = sorted(sectors[1:])
    symbols = []
    for i in range(len(file_names)):
        sector = sectors[i]
        file_name = file_names[i]
        sector_symbols = list(stock_info.loc[stock_info['Sector'] == sector, 'Symbol'])

        sec_data_dict = {}
        for symbol in sector_symbols:
            print symbol
            symbols.append(symbol)
            bad = []
            try:
                data = web.DataReader(str(symbol),'google',start,end)
                mrkcap = Share(str(symbol)).get_market_cap()
                if mrkcap is None:
                    mrkcap = 0.0
                    data['Mrk Cap'] = mrkcap
                elif 'M' in mrkcap:
                    mrkcap = float(mrkcap[:-1])*1000000
                    data['Mrk Cap'] = mrkcap
                elif 'B' in mrkcap:
                    mrkcap = float(mrkcap[:-1])*1000000000
                    data['Mrk Cap'] = mrkcap
                data['Change'] = data['Close'].diff()
                data['% Change'] = data['Close'].pct_change()
                sec_data_dict[symbol] = data
                print len(symbols), str(round(float(len(symbols))/float(4942),5))+'%'
            except:
                bad.append(symbol)

        reform = {(outk, ink): values for outk, ind in sec_data_dict.iteritems() 
                  for ink, values in ind.iteritems()}

        sector_data = pd.DataFrame(reform)
        sector_data.index = pd.to_datetime(sector_data.index)

        sector_data.to_csv(path+'\\'+str(file_name))

        #sector_data = pd.DataFrame.from_dict({(i,j): sec_data_dict[i][j] for i in sec_data_dict.keys() 
        #                                     for j in sec_data_dict[i].keys()},orient='index').T




pull_stock_data()


#def test1():
#    st = time.time()
#    sym_ind = [0]
#    for i, s in enumerate(header_rows):
#        if s == '% Change':
#            sym_ind.append(i)
#        elif s == 'Change':
#            sym_ind.append(i)
#        elif s == 'Close':
#            sym_ind.append(i)
#        elif s == 'Mrk Cap':
#            sym_ind.append(i)
#        elif s == 'Volume':
#            sym_ind.append(i)
#    sym_ind = np.array(sym_ind)
#    data = pd.read_csv(path+'\\'+file_names[index_num],header=0,index_col=0,usecols=sym_ind)[-1:]
#    data.columns = [x.split('.')[0] for x in data.columns]
#    et = time.time()
#    return et-st



def test():
    gl_path = "C:\\Users\\ajhau\\Desktop\\Finance Program\\finance5\\program\\Gainer_loser\\gainer_loser.csv"
    sec_path = "C:\\Users\\ajhau\\Desktop\\Finance Program\\finance5\\program\\Sector_data"
    
    data = []
    for files in os.listdir(sec_path):
       if files.endswith(".csv"):
            gl_data = pd.read_csv(sec_path+'\\'+files, header=[0,1])[-1:]
            data.append(gl_data)
    data = pd.concat(data,axis=1,join_axes=[gl_data.index])

            

            sym_ind = np.array(sym_ind)
            data = pd.read_csv(path+'\\'+file_names[index_num],header=0,index_col=0,usecols=sym_ind)[-1:]
            data.columns = [x.split('.')[0] for x in data.columns]
        et = time.time()
        return et-st, data

