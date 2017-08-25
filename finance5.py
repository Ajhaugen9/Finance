from PyQt4.uic import loadUiType
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas,NavigationToolbar2QT as NavigationToolbar)
import matplotlib.gridspec as gridspec
from matplotlib.widgets import *
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc, candlestick2_ohlc, volume_overlay
from matplotlib.ticker import LinearLocator, MaxNLocator
from matplotlib.dates import AutoDateLocator, HourLocator, MonthLocator, WeekdayLocator
import numpy as np
from matplotlib.dates import date2num
import math
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas_datareader import data as web
import datetime
from matplotlib.widgets import MultiCursor
import csv
from lxml import html
import requests
from yahoo_finance import Share
import string
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import os
import time
from datetime import timedelta
from collections import deque
from StringIO import StringIO
import sqlite3

####To do list#####
# 1. moving avg are being called but not plotted. mot being removed on edit page
# 2. volume need to be a bar graph or histogram
# 3. candlesticks

st_ = time.time()
years = YearLocator()   # every year
months = MonthLocator()  # every month
yearsFmt = DateFormatter('%Y')

start = datetime.date(2000,1,1)
end = datetime.date.today()

date_index = pd.read_csv('Sector_data/basic.csv',header=0,index_col=0,usecols=[0])[2:]
stock_list = pd.read_csv('stocklist.csv',header=0)
loaded_symbol_data = {} #if a stock is searched the data is loaded to the dict for easier access later
loaded_comp_data = {}
loaded_csdata = {}
todaysdata = {}

#glpath = "C:\\Users\\ajhau\\Desktop\\Finance Program\\finance5\\program\\Gainer_loser\\gainer_loser.csv"
#gldata = pd.read_csv(glpath, header=[0,1], index_col=0).tail(1)
#glsym = sorted(list(set(gldata.columns.get_level_values(0))))
#glv = sorted(list(set(gldata.columns.get_level_values(1))))
#glpd = pd.DataFrame(index=glsym,columns=glv)

#for i in range(len(glv)):
#    glpd[glpd.columns[i]] = [gldata[sym][glpd.columns[i]][0] for sym in glsym]
#glpd = glpd.dropna()

sec_data_path = "C:\\Users\\ajhau\\Desktop\\Sector_data" #-test
sectors = list(set(stock_list['Sector']))
sectors = sorted(sectors[1:])
sec_file_names = []
for files in os.listdir(sec_data_path):
    if files.endswith(".csv"):
        sec_file_names.append(str(files))

date_index = pd.to_datetime(date_index.index)
date_index = date_index[:-2]
date_e = date_index[-2].to_pydatetime()
year = date_e.year
month = date_e.month
day = date_e.day
et_ = time.time()
print 'Initial Setup Time:', et_- st_

outst = time.time()
Ui_MainWindow, QMainWindow = loadUiType('Finance_temp.ui')
class Main(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        st = time.time()
        super(Main, self).__init__(parent)
        self.setupUi(self)   
        inst = time.time()
        print 'Main Class', inst-outst

        '''Open each window'''
        self.mdiArea.addSubWindow(self.sector_summary)
        self.mdiArea.addSubWindow(self.companysummary)
        #self.mdiArea.addSubWindow(self.financials_window)
        #self.mdiArea.addSubWindow(self.market_summary)
        self.mdiArea.addSubWindow(self.subwindow)
        
        '''Sets up all the graphs'''
        #maingraph
        self.gs1 = gridspec.GridSpec(4, 1)
        self.gs1.update(left=0.01, right=0.97, top=1.0, bottom=0.04,wspace=0,hspace=0)
        self.tech_chart_fig = Figure(facecolor='black') 
        self.tech_chart_canvas = FigureCanvas(self.tech_chart_fig)
        self.techchart_layout_3.addWidget(self.tech_chart_canvas)  
        self.tech_chart_axis = self.tech_chart_fig.add_subplot(self.gs1[:, :],facecolor='#191919') 
        self.price_ax = self.tech_chart_axis.twinx()

        #indicator graph 1
        self.ind1 = gridspec.GridSpec(4, 1)
        self.ind1.update(left=0.01, right=0.97, top=.99, bottom=0.01,wspace=0,hspace=0)
        self.tech_chart_fig1 = Figure(facecolor='black') 
        self.tech_chart_canvas1 = FigureCanvas(self.tech_chart_fig1)
        self.tc_indlayout1.addWidget(self.tech_chart_canvas1)  
        self.tc_ind1_axis = self.tech_chart_fig1.add_subplot(self.ind1[:, :],facecolor='#191919',sharex=self.tech_chart_axis)

        #indicator graph 2
        self.ind2 = gridspec.GridSpec(4, 1)
        self.ind2.update(left=0.01, right=0.97, top=.99, bottom=0.01,wspace=0,hspace=0)
        self.tech_chart_fig2 = Figure(facecolor='black') 
        self.tech_chart_canvas2 = FigureCanvas(self.tech_chart_fig2)
        self.tc_indlayout2.addWidget(self.tech_chart_canvas2)  
        self.tc_ind2_axis = self.tech_chart_fig2.add_subplot(self.ind2[:, :],facecolor='#191919',sharex=self.tech_chart_axis)

        #indicator graph 3
        self.ind3 = gridspec.GridSpec(4, 1)
        self.ind3.update(left=0.01, right=0.97, top=.99, bottom=0.01,wspace=0,hspace=0)
        self.tech_chart_fig3 = Figure(facecolor='black') 
        self.tech_chart_canvas3 = FigureCanvas(self.tech_chart_fig3)
        self.tc_indlayout3.addWidget(self.tech_chart_canvas3)  
        self.tc_ind3_axis = self.tech_chart_fig3.add_subplot(self.ind3[:, :],facecolor='#191919',sharex=self.tech_chart_axis)

        #company summary graph
        self.cs1 = gridspec.GridSpec(4, 1)
        self.cs1.update(left=0.0, right=0.95, top=1.0, bottom=0.06,wspace=0,hspace=0)
        self.cs_chart_fig = Figure(facecolor='black') 
        self.cs_chart_canvas = FigureCanvas(self.cs_chart_fig)
        self.cs_chart_layout.addWidget(self.cs_chart_canvas)  
        self.cs_chart_axis = self.cs_chart_fig.add_subplot(self.cs1[:, :],facecolor='#191919') 

        #sector summary pie graph
        self.ss1 = gridspec.GridSpec(4, 1)
        self.ss1.update(left=0.0, right=0.95, top=1.0, bottom=0.06,wspace=0,hspace=0)
        self.ss_chart_fig = Figure(facecolor='black') 
        self.ss_chart_canvas = FigureCanvas(self.ss_chart_fig)
        self.ss_pie_layout.addWidget(self.ss_chart_canvas)  
        self.ss_chart_axis = self.ss_chart_fig.add_subplot(self.ss1[:, :],facecolor='#191919') 

        
        self.tc_mainsearch.setText('AAPL')

        
        '''Market Summary'''
        self.ms_gainer_filter.currentIndexChanged.connect(self.ms_gainlose_table)


        '''Company Summary'''
        self.cs_search.returnPressed.connect(self.company_summary)

        #comptetitors table
        cs_comp_header = [self.cs_sym_0,self.cs_name_0,self.cs_price_0,self.cs_chg_0,self.cs_mrk_0]
        for header in cs_comp_header:
            header.currentIndexChanged.connect(self.cs_competitor_table)
        et = time.time()
        print 'GUI Setup Time:', et-st

        #historical table edit page'
        self.cs_hist_edit.setMinimumHeight(0)
        self.cs_hist_edit.setMaximumHeight(0)
        self.cs_hist_oedit.clicked.connect(self.cs_hist_openedit)

        self.cs_hist_tc.clicked.connect(self.cs_hist_textcolor) 
        self.cs_hist_bc.clicked.connect(self.cs_hist_backgroundcolor) 

        #Date changes
        date_buttons = [self.cs_histedit_daily,self.cs_histedit_weekly,self.cs_histedit_monthly,
                        self.cs_histedit_yearly]
        for d in date_buttons:
            d.clicked.connect(self.cs_hist_table)

        data = self.get_symbol_data('TSLA')
        recdate = pd.to_datetime(data.index[-1])
        self.cs_hedit_datet.setDate(QtCore.QDate(recdate.year,recdate.month,recdate.day))
        self.cs_hedit_datef.setDate(QtCore.QDate(recdate.year-1,recdate.month,recdate.day))

        #Column/data chnages
        hedit_columns = [self.cs_hsearch0,self.cs_hsearch1,self.cs_hsearch2,self.cs_hsearch3,self.cs_hsearch4,
                        self.cs_hsearch5,self.cs_hsearch6,self.cs_hsearch7,self.cs_hsearch8,self.cs_hsearch9,
                        self.cs_hsearch10,self.cs_hsearch11,self.cs_hsearch12,self.cs_hsearch13,self.cs_hsearch14,
                        self.cs_hsearch15,self.cs_hsearch16,self.cs_hsearch17,self.cs_hsearch18,self.cs_hsearch19]
        for h in hedit_columns:
            h.returnPressed.connect(self.cs_hist_table)
        self.cs_hedit_datef.dateChanged.connect(self.cs_hist_table)
        self.cs_hedit_datet.dateChanged.connect(self.cs_hist_table)

        #top buttons
        cs_pagesb = [self.cs_smryb,self.cs_histb,self.cs_ratiob,self.cs_finstatb,self.cs_corpinfob]
        for p in cs_pagesb:
            p.clicked.connect(self.cs_pages)

        self.cs_histcomp_update.clicked.connect(self.cs_histtable_compare)

        '''New tecnical chart'''
        self.tc_mainsearch.returnPressed.connect(self.technical_chart)
        self.tc_editwidget.setMinimumHeight(0)
        self.tc_editwidget.setMaximumHeight(0)
        self.tc_openedit.clicked.connect(self.tc_edit) #edit open

        self.tc_olind_cb.setCurrentIndex(0)
        self.tc_olind_cb.currentIndexChanged.connect(self.tc_overlayindicator)
        self.tc_olind_cb.setMinimumWidth(500)
        self.tc_olind_cb.setMaximumWidth(500)
        self.tc_olind_header.setCurrentIndex(0)
        self.tc_olind_header.setMinimumWidth(315)
        self.tc_olind_header.setMaximumWidth(315)
        self.tc_stack_overlay_ind.setCurrentIndex(0)

        #Date Changes
        self.tc_todate.setDate(QtCore.QDate(year,month,day))
        self.tc_fromdate.setDate(QtCore.QDate(year-1,month,day))

        tc_date_buttons = [self.tc_oneday_db,self.tc_fiveday_db,self.tc_onemonth_db,self.tc_threemonth_db, 
                           self.tc_sixmonth_db,self.tc_oneyear_db,self.tc_fiveyear_db,self.tc_max_db]
        for b in tc_date_buttons:
            b.clicked.connect(self.tc_datechange)
            b.setChecked(False)

        #Colors
        self.tc_linecolor.clicked.connect(self.tc_linecolor_edit) 
        self.tc_linecolor_up.clicked.connect(self.tc_upcolor_edit) 
        self.tc_linecolor_down.clicked.connect(self.tc_downcolor_edit) 
        self.tc_backgroundcolor.clicked.connect(self.tc_backgroundcolor_edit)
        self.tc_textcolor.clicked.connect(self.tc_textcolor_edit)
        self.tc_gridcolor.clicked.connect(self.tc_gridcolor_edit)
        self.tc_bbupper_lc.clicked.connect(self.tc_bbupper_color) 
        self.tc_bbmiddle_lc.clicked.connect(self.tc_bbmiddle_color) 
        self.tc_bblower_lc.clicked.connect(self.tc_bblower_color) 
        self.tc_kcupper_lc.clicked.connect(self.tc_kcupper_color) 
        self.tc_kcmiddle_lc.clicked.connect(self.tc_kcmiddle_color) 
        self.tc_kclower_lc.clicked.connect(self.tc_kclower_color) 
        self.tc_ema_lc.clicked.connect(self.tc_ema_color) 
        self.tc_chexit_lc.clicked.connect(self.tc_chexit_color) 
        self.tc_pcupper_lc.clicked.connect(self.tc_pcupper_color) 
        self.tc_pcmiddle_lc.clicked.connect(self.tc_pcmiddle_color) 
        self.tc_pclower_lc.clicked.connect(self.tc_pclower_color) 
        self.tc_smaeupper_lc.clicked.connect(self.tc_smaeupper_color) 
        self.tc_smaelower_lc.clicked.connect(self.tc_smaelower_color) 
        self.tc_emaeupper_lc.clicked.connect(self.tc_emaeupper_color) 
        self.tc_emaelower_lc.clicked.connect(self.tc_emaelower_color) 
        self.tc_price_lc.clicked.connect(self.tc_price_color) 
        self.tc_accdist_lc.clicked.connect(self.tc_accdist_color) 
        self.tc_atr_lc.clicked.connect(self.tc_atr_color) 
        self.tc_bollwidth_lc.clicked.connect(self.tc_bollwidth_color) 
        self.tc_bollb_lc.clicked.connect(self.tc_bollb_color) 
        self.tc_macd_lc.clicked.connect(self.tc_macd_color) 
        self.tc_signal_lc.clicked.connect(self.tc_macdsignal_color) 
        self.tc_hist_lc.clicked.connect(self.tc_macdhist_color) 
        self.tc_macdhist_lc.clicked.connect(self.tc_histmacd_color) 


        #Update buttons
        tc_editupdates = [self.tc_editupdate,self.tc_olhelp_update,self.tc_olhelp_update2,
                          self.tc_olhelp_update3,self.tc_olhelp_update4,self.tc_olhelp_update5,
                          self.tc_olhelp_update6,self.tc_olhelp_update7,self.tc_olhelp_update8,
                          self.tc_olhelp_update9,self.tc_indhelp_update1,self.tc_indhelp_update2,
                          self.tc_indhelp_update3,self.tc_indhelp_update4,self.tc_indhelp_update5,
                          self.tc_indhelp_update6]
        for u in tc_editupdates:
            u.clicked.connect(self.technical_chart)

        self.tc_stack_overlay_ind.setCurrentIndex(0)
        self.tc_olstacked.setCurrentIndex(0)

        #choose overlay / inicator set params
        tc_overlay_cb = [self.tc_overlay1,self.tc_overlay2,self.tc_overlay3]
        for o in tc_overlay_cb:
            o.currentIndexChanged.connect(self.tc_set_overlayparam)
        
        #choose inicator set params
        tc_indicator_cb = [self.tc_indicator1,self.tc_indicator2,self.tc_indicator3]
        for i in tc_indicator_cb:
            i.currentIndexChanged.connect(self.tc_set_indicatorparam)

        #overlay help and back button
        overlay_help = [self.tc_olhelp1,self.tc_olhelp2,self.tc_olhelp3]
        for h in overlay_help:
            h.clicked.connect(self.tc_overlay_help)
        overlay_back = [self.tc_olhelp_b1,self.tc_olhelp_b2,self.tc_olhelp_b3,self.tc_olhelp_b4,
                        self.tc_olhelp_b5,self.tc_olhelp_b6,self.tc_olhelp_b7,self.tc_olhelp_b8,
                        self.tc_olhelp_b9]
        for b in overlay_back:
            b.clicked.connect(self.tc_olhelp_back)

        #indicator help and back button
        indicator_help = [self.tc_indhelp1,self.tc_indhelp2,self.tc_indhelp3]
        for h in indicator_help:
            h.clicked.connect(self.tc_indicator_help)
        indicator_back = [self.tc_indhelp_b1,self.tc_indhelp_b2,self.tc_indhelp_b3,self.tc_indhelp_b4,
                          self.tc_indhelp_b5,self.tc_indhelp_b6]
        for b in indicator_back:
            b.clicked.connect(self.tc_indhelp_back)

        '''Sector Summary'''
        self.ss_variable.currentIndexChanged.connect(self.sectors_summary)

        #start functions
        #self.sectors_summary()
        #self.ms_gainers_loser()
        #self.company_summary()
        #self.financial_window()
        self.technical_chart()


    def cs_competitor_table(self):
        st = time.time()
        symbol = str(self.cs_search.text())
        comp_data = self.cs_competitors(symbol)

        label_header = [self.cs_sym_0,self.cs_name_0,self.cs_price_0,self.cs_chg_0,self.cs_mrk_0]
        label_layout = [[self.cs_sym_1,self.cs_name_1,self.cs_price_1,self.cs_chg_1,self.cs_mrk_1],
                        [self.cs_sym_2,self.cs_name_2,self.cs_price_2,self.cs_chg_2,self.cs_mrk_2],
                        [self.cs_sym_3,self.cs_name_3,self.cs_price_3,self.cs_chg_3,self.cs_mrk_3],
                        [self.cs_sym_4,self.cs_name_4,self.cs_price_4,self.cs_chg_4,self.cs_mrk_4],
                        [self.cs_sym_5,self.cs_name_5,self.cs_price_5,self.cs_chg_5,self.cs_mrk_5],
                        [self.cs_sym_6,self.cs_name_6,self.cs_price_6,self.cs_chg_6,self.cs_mrk_6],
                        [self.cs_sym_7,self.cs_name_7,self.cs_price_7,self.cs_chg_7,self.cs_mrk_7],
                        [self.cs_sym_8,self.cs_name_8,self.cs_price_8,self.cs_chg_8,self.cs_mrk_8],
                        [self.cs_sym_9,self.cs_name_9,self.cs_price_9,self.cs_chg_9,self.cs_mrk_9],
                        [self.cs_sym_10,self.cs_name_10,self.cs_price_10,self.cs_chg_10,self.cs_mrk_10]]

        comp_col = [str(x.currentText()).lstrip() for x in label_header]
        comp_data = comp_data.sort_values('Mrk Cap',ascending=False)
        comp_data['Mrk Cap'] = ["${:,.0f}".format(int(x)) for x in comp_data['Mrk Cap']]
        comp_data['% Change'] = [str(round(float(c)*100,3))+'%' if c != '' else c for c in comp_data['% Change']]
        comp_data = comp_data[comp_col]

        ncols = range(len(comp_data.columns)) #[0,1,2,3,4]
        nrows = range(len(comp_data['Symbol'])) 
        if len(nrows) > 10:
            nrows = nrows[:10]
        else:
            pass 

        for row in nrows:
            for col in ncols:
                value = comp_data[comp_data.columns[col]][comp_data.index[row]]
                label_layout[row][col].setText(str(value))  

        et = time.time()
        print 'Cs_competitor_table Time:', et-st

    def sector_summary(self):
        pass

    def get_symbol_data(self, symbol):
        st0 = time.time()
        db_path = "C:\\Users\\ajhau\\Desktop\\Finance Program\\finance5\\data\\data_import\\Finance Project.db"
        conn = sqlite3.connect(db_path)

        data = pd.read_sql_query("SELECT Date, Open, High, Low, Close, Change, PChange, Volume from Stockdata WHERE Symbol = '%s'" % symbol,conn)
        data = data.rename(columns={'PChange':'% Change'})
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date',inplace=True)
        conn.close()

        et0 = time.time()
        print 'get_symbol_data', et0-st0
        return data

    def get_todays_data(self):
        st = time.time()
        path = "C:\\Users\\ajhau\\Desktop\\Sector_data\\"

        if 'data' in todaysdata:
            data = todaysdata['data']
            et = time.time()
            print 'get_todays_data', et-st
            return data
        else:
            filenames = ['basic','capitalgood','condur','conondur','conservice','energy','finance','health',
                         'misc','publicutil','tech','transport']
            all_data = []
            for name in filenames:
                with open(path+name+'.csv','r') as f:
                    reader = csv.reader(f)
                    header1 = next(reader)
                    header2 = next(reader)
                    lastlines = deque(f,2)

                    sectorh = [''] + ([name]*(len(header1)-1)) 
                    headers = [sectorh,header1,header2]
                    headers = list(zip(*headers))
                    header = pd.MultiIndex.from_tuples(headers, names=['first', 'second','third'])
                    data = pd.read_csv(StringIO(''.join(lastlines)))
                    data.columns = header
                    all_data.append(data)

            data = pd.concat(all_data,axis=1,join_axes=[data.index])
            todaysdata['data'] = data
            et = time.time()
            print 'get_todays_data', et-st
            return data

    def company_summary(self):  
        st = time.time()
        self.cs_stackedwidget.setCurrentIndex(0)

        symbol = str(self.cs_search.text())
        data = self.get_symbol_data(symbol)

        self.cs_competitors(symbol)
        stock = Share(symbol)
        today_date = data.index[-1].date()
        year_date = str(today_date.year-1)+'-'+str(today_date.month)+'-'+str(today_date.day)

        yearclose = data['Close'].loc[year_date]
        yearhigh = round(data['Close'].loc[year_date:today_date].max(),2)
        yearlow = round(data['Close'].loc[year_date:today_date].min(),2)
        avgvol = round(data['Volume'].loc[year_date:today_date].mean(),2)
        avgvol = "{:,.0f}".format(int(avgvol))

        dayopen = round(data['Open'][-1],2)
        dayclose = round(data['Close'][-1],2)
        dayhigh = round(data['High'][-1],2)
        daylow = round(data['Low'][-1],2)
        dayvol = round(data['Volume'][-1],2)
        dayvol = "{:,.0f}".format(int(dayvol))

        daychg = round(data['Change'][-1],2)
        daypchg = round(data['% Change'][-1]*100,2)
        yearchg = round(((dayclose - yearclose)/yearclose)*100,2)
        sym_eps = str(stock.get_earnings_share())
        sym_pe = str(stock.get_price_earnings_ratio())
        sym_div = str(stock.get_dividend_share())
        sym_divy = str(stock.get_dividend_yield())
        sym_mrkcap = str(stock.get_market_cap())
        sym_mrkcap = float(sym_mrkcap[:-1])*(10**9) if sym_mrkcap[-1] == 'B' else float(sym_mrkcap[:-1])*(10**6)
        sym_mrkcap = "${:,.0f}".format(int(sym_mrkcap))

        sym_shares = data['Mrk Cap'][-1]/float(data['Close'][-1])
        sym_shares = int(math.ceil(sym_shares/ 10000.0)) * 10000
        sym_shares = "{:,.0f}".format(int(sym_shares))
        close_data = data['Close']

        self.cs_price.setText(str(dayclose))
        self.cs_change.setText(str(daychg)+' ('+str(daypchg)+'%)')

        self.cs_drange.setText(str(daylow)+' - '+str(dayhigh))
        self.cs_yrange.setText(str(yearlow)+' - '+str(yearhigh))
        self.cs_vol_avgvol.setText(str(dayvol)+'/'+str(avgvol))
        self.cs_div_yield.setText(str(sym_div)+'/'+str(sym_divy))
        self.cs_ytdchg.setText(str(yearchg)+'%')
        self.cs_mrkcap.setText(str(sym_mrkcap))
        self.cs_sharesout.setText(sym_shares)
        self.cs_peratio.setText(str(sym_pe))
        self.cs_eps.setText(str(sym_eps))

        self.cs_sector.setText(list(stock_list.loc[stock_list['Symbol']==symbol,'Sector'])[0])
        self.cs_industry.setText(list(stock_list.loc[stock_list['Symbol']==symbol,'Industry'])[0])

        sector = stock_list.loc[stock_list['Symbol'] == symbol, 'Sector']
        self.cs_chart_axis.clear()
        self.cs_chart_axis.grid(True, which='major', color='w', linestyle='--')  
        self.cs_chart_axis.yaxis.label.set_color("w")
        self.cs_chart_axis.xaxis.label.set_color('w')
        self.cs_chart_axis.spines['bottom'].set_color("w")
        self.cs_chart_axis.spines['top'].set_color("#191919")
        self.cs_chart_axis.spines['left'].set_color("#191919")
        self.cs_chart_axis.spines['right'].set_color("w")
        self.cs_chart_axis.tick_params(axis='y', colors='w',labelsize=15)
        self.cs_chart_axis.tick_params(axis='x', colors='w',labelsize=15)
        #self.cs_chart_axis.yaxis.set_major_locator(LinearLocator(10))
        #self.cs_chart_axis.xaxis.set_major_locator(LinearLocator(12))
        self.cs_chart_axis.yaxis.tick_right()
        self.cs_chart_axis.fill_between(data.index,close_data,facecolor='blue')

        close_min = data['Close'].min()
        close_max = data['Close'].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        self.cs_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        self.cs_chart_axis.set_xlim([datetime.datetime(year-1,month,day),datetime.datetime(year,month,day)])

        self.cs_chart_axis.plot(data['Close'],lw=5,alpha=0.6,color='blue')
        dateform = mdates.DateFormatter('%m/%y')
        self.cs_chart_axis.xaxis.set_major_formatter(dateform)
        #self.cs_chart_axis.tick_params(axis='x',direction='out',pad=100)
    
        axis = self.cs_chart_axis
        fig = self.cs_chart_canvas
        et = time.time()
        print 'company_summary', et-st
        series = 'Close'
        self.cs_competitor_table()
        self.cs_hist_table()

    def cs_pages(self):
        cs_pagesb = [self.cs_smryb,self.cs_histb,self.cs_ratiob,self.cs_finstatb,self.cs_corpinfob]
        for i, p in enumerate(cs_pagesb):
            if p.isChecked() == True:
                self.cs_stackedwidget.setCurrentIndex(i)
            else:
                pass
            p.setChecked(False)

    def cs_competitors(self,symbol):
        st = time.time()

        if symbol in loaded_comp_data.keys():
            et = time.time()
            print 'cs_competitors preloaded', et-st
            return loaded_comp_data[symbol]
        else:
            path = "C:\\Users\\ajhau\\Desktop\\Sector_data"
            industry = list(stock_list.loc[stock_list['Symbol']==symbol, 'Industry'])[0]
            symbols = list(stock_list.loc[stock_list['Industry']==industry, 'Symbol'])
            sector = list(stock_list.loc[stock_list['Symbol']==symbol,'Sector'])[0] #get the sector for the symbol
            index_num = sectors.index(sector) #index number for that sector

            #opens the csv for that sector and makes a list for the first row symbols 
            with open(path+'\\'+sec_file_names[index_num]) as f:
                reader = csv.reader(f)
                sec_symbols = next(reader)

            #from that list return the position of the symbols
            sym_ind = [0]
            symb = []
            for i, s in enumerate(sec_symbols):
                if s in symbols:
                    sym_ind.append(i)
                    symb.append(s)
                else:
                    pass
            sym_ind = np.array(sym_ind)
            symb = sorted(list(set(symb)))

            #get the last row od data for the symbols in symb
            with open(path+'\\'+sec_file_names[index_num], 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                data_rows = []
                n = 0
                for row in reader:
                    if n == 0 or n == 1:
                        content = list(row[i] for i in sym_ind)
                        data_rows.append(content)
                    elif row[0] == '7/28/2017' or row[0] == '2017-07-28':
                        print True
                        content = list(row[i] for i in sym_ind)
                        data_rows.append(content)
                    n+=1

            data = pd.DataFrame(index=symb,columns=sorted(set(data_rows[1][1:])))
            for c in range(len(data.columns)):
                col_data = [data_rows[-1][x] for x in list(range(c+1,len(data_rows[1]),8))]
                data[data.columns[c]] = col_data
            mrk = list(data['Mrk Cap'])
            mrk = [float(mrk[i].split('+')[0][:-1])*(int(10**int(mrk[i].split('+')[1]))) 
                        if 'E' in mrk[i] else float(mrk[i]) if mrk[i] != '' else 0 for i in range(len(mrk))]
            names = [list(stock_list.loc[stock_list['Symbol']==symb[i],'Name'])[0] for i in range(len(symb))]

            data['Name'] = names
            data['Mrk Cap'] = mrk
            data['Symbol'] = data.index
            loaded_comp_data[symbol] = data

            et = time.time()
            print 'cs_competitors',et-st
            return data

    def cs_hist_table(self):
        '''calls cs_histable_sort to get the data then fills the table with that data'''
        st = time.time()
        #self.cs_stackedtables.setCurrentIndex(0)
        symbol = str(self.cs_search.text())
        self.cs_compare1.setText(symbol)
        data = self.cs_histable_sort(symbol)

        textcolor = self.cs_hist_tc.palette().button().color()
        textcolor = str(textcolor.name())
        backgroundcolor = self.cs_hist_bc.palette().button().color()
        backgroundcolor = str(backgroundcolor.name())

        self.cs_histable.setStyleSheet("QWidget { background-color: %s}" % backgroundcolor)
        self.cs_histable.setStyleSheet("QWidget { color: %s}" % textcolor)

        self.cs_histable.setStyleSheet("QWidget { background-color:"+str(backgroundcolor)+'; color:'+str(textcolor)+'}')

        edit_columns = [self.cs_hsearch0,self.cs_hsearch1,self.cs_hsearch2,self.cs_hsearch3,self.cs_hsearch4,
                        self.cs_hsearch5,self.cs_hsearch6,self.cs_hsearch7,self.cs_hsearch8,self.cs_hsearch9,
                        self.cs_hsearch10,self.cs_hsearch11,self.cs_hsearch12,self.cs_hsearch13,self.cs_hsearch14,
                        self.cs_hsearch15,self.cs_hsearch16,self.cs_hsearch17,self.cs_hsearch18,self.cs_hsearch19]
        headers = [str(x.text()) for x in edit_columns]
        col = [x for x in headers if x != '']
        try:
            data = data[col]
        except:
            print 'not found'
        self.cs_histable.setRowCount(len(data.index))
        #fill headers
        for d, date in enumerate(data.index):
            item = QtGui.QTableWidgetItem(str(data.index[d]))
            self.cs_histable.setVerticalHeaderItem(d,item)
        for h, header in enumerate(headers):
            item = QtGui.QTableWidgetItem(str(headers[h]))
            self.cs_histable.setHorizontalHeaderItem(h,item)
        #fill table data
        for c in range(len(headers)):
            #replace old/empty data with new data
            if headers[c] != '':
                for r in range(len(data.index)):
                    item = QtGui.QTableWidgetItem('     '+str(data[data.columns[c]][r]))
                    self.cs_histable.setItem(r,c,item)
            else:
                for r in range(len(data.index)):
                    item = QtGui.QTableWidgetItem(' ')
                    self.cs_histable.setItem(r,c,item)
                
        et = time.time()
        print 'cs_hist_table', et-st

    def cs_histtable_compare(self):
        st = time.time()

        if self.cs_histcomp_layout.currentText() == 'Vertical':
            tables = [self.cs_hist_vtable1,self.cs_hist_vtable2,self.cs_hist_vtable3]
            self.cs_stackedtables.setCurrentIndex(2)
        elif self.cs_histcomp_layout.currentText() == 'Horizontal':
            tables = [self.cs_hist_htable1,self.cs_hist_htable2,self.cs_hist_htable3]
            self.cs_stackedtables.setCurrentIndex(1)
        else:
            tables = [self.cs_hist_htable1,self.cs_hist_htable2,self.cs_hist_htable3]
            self.cs_stackedtables.setCurrentIndex(1)

        comp_searchs = [self.cs_compare1,self.cs_compare2,self.cs_compare3]
        symbols = [str(x.text()) for x in comp_searchs if str(x.text()) != '']
        data = [self.cs_histable_sort(x) for x in symbols]
        for i in range(len(symbols)):
            edit_columns = [self.cs_hsearch0,self.cs_hsearch1,self.cs_hsearch2,self.cs_hsearch3,self.cs_hsearch4,
                            self.cs_hsearch5,self.cs_hsearch6,self.cs_hsearch7,self.cs_hsearch8,self.cs_hsearch9,
                            self.cs_hsearch10,self.cs_hsearch11,self.cs_hsearch12,self.cs_hsearch13,self.cs_hsearch14,
                            self.cs_hsearch15,self.cs_hsearch16,self.cs_hsearch17,self.cs_hsearch18,self.cs_hsearch19]
            headers = [str(x.text()) for x in edit_columns]
            col = [x for x in headers if x != '']
            data[i] = data[i][col]
            tables[i].setRowCount(len(data[i].index))
            #fill headers
            for d, date in enumerate(data[i].index):
                item = QtGui.QTableWidgetItem(str(data[i].index[d]))
                self.cs_histable.setVerticalHeaderItem(d,item)
            for h, header in enumerate(data[i].columns):
                item = QtGui.QTableWidgetItem(str(data[i].columns[h]))
                self.cs_histable.setHorizontalHeaderItem(h,item)
            #fill table data
            for c in range(len(col)):
                #replace old/empty data with new data
                for r in range(len(data[i].index)):
                    item = QtGui.QTableWidgetItem('     '+str(data[i][data[i].columns[c]][r]))
                    self.cs_histable.setItem(r,c,item)
        et = time.time()
        print 'cs_histtable_compare', et-st

    def cs_histable_todate(self, data):
        st = time.time()
        #to-date formatting
        tdate = self.cs_hedit_datet.date()
        tdate = str(tdate.year())+'-'+str(tdate.month())+'-'+str(tdate.day())
        tdate = pd.to_datetime(tdate).date()
        tday = tdate.strftime('%A')
        tindex =  tday[:2]+'  '+str(tdate)

        if tindex in data.index:
            tnum = data.index.get_loc(tindex)
        else:
            if tday == 'Saturday':
                tdate = tdate - timedelta(1)
                tday = tdate.strftime('%A')
                tindex = tday[:2]+'  '+str(tdate)
                tnum = data.index.get_loc(tindex)
            elif tday == 'Sunday':
                tdate = tdate - timedelta(2)
                tday = tdate.strftime('%A')
                tindex = tday[:2]+'  '+str(tdate)
                tnum = data.index.get_loc(tindex)
        et = time.time()
        print 'cs_histable_todate', et-st
        return tnum

    def cs_histable_fromdate(self, data):
        st = time.time()
        #from-date formatting
        fdate = self.cs_hedit_datef.date()
        fdate = str(fdate.year())+'-'+str(fdate.month())+'-'+str(fdate.day())
        fdate = pd.to_datetime(fdate).date()
        fday = fdate.strftime('%A')
        findex =  fday[:2]+'  '+str(fdate)

        if findex in data.index:
            fnum = data.index.get_loc(findex)
        else:
            if fday == 'Saturday':
                fdate = fdate + timedelta(2)
                fday = fdate.strftime('%A')
                findex = findex = fday[:2]+'  '+str(fdate)
                fnum = data.index.get_loc(findex)
            elif fday == 'Sunday':
                fdate = fdate + timedelta(1)
                fday = fdate.strftime('%A')
                findex = findex = fday[:2]+'  '+str(fdate)
                fnum = data.index.get_loc(findex)
        et = time.time()
        print 'cs_histable_fromdate', et-st
        return fnum

    def cs_histable_sort(self,symbol):
        '''sorts the data to fit the chosen date range, then formats the data depending
           on if daily weekly monthly quarterly or yearly averages is requested'''
        st = time.time()
        data = self.get_symbol_data(symbol)
        dayending = str(self.cs_hist_endingday.currentText()).split()[1][:2]

        if type(data.index[0]) == str:
            #date index already formatted
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:] 
            data = data.iloc[::-1]
        else:
            #date index need formatting
            dates = [d.strftime('%A')[:2]+'  '+str(d.date()) for d in data.index]
            data.index = dates
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:] 
            data = data.iloc[::-1]
        tnum = self.cs_histable_todate(data) #index for to date
        fnum = self.cs_histable_fromdate(data) #index for from date
        data = data[data.columns][tnum:fnum]
            
        #Daily
        if self.cs_histedit_daily.isChecked() == True:
            data['Volume'] = ["{:,.0f}".format(float(x)) for x in data['Volume'] if x != 'nan']
            data['% Change'] = [float(x)*100 for x in data['% Change']]
            data = data[data.columns].round(2)
            data['Mrk Cap'] = ["${:,.0f}".format(float(x)) for x in data['Mrk Cap'] if x != 'nan']
        #Weekly
        elif self.cs_histedit_weekly.isChecked() == True:
            fri = [x for x in range(len(data.index)) if str(data.index[x])[:2] == dayending]
            avgdata = [data[list(data.columns)][x:x+5].mean() for x in fri]
            wdata = pd.DataFrame(avgdata,index=data.index[fri],columns=data.columns)
            data = wdata
            data['Volume'] = ["{:,.0f}".format(float(x)) for x in data['Volume'] if x != 'nan']
            data['% Change'] = [float(x)*100 for x in data['% Change']]
            data = data[data.columns].round(2)
            data['Mrk Cap'] = ["${:,.0f}".format(float(x)) for x in data['Mrk Cap'] if x != 'nan']
        #Monthly
        elif self.cs_histedit_monthly.isChecked() == True:                                                                                                  
            mont = [m.split()[1].split('-')[1] for m in data.index]
            var = mont[0]
            ind = []
            for i in range(len(mont)):
                if mont[i] == var:
                    pass
                else:
                    ind.append(i)
                    var = mont[i]   
            indx = [0] + ind
            avgdata = [data[data.columns][indx[x]:indx[x+1]].mean() for x in range(len(indx)) if x+1 < len(indx)]
            data = pd.DataFrame(avgdata,index=data.index[indx[:-1]],columns=data.columns)
            data['Volume'] = ["{:,.0f}".format(float(x)) for x in data['Volume'] if x != 'nan']
            data['% Change'] = [float(x)*100 for x in data['% Change']]
            data = data[data.columns].round(2)
            data['Mrk Cap'] = ["${:,.0f}".format(float(x)) for x in data['Mrk Cap'] if x != 'nan']
        #Yearly
        elif self.cs_histedit_yearly.isChecked() == True:      
            mont = [m.split()[1].split('-')[0] for m in data.index]
            var = mont[0]
            ind = []
            for i in range(len(mont)):
                if mont[i] == var:
                    pass
                else:
                    ind.append(i)
                    var = mont[i]   
            indx = [0] + ind
            avgdata = [data[data.columns][indx[x]:indx[x+1]].mean() for x in range(len(indx)) if x+1 < len(indx)]
            data = pd.DataFrame(avgdata,index=data.index[indx[:-1]],columns=data.columns)
            data['Volume'] = ["{:,.0f}".format(float(x)) for x in data['Volume'] if x != 'nan']
            data['% Change'] = [float(x)*100 for x in data['% Change']]
            data = data[data.columns].round(2)
            data['Mrk Cap'] = ["${:,.0f}".format(float(x)) for x in data['Mrk Cap'] if x != 'nan'] 
        else:
            pass

        et = time.time()
        print 'cs_histable_sort', et-st
        return data

    def cs_hist_openedit(self):
        if self.cs_hist_oedit.text() =='>>>':
            self.cs_hist_edit.setMinimumHeight(370)
            self.cs_hist_edit.setMaximumHeight(370)
            self.cs_hist_oedit.setText('<<<')               
        else:
            self.cs_hist_edit.setMinimumHeight(0)
            self.cs_hist_edit.setMaximumHeight(0)
            self.cs_hist_oedit.setText('>>>')

    def market_summary(self):
        filter = str(self.ms_gainer_filter.currentText())
        symbols = [x.split(':')[1] for x in glpd.index]
        glpd['Symbol'] = symbols
        gain_loss = glpd[['Symbols','Mrk Cap','Change','% Change']]

        gainers = [[self.ms_gainer_sym1,self.ms_gainer_sym2,self.ms_gainer_sym3,self.ms_gainer_sym4,self.ms_gainer_sym5],
                  [self.ms_gainer_name1,self.ms_gainer_name2,self.ms_gainer_name3,self.ms_gainer_name4,self.ms_gainer_name5],
                  [self.ms_gainer_price1,self.ms_gainer_price2,self.ms_gainer_price3,self.ms_gainer_price4,self.ms_gainer_price5]
                  [self.ms_gainer_chg1,ms_gainer_chg2,ms_gainer_chg3,ms_gainer_chg4,ms_gainer_chg5]]

        top_five = gain_loss.sort_values('% Change', ascending=False).head(5)
        try:
            names = [list(stock_list.loc[stock_list['Symbol']==sym, 'Name'])[0] for sym in top_five['Symbol']]
            top_five['Name'] = names
        except:
            names = ['Not Found','Not Found','Not Found','Not Found','Not Found']
            top_five['Name'] = names
        self.ms_gainlose_table(gainers,top_five)
          
    def ms_gainlose_table(self,gainers,top_five):
        top_five = top_five[['Symbols','Name','Mrk Cap','Change','% Change']]
        for x in range(len(gainers)):
            for i in range(len(x)):
                gainers[x][i].setText(top_five[top_five.columns[x]][i])

    #Technical Chart
    def technical_chart(self):
        st = time.time()
        symbol = str(self.tc_mainsearch.text())
        data = self.get_symbol_data(symbol)

        #self.tc_maingraph.setMinimumHeight(1300)
        #self.tc_maingraph.setMaximumHeight(1300)

        #make sure only main graph is visible
        self.tc_topgraghs.setMinimumHeight(0)
        self.tc_topgraghs.setMaximumHeight(0)
        self.tc_bottomgraghs.setMinimumHeight(0)
        self.tc_bottomgraghs.setMaximumHeight(0)
        self.tc_indgragh1.setMinimumHeight(0)
        self.tc_indgragh1.setMaximumHeight(0)
        self.tc_indgragh2.setMinimumHeight(0)
        self.tc_indgragh2.setMaximumHeight(0)
        self.tc_indgragh2.setMinimumHeight(0)
        self.tc_indgragh2.setMaximumHeight(0)

        #colors
        gridcolor = self.tc_gridcolor.palette().button().color()
        gridcolor = str(gridcolor.name())
        textcolor = self.tc_textcolor.palette().button().color()
        textcolor = str(textcolor.name())
        backgroundcolor = self.tc_backgroundcolor.palette().button().color()
        backgroundcolor = str(backgroundcolor.name())

        #maingraph
        #clear lines
        if len(self.tech_chart_axis.lines) == 0:
            pass
        elif len(self.tech_chart_axis.lines) == 1:
            l = self.main_plot.pop(0)
            l.remove()
            del l
        else:
            self.tech_chart_axis.cla()

        self.tech_chart_axis.set_facecolor(backgroundcolor)
        self.tech_chart_axis.grid(True, which='major', color=gridcolor, linestyle='--')  
        self.tech_chart_axis.yaxis.label.set_color("yellow")
        self.tech_chart_axis.xaxis.label.set_color('yellow')
        self.tech_chart_axis.spines['top'].set_color('yellow')
        self.tech_chart_axis.spines['top'].set_visible(True)
        self.tech_chart_axis.spines['bottom'].set_color('yellow')
        self.tech_chart_axis.spines['right'].set_color('yellow')
        self.tech_chart_axis.tick_params(axis='y', colors=textcolor,labelsize=20)
        self.tech_chart_axis.tick_params(axis='x', colors=textcolor,labelsize=20)

        #self.tech_chart_axis.xaxis.set_major_locator(mdates.MonthLocator())
        date_format = str(self.tc_date_format.currentText())
        dateform = mdates.DateFormatter(date_format)
        self.tech_chart_axis.xaxis.set_major_formatter(dateform)
        self.tech_chart_axis.yaxis.tick_right()
        self.price_ax.yaxis.tick_left()
        #self.gs1.update(left=0.00, right=0.99, top=.99, bottom=0.03,wspace=0,hspace=0)

        self.tc_olind_cb.setMinimumHeight(50)
        self.tc_olind_cb.setMaximumHeight(50)
        self.tc_olind_header.setMinimumHeight(50)
        self.tc_olind_header.setMaximumHeight(50)
        self.tc_olstacked.setCurrentIndex(50)

        self.tc_attributes(data,symbol)
        self.tc_indicators(data,symbol)
        self.tc_overlays(data,symbol)
        self.tc_moving_averages(data,symbol)
        self.tc_legend()
        #self.tc_datechange()
        self.tech_chart_canvas.draw()

        et = time.time()
        print '*Total* technical_chart', et-st

    def tc_attributes(self,data,symbol):
        st = time.time()
        
        #make sure dates dont have the day name in it
        #remove nan rows
        if type(data.index[-1]) == str:
            newindex = [x.split()[1] for x in data.index]
            data.index = pd.to_datetime(newindex)
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]
        else:
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]

        #Gets the dates from the QtdateEdits and sets the data index the that range
        from_year = self.tc_fromdate.date().year()
        from_month = self.tc_fromdate.date().month()
        from_day = self.tc_fromdate.date().day()
        to_year = self.tc_todate.date().year()
        to_month = self.tc_todate.date().month()
        to_day = self.tc_todate.date().day()
        from_date = datetime.datetime(from_year,from_month,from_day)
        to_date = datetime.datetime(to_year,to_month,to_day)
        data = data[data.columns][from_date:to_date]
        self.tech_chart_axis.set_xlim([datetime.datetime(from_year,from_month,from_day),datetime.datetime(to_year,to_month,to_day)])

        #get line colors and size
        linesize = int(self.tc_linesize.text())
        linecolor = self.tc_linecolor.palette().button().color()
        linecolor = str(linecolor.name())
        linecolor_up = self.tc_linecolor_up.palette().button().color()
        linecolor_up = str(linecolor_up.name())
        linecolor_down = self.tc_linecolor_down.palette().button().color()
        linecolor_down = str(linecolor_down.name())
        line_legend = symbol+' ('+str(data['Close'][-1])+')'

        st4 = time.time()
        if self.tc_linetype.currentText() == 'Candlesticks':
            close_min = data['Close'].min()
            close_max = data['Close'].max()
            close_diff = float(close_max - close_min)
            ax1_min = float(close_min - (close_diff*0.10))
            ax1_max = float(close_max + (close_diff*0.10))
            self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
            cs_data = data.reset_index()
            cs_data = cs_data[['index','Open','High','Low','Close']]
            cs_data['index'] = cs_data['index'].map(mdates.date2num)
            loaded_csdata[symbol] = cs_data 
            candlestick_ohlc(self.tech_chart_axis, cs_data.values, width=linesize, colorup=linecolor_up, colordown=linecolor_down)

        elif self.tc_linetype.currentText() == 'Solid Line':
            close_min = data['Close'].min()
            close_max = data['Close'].max()
            close_diff = float(close_max - close_min)
            ax1_min = float(close_min - (close_diff*0.10))
            ax1_max = float(close_max + (close_diff*0.10))
            self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
            self.main_plot = self.tech_chart_axis.plot(data['Close'],lw=linesize,alpha=0.75,color=linecolor,linestyle='solid',label=line_legend)

        elif self.tc_linetype.currentText() == 'Dashed Line':
            close_min = data['Close'].min()
            close_max = data['Close'].max()
            close_diff = float(close_max - close_min)
            ax1_min = float(close_min - (close_diff*0.10))
            ax1_max = float(close_max + (close_diff*0.10))
            self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
            self.tech_chart_axis.plot(data['Close'],lw=linesize,alpha=0.75,color=linecolor,linestyle='dashed',label=line_legend)

        elif self.tc_linetype.currentText() == 'Dotted Line':
            close_min = data['Close'].min()
            close_max = data['Close'].max()
            close_diff = float(close_max - close_min)
            ax1_min = float(close_min - (close_diff*0.10))
            ax1_max = float(close_max + (close_diff*0.10))
            self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
            self.tech_chart_axis.plot(data['Close'],lw=linesize,alpha=0.75,color=linecolor,linestyle='dotted',label=line_legend)

        elif self.tc_linetype.currentText() == 'Performance':
            close_min = data['% Change'].min()
            close_max = data['% Change'].max()
            close_diff = float(close_max - close_min)
            ax1_min = float(close_min - (close_diff*0.10))
            ax1_max = float(close_max + (close_diff*0.10))
            self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
            line_legend = symbol+' ('+str(data['% Change'][-1])+')'
            self.tech_chart_axis.plot(data['% Change'],lw=linesize,alpha=0.75,color=linecolor,linestyle='solid',label=line_legend)
            
        elif self.tc_linetype.currentText() == 'Area':
            close_min = data['Close'].min()
            close_max = data['Close'].max()
            close_diff = float(close_max - close_min)
            ax1_min = float(close_min - (close_diff*0.10))
            ax1_max = float(close_max + (close_diff*0.10))
            self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
            self.tech_chart_axis.plot(data['Close'],lw=linesize,alpha=0.75,color=linecolor,linestyle='solid',label=line_legend)
            self.tech_chart_axis.fill_between(data.index, data['Close'], 0,alpha=0.5)

        elif self.tc_linetype.currentText() == 'Histogram':
            pass
        else:
            pass
        et4 = time.time()
        print 'tc_attributes 4', et4-st4

        #volume_ax = self.tech_chart_axis.twinx()
        #volume_ax.set_position(matplotlib.transforms.Bbox([[0.125,0.1],[0.9,0.32]]))

        #pos = data['Open'] - data['Close'] < 0
        #neg = data['Open'] - data['Close'] > 0
        #volume_ax.bar(data.index[pos],data['Volume'][pos],color='green',width=1,align='center')
        #volume_ax.bar(data.index[neg],data['Volume'][neg],color='red',width=1,align='center')

        et = time.time()
        print 'tc_attributes', et-st

    def tc_overlays(self,data,symbol):
        st = time.time()
        
        #make sure dates dont have the day name in it
        #remove nan rows
        if type(data.index[-1]) == str:
            newindex = [x.split()[1] for x in data.index]
            data.index = pd.to_datetime(newindex)
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]
        else:
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]

        overlays = [self.tc_overlay1,self.tc_overlay2,self.tc_overlay3]
        params = [self.tc_olparam1,self.tc_olparam2,self.tc_olparam3]

        for o in range(len(overlays)):
            if overlays[o].currentText() == '-None-':
                params[o].setText(' ')
            elif overlays[o].currentText() == 'Bollinger Bands':
                parm = str(params[o].text())
                self.tc_bollinger_bands(data,parm)
            elif overlays[o].currentText() == 'Keltner Channels':
                parm = str(params[o].text())
                self.tc_keltner_channels(data,parm)
            elif overlays[o].currentText() == 'Exp. Moving Avg.':
                parm = str(params[o].text())
                self.tc_ema(data,parm)
            elif overlays[o].currentText() == 'Chandelier Exit':
                parm = str(params[o].text())
                self.tc_chandelier_exit(data,parm)
            elif overlays[o].currentText() == 'Price Channels':
                parm = str(params[o].text())
                self.tc_price_channels(data,parm)
            elif overlays[o].currentText() == 'SMA Envelopes':
                parm = str(params[o].text())
                self.tc_sma_envelope(data,parm)
            elif overlays[o].currentText() == 'EMA Envelopes':
                parm = str(params[o].text())
                self.tc_ema_envelope(data,parm)
            elif overlays[o].currentText() == 'Price':
                parm = str(params[o].text())
                self.tc_price_compare(data,parm,'Close')
            elif overlays[o].currentText() == 'Price - Performance':
                parm = str(params[o].text())
                self.tc_pricep_compare(data,parm,'% Change')

        et = time.time()
        print 'tc_overlays', et-st

    def tc_indicators(self,data,symbol):
        st = time.time()

        #Gets the dates from the QtdateEdits and sets the data index the that range
        from_year = self.tc_fromdate.date().year()
        from_month = self.tc_fromdate.date().month()
        from_day = self.tc_fromdate.date().day()
        to_year = self.tc_todate.date().year()
        to_month = self.tc_todate.date().month()
        to_day = self.tc_todate.date().day()
        from_date = datetime.datetime(from_year,from_month,from_day)
        to_date = datetime.datetime(to_year,to_month,to_day)
        data = data[data.columns][from_date:to_date]

        #make sure dates dont have the day name in it
        #remove nan rows
        if type(data.index[-1]) == str:
            newindex = [x.split()[1] for x in data.index]
            data.index = pd.to_datetime(newindex)
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]
        else:
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]

        indicators = [self.tc_indicator1,self.tc_indicator2,self.tc_indicator3]
        params = [self.tc_indparam1,self.tc_indparam2,self.tc_indparam3]

        for i in range(len(indicators)):
            graph_num = i
            if indicators[i].currentText() == '-None-':
                params[i].setText(' ')
            elif indicators[i].currentText() == 'Accum/Distribution Line':
                self.tc_accumdist(data,graph_num)
            elif indicators[i].currentText() == 'Average True Range':
                parm = str(params[i].text())
                self.tc_avgtruerange(data,parm,graph_num)
            elif indicators[i].currentText() == 'Bollinger Band Width':
                parm = str(params[i].text())
                self.tc_bollbandwidth(data,parm,graph_num)
            elif indicators[i].currentText() == 'Bollinger %B':
                parm = str(params[i].text())
                self.tc_bollbandB(data,parm,graph_num)
            elif indicators[i].currentText() == 'Correlation':
                pass
            elif indicators[i].currentText() == 'Dividends':
                pass
            elif indicators[i].currentText() == 'MACD':
                parm = str(params[i].text())
                self.tc_macd(data,parm,graph_num)
            elif indicators[i].currentText() == 'MACD Histogram':
                parm = str(params[i].text())
                self.tc_macdhist(data,parm,graph_num)
            elif indicators[i].currentText() == 'Price':
                pass
            elif indicators[i].currentText() == 'Price - Performance':
                pass
            elif indicators[i].currentText() == 'RSI':
                pass
            elif indicators[i].currentText() == 'Slope (Linear Regression)':
                pass
            elif indicators[i].currentText() == 'Standard Deviation':
                pass
            else:
                pass

    def tc_set_overlayparam(self):
        st = time.time()
        overlays = [self.tc_overlay1,self.tc_overlay2,self.tc_overlay3]
        params = [self.tc_olparam1,self.tc_olparam2,self.tc_olparam3]
        for o in range(len(overlays)):
            if overlays[o]:
                if overlays[o].currentText() == '-None-':
                    params[o].setText(' ')
                elif overlays[o].currentText() == 'Bollinger Bands':
                    params[o].setText('20,2')
                elif overlays[o].currentText() == 'Keltner Channels':
                    params[o].setText('20,10,2')
                elif overlays[o].currentText() == 'Exp. Moving Avg.':
                    params[o].setText('20')
                elif overlays[o].currentText() == 'Chandelier Exit':
                    params[o].setText('22,3,Long')
                elif overlays[o].currentText() == 'Price Channels':
                    params[o].setText('20')
                elif overlays[o].currentText() == 'SMA Envelopes':
                    params[o].setText('20,2.50')
                elif overlays[o].currentText() == 'EMA Envelopes':
                    params[o].setText('20,2.50')
                elif overlays[o].currentText() == 'Price':
                    params[o].setText('GOOG')
                elif overlays[o].currentText() == 'Price - Performance':
                    params[o].setText('GOOG')
            else:
                pass
        et = time.time()
        print 'tc_set_overlayparam', et-st
        self.technical_chart()

    def tc_set_indicatorparam(self):
        st = time.time()
        indicators = [self.tc_indicator1,self.tc_indicator2,self.tc_indicator3]
        params = [self.tc_indparam1,self.tc_indparam2,self.tc_indparam3]
        positions = [self.tc_indposition1,self.tc_indposition2,self.tc_indposition3]

        for i in range(len(indicators)):
            if indicators[i].currentText() == '-None-':
                params[i].setText(' ')
                positions[i].setCurrentIndex(0)
            elif indicators[i].currentText() == 'Accum/Distribution Line':
                params[i].setText(' ')
                positions[i].setCurrentIndex(1)
            elif indicators[i].currentText() == 'Average True Range':
                params[i].setText('14')
                positions[i].setCurrentIndex(1)
            elif indicators[i].currentText() == 'Bollinger Band Width':
                params[i].setText('20,2')
                positions[i].setCurrentIndex(1)
            elif indicators[i].currentText() == 'Bollinger %B':
                params[i].setText('20,2')
                positions[i].setCurrentIndex(1)
            elif indicators[i].currentText() == 'Correlation':
                pass
            elif indicators[i].currentText() == 'Dividends':
                pass
            elif indicators[i].currentText() == 'MACD':
                params[i].setText('12,26,9')
                positions[i].setCurrentIndex(1)
            elif indicators[i].currentText() == 'MACD Histogram':
                params[i].setText('12,26,9')
                positions[i].setCurrentIndex(1)
            elif indicators[i].currentText() == 'Price':
                pass
            elif indicators[i].currentText() == 'Price - Performance':
                pass
            elif indicators[i].currentText() == 'RSI':
                pass
            elif indicators[i].currentText() == 'Slope (Linear Regression)':
                pass
            elif indicators[i].currentText() == 'Standard Deviation':
                pass
            else:
                pass
        et = time.time()
        print 'tc_set_indicatorparam', et-st
        self.technical_chart()

    def tc_overlay_help(self):
        overlays = [self.tc_overlay1,self.tc_overlay2,self.tc_overlay3]
        overlay_help = [self.tc_olhelp1,self.tc_olhelp2,self.tc_olhelp3]
        params = [self.tc_olparam1,self.tc_olparam2,self.tc_olparam3]

        for i in range(len(overlay_help)):
            if overlay_help[i].isChecked():
                self.tc_olind_cb.setMinimumHeight(0)
                self.tc_olind_cb.setMaximumHeight(0)
                self.tc_olind_header.setMinimumHeight(0)
                self.tc_olind_header.setMaximumHeight(0)

                overlay = str(overlays[i].currentText())
                if overlays[i].currentText() == '-None-':
                    params[i].setText('Select an Overlay')
                elif overlays[i].currentText() == 'Bollinger Bands':
                    self.tc_olstacked.setCurrentIndex(1)
                elif overlays[i].currentText() == 'Keltner Channels':
                    self.tc_olstacked.setCurrentIndex(2)
                elif overlays[i].currentText() == 'Exp. Moving Avg.':
                    self.tc_olstacked.setCurrentIndex(3)
                elif overlays[i].currentText() == 'Chandelier Exit':
                    self.tc_olstacked.setCurrentIndex(4)
                elif overlays[i].currentText() == 'Price Channels':
                    self.tc_olstacked.setCurrentIndex(5)
                elif overlays[i].currentText() == 'SMA Envelopes':
                    self.tc_olstacked.setCurrentIndex(6)
                elif overlays[i].currentText() == 'EMA Envelopes':
                    self.tc_olstacked.setCurrentIndex(7)
                elif overlays[i].currentText() == 'Price':
                    self.tc_olstacked.setCurrentIndex(8)
                elif overlays[i].currentText() == 'Price - Performance':
                    self.tc_olstacked.setCurrentIndex(9)
            else:
                pass

    def tc_indicator_help(self):
        indicators = [self.tc_indicator1,self.tc_indicator2,self.tc_indicator3]
        indicator_help = [self.tc_indhelp1,self.tc_indhelp2,self.tc_indhelp3]
        params = [self.tc_indparam1,self.tc_indparam2,self.tc_indparam3]

        for i in range(len(indicator_help)):
            if indicator_help[i].isChecked():
                self.tc_olind_cb.setMinimumHeight(0)
                self.tc_olind_cb.setMaximumHeight(0)
                self.tc_olind_header.setMinimumHeight(0)
                self.tc_olind_header.setMaximumHeight(0)

                indicator = str(indicators[i].currentText())
                if indicators[i].currentText() == '-None-':
                    params[i].setText('Select an Overlay')
                elif indicators[i].currentText() == 'Accum/Distribution Line':
                    self.tc_indstacked.setCurrentIndex(1)
                elif indicators[i].currentText() == 'Average True Range':
                    self.tc_indstacked.setCurrentIndex(2)
                elif indicators[i].currentText() == 'Bollinger Band Width':
                    self.tc_indstacked.setCurrentIndex(3)
                elif indicators[i].currentText() == 'Bollinger %B':
                    self.tc_indstacked.setCurrentIndex(4)
                elif indicators[i].currentText() == 'Correlation':
                    pass
                elif indicators[i].currentText() == 'Dividends':
                    pass
                elif indicators[i].currentText() == 'MACD':
                    self.tc_indstacked.setCurrentIndex(5)
                elif indicators[i].currentText() == 'MACD Histogram':
                    self.tc_indstacked.setCurrentIndex(6)
                elif indicators[i].currentText() == 'Price':
                    pass
                elif indicators[i].currentText() == 'Price - Performance':
                    pass
                elif indicators[i].currentText() == 'RSI':
                    pass
                elif indicators[i].currentText() == 'Slope (Linear Regression)':
                    pass
                elif indicators[i].currentText() == 'Standard Deviation':
                    pass

            else:
                pass

    def tc_olhelp_back(self):
        st = time.time()
        self.tc_olind_cb.setMinimumHeight(50)
        self.tc_olind_cb.setMaximumHeight(50)
        self.tc_olind_header.setMinimumHeight(50)
        self.tc_olind_header.setMaximumHeight(50)
        overlay_back = [self.tc_olhelp_b1,self.tc_olhelp_b2,self.tc_olhelp_b3,self.tc_olhelp_b4,
                        self.tc_olhelp_b5,self.tc_olhelp_b6,self.tc_olhelp_b7,self.tc_olhelp_b8,
                        self.tc_olhelp_b9]
        for i in range(len(overlay_back)):
            if overlay_back[i].isChecked():
                self.tc_olstacked.setCurrentIndex(0)
                overlay_back[i].setChecked(False)
            else:
                pass
        et = time.time()
        print 'tc_olhelp_back', et-st

    def tc_indhelp_back(self):
        st = time.time()
        self.tc_olind_cb.setMinimumHeight(50)
        self.tc_olind_cb.setMaximumHeight(50)
        self.tc_olind_header.setMinimumHeight(50)
        self.tc_olind_header.setMaximumHeight(50)
        indicator_back = [self.tc_indhelp_b1,self.tc_indhelp_b2,self.tc_indhelp_b3,self.tc_indhelp_b4,
                        self.tc_indhelp_b5,self.tc_indhelp_b6]
        for i in range(len(indicator_back)):
            if indicator_back[i].isChecked():
                self.tc_indstacked.setCurrentIndex(0)
                indicator_back[i].setChecked(False)
            else:
                pass
        et = time.time()
        print 'tc_indhelp_back', et-st

    def tc_datechange(self):
        st = time.time()
        symbol = str(self.tc_mainsearch.text())
        data = self.get_symbol_data(symbol)

        gridcolor = self.tc_gridcolor.palette().button().color()
        gridcolor = str(gridcolor.name())
        textcolor = self.tc_textcolor.palette().button().color()
        textcolor = str(textcolor.name())

        #make sure dates dont have the day name in it
        if type(data.index[-1]) == str:
            newindex = [x.split()[1] for x in data.index]
            data.index = pd.to_datetime(newindex)
        else:
            pass

        #set the Qdateedit to the dates of the buttons pressed
        self.tc_todate.setDate(QtCore.QDate(year,month,day))
        if self.tc_oneday_db.isChecked():
            self.tc_fromdate.setDate(QtCore.QDate(year,month,day-1))
            self.tech_chart_axis.grid(True, which='minor', color=gridcolor, linestyle='--')  
            self.tech_chart_axis.tick_params(axis='x',which='minor',colors=textcolor,labelsize=20)

            xax = self.tech_chart_axis.get_xaxis()
            self.tech_chart_axis.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0,24)))
            self.tech_chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
            self.tech_chart_axis.xaxis.set_tick_params(which='major', pad=15) 

        elif self.tc_fiveday_db.isChecked():
            self.tc_fromdate.setDate(QtCore.QDate(year,month,day-5))
            self.tech_chart_axis.grid(True, which='minor', color=gridcolor, linestyle='--')  
            self.tech_chart_axis.tick_params(axis='x',which='minor',colors=textcolor,labelsize=20)

            xax = self.tech_chart_axis.get_xaxis()
            self.tech_chart_axis.xaxis.set_major_locator(mdates.DayLocator())
            self.tech_chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
            self.tech_chart_axis.xaxis.set_tick_params(which='major', pad=25) 

        elif self.tc_onemonth_db.isChecked():
            self.tc_fromdate.setDate(QtCore.QDate(year,month-1,day))
            self.tech_chart_axis.grid(True, which='minor', color=gridcolor, linestyle='--')  
            self.tech_chart_axis.tick_params(axis='x',which='minor',colors=textcolor,labelsize=20)

            xax = self.tech_chart_axis.get_xaxis()
            self.tech_chart_axis.xaxis.set_major_locator(mdates.MonthLocator())
            self.tech_chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            self.tech_chart_axis.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=range()))
            self.tech_chart_axis.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
            self.tech_chart_axis.xaxis.set_tick_params(which='major', pad=25) 

        elif self.tc_threemonth_db.isChecked():
            self.tc_fromdate.setDate(QtCore.QDate(year,month-3,day))
            self.tech_chart_axis.grid(True, which='minor', color=gridcolor, linestyle='--')  
            self.tech_chart_axis.tick_params(axis='x',which='minor',colors=textcolor,labelsize=20)
            xax = self.tech_chart_axis.get_xaxis()
            self.tech_chart_axis.xaxis.set_major_locator(mdates.MonthLocator())
            self.tech_chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            self.tech_chart_axis.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=range(3,31,3)))
            self.tech_chart_axis.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
            self.tech_chart_axis.xaxis.set_tick_params(which='major', pad=25)

        elif self.tc_sixmonth_db.isChecked():
            self.tc_fromdate.setDate(QtCore.QDate(year,month-6,day))
            self.tech_chart_axis.grid(True, which='minor', color=gridcolor, linestyle='--')  
            self.tech_chart_axis.tick_params(axis='x',which='minor',colors=textcolor,labelsize=20)

            xax = self.tech_chart_axis.get_xaxis()
            self.tech_chart_axis.xaxis.set_major_locator(mdates.MonthLocator())
            self.tech_chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            self.tech_chart_axis.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=range(6,28,6)))
            self.tech_chart_axis.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
            self.tech_chart_axis.xaxis.set_tick_params(which='major', pad=25)

        elif self.tc_oneyear_db.isChecked():
            self.tc_fromdate.setDate(QtCore.QDate(year-1,month,day))
            self.tech_chart_axis.grid(True, which='minor', color=gridcolor, linestyle='--')  
            self.tech_chart_axis.tick_params(axis='x',which='minor',colors=textcolor,labelsize=20)
            xax = self.tech_chart_axis.get_xaxis()
            self.tech_chart_axis.xaxis.set_major_locator(mdates.YearLocator())
            self.tech_chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            self.tech_chart_axis.xaxis.set_minor_locator(mdates.MonthLocator())
            self.tech_chart_axis.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
            self.tech_chart_axis.xaxis.set_tick_params(which='major', pad=25) 
 
        elif self.tc_fiveyear_db.isChecked():
            self.tc_fromdate.setDate(QtCore.QDate(year-5,month,day))   
            self.tech_chart_axis.grid(True, which='minor', color=gridcolor, linestyle='--')  
            self.tech_chart_axis.tick_params(axis='x',which='minor',colors=textcolor,labelsize=20)
            xax = self.tech_chart_axis.get_xaxis()
            self.tech_chart_axis.xaxis.set_major_locator(mdates.YearLocator())
            self.tech_chart_axis.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            self.tech_chart_axis.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=range(4,12,3)))
            self.tech_chart_axis.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))
            self.tech_chart_axis.xaxis.set_tick_params(which='major', pad=25)
    
        elif self.tc_max_db.isChecked():
            start_date = data.first_valid_index().to_pydatetime()
            start_year = start_date.year
            start_month = start_date.month
            start_day = start_date.day
            self.tc_fromdate.setDate(QtCore.QDate(start_year,start_month,start_day))

        et = time.time()
        print 'tc_datechange', et-st

        self.tc_attributes()

    def tc_edit(self):
        if self.tc_openedit.isChecked():
            self.tc_editwidget.setMinimumHeight(250)
            self.tc_editwidget.setMaximumHeight(250)
            self.tc_maingraph.setMinimumHeight(0)

        else:
            self.tc_editwidget.setMinimumHeight(0)
            self.tc_editwidget.setMaximumHeight(0)
            self.tc_maingraph.setMinimumHeight(0)

    def tc_overlayindicator(self):
        st = time.time()
        if self.tc_olind_cb.currentText() == 'Overlays':
            self.tc_stack_overlay_ind.setCurrentIndex(0)
            self.tc_olstacked.setCurrentIndex(0)
            self.tc_olind_cb.setMinimumWidth(505)
            self.tc_olind_cb.setMaximumWidth(505)
            self.tc_olind_header.setCurrentIndex(0)
            self.tc_olind_header.setMinimumWidth(315)
            self.tc_olind_header.setMaximumWidth(315)

        elif self.tc_olind_cb.currentText() == 'Indicators':
            self.tc_stack_overlay_ind.setCurrentIndex(1)
            self.tc_olind_cb.setMinimumWidth(400)
            self.tc_olind_cb.setMaximumWidth(400)
            self.tc_olind_header.setCurrentIndex(1)
            self.tc_olind_header.setMinimumWidth(435)
            self.tc_olind_header.setMaximumWidth(435)
        et = time.time()
        print 'tc_overlayindicator', et-st

    def tc_legend(self):
        st = time.time()
        axis = [self.tech_chart_axis,self.tc_ind1_axis,self.tc_ind2_axis,self.tc_ind3_axis]
        canvas = [self.tech_chart_canvas,self.tech_chart_canvas1,self.tech_chart_canvas2,self.tech_chart_canvas3]
        positions = [self.tc_indposition1,self.tc_indposition2,self.tc_indposition3]
        pos = ['Main'] + [i.currentText() for i in positions]

        for a in range(len(axis)):
            if pos[a] == '-None-':
                pass
            else:
                handles, labels = axis[a].get_legend_handles_labels()
                keep_labels = []
                keep_handles = []
                for x in range(len(labels)):
                    if str(labels[x]) == 'Close':
                        pass
                    elif str(labels[x]) == 'High':
                        pass
                    else:
                        keep_labels.append(labels[x])
                        keep_handles.append(handles[x])
                axis[a].legend(keep_handles, keep_labels, loc=2, fontsize=20)

        et = time.time()
        print 'tc_legend', et-st

    # Chart Overlays    
    def tc_moving_averages(self,data,symbol): 
        st = time.time()   

        #make sure dates dont have the day name in it
        #remove nan rows
        if type(data.index[-1]) == str:
            newindex = [x.split()[1] for x in data.index]
            data.index = pd.to_datetime(newindex)
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]
        else:
            date = data['Open'].first_valid_index() #first real value
            ind = data.index.get_loc(date) #index of thet value
            data = data[data.columns][ind:]

        ##Gets the dates from the QtdateEdits and sets the data index the that range
        #from_year = self.tc_fromdate.date().year()
        #from_month = self.tc_fromdate.date().month()
        #from_day = self.tc_fromdate.date().day()
        #to_year = self.tc_todate.date().year()
        #to_month = self.tc_todate.date().month()
        #to_day = self.tc_todate.date().day()
        #from_date = datetime.datetime(from_year,from_month,from_day)
        #to_date = datetime.datetime(to_year,to_month,to_day)
        #data = data[data.columns][from_date:to_date]

        moving_avgs = [self.tc_movavgs1,self.tc_movavgs2,self.tc_movavgs3]
        for m in range(len(moving_avgs)):
            if moving_avgs[m].text() != '':
                print 'MA???'
                num_days = int(moving_avgs[m].text())
                mov_avg = data['Close'].rolling(window=num_days,center=False).mean()
                ma_legend = 'MA ('+str(num_days)+')'
                self.tech_chart_axis.plot(mov_avg,lw=3,alpha=0.75,color='blue',linestyle='solid',label=ma_legend)
            else:
                print 'MA!!!'

        et = time.time()
        print 'tc_moving_averages', et-st

    def tc_bollinger_bands(self,data,defualt_parm):
        st = time.time()
        num_days = int(defualt_parm.split(',')[0])
        multiplier = int(defualt_parm.split(',')[1]) 

        upper_ls = int(self.tc_bbupper_ls.text())
        upper_lc = self.tc_bbupper_lc.palette().button().color()
        upper_lc = str(upper_lc.name())
        upper_lt = str(self.tc_bbupper_lt.currentText()).lower()

        middle_ls = int(self.tc_bbmiddle_ls.text())
        middle_lc = self.tc_bbmiddle_lc.palette().button().color()
        middle_lc = str(middle_lc.name())
        middle_lt = str(self.tc_bbmiddle_lt.currentText()).lower()

        lower_ls = int(self.tc_bblower_ls.text())
        lower_lc = self.tc_bblower_lc.palette().button().color()
        lower_lc = str(lower_lc.name())
        lower_lt = str(self.tc_bblower_lt.currentText()).lower()

        middle_band = data['Close'].rolling(window=num_days,center=False).mean()
        upper_band = middle_band + (data['Close'].rolling(window=num_days,center=False).std()*multiplier)
        lower_band = middle_band - (data['Close'].rolling(window=num_days,center=False).std()*multiplier)

        line_legend = 'BB('+str(defualt_parm)+')'+' '+str(round(lower_band[-1],2))+' - '+str(round(middle_band[-1],2))+' - '+str(round(upper_band[-1],2))
        self.tech_chart_axis.plot(upper_band,lw=upper_ls,alpha=0.50,color=upper_lc,linestyle=upper_lt)
        self.tech_chart_axis.plot(middle_band,lw=middle_ls,alpha=0.50,color=middle_lc,linestyle=middle_lt,label=line_legend)
        self.tech_chart_axis.plot(lower_band,lw=lower_ls,alpha=0.50,color=lower_lc,linestyle=lower_lt)
        
        et = time.time()
        print 'tc_bollinger_bands', et-st

    def tc_keltner_channels(self,data,defualt_parm): 
        st = time.time()
        sma_days = int(defualt_parm.split(',')[0])
        atr_days = int(defualt_parm.split(',')[1])
        multiplier = int(defualt_parm.split(',')[2])

        upper_ls = int(self.tc_kcupper_ls.text())
        upper_lc = self.tc_kcupper_lc.palette().button().color()
        upper_lc = str(upper_lc.name())
        upper_lt = str(self.tc_kcupper_lt.currentText()).lower()

        middle_ls = int(self.tc_kcmiddle_ls.text())
        middle_lc = self.tc_kcmiddle_lc.palette().button().color()
        middle_lc = str(middle_lc.name())
        middle_lt = str(self.tc_kcmiddle_lt.currentText()).lower()

        lower_ls = int(self.tc_kclower_ls.text())
        lower_lc = self.tc_kclower_lc.palette().button().color()
        lower_lc = str(lower_lc.name())
        lower_lt = str(self.tc_kclower_lt.currentText()).lower()
        
        #ATR
        data['ATR1'] = abs(data['High'] - data['Low'])
        data['ATR2'] = abs(data['High'] - data['Close'].shift())
        data['ATR3'] = abs(data['Low'] - data['Close'].shift())
        atr = data[['ATR1','ATR2','ATR3']].max(axis=1)
        atr = atr.rolling(window=atr_days,center=False).mean()

        middle_line = pd.ewma(data['Close'],span=sma_days)
        upper_line = middle_line + (multiplier * atr)
        lower_line = middle_line - (multiplier * atr)

        line_legend = 'KELT('+str(defualt_parm)+')'+' '+str(round(lower_line[-1],2))+' - '+str(round(middle_line[-1],2))+' - '+str(round(upper_line[-1],2))
        self.tech_chart_axis.plot(upper_line,lw=upper_ls,alpha=0.50,color=upper_lc,linestyle=upper_lt)
        self.tech_chart_axis.plot(middle_line,lw=middle_ls,alpha=0.50,color=middle_lc,linestyle=middle_lt,label=line_legend)
        self.tech_chart_axis.plot(lower_line,lw=lower_ls,alpha=0.50,color=lower_lc,linestyle=lower_lt)

        et = time.time()
        print 'tc_keltner_channels', et-st

    def tc_ema(self,data,defualt_parm):
        st = time.time()
        ema_days = int(defualt_parm.split(',')[0])

        ema_ls = int(self.tc_ema_ls.text())
        ema_lc = self.tc_ema_lc.palette().button().color()
        ema_lc = str(ema_lc.name())
        ema_lt = str(self.tc_ema_lt.currentText()).lower()

        ema = pd.ewma(data['Close'],span=ema_days)
        line_legend = 'EMA('+str(ema_days)+') '+str(round(ema[-1],2))
        self.tech_chart_axis.plot(ema,lw=ema_ls,alpha=0.50,color=ema_lc,linestyle=ema_lt,label=line_legend)
        et = time.time()
        print 'tc_ema', et-st

    def tc_chandelier_exit(self,data,defualt_parm):
        st = time.time()
        num_days = int(defualt_parm.split(',')[0])
        multiplier = int(defualt_parm.split(',')[1])
        long_short = str(defualt_parm.split(',')[2]).lower()

        chexit_ls = int(self.tc_chexit_ls.text())
        chexit_lc = self.tc_chexit_lc.palette().button().color()
        chexit_lc = str(chexit_lc.name())
        chexit_lt = str(self.tc_chexit_lt.currentText()).lower()

        #ATR
        data['ATR1'] = abs(data['High'] - data['Low'])
        data['ATR2'] = abs(data['High'] - data['Close'].shift())
        data['ATR3'] = abs(data['Low'] - data['Close'].shift())
        atr = data[['ATR1','ATR2','ATR3']].max(axis=1)
        atr = atr.rolling(window=num_days,center=False).mean()

        if long_short == 'long':
            chexit = data['High'].rolling(window=num_days,center=False).mean() - (atr*3)
        elif long_short == 'short':
            chexit = data['High'].rolling(window=num_days,center=False).mean() + (atr*3)

        line_legend = 'CHANDLR('+str(defualt_parm)+') '+str(round(chexit[-1],2))
        self.tech_chart_axis.plot(chexit,lw=chexit_ls,alpha=0.50,color=chexit_lc,linestyle=chexit_lt,label=line_legend)
        et = time.time()
        print 'tc_chandelier_exit', et-st

    def tc_price_channels(self,data,defualt_parm):
        st = time.time()
        num_days = int(defualt_parm.split(',')[0])

        upper_ls = int(self.tc_pcupper_ls.text())
        upper_lc = self.tc_pcupper_lc.palette().button().color()
        upper_lc = str(upper_lc.name())
        upper_lt = str(self.tc_pcupper_lt.currentText()).lower()

        middle_ls = int(self.tc_pcmiddle_ls.text())
        middle_lc = self.tc_pcmiddle_lc.palette().button().color()
        middle_lc = str(middle_lc.name())
        middle_lt = str(self.tc_pcmiddle_lt.currentText()).lower()

        lower_ls = int(self.tc_pclower_ls.text())
        lower_lc = self.tc_pclower_lc.palette().button().color()
        lower_lc = str(lower_lc.name())
        lower_lt = str(self.tc_pclower_lt.currentText()).lower()

        upper_line = data['High'].rolling(window=num_days,center=False).mean()
        lower_line = data['Low'].rolling(window=num_days,center=False).mean()
        middle_line = (upper_line + lower_line) / 2

        line_legend = 'PRICECHAN('+str(num_days)+')'+' '+str(round(lower_line[-1],2))+'-'+str(round(middle_line[-1],2))+'-'+str(round(upper_line[-1],2))
        self.tech_chart_axis.plot(upper_line,lw=upper_ls,alpha=0.50,color=upper_lc,linestyle=upper_lt)
        self.tech_chart_axis.plot(middle_line,lw=middle_ls,alpha=0.50,color=middle_lc,linestyle=middle_lt)
        self.tech_chart_axis.plot(lower_line,lw=lower_ls,alpha=0.50,color=lower_lc,linestyle=lower_lt,label=line_legend)

        et = time.time()
        print 'tc_price_channels', et-st

    def tc_sma_envelope(self,data,defualt_parm):
        st = time.time()
        num_days = int(defualt_parm.split(',')[0])
        multiplier = str(defualt_parm.split(',')[1])

        upper_ls = int(self.tc_smaeupper_ls.text())
        upper_lc = self.tc_smaeupper_lc.palette().button().color()
        upper_lc = str(upper_lc.name())
        upper_lt = str(self.tc_smaeupper_lt.currentText()).lower()

        lower_ls = int(self.tc_smaelower_ls.text())
        lower_lc = self.tc_smaelower_lc.palette().button().color()
        lower_lc = str(lower_lc.name())
        lower_lt = str(self.tc_smaelower_lt.currentText()).lower()

        sma = data['Close'].rolling(window=num_days,center=False).mean()

        upper_line = sma + (sma * (float(multiplier)/float(100)))
        lower_line = sma - (sma * (float(multiplier)/float(100)))

        line_legend = 'ENV('+str(defualt_parm)+')'+' '+str(round(lower_line[-1],2))+'-'+str(round(upper_line[-1],2))
        self.tech_chart_axis.plot(upper_line,lw=upper_ls,alpha=0.50,color=upper_lc,linestyle=upper_lt)
        self.tech_chart_axis.plot(lower_line,lw=lower_ls,alpha=0.50,color=lower_lc,linestyle=lower_lt,label=line_legend)

        et = time.time()
        print 'tc_sma_envelope', et-st

    def tc_ema_envelope(self,data,defualt_parm):
        st = time.time()
        num_days = int(defualt_parm.split(',')[0])
        multiplier = str(defualt_parm.split(',')[1])

        upper_ls = int(self.tc_emaeupper_ls.text())
        upper_lc = self.tc_emaeupper_lc.palette().button().color()
        upper_lc = str(upper_lc.name())
        upper_lt = str(self.tc_emaeupper_lt.currentText()).lower()

        lower_ls = int(self.tc_emaelower_ls.text())
        lower_lc = self.tc_emaelower_lc.palette().button().color()
        lower_lc = str(lower_lc.name())
        lower_lt = str(self.tc_emaelower_lt.currentText()).lower()

        ema = pd.ewma(data['Close'],span=num_days)

        upper_line = ema + (ema * (float(multiplier)/float(100)))
        lower_line = ema - (ema * (float(multiplier)/float(100)))

        line_legend = 'EMAENV('+str(defualt_parm)+')'+' '+str(round(upper_line[-1],2))+'-'+str(round(upper_line[-1],2))
        self.tech_chart_axis.plot(upper_line,lw=upper_ls,alpha=0.50,color=upper_lc,linestyle=upper_lt)
        self.tech_chart_axis.plot(lower_line,lw=lower_ls,alpha=0.50,color=lower_lc,linestyle=lower_lt,label=line_legend)

        et = time.time()
        print 'tc_ema_envelope', et-st

    def tc_price_compare(self,data,defualt_parm,var):
        st = time.time()
        symbol = str(defualt_parm.split(',')[0])

        #colors
        gridcolor = self.tc_gridcolor.palette().button().color()
        gridcolor = str(gridcolor.name())
        linecolor = self.tc_linecolor.palette().button().color()
        linecolor = str(linecolor.name())
        price_lc = self.tc_price_lc.palette().button().color()
        price_lc = str(price_lc.name())
        price_ls = int(self.tc_price_ls.text())
        price_lt = str(self.tc_price_lt.currentText()).lower()

        #match y axis label colors
        self.tech_chart_axis.tick_params(axis='y', colors=linecolor,labelsize=20)
        self.price_ax.tick_params(axis='y', colors=price_lc,labelsize=20)
        self.price_ax.spines["right"].set_position(("axes", 1.035))
        self.price_ax.spines["right"].set_visible(True)
        self.price_ax.spines["right"].set_color(gridcolor)
        self.tech_chart_axis.yaxis.tick_right()
        self.price_ax.yaxis.tick_right()

        price_data = self.get_symbol_data(symbol)
        #make sure dates dont have the day name in it
        #remove nan rows
        if type(price_data.index[-1]) == str:
            newindex = [x.split()[1] for x in price_data.index]
            price_data.index = pd.to_datetime(newindex)
            date = price_data['Open'].first_valid_index() #first real value
            ind = price_data.index.get_loc(date) #index of thet value
            price_data = price_data[price_data.columns][ind:]
        else:
            date = price_data['Open'].first_valid_index() #first real value
            ind = price_data.index.get_loc(date) #index of thet value
            price_data = price_data[price_data.columns][ind:]

        #Gets the dates from the QtdateEdits and sets the data index the that range
        from_year = self.tc_fromdate.date().year()
        from_month = self.tc_fromdate.date().month()
        from_day = self.tc_fromdate.date().day()
        to_year = self.tc_todate.date().year()
        to_month = self.tc_todate.date().month()
        to_day = self.tc_todate.date().day()
        from_date = datetime.datetime(from_year,from_month,from_day)
        to_date = datetime.datetime(to_year,to_month,to_day)
        price_data = price_data[price_data.columns][from_date:to_date]
        self.price_ax.set_xlim([datetime.datetime(from_year,from_month,from_day),datetime.datetime(to_year,to_month,to_day)])

        line_legend = str(symbol)+' '+str(price_data[var][-1])
        self.price_ax.plot(price_data[var],lw=price_ls,alpha=0.50,color=price_lc,linestyle=price_lt,label=line_legend)
        self.gs1.update(left=0.01, right=0.94, top=.99, bottom=0.03,wspace=0,hspace=0)
        self.tech_chart_fig.subplots_adjust(left=0.05)
        self.price_ax.set_yticks(np.linspace(self.price_ax.get_yticks()[0],self.price_ax.get_yticks()[-1],len(self.price_ax.get_yticks())))
        
        et = time.time()
        print 'tc_price_compare', et-st

    #Chart Indicators 
    def tc_indicator_graph(self,graph_num):
        st = time.time()

        #colors
        gridcolor = self.tc_gridcolor.palette().button().color()
        gridcolor = str(gridcolor.name())
        textcolor = self.tc_textcolor.palette().button().color()
        textcolor = str(textcolor.name())
        backgroundcolor = self.tc_backgroundcolor.palette().button().color()
        backgroundcolor = str(backgroundcolor.name())

        graphs = [self.tc_indgragh1,self.tc_indgragh2,self.tc_indgragh3]
        indicators = [self.tc_indicator1,self.tc_indicator2,self.tc_indicator3]
        params = [self.tc_indparam1,self.tc_indparam2,self.tc_indparam3]
        positions = [self.tc_indposition1,self.tc_indposition2,self.tc_indposition3]
        pos = [i.currentText() for i in positions]
        canv = [self.tech_chart_canvas1,self.tech_chart_canvas2,self.tech_chart_canvas3]
        axis = [self.tc_ind1_axis,self.tc_ind2_axis,self.tc_ind3_axis]

        if positions[graph_num].currentText() == 'Above':
            self.tc_tglayout1.addWidget(graphs[graph_num])
            axis[graph_num].clear()
            axis[graph_num].set_facecolor(backgroundcolor)
            axis[graph_num].grid(True, which='major', color=gridcolor, linestyle='--')  
            axis[graph_num].yaxis.label.set_color("w")
            axis[graph_num].xaxis.label.set_color('w')
            axis[graph_num].tick_params(axis='y', colors=textcolor,labelsize=20)
            axis[graph_num].tick_params(axis='x', colors=textcolor,labelsize=20)
            axis[graph_num].spines['top'].set_color(gridcolor)
            axis[graph_num].spines['bottom'].set_color(gridcolor)
            axis[graph_num].spines['top'].set_visible(True)
            axis[graph_num].spines['bottom'].set_visible(True)
            axis[graph_num].yaxis.tick_right()

            if pos.count('Above') == 1:
                self.tc_topgraghs.setMinimumHeight(300)
                self.tc_topgraghs.setMaximumHeight(300)
                graphs[graph_num].setMinimumHeight(300)
                graphs[graph_num].setMaximumHeight(300)
            elif pos.count('Above') == 2:
                self.tc_topgraghs.setMinimumHeight(600)
                self.tc_topgraghs.setMaximumHeight(600)
                graphs[graph_num].setMinimumHeight(300)
                graphs[graph_num].setMaximumHeight(300)
            elif pos.count('Above') == 3:
                self.tc_topgraghs.setMinimumHeight(900)
                self.tc_topgraghs.setMaximumHeight(900)
                graphs[graph_num].setMinimumHeight(300)
                graphs[graph_num].setMaximumHeight(300)

        elif positions[graph_num].currentText() == 'Below':
            self.tc_btlayout1.addWidget(graphs[graph_num])
            axis[graph_num].clear()
            axis[graph_num].set_facecolor(backgroundcolor)
            axis[graph_num].grid(True, which='major', color=gridcolor, linestyle='--')  
            axis[graph_num].yaxis.label.set_color("w")
            axis[graph_num].xaxis.label.set_color('w')
            axis[graph_num].tick_params(axis='y', colors=textcolor,labelsize=20)
            axis[graph_num].tick_params(axis='x', colors=textcolor,labelsize=20)
            axis[graph_num].spines['top'].set_color(gridcolor)
            axis[graph_num].spines['bottom'].set_color(gridcolor)
            axis[graph_num].spines['top'].set_visible(True)
            axis[graph_num].spines['bottom'].set_visible(True)
            axis[graph_num].yaxis.tick_right()

            if pos.count('Below') == 1:
                self.tc_bottomgraghs.setMinimumHeight(300)
                self.tc_bottomgraghs.setMaximumHeight(300)
                graphs[graph_num].setMinimumHeight(300)
                graphs[graph_num].setMaximumHeight(300)
            elif pos.count('Below') == 2:
                self.tc_bottomgraghs.setMinimumHeight(600)
                self.tc_bottomgraghs.setMaximumHeight(600)
                graphs[graph_num].setMinimumHeight(300)
                graphs[graph_num].setMaximumHeight(300)
            elif pos.count('Below') == 3:
                self.tc_bottomgraghs.setMinimumHeight(900)
                self.tc_bottomgraghs.setMaximumHeight(900)
                graphs[graph_num].setMinimumHeight(300)
                graphs[graph_num].setMaximumHeight(300)

        date_format = str(self.tc_date_format.currentText())
        dateform = mdates.DateFormatter(date_format)
        self.tech_chart_axis.xaxis.set_major_formatter(dateform)
        et = time.time()
        print 'tc_indicator_graph',et-st
        return axis[graph_num], canv[graph_num]

    def tc_accumdist(self,data,graph_num):
        st = time.time()
        
        axis, canv = self.tc_indicator_graph(graph_num)

        line_ls = int(self.tc_accdist_ls.text())
        line_lc = self.tc_accdist_lc.palette().button().color()
        line_lc = str(line_lc.name())
        line_lt = str(self.tc_accdist_lt.currentText()).lower()

        #calculations for accumulation distribution line
        data['MFM'] = ((data['Close']-data['Low']) - (data['High']-data['Close'])) / (data['High']-data['Low'])
        data['MFV'] = data['MFM'] * data['Volume'] 
        data['ADL'] = data['MFV'].cumsum()

        #center the line in middle of graph
        close_min = data['ADL'].min()
        close_max = data['ADL'].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        line_legend = 'Accum/Dist'
        axis.plot(data['ADL'],lw=line_ls,alpha=0.75,color=line_lc,linestyle=line_lt,label=line_legend)
        canv.draw()
        et = time.time()
        print 'tc_accumdist', et-st

    def tc_avgtruerange(self,data,defualt_parm,graph_num):
        st = time.time()

        axis, canv = self.tc_indicator_graph(graph_num)

        line_ls = int(self.tc_atr_ls.text())
        line_lc = self.tc_atr_lc.palette().button().color()
        line_lc = str(line_lc.name())
        line_lt = str(self.tc_atr_lt.currentText()).lower()

        #ATR
        data['ATR1'] = abs(data['High'] - data['Low'])
        data['ATR2'] = abs(data['High'] - data['Close'].shift())
        data['ATR3'] = abs(data['Low'] - data['Close'].shift())
        data['ATR'] = data[['ATR1','ATR2','ATR3']].max(axis=1)
        data['ATR'] = data['ATR'].rolling(window=int(defualt_parm),center=False).mean()

        #center the line in middle of graph
        close_min = data['ATR'].min()
        close_max = data['ATR'].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        line_legend = 'ATR ('+str(defualt_parm)+') '+str(round(data['ATR'][-1],2))
        axis.plot(data['ATR'],lw=line_ls,alpha=0.75,color=line_lc,linestyle=line_lt,label=line_legend)
        canv.draw()

        et = time.time()
        print 'tc_avgtruerange', et-st

    def tc_bollbandwidth(self,data,defualt_parm,graph_num):
        st = time.time()

        axis, canv = self.tc_indicator_graph(graph_num)

        line_ls = int(self.tc_bollwidth_ls.text())
        line_lc = self.tc_bollwidth_lc.palette().button().color()
        line_lc = str(line_lc.name())
        line_lt = str(self.tc_bollwidth_lt.currentText()).lower()

        num_days = int(defualt_parm.split(',')[0])
        multiplier = int(defualt_parm.split(',')[1]) 

        data['Mid Band'] = data['Close'].rolling(window=num_days,center=False).mean()
        data['Up Band'] = data['Mid Band'] + (data['Close'].rolling(window=num_days,center=False).std()*multiplier)
        data['Low Band'] = data['Mid Band'] - (data['Close'].rolling(window=num_days,center=False).std()*multiplier)
        data['Band Width'] = ((data['Up Band'] - data['Low Band']) / data['Mid Band']) *100

        #center the line in middle of graph
        close_min = data['Band Width'].min()
        close_max = data['Band Width'].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        line_legend = 'BB Width('+str(defualt_parm)+') '+str(round(data['Band Width'][-1],2))
        axis.plot(data['Band Width'],lw=line_ls,alpha=0.75,color=line_lc,linestyle=line_lt,label=line_legend)
        canv.draw()

        et = time.time()
        print 'tc_bollbandwidth', et-st

    def tc_bollbandB(self,data,defualt_parm,graph_num):
        st = time.time()

        axis, canv = self.tc_indicator_graph(graph_num)

        line_ls = int(self.tc_bollb_ls.text())
        line_lc = self.tc_bollb_lc.palette().button().color()
        line_lc = str(line_lc.name())
        line_lt = str(self.tc_bollb_lt.currentText()).lower()

        num_days = int(defualt_parm.split(',')[0])
        multiplier = int(defualt_parm.split(',')[1]) 

        data['Mid Band'] = data['Close'].rolling(window=num_days,center=False).mean()
        data['Up Band'] = data['Mid Band'] + (data['Close'].rolling(window=num_days,center=False).std()*multiplier)
        data['Low Band'] = data['Mid Band'] - (data['Close'].rolling(window=num_days,center=False).std()*multiplier)
        data['BandB'] = (data['Close'] - data['Low Band'])/(data['Up Band'] - data['Low Band'])

        #center the line in middle of graph
        close_min = data['BandB'].min()
        close_max = data['BandB'].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        line_legend = '%B('+str(defualt_parm)+') '+str(round(data['BandB'][-1],2))
        axis.plot(data['BandB'],lw=line_ls,alpha=0.75,color=line_lc,linestyle=line_lt,label=line_legend)
        canv.draw()

        et = time.time()
        print 'tc_bollbandB', et-st

    def tc_macd(self,data,defualt_parm,graph_num):
        st = time.time()

        axis, canv = self.tc_indicator_graph(graph_num)

        emadays1 = int(defualt_parm.split(',')[0])
        emadays2 = int(defualt_parm.split(',')[1])
        emadays3 = int(defualt_parm.split(',')[2])

        macd_ls = int(self.tc_macd_ls.text())
        macd_lc = self.tc_macd_lc.palette().button().color()
        macd_lc = str(macd_lc.name())
        macd_lt = str(self.tc_macd_lt.currentText()).lower()

        signal_ls = int(self.tc_signal_ls.text())
        signal_lc = self.tc_signal_lc.palette().button().color()
        signal_lc = str(signal_lc.name())
        signal_lt = str(self.tc_signal_lt.currentText()).lower()

        hist_ls = int(self.tc_hist_ls.text())
        hist_lc = self.tc_hist_lc.palette().button().color()
        hist_lc = str(hist_lc.name())
        hist_lt = str(self.tc_hist_lt.currentText()).lower()

        ema1 = pd.ewma(data['Close'],span=emadays1)
        ema2 = pd.ewma(data['Close'],span=emadays2)

        data['MACD'] = ema1 - ema2
        data['Signal'] = pd.ewma(data['MACD'],span=emadays3)
        data['Hist'] = data['MACD'] - data['Signal']

        #center the line in middle of graph
        close_min = data['MACD'].min()
        close_max = data['MACD'].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        line_legend = 'MACD('+str(defualt_parm)+') '+str(round(data['MACD'][-1],2))+', '+str(round(data['Signal'][-1],2))+', '+str(round(data['Hist'][-1],2))
        axis.plot(data['MACD'],lw=macd_ls,alpha=0.75,color=macd_lc,linestyle=macd_lt)
        axis.plot(data['Signal'],lw=signal_ls,alpha=0.75,color=signal_lc,linestyle=signal_lt)
        axis.plot(data['Hist'],lw=hist_ls,alpha=0.75,color=hist_lc,linestyle=hist_lt,label=line_legend)
        canv.draw()

        et = time.time()
        print 'tc_macd', et-st

    def tc_macdhist(self,data,defualt_parm,graph_num):
        st = time.time()

        axis, canv = self.tc_indicator_graph(graph_num)

        emadays1 = int(defualt_parm.split(',')[0])
        emadays2 = int(defualt_parm.split(',')[1])
        emadays3 = int(defualt_parm.split(',')[2])

        hist_ls = int(self.tc_hist_ls.text())
        hist_lc = self.tc_hist_lc.palette().button().color()
        hist_lc = str(hist_lc.name())
        hist_lt = str(self.tc_hist_lt.currentText()).lower()

        ema1 = pd.ewma(data['Close'],span=emadays1)
        ema2 = pd.ewma(data['Close'],span=emadays2)

        data['MACD'] = ema1 - ema2
        data['Signal'] = pd.ewma(data['MACD'],span=emadays3)
        data['Hist'] = data['MACD'] - data['Signal']

        #center the line in middle of graph
        close_min = data['Hist'].min()
        close_max = data['Hist'].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        line_legend = 'MACD Hist('+str(defualt_parm)+') '+str(round(data['Hist'][-1],2))
        axis.plot(data['Hist'],lw=hist_ls,alpha=0.75,color=hist_lc,linestyle=hist_lt,label=line_legend)
        canv.draw()

        et = time.time()
        print 'tc_macdhist', et-st

    #Technical chart colors
    def tc_linecolor_edit(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_linecolor.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_upcolor_edit(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_linecolor_up.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_downcolor_edit(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_linecolor_down.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_backgroundcolor_edit(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_backgroundcolor.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_textcolor_edit(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_textcolor.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_gridcolor_edit(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_gridcolor.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_bbupper_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_bbupper_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_bbmiddle_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_bbmiddle_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_bblower_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_bblower_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_kcupper_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_kcupper_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_kcmiddle_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_kcmiddle_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_kclower_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_kclower_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_ema_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_ema_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_chexit_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_chexit_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_pcupper_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_pcupper_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_pcmiddle_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_pcmiddle_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_pclower_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_pclower_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_smaeupper_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_smaeupper_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_smaelower_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_smaelower_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_emaeupper_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_emaeupper_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_emaelower_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_emaelower_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_price_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_price_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_accdist_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_accdist_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_atr_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_atr_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_bollwidth_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_bollwidth_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_bollb_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_bollb_ls.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_macd_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_macd_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_macdsignal_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_signal_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_macdhist_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_hist_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def tc_histmacd_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_macdhist_lc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def cs_hist_textcolor(self):
        color = QtGui.QColorDialog.getColor()
        self.cs_hist_tc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    def cs_hist_backgroundcolor(self):
        color = QtGui.QColorDialog.getColor()
        self.cs_hist_bc.setStyleSheet("QWidget { background-color: %s}" % color.name())

    #Sector Summary

    def sectors_summary(self):
        st = time.time()
        data = self.get_todays_data()

        self.ss_chart_axis.clear()
        var = str(self.ss_variable.currentText())
        var_data = data.iloc[:,data.columns.get_level_values(2)==var]
        var_data.columns = var_data.columns.droplevel(level=2)
        var_data.dropna()

        sectors = list(set(var_data.columns.get_level_values(0)))

        values = [round(var_data[s].mean(axis=1)[0]*100,5) for s in sectors]
        color = ['green' if x > 0 else 'red' for x in values]
        divider = [0.005 for i in range(len(values))]
        absval = [abs(x) for x in values]
        self.ss_chart_axis.pie(absval,labels=sectors,colors=color,explode=divider,autopct='%1.1f%%',textprops={'color':'white'})

        self.ss_chart_canvas.draw()
        et = time.time()
        print 'sectors_summary',et-st

    def ss_basicind(self):
        st = time.time()
        data = self.get_todays_data()

        self.ss_chart_axis.clear()
        var = str(self.ss_variable.currentText())
        var_data = data.iloc[:,data.columns.get_level_values(2)==var]
        var_data.columns = var_data.columns.droplevel(level=2)
        var_data.dropna()

        sectors = list(set(var_data.columns.get_level_values(0)))

        values = [round(var_data[s].mean(axis=1)[0]*100,5) for s in sectors]
        color = ['green' if x > 0 else 'red' for x in values]
        divider = [0.005 for i in range(len(values))]
        absval = [abs(x) for x in values]
        self.ss_chart_axis.pie(absval,labels=sectors,colors=color,explode=divider,autopct='%1.1f%%',textprops={'color':'white'})
        self.ss_chart_canvas.draw()
        et = time.time()
        print 'sectors_summary',et-st

if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet('QMainWindow{background-color: black;border: 1px solid black;}')
    main = Main()

    main.show()
    sys.exit(app.exec_())









