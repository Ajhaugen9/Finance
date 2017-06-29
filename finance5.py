from PyQt4.uic import loadUiType
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas,NavigationToolbar2QT as NavigationToolbar)
import matplotlib.gridspec as gridspec
from matplotlib.widgets import *
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc, candlestick2_ohlc
from matplotlib.ticker import LinearLocator, MaxNLocator
from matplotlib.dates import AutoDateLocator, HourLocator, MonthLocator, WeekdayLocator
import numpy as np
from matplotlib.dates import date2num
from matplotlib.finance import candlestick_ohlc


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

####To do list#####
# 1. moving avg are being called but not plotted. mot being removed on edit page
# 2. volume need to be a bar graph or histogram
# 3. candlesticks




#import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
#import datetime as datetime
#import numpy as np
#import pandas as pd
#import matplotlib.dates as mdates
#from matplotlib.finance import candlestick_ohlc, candlestick2_ohlc
#all_stocks = pd.read_csv('all_stocks.csv',header=[0,1],index_col=0)
#all_stocks.index = all_stocks.index.to_datetime()
#quotes = all_stocks['AAPL'][-67:-1]
#quotes = quotes.reset_index()
#quotes = quotes[["index","Open","High",'Low',"Close"]]
#quotes['index'] = quotes['index'].map(mdates.date2num)
#fig, ax = plt.subplots()
#candlestick2_ohlc(ax,quotes['Open'],quotes['High'],quotes['Low'],quotes['Close'],width=1.0, colorup='green', colordown='red',alpha=0.75)
#plt.show()

years = YearLocator()   # every year
months = MonthLocator()  # every month
yearsFmt = DateFormatter('%Y')

start = datetime.date(1975,1,1)
end = datetime.date.today()

stock_list = pd.read_csv('stocklist.csv',header=0)
basic_data = pd.read_csv('basic_industries.csv',header=[0,1],index_col=0)
basic_data.index = basic_data.index.to_datetime()
capgood_data = pd.read_csv('capital_goods.csv',header=[0,1],index_col=0)
capgood_data.index = capgood_data.index.to_datetime()
condur_data = pd.read_csv('consumer_durables.csv',header=[0,1],index_col=0)
condur_data.index = condur_data.index.to_datetime()
nondur_data = pd.read_csv('consumer_nondurable.csv',header=[0,1],index_col=0)
nondur_data.index = nondur_data.index.to_datetime()
conserve_data = pd.read_csv('consumer_service.csv',header=[0,1],index_col=0)
conserve_data.index = conserve_data.index.to_datetime()
energy_data = pd.read_csv('energy.csv',header=[0,1],index_col=0)
energy_data.index = energy_data.index.to_datetime()
finance_data = pd.read_csv('finance.csv',header=[0,1],index_col=0)
finance_data.index = finance_data.index.to_datetime()
health_data = pd.read_csv('health_care.csv',header=[0,1],index_col=0)
health_data.index = health_data.index.to_datetime()
misc_data = pd.read_csv('miscellaneous.csv',header=[0,1],index_col=0)
misc_data.index = misc_data.index.to_datetime()
tech_data = pd.read_csv('technology.csv',header=[0,1],index_col=0)
tech_data.index = tech_data.index.to_datetime()
trans_data = pd.read_csv('transportation.csv',header=[0,1],index_col=0)
trans_data.index = trans_data.index.to_datetime()
utility_data = pd.read_csv('utilities.csv',header=[0,1],index_col=0)
utility_data.index = utility_data.index.to_datetime()


#all_stocks = pd.read_csv('allstocks.csv',header=[0,1],index_col=0)
#all_stocks.index = all_stocks.index.to_datetime()

d = basic_data.index.to_datetime()
date_e = d[-1].to_pydatetime()
year = date_e.year
month = date_e.month
day = date_e.day
print year, month, day
import time



Ui_MainWindow, QMainWindow = loadUiType('Finance_temp.ui')
class Main(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(Main, self).__init__(parent)
        self.setupUi(self)   
        
        #self.mdiArea.addSubWindow(self.market_summary)
        self.mdiArea.addSubWindow(self.tech_chart)
        #self.mdiArea.addSubWindow(self.market_summary)
        #self.mdiArea.addSubWindow(self.sector_summary)
        self.mdiArea.addSubWindow(self.companysummary)
        self.mdiArea.addSubWindow(self.financials_window)


        #Set up technical chart
        '''Sets up the main tech charts'''

        gs1 = gridspec.GridSpec(4, 1)
        gs1.update(left=0.01, right=0.95, top=.98, bottom=0.03,wspace=0,hspace=0)
        self.tech_chart_fig = Figure(facecolor='#191919') 
        self.tech_chart_canvas = FigureCanvas(self.tech_chart_fig)
        self.techchart_layout.addWidget(self.tech_chart_canvas)  
        self.tech_chart_axis = self.tech_chart_fig.add_subplot(gs1[:, :],axisbg='#191919') 
        self.tc_main_search.setText('AAPL')
        self.tc_sec_search1.setText('AAPL')

        gs2 = gridspec.GridSpec(4, 1)
        gs2.update(left=0.01, right=0.95, top=1.0, bottom=0.09,wspace=0,hspace=0)
        self.tech_chart_fig2 = Figure(facecolor='#191919') 
        self.tech_chart_canvas2 = FigureCanvas(self.tech_chart_fig2)
        self.techchart_layout2.addWidget(self.tech_chart_canvas2)  
        self.tech_chart_axis2 = self.tech_chart_fig2.add_subplot(gs2[:, :],axisbg='#191919') 

        gs3 = gridspec.GridSpec(4, 1)
        gs3.update(left=0.01, right=0.95, top=.98, bottom=0.035,wspace=0,hspace=0)
        self.tech_chart_fig3 = Figure(facecolor='#191919') 
        self.tech_chart_canvas3 = FigureCanvas(self.tech_chart_fig3)
        self.techchart_layout3.addWidget(self.tech_chart_canvas3)  
        self.tech_chart_axis3 = self.tech_chart_fig3.add_subplot(gs3[:, :],axisbg='#191919') 

        gs4 = gridspec.GridSpec(4, 1)
        gs4.update(left=0.00, right=0.925, top=1.00, bottom=0.0675,wspace=0,hspace=0)
        self.cs_chart_fig = Figure(facecolor='#323232') 
        self.cs_chart_canvas = FigureCanvas(self.cs_chart_fig)
        self.cs_chart_layout.addWidget(self.cs_chart_canvas)  
        self.cs_chart_axis = self.cs_chart_fig.add_subplot(gs4[:, :],axisbg='#323232') 

        gs5 = gridspec.GridSpec(4, 1)
        gs5.update(left=0.00, right=0.925, top=1.00, bottom=0.0675,wspace=0,hspace=0)
        self.ss_pie_fig = Figure(facecolor='#323232') 
        self.ss_pie_canvas = FigureCanvas(self.ss_pie_fig)
        self.ss_pie_layout.addWidget(self.ss_pie_canvas)  
        self.ss_pie_axis = self.ss_pie_fig.add_subplot(gs5[:, :],axisbg='#323232') 

        #Tech Chart Search
        '''Main search bar in tech chart. when you press enter it calls the main search function'''
        self.tc_main_search.returnPressed.connect(self.tc_search1)
        self.tc_sec_search1.returnPressed.connect(self.tc_search2)
        self.tc_sec_search2.returnPressed.connect(self.tc_search3)

        #Tech chart tab buttons
        '''Makes sure the side panel is hidden but if you press the button itll call tab 
           button function to open it'''
        self.tc_secstudy_tab.setMaximumWidth(0)
        self.tc_secstudy_tab.setMinimumWidth(0)
        self.tc_secstudy_bt.clicked.connect(self.tc_tab_buttons) #opens up side panel

        #Tech Chart Sec/Study
        '''When the side panel is open and you change a filter box it will call sec study 
           id the edit buttons are pressed it will call edit function. if you press add 
           study it will call that function and add another row of filters'''
        self.study_filter1.currentIndexChanged.connect(self.tc_study1)
        self.study_filter2.currentIndexChanged.connect(self.tc_study2)
        #self.study_filter3.currentIndexChanged.connect(self.tc_secstudy)
        self.tc_movavg.returnPressed.connect(self.tc_movingavg)
        self.tc_movavg2.returnPressed.connect(self.tc_movingavg)
        self.tc_movavg3.returnPressed.connect(self.tc_movingavg)
        self.tc_addstudy1_bt.clicked.connect(self.tc_addstudy)
        #self.study_edit1.clicked.connect(self.tc_study_edit)

        #Tech Chart Edit
        '''Makes sure the chart is visible and not the edit page. if you press edit it will change 
           the widgets index and show the edit page, the update and cancel buttons close it'''

        '''pre-sets the first line in the edit page which will is used to plot this default'''
        self.techchart_widget.setCurrentIndex(0)
        self.tc_chartedit_panel.setCurrentIndex(1)
        self.tc_chartedit_symbol.setText('AAPL')
        self.tc_chartedit_series.setText('Close')
        self.tc_chartedit_line.setCurrentIndex(0)
        self.tc_chartedit_size.setText('5')
        self.tc_chartedit_color.setStyleSheet('background-color: rgb(87, 188, 255);')
        self.tc_edit_bt.clicked.connect(self.tc_edit) #opens edit page
        self.tc_edit_update.clicked.connect(self.tc_chartedit_update) #update edit page
        self.tc_edit_cancel.clicked.connect(self.tc_chartedit_cancel)
        '''hides all other lines on edit page so the default above is the only one shown'''
        self.tc_edit_cancel.clicked.connect(self.tc_edit)
        signals = [self.tc_chartedit_panel_2,self.tc_chartedit_panel_3,
                   self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6,
                   self.tc_chartedit_symbol_2,self.tc_chartedit_symbol_3,
                   self.tc_chartedit_symbol_4,self.tc_chartedit_symbol_5,self.tc_chartedit_symbol_6,
                   self.tc_chartedit_series_2,self.tc_chartedit_series_3,
                   self.tc_chartedit_series_4,self.tc_chartedit_series_5,self.tc_chartedit_series_6,
                   self.tc_chartedit_line_2,self.tc_chartedit_line_3,
                   self.tc_chartedit_line_4,self.tc_chartedit_line_5,self.tc_chartedit_line_6,
                   self.tc_chartedit_size_2,self.tc_chartedit_size_3,
                   self.tc_chartedit_size_4,self.tc_chartedit_size_5,self.tc_chartedit_size_6,
                   self.tc_chartedit_color_2,self.tc_chartedit_color_3,
                   self.tc_chartedit_color_4,self.tc_chartedit_color_5,self.tc_chartedit_color_6,
                   self.tc_chartedit_hilow_2,self.tc_chartedit_hilow_3,
                   self.tc_chartedit_hilow_4,self.tc_chartedit_hilow_5,self.tc_chartedit_hilow_6,
                   self.tc_chartedit_color_4,self.tc_chartedit_color_5,self.tc_chartedit_color_6,
                   self.tc_chartedit_style_2,self.tc_chartedit_style_3,
                   self.tc_chartedit_style_4,self.tc_chartedit_style_5,self.tc_chartedit_style_6]
        for s in signals:            
            s.setMaximumHeight(0)
            s.setMinimumHeight(0)
        self.tc_bottomedit.setCurrentIndex(0)
        self.tc_chartedit_color.clicked.connect(self.tc_color_edit) #opens the qt color picker
        self.tc_chartedit_color_2.clicked.connect(self.tc_color_edit2)
        self.tc_chartedit_color_3.clicked.connect(self.tc_color_edit3)
        self.tc_chartedit_color_4.clicked.connect(self.tc_color_edit4)
        self.tc_bgcolor.clicked.connect(self.tc_bg_color)
        #self.tc_rgb_red.valueChanged.connect(self.tc_rgb_edit)
        #self.tc_rgb_green.valueChanged.connect(self.tc_rgb_edit)
        #self.tc_rgb_blue.valueChanged.connect(self.tc_rgb_edit)

        #Technical chart date change
        self.tc_date_to.setDate(QtCore.QDate(year,month,day))
        self.tc_date_from.setDate(QtCore.QDate(year-1,month,day))
        self.tc_date_to.dateChanged.connect(self.tc_chartedit_update)
        self.tc_date_from.dateChanged.connect(self.tc_chartedit_update)
        to_year = self.tc_date_to.date().year()
        print 'a', to_year

        #Technical chart date buttons
        date_buttons = [self.tc_one_day,self.tc_five_day,self.tc_one_month,self.tc_three_month, self.tc_six_month,
                        self.tc_one_year,self.tc_five_year,self.tc_max_date]
        for b in date_buttons:
            b.clicked.connect(self.tc_date_buttons)

        #Market Summary
        self.ms_gainer_filter.currentIndexChanged.connect(self.ms_gainers_loser)

        #Fiancials Window
        self.is_rb_1.clicked.connect(self.financial_window)
        self.is_rb_2.clicked.connect(self.financial_window)
        self.is_rb_3.clicked.connect(self.financial_window)
        self.is_rb_4.clicked.connect(self.financial_window)
        self.is_rb_5.clicked.connect(self.financial_window)
        self.is_rb_6.clicked.connect(self.financial_window)
        self.is_rb_7.clicked.connect(self.financial_window)
        self.is_rb_8.clicked.connect(self.financial_window)
        self.is_rb_9.clicked.connect(self.financial_window)
        self.is_rb_10.clicked.connect(self.financial_window)
        self.is_rb_11.clicked.connect(self.financial_window)
        self.is_rb_12.clicked.connect(self.financial_window)
        self.is_rb_13.clicked.connect(self.financial_window)

        
        #start functions
        self.tc_mainsearch() #clears all graph data and plots just the default data
        self.ms_gainers_loser()
        self.company_summary()
        self.financial_window()

    def tc_search1(self):
        '''called when the top search bar is used. when a new str is entered it updates the 
           first line of the eddit page'''
        symbol = str(self.tc_main_search.text())
        self.tc_sec_search1.setText(symbol)
        self.techchart_widget.setCurrentIndex(0)
        self.tc_chartedit_panel.setCurrentIndex(1)
        self.tc_chartedit_symbol.setText(symbol)
        self.tc_chartedit_series.setText('Close')
        self.tc_chartedit_line.setCurrentIndex(0)
        self.tc_chartedit_size.setText('5')
        self.tc_chartedit_color.setStyleSheet('background-color: rgb(87, 188, 255);')
        self.tc_chartedit_style.setCurrentIndex(0)

        hidepan =  [self.tc_chartedit_panel_2,self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6,
                    self.tc_chartedit_symbol_2,self.tc_chartedit_symbol_3,self.tc_chartedit_symbol_4,self.tc_chartedit_symbol_5,self.tc_chartedit_symbol_6,
                    self.tc_chartedit_series_2,self.tc_chartedit_series_3,self.tc_chartedit_series_4,self.tc_chartedit_series_5,self.tc_chartedit_series_6,
                    self.tc_chartedit_line_2,self.tc_chartedit_line_3,self.tc_chartedit_line_4,self.tc_chartedit_line_5,self.tc_chartedit_line_6,
                    self.tc_chartedit_size_2,self.tc_chartedit_size_3,self.tc_chartedit_size_4,self.tc_chartedit_size_5,self.tc_chartedit_size_6,
                    self.tc_chartedit_color_2,self.tc_chartedit_color_3,self.tc_chartedit_color_4,self.tc_chartedit_color_5,self.tc_chartedit_color_6,
                    self.tc_chartedit_style_2,self.tc_chartedit_style_3,self.tc_chartedit_style_4,self.tc_chartedit_style_5,self.tc_chartedit_style_6,
                    self.tc_chartedit_hilow_2,self.tc_chartedit_hilow_3,self.tc_chartedit_hilow_4,self.tc_chartedit_hilow_5,self.tc_chartedit_hilow_6]
        for h in hidepan:
            h.setMaximumHeight(0)
            h.setMinimumHeight(0)
            
        panels =  [self.tc_chartedit_panel_2,self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6]
        for p in panels:
            p.setCurrentIndex(0)
        self.tc_mainsearch() ###

    def tc_search2(self):
        ##same as tc_search1 but need to add more##
        '''called when the side panel search bar is used'''
        symbol = str(self.tc_sec_search1.text())
        self.techchart_widget.setCurrentIndex(0)
        self.tc_chartedit_panel.setCurrentIndex(1)
        self.tc_chartedit_symbol.setText(symbol)
        self.tc_chartedit_series.setText('Close')
        self.tc_chartedit_line.setCurrentIndex(0)
        self.tc_chartedit_size.setText('5')
        self.tc_chartedit_color.setStyleSheet('background-color: rgb(87, 188, 255);')
        self.tc_main_search.setText(symbol)
        self.tc_chartedit_style.setCurrentIndex(0)

        hidepan =  [self.tc_chartedit_panel_2,self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6,
                    self.tc_chartedit_symbol_2,self.tc_chartedit_symbol_3,self.tc_chartedit_symbol_4,self.tc_chartedit_symbol_5,self.tc_chartedit_symbol_6,
                    self.tc_chartedit_series_2,self.tc_chartedit_series_3,self.tc_chartedit_series_4,self.tc_chartedit_series_5,self.tc_chartedit_series_6,
                    self.tc_chartedit_line_2,self.tc_chartedit_line_3,self.tc_chartedit_line_4,self.tc_chartedit_line_5,self.tc_chartedit_line_6,
                    self.tc_chartedit_size_2,self.tc_chartedit_size_3,self.tc_chartedit_size_4,self.tc_chartedit_size_5,self.tc_chartedit_size_6,
                    self.tc_chartedit_color_2,self.tc_chartedit_color_3,self.tc_chartedit_color_4,self.tc_chartedit_color_5,self.tc_chartedit_color_6,
                    self.tc_chartedit_style_2,self.tc_chartedit_style_3,self.tc_chartedit_style_4,self.tc_chartedit_style_5,self.tc_chartedit_style_6,
                    self.tc_chartedit_hilow_2,self.tc_chartedit_hilow_3,self.tc_chartedit_hilow_4,self.tc_chartedit_hilow_5,self.tc_chartedit_hilow_6]
        for h in hidepan:
            h.setMaximumHeight(0)
            h.setMinimumHeight(0)
            
        panels =  [self.tc_chartedit_panel_2,self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6]
        for p in panels:
            p.setCurrentIndex(0)
        self.tc_mainsearch()

    def tc_search3(self):
        symbol1 = str(self.tc_sec_search1.text())
        self.techchart_widget.setCurrentIndex(0)
        self.tc_chartedit_panel.setCurrentIndex(1)
        self.tc_chartedit_symbol.setText(symbol1)
        self.tc_chartedit_series.setText('Close')
        self.tc_chartedit_line.setCurrentIndex(0)
        self.tc_chartedit_size.setText('5')
        self.tc_chartedit_color.setStyleSheet('background-color: rgb(87, 188, 255);')
        self.tc_chartedit_style.setCurrentIndex(0)

        symbol2 = str(self.tc_sec_search2.text())
        self.techchart_widget.setCurrentIndex(0)
        self.tc_chartedit_panel_2.setCurrentIndex(1)
        self.tc_chartedit_symbol_2.setText(symbol2)
        self.tc_chartedit_series_2.setText('Close')
        self.tc_chartedit_line_2.setCurrentIndex(0)
        self.tc_chartedit_size_2.setText('5')
        self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(87, 188, 255);')
        self.tc_chartedit_style_2.setCurrentIndex(0)

        hidepan =  [self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6,
                    self.tc_chartedit_symbol_3,self.tc_chartedit_symbol_4,self.tc_chartedit_symbol_5,self.tc_chartedit_symbol_6,
                    self.tc_chartedit_series_3,self.tc_chartedit_series_4,self.tc_chartedit_series_5,self.tc_chartedit_series_6,
                    self.tc_chartedit_line_3,self.tc_chartedit_line_4,self.tc_chartedit_line_5,self.tc_chartedit_line_6,
                    self.tc_chartedit_size_3,self.tc_chartedit_size_4,self.tc_chartedit_size_5,self.tc_chartedit_size_6,
                    self.tc_chartedit_color_3,self.tc_chartedit_color_4,self.tc_chartedit_color_5,self.tc_chartedit_color_6,
                    self.tc_chartedit_style_3,self.tc_chartedit_style_4,self.tc_chartedit_style_5,self.tc_chartedit_style_6,
                    self.tc_chartedit_hilow_3,self.tc_chartedit_hilow_4,self.tc_chartedit_hilow_5,self.tc_chartedit_hilow_6]
        for h in hidepan:
            h.setMaximumHeight(0)
            h.setMinimumHeight(0)

        keep = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
        for k in keep:
            k.setMaximumHeight(60)
            k.setMinimumHeight(60)
            
        panels =  [self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6]
        for p in panels:
            p.setCurrentIndex(0)
        self.tc_compare()

    def tc_compare(self):
        st = time.time()
        symbol1 = str(self.tc_chartedit_symbol.text())
        symbol2 = str(self.tc_chartedit_symbol_2.text())
        data1 = self.get_symbol_data(symbol1)
        data2 = self.get_symbol_data(symbol2)

        #Gets the dates from the QtdateEdits
        from_year = self.tc_date_from.date().year()
        from_month = self.tc_date_from.date().month()
        from_day = self.tc_date_from.date().day()
        to_year = self.tc_date_to.date().year()
        to_month = self.tc_date_to.date().month()
        to_day = self.tc_date_to.date().day()

        self.tech_chart_axis.set_xlim([datetime.datetime(from_year,from_month,from_day,9,0,0),datetime.datetime(to_year,to_month,to_day-1,17,0,0)])

        #Format the QtdateEdit to us in index
        from_ = datetime.datetime(from_year,from_month,from_day)
        to_ = datetime.datetime(to_year,to_month,to_day)
            
        from_index = from_.strftime('%Y-%m-%d')
        to_index = to_.strftime('%Y-%m-%d')


        self.tech_chart_axis.clear()
        self.tech_chart_axis.grid(True, which='major', color='w', linestyle='--')  
        self.tech_chart_axis.yaxis.label.set_color("w")
        self.tech_chart_axis.xaxis.label.set_color('w')
        self.tech_chart_axis.spines['bottom'].set_color("w")
        self.tech_chart_axis.spines['top'].set_color("#323232")
        self.tech_chart_axis.spines['left'].set_color("#323232")
        self.tech_chart_axis.spines['right'].set_color("w")
        self.tech_chart_axis.tick_params(axis='y', colors='w',labelsize=20)
        self.tech_chart_axis.tick_params(axis='x', colors='w',labelsize=20)
        self.tech_chart_axis.yaxis.set_major_locator(LinearLocator(10))
        self.tech_chart_axis.xaxis.set_major_locator(LinearLocator(10))
        self.tech_chart_fig.set_tight_layout(tight=True)
        self.tech_chart_axis.plot(data1['Close'],lw=5,alpha=0.75,color='grey',linestyle='-')
        
        self.tech_chart_axis_c = self.tech_chart_axis.twinx()   
        self.tech_chart_axis_c.spines['right'].set_color("w")
        self.tech_chart_axis_c.plot(data2['Close'],lw=5,alpha=0.75,color='orange',linestyle='-')
        self.tech_chart_axis_c.yaxis.tick_right()
        self.tech_chart_axis.yaxis.tick_right()

        #sets the graph so the highest and lowest point on the line is 10% away from the edge
        min1 = data1['Close'].loc[from_index:to_index].min()
        max1 = data1['Close'].loc[from_index:to_index].max()
        close_diff1 = float(max1 - min1)
        ax1_min1 = float(min1 - (close_diff1*0.10))
        ax1_max1 = float(max1 + (close_diff1*0.10))
        self.tech_chart_axis.set_ylim([round(ax1_min1,2),round(ax1_max1,2)])

        min2 = data2['Close'].loc[from_index:to_index].min()
        max2 = data2['Close'].loc[from_index:to_index].max()
        close_diff2 = float(max1 - min1)
        ax1_min2 = float(min2 - (close_diff2*0.10))
        ax1_max2 = float(max2 + (close_diff2*0.10))
        self.tech_chart_axis_c.set_ylim([round(ax1_min2,2),round(ax1_max2,2)])


        self.tech_chart_canvas.draw()

        et = time.time()
        print 'tc_compare ', et-st

    def tc_mainsearch(self):
        st = time.time()
        '''Fisrt function to be called. sets up the main charts axis and grid then plots 
           the most recent years stock prices of a default company. Called whenever the 
           tech chart main search is used and deletes lines on edit page, and study tab'''
        panels = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                    self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2]
        for p in panels:
            p.setMaximumHeight(0)
            p.setMinimumHeight(0)

        self.tc_chartedit_panel_2.setCurrentIndex(0)
        self.tc_chartedit_symbol_2.setText('')
        self.tc_chartedit_series_2.setText(''),
        self.tc_chartedit_line_2.setCurrentIndex(0)
        self.tc_chartedit_size_2.setText('')
        
        #hides the other filters
        self.study_edit2.setMinimumHeight(0)
        self.study_edit2.setMaximumHeight(0)
        self.study_filter2.setMinimumHeight(0)
        self.study_filter2.setMaximumHeight(0)
        self.study_line1.setMinimumHeight(0)
        self.study_line1.setMaximumHeight(0)
        self.study_edit3.setMinimumHeight(0)
        self.study_edit3.setMaximumHeight(0)
        self.study_filter3.setMinimumHeight(0)
        self.study_filter3.setMaximumHeight(0)
        self.study_line2.setMinimumHeight(0)
        self.study_line2.setMaximumHeight(0)

        self.study_filter1.setCurrentIndex(0)
        self.study_filter2.setCurrentIndex(0)
        self.study_filter3.setCurrentIndex(0)
        try:
            self.tc_gragh_layout.removeWidget(self.techchart_widget2)
            self.tc_gragh_layout.removeWidget(self.techchart_widget2)
        except:
            self.techchart_widget2.setMaximumHeight(0)
            self.techchart_widget2.setMinimumHeight(0)
            self.techchart_widget3.setMaximumHeight(0)
            self.techchart_widget3.setMinimumHeight(0)

        #set up the grid line, colors, layout
        self.tech_chart_axis.clear()
        self.tech_chart_axis.grid(True, which='major', color='w', linestyle='--')  
        self.tech_chart_axis.yaxis.label.set_color("w")
        self.tech_chart_axis.xaxis.label.set_color('w')
        self.tech_chart_axis.spines['bottom'].set_color("w")
        self.tech_chart_axis.spines['top'].set_color("#191919")
        self.tech_chart_axis.spines['left'].set_color("#191919")
        self.tech_chart_axis.spines['right'].set_color("w")
        self.tech_chart_axis.tick_params(axis='y', colors='w',labelsize=20)
        self.tech_chart_axis.tick_params(axis='x', colors='w',labelsize=20)
        self.tech_chart_axis.yaxis.set_major_locator(LinearLocator(10))
        self.tech_chart_axis.xaxis.set_major_locator(LinearLocator(12))
        self.tech_chart_fig.set_tight_layout(tight=True)
        self.tech_chart_axis.yaxis.tick_right()

        #Gets the dates from the QtdateEdits
        from_year = self.tc_date_from.date().year()
        from_month = self.tc_date_from.date().month()
        from_day = self.tc_date_from.date().day()
        to_year = self.tc_date_to.date().year()
        to_month = self.tc_date_to.date().month()
        to_day = self.tc_date_to.date().day()

        self.tech_chart_axis.set_xlim([datetime.datetime(from_year,from_month,from_day,9,0,0),datetime.datetime(to_year,to_month,to_day-1,17,0,0)])

        #Format the QtdateEdit to us in index
        from_ = datetime.datetime(from_year,from_month,from_day)
        to_ = datetime.datetime(to_year,to_month,to_day)

        cal = USFederalHolidayCalendar()
        holidays = cal.holidays().to_pydatetime()
        if from_.strftime('%A') == 'Saturday':
            from_ = datetime.datetime(from_year,from_month,from_day+2)
        elif from_.strftime('%A') == 'Sunday':
            from_ = datetime.datetime(from_year,from_month,from_day+1)
        elif from_ in holidays:
            from_ = datetime.datetime(from_year,from_month,from_day+1)
        elif to_.strftime('%A') == 'Saturday':
            to_ = datetime.datetime(from_year,from_month,from_day-1)
        elif to_.strftime('%A') == 'Sunday':
            to_ = datetime.datetime(from_year,from_month,from_day-2)
        elif to_ in holidays:
            to_ = datetime.datetime(from_year,from_month,from_day+1)
            
        from_index = from_.strftime('%Y-%m-%d')
        to_index = to_.strftime('%Y-%m-%d')

        symbol = str(self.tc_main_search.text())
        data = self.get_symbol_data(symbol)

        '''still need to add candlestick'''
        self.tech_chart_axis.plot(data['Close'],lw=5,alpha=0.75,color='#57bcff',linestyle='-')
        #candlestick2_ohlc(self.tech_chart_axis,data['Open'],data['High'],data['Low'],data['Close'])
        #candlestick_ohlc(self.tech_chart_axis,data[['Open','High','Low','Close','Volume']])

        #sets the graph so the highest and lowest point on the line is 10% away from the edge
        close_min = data['Close'].loc[from_index:to_index].min()
        close_max = data['Close'].loc[from_index:to_index].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])

        self.tech_chart_canvas.draw()
        et = time.time()
        print 'tc_mainsearch', et-st

        name = stock_list.loc[stock_list['Symbol']==symbol,'Name']
        name = list(name)
        self.tc_legend_name.setText(str(name[0])+' ('+symbol+')')
        self.tc_legend_price.setText(str(round(data['Close'][-1],2)))
        self.tc_legend_change.setText(str(round(data['Change'][-1],2))+' '+str(round(data['% Change'][-1],3))+'%')
        self.tc_legend_prevclose.setText(str(round(data['Close'][-2],2)))
        self.tc_legend_open.setText(str(round(data['Open'][-1],2)))
        self.tc_legend_high.setText(str(round(data['High'][-1],2)))
        self.tc_legend_low.setText(str(round(data['Low'][-1],2)))
        #Time: 0.95

    def tc_study1(self):
        st = time.time()
        '''called when the first filter changes takes the new filter and updates the edit page'''
        if self.study_filter1.currentText() == 'Close':
            self.techchart_widget.setCurrentIndex(0)
            self.tc_chartedit_panel.setCurrentIndex(1)
            self.tc_chartedit_symbol.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series.setText('Close')
            self.tc_chartedit_line.setCurrentIndex(0)
            self.tc_chartedit_size.setText('5')
            self.tc_chartedit_color.setStyleSheet('background-color: rgb(87, 188, 255);')
            self.tc_chartedit_style.setCurrentIndex(0)
        elif self.study_filter1.currentText() == 'Volume':
            self.techchart_widget.setCurrentIndex(0)

            self.study_edit2.setMinimumHeight(35)
            self.study_edit2.setMaximumHeight(35)
            self.study_filter2.setMinimumHeight(50)
            self.study_filter2.setMaximumHeight(50)
            self.study_line1.setMinimumHeight(5)
            self.study_line1.setMaximumHeight(5)

            self.study_filter2.setCurrentIndex(2)
            self.study_filter1.setCurrentIndex(0)

            self.tc_chartedit_panel.setCurrentIndex(1)
            self.tc_chartedit_symbol.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series.setText('Close')
            self.tc_chartedit_line.setCurrentIndex(0)
            self.tc_chartedit_size.setText('5')
            self.tc_chartedit_color.setStyleSheet('background-color: rgb(87, 188, 255);')
            self.tc_chartedit_style.setCurrentIndex(0)

            panels = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                      self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2]
            for p in panels:
                p.setMaximumHeight(60)
                p.setMinimumHeight(60)

            self.tc_chartedit_panel_2.setCurrentIndex(2)
            self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_2.setText('Volume')
            self.tc_chartedit_line_2.setCurrentIndex(1)
            self.tc_chartedit_size_2.setText('5')
            self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(87, 188, 255);')
            self.tc_chartedit_style_2.setCurrentIndex(0)
        et = time.time()
        print 'tc_study1 ', et-st

        self.tc_editline1()
        self.tc_editline2()

    def tc_study2(self):
        '''called when the second filter changes. the change in the filter causes the edit page to add and updates lines
           then calls tc_editlines which is what calls the plot functions '''
        st = time.time()
        if self.study_filter2.currentText() == 'Close':
            self.techchart_widget.setCurrentIndex(0)
            self.tc_chartedit_panel_2.setCurrentIndex(2)
            self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_2.setText('Close')
            self.tc_chartedit_line_2.setCurrentIndex(1)
            self.tc_chartedit_size_2.setText('5')
            self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(87, 188, 255);')
            self.tc_chartedit_style_2.setCurrentIndex(0)

        elif self.study_filter2.currentText() == 'Volume':
            self.tc_main_search.setText(self.tc_chartedit_symbol.text())
            self.tc_sec_search1.setText(self.tc_chartedit_symbol.text())

            #hides other edit lines
            hidepan =  [self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6,
                        self.tc_chartedit_symbol_3,self.tc_chartedit_symbol_4,self.tc_chartedit_symbol_5,self.tc_chartedit_symbol_6,
                        self.tc_chartedit_series_3,self.tc_chartedit_series_4,self.tc_chartedit_series_5,self.tc_chartedit_series_6,
                        self.tc_chartedit_line_3,self.tc_chartedit_line_4,self.tc_chartedit_line_5,self.tc_chartedit_line_6,
                        self.tc_chartedit_size_3,self.tc_chartedit_size_4,self.tc_chartedit_size_5,self.tc_chartedit_size_6,
                        self.tc_chartedit_color_3,self.tc_chartedit_color_4,self.tc_chartedit_color_5,self.tc_chartedit_color_6,
                        self.tc_chartedit_style_3,self.tc_chartedit_style_4,self.tc_chartedit_style_5,self.tc_chartedit_style_6,
                        self.tc_chartedit_hilow_3,self.tc_chartedit_hilow_4,self.tc_chartedit_hilow_5,self.tc_chartedit_hilow_6]
            for h in hidepan:
                h.setMaximumHeight(0)
                h.setMinimumHeight(0)
            
            #sets the first column of each hidden line to 0 so the tc_lineedit functions doesnt use these lines 
            panels =  [self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6]
            for p in panels:
                p.setCurrentIndex(0)
            
            keep = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                      self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
            for k in keep:
                k.setMaximumHeight(60)
                k.setMinimumHeight(60)

            #Sets the default volume settings for the edit line
            self.techchart_widget.setCurrentIndex(0)
            self.tc_chartedit_panel_2.setCurrentIndex(2)
            self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_2.setText('Volume')
            self.tc_chartedit_line_2.setCurrentIndex(2)
            self.tc_chartedit_size_2.setText('1')
            self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(87, 188, 255);')
            self.tc_chartedit_style_2.setCurrentIndex(1)

        elif self.study_filter2.currentText() == 'Bollinger Bands':
            panels = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,self.tc_chartedit_line_2,
                      self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2,self.tc_chartedit_hilow_2,
                      self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3,self.tc_chartedit_style_3,
                      self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_hilow_3,
                      self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4,self.tc_chartedit_style_4,
                      self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_hilow_4]

            for p in panels:
                p.setMaximumHeight(60)
                p.setMinimumHeight(60)
            self.techchart_widget.setCurrentIndex(0)

            #bollinger bands have 3 lines so we add 3 lines to the edit page
            self.tc_chartedit_panel_2.setCurrentIndex(1)
            self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_2.setText('Upper Band')
            self.tc_chartedit_line_2.setCurrentIndex(1)
            self.tc_chartedit_size_2.setText('3')
            self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(175, 175, 175);')
            self.tc_chartedit_style_2.setCurrentIndex(2)

            self.tc_chartedit_panel_3.setCurrentIndex(1)
            self.tc_chartedit_symbol_3.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_3.setText('Middle Band')
            self.tc_chartedit_line_3.setCurrentIndex(1)
            self.tc_chartedit_size_3.setText('3')
            self.tc_chartedit_color_3.setStyleSheet('background-color: rgb(255, 170, 0);')
            self.tc_chartedit_style_3.setCurrentIndex(1)

            self.tc_chartedit_panel_4.setCurrentIndex(1)
            self.tc_chartedit_symbol_4.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_4.setText('Lower Band')
            self.tc_chartedit_line_4.setCurrentIndex(1)
            self.tc_chartedit_size_4.setText('3')
            self.tc_chartedit_color_4.setStyleSheet('background-color: rgb(255, 255, 255);')
            self.tc_chartedit_style_4.setCurrentIndex(2)

        elif self.study_filter2.currentText() == 'MACD':
            keep = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2, self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2,
                    self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3, self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_style_3,
                    self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4, self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_style_4]
            for k in keep:
                k.setMaximumHeight(60)
                k.setMinimumHeight(60)
            self.tc_chartedit_panel_2.setCurrentIndex(2)
            self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_2.setText('MACD')
            self.tc_chartedit_line_2.setCurrentIndex(1)
            self.tc_chartedit_size_2.setText('3')
            self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(175, 175, 175);')
            self.tc_chartedit_style_2.setCurrentIndex(1)

            self.tc_chartedit_panel_3.setCurrentIndex(2)
            self.tc_chartedit_symbol_3.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_3.setText('Signal Line')
            self.tc_chartedit_line_3.setCurrentIndex(1)
            self.tc_chartedit_size_3.setText('3')
            self.tc_chartedit_color_3.setStyleSheet('background-color: rgb(255, 170, 0);')
            self.tc_chartedit_style_3.setCurrentIndex(1)

            self.tc_chartedit_panel_4.setCurrentIndex(2)
            self.tc_chartedit_symbol_4.setText(str(self.tc_sec_search1.text()))
            self.tc_chartedit_series_4.setText('MACD Histogram')
            self.tc_chartedit_line_4.setCurrentIndex(1)
            self.tc_chartedit_size_4.setText('3')
            self.tc_chartedit_color_4.setStyleSheet('background-color: rgb(255, 255, 255);')
            self.tc_chartedit_style_4.setCurrentIndex(2)
        et = time.time()
        print 'study 2:', et-st
        #Time: 0.001-0.004



        self.tc_editline1()
        self.tc_editline2()
        self.tc_editline3()
        self.tc_editline4()

    def tc_movingavg(self):
        '''needs work'''
        panels =  [self.tc_chartedit_panel_2,self.tc_chartedit_panel_3,self.tc_chartedit_panel_4,self.tc_chartedit_panel_5,self.tc_chartedit_panel_6]
        newline = []
        for p in panels:
            if p.currentIndex() == 0:
                newline.append(panels.index(p))
            else:
                pass
        print 'nl', newline
        if self.tc_movavg.text() != '':
            if newline[0]+2 == 2:
                keep = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                        self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_2.setCurrentIndex(1)
                self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_2.setText('MA '+str(self.tc_movavg.text()))
                self.tc_chartedit_line_2.setCurrentIndex(1)
                self.tc_chartedit_size_2.setText('3')
                self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_2.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_2.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                        self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 3:
                keep = [self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3,
                          self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_style_3]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_3.setCurrentIndex(1)
                self.tc_chartedit_symbol_3.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_3.setText('MA '+str(self.tc_movavg.text()))
                self.tc_chartedit_line_3.setCurrentIndex(1)
                self.tc_chartedit_size_3.setText('3')
                self.tc_chartedit_color_3.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_3.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_3.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3,
                        self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_style_3]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 4:
                keep = [self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4,
                          self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_style_4]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_4.setCurrentIndex(1)
                self.tc_chartedit_symbol_4.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_4.setText('MA '+str(self.tc_movavg.text()))
                self.tc_chartedit_line_4.setCurrentIndex(1)
                self.tc_chartedit_size_4.setText('3')
                self.tc_chartedit_color_4.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_4.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_4.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4,
                        self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_style_4]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 5:
                keep = [self.tc_chartedit_panel_5,self.tc_chartedit_symbol_5,self.tc_chartedit_series_5,
                          self.tc_chartedit_line_5,self.tc_chartedit_size_5,self.tc_chartedit_color_5,self.tc_chartedit_style_5]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_5.setCurrentIndex(1)
                self.tc_chartedit_symbol_5.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_5.setText('MA '+str(self.tc_movavg.text()))
                self.tc_chartedit_line_5.setCurrentIndex(1)
                self.tc_chartedit_size_5.setText('3')
                self.tc_chartedit_color_5.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_5.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_5.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_5,self.tc_chartedit_symbol_5,self.tc_chartedit_series_5,
                        self.tc_chartedit_line_5,self.tc_chartedit_size_5,self.tc_chartedit_color_5,self.tc_chartedit_style_5]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

        elif self.tc_movavg2.text() != '':
            if newline[0]+2 == 2:
                keep = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                          self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_2.setCurrentIndex(1)
                self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_2.setText('MA '+str(self.tc_movavg2.text()))
                self.tc_chartedit_line_2.setCurrentIndex(1)
                self.tc_chartedit_size_2.setText('3')
                self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_2.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_2.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                        self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 3:
                keep = [self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3,
                          self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_style_3]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_3.setCurrentIndex(1)
                self.tc_chartedit_symbol_3.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_3.setText('MA '+str(self.tc_movavg2.text()))
                self.tc_chartedit_line_3.setCurrentIndex(1)
                self.tc_chartedit_size_3.setText('3')
                self.tc_chartedit_color_3.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_3.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_3.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3,
                        self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_style_3]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 4:
                keep = [self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4,
                          self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_style_4]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_4.setCurrentIndex(1)
                self.tc_chartedit_symbol_4.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_4.setText('MA '+str(self.tc_movavg2.text()))
                self.tc_chartedit_line_4.setCurrentIndex(1)
                self.tc_chartedit_size_4.setText('3')
                self.tc_chartedit_color_4.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_4.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_4.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4,
                        self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_style_4]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 5:
                keep = [self.tc_chartedit_panel_5,self.tc_chartedit_symbol_5,self.tc_chartedit_series_5,
                          self.tc_chartedit_line_5,self.tc_chartedit_size_5,self.tc_chartedit_color_5,self.tc_chartedit_style_5]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_5.setCurrentIndex(1)
                self.tc_chartedit_symbol_5.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_5.setText('MA '+str(self.tc_movavg2.text()))
                self.tc_chartedit_line_5.setCurrentIndex(1)
                self.tc_chartedit_size_5.setText('3')
                self.tc_chartedit_color_5.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_5.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_5.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_5,self.tc_chartedit_symbol_5,self.tc_chartedit_series_5,
                        self.tc_chartedit_line_5,self.tc_chartedit_size_5,self.tc_chartedit_color_5,self.tc_chartedit_style_5]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

        elif self.tc_movavg3.text() != '':
            if newline[0]+2 == 2:
                keep = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                          self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_2.setCurrentIndex(1)
                self.tc_chartedit_symbol_2.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_2.setText('MA '+str(self.tc_movavg3.text()))
                self.tc_chartedit_line_2.setCurrentIndex(1)
                self.tc_chartedit_size_2.setText('3')
                self.tc_chartedit_color_2.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_2.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_2.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_2,self.tc_chartedit_symbol_2,self.tc_chartedit_series_2,
                        self.tc_chartedit_line_2,self.tc_chartedit_size_2,self.tc_chartedit_color_2,self.tc_chartedit_style_2]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 3:
                keep = [self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3,
                          self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_style_3]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_3.setCurrentIndex(1)
                self.tc_chartedit_symbol_3.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_3.setText('MA '+str(self.tc_movavg3.text()))
                self.tc_chartedit_line_3.setCurrentIndex(1)
                self.tc_chartedit_size_3.setText('3')
                self.tc_chartedit_color_3.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_3.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_3.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_3,self.tc_chartedit_symbol_3,self.tc_chartedit_series_3,
                        self.tc_chartedit_line_3,self.tc_chartedit_size_3,self.tc_chartedit_color_3,self.tc_chartedit_style_3]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 4:
                keep = [self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4,
                          self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_style_4]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_4.setCurrentIndex(1)
                self.tc_chartedit_symbol_4.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_4.setText('MA '+str(self.tc_movavg3.text()))
                self.tc_chartedit_line_4.setCurrentIndex(1)
                self.tc_chartedit_size_4.setText('3')
                self.tc_chartedit_color_4.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_4.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_4.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_4,self.tc_chartedit_symbol_4,self.tc_chartedit_series_4,
                        self.tc_chartedit_line_4,self.tc_chartedit_size_4,self.tc_chartedit_color_4,self.tc_chartedit_style_4]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)

            if newline[0]+2 == 5:
                keep = [self.tc_chartedit_panel_5,self.tc_chartedit_symbol_5,self.tc_chartedit_series_5,
                          self.tc_chartedit_line_5,self.tc_chartedit_size_5,self.tc_chartedit_color_5,self.tc_chartedit_style_5]
                for k in keep:
                    k.setMaximumHeight(60)
                    k.setMinimumHeight(60)
                self.tc_chartedit_panel_5.setCurrentIndex(1)
                self.tc_chartedit_symbol_5.setText(str(self.tc_sec_search1.text()))
                self.tc_chartedit_series_5.setText('MA '+str(self.tc_movavg3.text()))
                self.tc_chartedit_line_5.setCurrentIndex(1)
                self.tc_chartedit_size_5.setText('3')
                self.tc_chartedit_color_5.setStyleSheet('background-color: rgb(175, 175, 175);')
                self.tc_chartedit_style_5.setCurrentIndex(1)
            else:
                self.tc_chartedit_panel_5.setCurrentIndex(0)
                hide = [self.tc_chartedit_panel_5,self.tc_chartedit_symbol_5,self.tc_chartedit_series_5,
                        self.tc_chartedit_line_5,self.tc_chartedit_size_5,self.tc_chartedit_color_5,self.tc_chartedit_style_5]
                for h in hide:
                    h.setMaximumHeight(0)
                    h.setMinimumHeight(0)
        self.tc_editline1()
        self.tc_editline2()
        self.tc_editline3()
        self.tc_editline4()

    def tc_editline1(self):
        '''called whenever a filter on the side panel changes or when the edit page is updated.
           theres a function for each edit line so each one can be plotted individually'''
        st = time.time()
        panel = str(self.tc_chartedit_panel.currentIndex())
        symbol = str(self.tc_chartedit_symbol.text())
        series = str(self.tc_chartedit_series.text())
        line = str(self.tc_chartedit_line.currentIndex())
        size = str(self.tc_chartedit_size.text())
        col = self.tc_chartedit_color.palette().button().color()
        color = str(col.name())
        bgcol = self.tc_bgcolor.palette().button().color()
        bgcolor = str(bgcol.name())
        style = str(self.tc_chartedit_style.currentText())

        self.tc_main_search.setText(symbol)
        self.tc_sec_search1.setText(symbol)

        if panel == '1':
            #set up the grid line, colors, layout  
            self.techchart_widget2.setMinimumHeight(0)
            self.techchart_widget2.setMaximumHeight(0) 
            self.techchart_widget3.setMinimumHeight(0)
            self.techchart_widget3.setMaximumHeight(0) 

            self.tech_chart_axis.clear()
            self.tech_chart_axis.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis.yaxis.label.set_color("w")
            self.tech_chart_axis.xaxis.label.set_color('w')
            self.tech_chart_axis.spines['bottom'].set_color("w")
            self.tech_chart_axis.spines['top'].set_color("#191919")
            self.tech_chart_axis.spines['left'].set_color("#191919")
            self.tech_chart_axis.spines['right'].set_color("w")
            self.tech_chart_axis.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis.set_axis_bgcolor(bgcolor)
            self.tech_chart_axis.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig.set_tight_layout(tight=True)
            self.tech_chart_axis.yaxis.tick_right()
            axis = self.tech_chart_axis
            fig = self.tech_chart_canvas
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)
                

        elif panel == '2':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget2)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis2.clear()
            self.tech_chart_axis2.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis2.yaxis.label.set_color("w")
            self.tech_chart_axis2.xaxis.label.set_color('w')
            self.tech_chart_axis2.spines['bottom'].set_color("w")
            self.tech_chart_axis2.spines['top'].set_color("#191919")
            self.tech_chart_axis2.spines['left'].set_color("#191919")
            self.tech_chart_axis2.spines['right'].set_color("w")
            self.tech_chart_axis2.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis2.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis2.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis2.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig2.set_tight_layout(tight=True)
            self.tech_chart_axis2.yaxis.tick_right()
            axis = self.tech_chart_axis2
            fig = self.tech_chart_canvas2
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)

        elif panel == '3':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget3)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis3.clear()
            self.tech_chart_axis3.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis3.yaxis.label.set_color("w")
            self.tech_chart_axis3.xaxis.label.set_color('w')
            self.tech_chart_axis3.spines['bottom'].set_color("w")
            self.tech_chart_axis3.spines['top'].set_color("#191919")
            self.tech_chart_axis3.spines['left'].set_color("#191919")
            self.tech_chart_axis3.spines['right'].set_color("w")
            self.tech_chart_axis3.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis3.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis3.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis3.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig3.set_tight_layout(tight=True)
            self.tech_chart_axis3.yaxis.tick_right()
            axis = self.tech_chart_axis3
            fig = self.tech_chart_canvas3
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)

        et = time.time()
        print 'tc_editline1 ', et-st
        #Time: 1.05 - 1.12

    def tc_editline2(self):
        st = time.time()

        panel = str(self.tc_chartedit_panel_2.currentIndex())
        symbol = str(self.tc_chartedit_symbol_2.text())
        series = str(self.tc_chartedit_series_2.text())
        line = str(self.tc_chartedit_line_2.currentIndex())
        size = str(self.tc_chartedit_size_2.text())
        col = self.tc_chartedit_color_2.palette().button().color()
        color = str(col.name())
        style = str(self.tc_chartedit_style_2.currentText())

        if panel == '1':
            #set up the grid line, colors, layout  
            self.tech_chart_axis.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis.yaxis.label.set_color("w")
            self.tech_chart_axis.xaxis.label.set_color('w')
            self.tech_chart_axis.spines['bottom'].set_color("w")
            self.tech_chart_axis.spines['top'].set_color("#191919")
            self.tech_chart_axis.spines['left'].set_color("#191919")
            self.tech_chart_axis.spines['right'].set_color("w")
            self.tech_chart_axis.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig.set_tight_layout(tight=True)
            self.tech_chart_axis.yaxis.tick_right()
            axis = self.tech_chart_axis
            fig = self.tech_chart_canvas
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)


        elif panel == '2':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget2)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis.tick_params(axis='x', colors='black',labelsize=5)

            self.tech_chart_axis2.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis2.yaxis.label.set_color("w")
            self.tech_chart_axis2.xaxis.label.set_color('w')
            self.tech_chart_axis2.spines['bottom'].set_color("w")
            self.tech_chart_axis2.spines['top'].set_color("#191919")
            self.tech_chart_axis2.spines['left'].set_color("#191919")
            self.tech_chart_axis2.spines['right'].set_color("w")
            self.tech_chart_axis2.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis2.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis2.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis2.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig2.set_tight_layout(tight=True)
            self.tech_chart_axis2.yaxis.tick_right()
            axis = self.tech_chart_axis2
            fig = self.tech_chart_canvas2
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)


        elif panel == '3':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget3)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis3.clear()
            self.tech_chart_axis3.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis3.yaxis.label.set_color("w")
            self.tech_chart_axis3.xaxis.label.set_color('w')
            self.tech_chart_axis3.spines['bottom'].set_color("w")
            self.tech_chart_axis3.spines['top'].set_color("#191919")
            self.tech_chart_axis3.spines['left'].set_color("#191919")
            self.tech_chart_axis3.spines['right'].set_color("w")
            self.tech_chart_axis3.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis3.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis3.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis3.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig3.set_tight_layout(tight=True)
            self.tech_chart_axis3.yaxis.tick_right()
            axis = self.tech_chart_axis3
            fig = self.tech_chart_canvas3
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)
        et = time.time()
        print 'tc_editline2 ', et-st
        #Time: 0.21

    def tc_editline3(self):
        st = time.time()
        panel = str(self.tc_chartedit_panel_3.currentIndex())
        symbol = str(self.tc_chartedit_symbol_3.text())
        series = str(self.tc_chartedit_series_3.text())
        line = str(self.tc_chartedit_line_3.currentIndex())
        size = str(self.tc_chartedit_size_3.text())
        col = self.tc_chartedit_color_3.palette().button().color()
        color = str(col.name())
        style = str(self.tc_chartedit_style_3.currentText())

        if panel == '1':
            #set up the grid line, colors, layout  
            self.tech_chart_axis.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis.yaxis.label.set_color("w")
            self.tech_chart_axis.xaxis.label.set_color('w')
            self.tech_chart_axis.spines['bottom'].set_color("w")
            self.tech_chart_axis.spines['top'].set_color("#191919")
            self.tech_chart_axis.spines['left'].set_color("#191919")
            self.tech_chart_axis.spines['right'].set_color("w")
            self.tech_chart_axis.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig.set_tight_layout(tight=True)
            self.tech_chart_axis.yaxis.tick_right()
            axis = self.tech_chart_axis
            fig = self.tech_chart_canvas
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)

        elif panel == '2':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget2)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis2.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis2.yaxis.label.set_color("w")
            self.tech_chart_axis2.xaxis.label.set_color('w')
            self.tech_chart_axis2.spines['bottom'].set_color("w")
            self.tech_chart_axis2.spines['top'].set_color("#191919")
            self.tech_chart_axis2.spines['left'].set_color("#191919")
            self.tech_chart_axis2.spines['right'].set_color("w")
            self.tech_chart_axis2.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis2.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis2.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis2.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig2.set_tight_layout(tight=True)
            self.tech_chart_axis2.yaxis.tick_right()
            axis = self.tech_chart_axis2
            fig = self.tech_chart_canvas2
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)

        elif panel == '3':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget3)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis3.clear()
            self.tech_chart_axis3.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis3.yaxis.label.set_color("w")
            self.tech_chart_axis3.xaxis.label.set_color('w')
            self.tech_chart_axis3.spines['bottom'].set_color("w")
            self.tech_chart_axis3.spines['top'].set_color("#191919")
            self.tech_chart_axis3.spines['left'].set_color("#191919")
            self.tech_chart_axis3.spines['right'].set_color("w")
            self.tech_chart_axis3.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis3.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis3.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis3.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig3.set_tight_layout(tight=True)
            self.tech_chart_axis3.yaxis.tick_right()
            axis = self.tech_chart_axis3
            fig = self.tech_chart_canvas3
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)
        et = time.time()
        print 'tc_editline3 ', et-st
        #Time: 0.20
        
    def tc_editline4(self):
        st = time.time()
        panel = str(self.tc_chartedit_panel_4.currentIndex())
        symbol = str(self.tc_chartedit_symbol_4.text())
        series = str(self.tc_chartedit_series_4.text())
        line = str(self.tc_chartedit_line_4.currentIndex())
        size = str(self.tc_chartedit_size_4.text())
        col = self.tc_chartedit_color_4.palette().button().color()
        color = str(col.name())
        style = str(self.tc_chartedit_style_4.currentText())

        if panel == '1':
            #set up the grid line, colors, layout  
            self.tech_chart_axis.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis.yaxis.label.set_color("w")
            self.tech_chart_axis.xaxis.label.set_color('w')
            self.tech_chart_axis.spines['bottom'].set_color("w")
            self.tech_chart_axis.spines['top'].set_color("#191919")
            self.tech_chart_axis.spines['left'].set_color("#191919")
            self.tech_chart_axis.spines['right'].set_color("w")
            self.tech_chart_axis.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig.set_tight_layout(tight=True)
            self.tech_chart_axis.yaxis.tick_right()
            axis = self.tech_chart_axis
            fig = self.tech_chart_canvas
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)

        elif panel == '2':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget2)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis2.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis2.yaxis.label.set_color("w")
            self.tech_chart_axis2.xaxis.label.set_color('w')
            self.tech_chart_axis2.spines['bottom'].set_color("w")
            self.tech_chart_axis2.spines['top'].set_color("#191919")
            self.tech_chart_axis2.spines['left'].set_color("#191919")
            self.tech_chart_axis2.spines['right'].set_color("w")
            self.tech_chart_axis2.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis2.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis2.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis2.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig2.set_tight_layout(tight=True)
            self.tech_chart_axis2.yaxis.tick_right()
            axis = self.tech_chart_axis2
            fig = self.tech_chart_canvas2
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)

        elif panel == '3':
            #set up the grid line, colors, layout  
            self.tc_graph_layout.addWidget(self.techchart_widget3)  
            self.techchart_widget2.setMinimumHeight(350)
            self.techchart_widget2.setMaximumHeight(350)  
            self.tech_chart_axis3.clear()
            self.tech_chart_axis3.grid(True, which='major', color='w', linestyle='--')  
            self.tech_chart_axis3.yaxis.label.set_color("w")
            self.tech_chart_axis3.xaxis.label.set_color('w')
            self.tech_chart_axis3.spines['bottom'].set_color("w")
            self.tech_chart_axis3.spines['top'].set_color("#191919")
            self.tech_chart_axis3.spines['left'].set_color("#191919")
            self.tech_chart_axis3.spines['right'].set_color("w")
            self.tech_chart_axis3.tick_params(axis='y', colors='w',labelsize=20)
            self.tech_chart_axis3.tick_params(axis='x', colors='w',labelsize=20)
            self.tech_chart_axis3.yaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_axis3.xaxis.set_major_locator(LinearLocator(10))
            self.tech_chart_fig3.set_tight_layout(tight=True)
            self.tech_chart_axis3.yaxis.tick_right()
            axis = self.tech_chart_axis3
            fig = self.tech_chart_canvas3
            if series == 'Close':
                self.tc_plot_close(axis,symbol,size,panel,fig,color,style)
            elif series == 'Volume':
                self.tc_plot_volume(axis,symbol,size,panel,fig,color,style)
            elif series == 'Upper Band':
                self.tc_plot_upperboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Middle Band':
                self.tc_plot_middleboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'Lower Band':
                self.tc_plot_lowerboll(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD':
                self.tc_plot_macdline(axis,symbol,size,panel,fig,color,style)
            elif series == 'Signal Line':
                self.tc_plot_macdsignal(axis,symbol,size,panel,fig,color,style)
            elif series == 'MACD Histogram':
                self.tc_plot_macdhist(axis,symbol,size,panel,fig,color,style)
        et = time.time()
        print 'tc_editline4 ', et-st

    def tc_plot_close(self,axis,symbol,size,panel,fig,color,style):
        st = time.time()
        data = self.get_symbol_data(symbol)
        #if style == 'Line Plot':
        axis.tick_params(axis='x', colors='w',labelsize=20)
        axis.plot(data['Close'],lw=int(size),alpha=0.6,color=color,linestyle=style[6:])
        self.tc_set_axis(axis,symbol,fig,'Close')
        fig.draw()
        #elif style == 'OHLC Candlestick':
        #    quotes = data
        #    quotes = quotes.reset_index()
        #    quotes = quotes[["index","Open","High",'Low',"Close"]]
        #    quotes['index'] = quotes['index'].map(mdates.date2num)
        #    candlestick2_ohlc(axis,quotes['Open'],quotes['High'],quotes['Low'],quotes['Close'],width=1.0, colorup='green', colordown='red',alpha=0.75)
        #    self.tech_chart_canvas.draw()
        et = time.time()
        print 'tc_plot_close: ', et-st
        #Time: 0.80 - 0.87
  
    def tc_plot_volume(self,axis,symbol,size,panel,fig,color,style):
        st = time.time()
        data = self.get_symbol_data(symbol)

        '''bar chart is taking too long'''
        #quotes = data[-300:-1]
        #quotes = quotes.reset_index()
        #dates = np.asarray(quotes['index'])
        #volume = np.asarray(quotes['Volume'])

        axis.clear()
        self.tech_chart_axis.tick_params(axis='x', colors='black',labelsize=5)
        axis.grid(True, which='major', color='w', linestyle='--')  
        axis.yaxis.label.set_color("w")
        axis.xaxis.label.set_color('w')
        axis.spines['bottom'].set_color("w")
        axis.spines['top'].set_color("#191919")
        axis.spines['left'].set_color("#191919")
        axis.spines['right'].set_color("w")
        axis.tick_params(axis='y', colors='w',labelsize=20)
        axis.tick_params(axis='x', colors='w',labelsize=20)
        axis.yaxis.set_major_locator(LinearLocator(5))
        axis.xaxis.set_major_locator(LinearLocator(10))
        axis.tick_params(axis='x', colors='w',labelsize=20)

        #axis.bar(dates,volume,width=int(size),color=color,align='center')
        axis.plot(data['Volume'],lw=int(size),alpha=0.6,color=str(color),linestyle=style[6:])
        self.tc_set_axis(axis,symbol,fig,'Volume')
        self.tech_chart_canvas.draw()
        self.tech_chart_canvas2.draw()
        et = time.time()
        print 'tc_plot_voluem: ', et-st

    def tc_plot_upperboll(self,axis,symbol,size,panel,fig,color,style):
        st = time.time()
        data = self.get_symbol_data(symbol)

        boll_band_period = 20
        boll_band_deviance = 1.5

        std_dev = data['Close'][-boll_band_period:].std()
        sma = data['Close'].rolling(window=boll_band_period).mean()
        upper_band = sma + (std_dev*boll_band_deviance)
        lower_band = sma - (std_dev*boll_band_deviance)
        axis.plot(upper_band,lw=int(size),alpha=0.5,color=str(color),linestyle=style[6:])
        fig.draw()


        et = time.time()
        print 'time', et-st

    def tc_plot_middleboll(self,axis,symbol,size,panel,fig,color,style):
        st = time.time()
        data = self.get_symbol_data(symbol)

        boll_band_period = 20
        boll_band_deviance = 1.5

        std_dev = data['Close'][-boll_band_period:].std()
        sma = data['Close'].rolling(window=boll_band_period).mean()
        upper_band = sma + (std_dev*boll_band_deviance)
        lower_band = sma - (std_dev*boll_band_deviance)
        axis.plot(sma,lw=int(size),alpha=0.5,color=str(color),linestyle=style[6:])
        fig.draw()

        et = time.time()
        print 'time', et-st

    def tc_plot_lowerboll(self,axis,symbol,size,panel,fig,color,style):
        st = time.time()
        data = self.get_symbol_data(symbol)

        boll_band_period = 20
        boll_band_deviance = 1.5

        #Gets the dates from the QtdateEdits
        from_year = self.tc_date_from.date().year()
        from_month = self.tc_date_from.date().month()
        from_day = self.tc_date_from.date().day()
        to_year = self.tc_date_to.date().year()
        to_month = self.tc_date_to.date().month()
        to_day = self.tc_date_to.date().day()

        #Sets the x axis on the greaph
        axis.set_xlim([datetime.datetime(from_year,from_month,from_day,9,0,0),datetime.datetime(to_year,to_month,to_day-1,17,0,0)])

        #Format the QtdateEdit to us in index
        from_ = datetime.datetime(from_year,from_month,from_day)
        to_ = datetime.datetime(to_year,to_month,to_day)

        from_index = from_.strftime('%Y-%m-%d')
        to_index = to_.strftime('%Y-%m-%d')

        std_dev = data['Close'][-boll_band_period:].std()
        sma = data['Close'].rolling(window=boll_band_period).mean()
        upper_band = sma + (std_dev*boll_band_deviance)
        lower_band = sma - (std_dev*boll_band_deviance)
        axis.plot(lower_band,lw=int(size),alpha=0.5,color=str(color),linestyle=style[6:])

        #Sets the y-axis max and min based on high and low
        boll_max = upper_band.loc[from_index:to_index].max()
        boll_min = lower_band.loc[from_index:to_index].min()
        boll_diff = float(boll_max - boll_min)
        ax1_min = float(boll_min - (boll_diff*0.10))
        ax1_max = float(boll_max + (boll_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        fig.draw()
        et = time.time()
        print 'time', et-st

    def tc_plot_macdsignal(self,axis,symbol,size,panel,fig,color,style):
        data = self.get_symbol_data(symbol)

        slow_ = pd.ewma(data['Close'],span=12)
        fast_ = pd.ewma(data['Close'],span=26)
        macd = slow_ - fast_
        signal = pd.ewma(macd,span=9)
        print signal
        axis.plot(signal,color=str(color),lw=int(size))

        fig.draw()

    def tc_plot_macdhist(self,axis,symbol,size,panel,fig,color,style):
        data = self.get_symbol_data(symbol)

        slow_ = pd.ewma(data['Close'],span=12)
        fast_ = pd.ewma(data['Close'],span=26)
        macd = slow_ - fast_
        signal = pd.ewma(macd,span=9)
        macdhist = macd - signal
        print macdhist
        axis.plot(macdhist,color=str(color),lw=int(size))
        fig.draw()

    def tc_plot_macdline(self,axis,symbol,size,panel,fig,color,style):
        data = self.get_symbol_data(symbol)

        #Gets the dates from the QtdateEdits
        from_year = self.tc_date_from.date().year()
        from_month = self.tc_date_from.date().month()
        from_day = self.tc_date_from.date().day()
        to_year = self.tc_date_to.date().year()
        to_month = self.tc_date_to.date().month()
        to_day = self.tc_date_to.date().day()

        slow_ = pd.ewma(data['Close'],span=12)
        fast_ = pd.ewma(data['Close'],span=26)
        macd = slow_ - fast_
        print macd
        axis.plot(macd,color=str(color),lw=int(size))

        #Sets the x axis on the greaph
        axis.set_xlim([datetime.datetime(from_year,from_month,from_day,9,0,0),datetime.datetime(to_year,to_month,to_day-1,17,0,0)])

        #Format the QtdateEdit to us in index
        from_ = datetime.datetime(from_year,from_month,from_day)
        to_ = datetime.datetime(to_year,to_month,to_day)

        from_index = from_.strftime('%Y-%m-%d')
        to_index = to_.strftime('%Y-%m-%d')


        #Sets the y-axis max and min based on high and low
        macd_min = macd.loc[from_index:to_index].min()
        macd_max = macd.loc[from_index:to_index].max()
        macd_diff = float(macd_max - macd_min)
        ax1_min = float(macd_min - (macd_diff*0.10))
        ax1_max = float(macd_max + (macd_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        fig.draw()

    def tc_plot_ma(self,axis,symbol,size,panel,fig,color,style):
        data = self.get_symbol_data(symbol)

        ma1_days = self.tc_movavg.text()
        ma2_days = self.tc_movavg2.text()
        ma3_days = self.tc_movavg3.text()
        if self.tc_movavg.text() != '':
            ma_one = data['Close'].rolling(window=int(ma1_days)).mean()
            axis.plot(ma_one,lw=int(size),alpha=0.5,color=color,linestyle=style[6:])
            self.tech_chart_canvas.draw()
        else:
            pass
        if self.tc_movavg2.text() != '':
            ma_two = data['Close'].rolling(window=int(ma2_days)).mean()
            axis.plot(ma_two,lw=int(size),alpha=0.5,color=color,linestyle=style[6:])
            self.tech_chart_canvas.draw()
        else:
            pass
        if self.tc_movavg3.text() != '':
            ma_three = data['Close'].rolling(window=int(ma3_days)).mean()
            axis.plot(ma_three,lw=int(size),alpha=0.5,color=color,linestyle=style[6:])
            self.tech_chart_canvas.draw()
        else:
            pass

    def tc_color_edit(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_chartedit_color.setStyleSheet("QWidget { background-color: %s}" % color.name())
        print color.name()     
 
    def tc_color_edit2(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_chartedit_color_2.setStyleSheet("QWidget { background-color: %s}" % color.name())
        print color.name()    

    def tc_color_edit3(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_chartedit_color_3.setStyleSheet("QWidget { background-color: %s}" % color.name())
        print color.name()  
  
    def tc_color_edit4(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_chartedit_color_4.setStyleSheet("QWidget { background-color: %s}" % color.name())
        print color.name()    
    
    def tc_bg_color(self):
        color = QtGui.QColorDialog.getColor()
        self.tc_bgcolor.setStyleSheet("QWidget { background-color: %s}" % color.name())
        bgcolor = color.name() 

    def tc_background_color(self):
        col = self.tc_bgcolor.palette().button().color()
        bgcolor = str(col.name())

        gs1 = gridspec.GridSpec(4, 1)
        gs1.update(left=0.01, right=0.90, top=.98, bottom=0.03,wspace=0,hspace=0)
        self.tech_chart_fig = Figure(facecolor='#191919') 
        self.tech_chart_canvas = FigureCanvas(self.tech_chart_fig)
        self.techchart_layout.addWidget(self.tech_chart_canvas)  
        self.tech_chart_axis = self.tech_chart_fig.add_subplot(gs1[:, :],axisbg=bgcolor) 
        self.tc_main_search.setText('AAPL')
        self.tc_sec_search1.setText('AAPL')

    def tc_set_axis(self,axis,symbol,fig,series):
        st = time.time()
        data = self.get_symbol_data(symbol)

        '''Called from the main search function and also whenever the date range or buttons is changed. 
           gets the updated date from either the buttons or range, then sets the chart axis to the same start/end dates '''

        #Gets the dates from the QtdateEdits
        from_year = self.tc_date_from.date().year()
        from_month = self.tc_date_from.date().month()
        from_day = self.tc_date_from.date().day()
        to_year = self.tc_date_to.date().year()
        to_month = self.tc_date_to.date().month()
        to_day = self.tc_date_to.date().day()

        #Sets the x axis on the greaph
        axis.set_xlim([datetime.datetime(from_year,from_month,from_day,9,0,0),datetime.datetime(to_year,to_month,to_day-1,17,0,0)])

        #Format the QtdateEdit to us in index
        from_ = datetime.datetime(from_year,from_month,from_day)
        to_ = datetime.datetime(to_year,to_month,to_day)

        cal = USFederalHolidayCalendar()
        holidays = cal.holidays().to_pydatetime()
        if from_.strftime('%A') == 'Saturday':
            from_ = datetime.datetime(from_year,from_month,from_day+2)
        elif from_.strftime('%A') == 'Sunday':
            from_ = datetime.datetime(from_year,from_month,from_day+1)
        elif from_ in holidays:
            from_ = datetime.datetime(from_year,from_month,from_day+1)
        elif to_.strftime('%A') == 'Saturday':
            to_ = datetime.datetime(from_year,from_month,from_day-1)
        elif to_.strftime('%A') == 'Sunday':
            to_ = datetime.datetime(from_year,from_month,from_day-2)
        elif to_ in holidays:
            to_ = datetime.datetime(from_year,from_month,from_day+1)
            
        from_index = from_.strftime('%Y-%m-%d')
        to_index = to_.strftime('%Y-%m-%d')

        #Sets the y-axis max and min based on high and low
        close_min = data[series].loc[from_index:to_index].min()
        close_max = data[series].loc[from_index:to_index].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        date_buttons = [self.tc_one_day,self.tc_five_day,self.tc_one_month,self.tc_three_month, self.tc_six_month,
                        self.tc_one_year,self.tc_five_year,self.tc_max_date]
        for b in date_buttons:
            b.setChecked(False)
        et = time.time()
        print 'set axis', et-st
        fig.draw()

    def tc_date_buttons(self):
        starttime = time.time()

        year_ = self.tc_date_to.date().year()
        month_ = self.tc_date_to.date().month()
        day_ = self.tc_date_to.date().day()
        date_to = datetime.datetime(year_, month_, day_)

        if date_to == date_e:
            pass
        else:
            self.tc_date_to.setDate(QtCore.QDate(year,month,day))
        if self.tc_one_day.isChecked():
            self.tc_date_from.setDate(QtCore.QDate(year,month,day-1))
        elif self.tc_five_day.isChecked():
            self.tc_date_from.setDate(QtCore.QDate(year,month,day-7))
            date_form = mdates.DateFormatter('%d/%m')
            self.tech_chart_axis.xaxis.set_major_formatter(date_form)
        elif self.tc_one_month.isChecked():
            self.tc_date_from.setDate(QtCore.QDate(year,month-1,day))
            date_form = mdates.DateFormatter('%d/%m')
            self.tech_chart_axis.xaxis.set_major_formatter(date_form)
        elif self.tc_three_month.isChecked():
            self.tc_date_from.setDate(QtCore.QDate(year,month-3,day))
            date_form = mdates.DateFormatter('%d/%m')
            self.tech_chart_axis.xaxis.set_major_formatter(date_form)
        elif self.tc_six_month.isChecked():
            self.tc_date_from.setDate(QtCore.QDate(year,month-6,day))
            date_form = mdates.DateFormatter('%m/%y')
            self.tech_chart_axis.xaxis.set_major_formatter(date_form)
        elif self.tc_one_year.isChecked():
            self.tc_date_from.setDate(QtCore.QDate(year-1,month,day))
            date_form = mdates.DateFormatter('%m/%y')
            self.tech_chart_axis.xaxis.set_major_formatter(date_form)
        elif self.tc_five_year.isChecked():
            self.tc_date_from.setDate(QtCore.QDate(year-5,month,day))
            date_form = mdates.DateFormatter('%m/%y')
            self.tech_chart_axis.xaxis.set_major_formatter(date_form)
        elif self.tc_max_date.isChecked():
            #gets the first data value is the dataframe
            symbol = str(self.tc_main_search.text())
            data = data
            data.index = data.index.to_datetime()
            start_date = data.first_valid_index().to_pydatetime()
            start_year = start_date.year
            start_month = start_date.month
            start_day = start_date.day
            self.tc_date_from.setDate(QtCore.QDate(start_year,start_month,start_day))
            date_form = mdates.DateFormatter('%Y')
            self.tech_chart_axis.xaxis.set_major_formatter(date_form)
        endtime = time.time()
        print '3', endtime-starttime

    def tc_chartedit_update(self):
        '''called when the edit page is updated then calls each lines function'''
        self.techchart_widget.setCurrentIndex(0)
        self.tc_edit_update.setChecked(False)
        self.tc_editline1()
        self.tc_editline2()
        self.tc_editline3()
        self.tc_editline4()

    def tc_chartedit_cancel(self):
        self.techchart_widget.setCurrentIndex(0)
        self.tc_edit_update.setChecked(False)

    def tc_edit(self):
        if self.tc_edit_bt.isChecked():
            self.techchart_widget.setCurrentIndex(1)
            self.tc_edit_bt.setChecked(False)
        else:
            pass

    def tc_tab_buttons(self):
        self.tc_sec_search1.setText(str(self.tc_main_search.text()))       
        if self.tc_secstudy_bt.isChecked():
            self.tc_secstudy_tab.setMinimumWidth(500)
            self.tc_secstudy_tab.setMaximumWidth(500)
        else:
            self.tc_secstudy_tab.setMinimumWidth(0)
            self.tc_secstudy_tab.setMaximumWidth(0)

    def tc_study_edit(self):
        self.tc_line_edit.setMinimumHeight(600)
        self.tc_line_edit.setMaximumHeight(600)
        self.tc_line_edit.setMinimumWidth(1000)
        self.tc_line_edit.setMaximumWidth(1000)

    def tc_addstudy(self):
        if self.tc_addstudy1_bt.isChecked():
            self.study_edit2.setMinimumHeight(35)
            self.study_edit2.setMaximumHeight(35)
            
            self.study_filter2.setMinimumHeight(50)
            self.study_filter2.setMaximumHeight(50)

            self.study_line1.setMinimumHeight(5)
            self.study_line1.setMaximumHeight(5)
        else:
            self.study_edit3.setMinimumHeight(35)
            self.study_edit3.setMaximumHeight(35)
            
            self.study_filter3.setMinimumHeight(50)
            self.study_filter3.setMaximumHeight(50)

            self.study_line2.setMinimumHeight(5)
            self.study_line2.setMaximumHeight(5)

    def ms_gainers_loser(self):
        pass
        #st = time.time()

        #last_change = {}
        #last_pchange = {}
        #stock = list(all_stocks.columns.levels[0])
        #for i in stock:
        #    chg = round(all_stocks[i]['Change'][-1],2)
        #    pchg = round(all_stocks[i]['% Change'][-1],2)
        #    last_change[i] = chg
        #    last_pchange[i] = pchg

        #last_chg = pd.DataFrame(last_change,index=last_change.keys())
        #last_chg.index = range(len(last_chg.index))
        #last_chg = last_chg[:1]
        #last_chg = last_chg.T
        #last_chg['Rank'] = last_chg[0].rank(ascending=False)

        #last_pchg = pd.DataFrame(last_pchange,index=last_pchange.keys())
        #last_pchg.index = range(len(last_pchg.index))
        #last_pchg = last_pchg[:1]
        #last_pchg = last_pchg.T
        #last_pchg['Rank'] = last_pchg[0].rank(ascending=False)

        #if self.ms_gainer_filter.currentText() == 'Price Change':
        #    gain1 = last_chg.loc[last_chg['Rank']==1]
        #    gainsym1 = str(list(gain1.index)[0])
        #    self.ms_gainer_sym1.setText(gainsym1)
        #    gainname1 = str(list(stock_list.loc[stock_list['Symbol']==gainsym1,'Name'])[0])
        #    self.ms_gainer_name1.setText(gainname1)
        #    self.ms_gainer_price1.setText(str(round(all_stocks[gainsym1]['Close'][-1],2)))
        #    self.ms_gainer_chg1.setText('+'+str(list(last_chg.loc[last_chg.index==gainsym1,0])[0]))

        #    gain2 = last_chg.loc[last_chg['Rank']==2]
        #    gainsym2 = str(list(gain2.index)[0])
        #    self.ms_gainer_sym2.setText(gainsym2)
        #    gainname2 = str(list(stock_list.loc[stock_list['Symbol']==gainsym2,'Name'])[0])
        #    self.ms_gainer_name2.setText(gainname2)
        #    self.ms_gainer_price2.setText(str(round(all_stocks[gainsym2]['Close'][-1],2)))
        #    self.ms_gainer_chg2.setText('+'+str(list(last_chg.loc[last_chg.index==gainsym2,0])[0]))

        #    gain3 = last_chg.loc[last_chg['Rank']==3]
        #    gainsym3 = str(list(gain3.index)[0])
        #    self.ms_gainer_sym3.setText(gainsym3)
        #    gainname3 = str(list(stock_list.loc[stock_list['Symbol']==gainsym3,'Name'])[0])
        #    self.ms_gainer_name3.setText(gainname3)
        #    self.ms_gainer_price3.setText(str(round(all_stocks[gainsym3]['Close'][-1],2)))
        #    self.ms_gainer_chg3.setText('+'+str(list(last_chg.loc[last_chg.index==gainsym3,0])[0]))

        #    gain4 = last_chg.loc[last_chg['Rank']==4]
        #    gainsym4 = str(list(gain4.index)[0])
        #    self.ms_gainer_sym4.setText(gainsym4)
        #    gainname4 = str(list(stock_list.loc[stock_list['Symbol']==gainsym4,'Name'])[0])
        #    self.ms_gainer_name4.setText(gainname4)
        #    self.ms_gainer_price4.setText(str(round(all_stocks[gainsym4]['Close'][-1],2)))
        #    self.ms_gainer_chg4.setText('+'+str(list(last_chg.loc[last_chg.index==gainsym4,0])[0]))

        #    gain5 = last_chg.loc[last_chg['Rank']==5]
        #    gainsym5 = str(list(gain5.index)[0])
        #    self.ms_gainer_sym5.setText(gainsym5)
        #    gainname5 = str(list(stock_list.loc[stock_list['Symbol']==gainsym5,'Name'])[0])
        #    self.ms_gainer_name5.setText(gainname5)
        #    self.ms_gainer_price5.setText(str(round(all_stocks[gainsym5]['Close'][-1],2)))
        #    self.ms_gainer_chg5.setText('+'+str(list(last_chg.loc[last_chg.index==gainsym5,0])[0]))

        #    loss1 = last_chg.loc[last_chg['Rank']==494]
        #    losssym1 = str(list(loss1.index)[0])
        #    self.ms_loser_sym1.setText(losssym1)
        #    lossname1 = str(list(stock_list.loc[stock_list['Symbol']==losssym1,'Name'])[0])
        #    self.ms_loser_name1.setText(lossname1)
        #    self.ms_loser_price1.setText(str(round(all_stocks[losssym1]['Close'][-1],2)))
        #    self.ms_loser_chg1.setText(str(list(last_chg.loc[last_chg.index==losssym1,0])[0]))

        #    loss2 = last_chg.loc[last_chg['Rank']==493]
        #    losssym2 = str(list(loss2.index)[0])
        #    self.ms_loser_sym2.setText(losssym2)
        #    lossname2 = str(list(stock_list.loc[stock_list['Symbol']==losssym2,'Name'])[0])
        #    self.ms_loser_name2.setText(lossname2)
        #    self.ms_loser_price2.setText(str(round(all_stocks[losssym2]['Close'][-1],2)))
        #    self.ms_loser_chg2.setText(str(list(last_chg.loc[last_chg.index==losssym2,0])[0]))

        #    loss3 = last_chg.loc[last_chg['Rank']==492]
        #    losssym3 = str(list(loss3.index)[0])
        #    self.ms_loser_sym3.setText(losssym3)
        #    lossname3 = str(list(stock_list.loc[stock_list['Symbol']==losssym3,'Name'])[0])
        #    self.ms_loser_name3.setText(lossname3)
        #    self.ms_loser_price3.setText(str(round(all_stocks[losssym3]['Close'][-1],2)))
        #    self.ms_loser_chg3.setText(str(list(last_chg.loc[last_chg.index==losssym3,0])[0]))

        #    loss4 = last_chg.loc[last_chg['Rank']==491]
        #    losssym4 = str(list(loss4.index)[0])
        #    self.ms_loser_sym4.setText(losssym4)
        #    lossname4 = str(list(stock_list.loc[stock_list['Symbol']==losssym4,'Name'])[0])
        #    self.ms_loser_name4.setText(lossname4)
        #    self.ms_loser_price4.setText(str(round(all_stocks[losssym4]['Close'][-1],2)))
        #    self.ms_loser_chg4.setText(str(list(last_chg.loc[last_chg.index==losssym4,0])[0]))

        #    loss5 = last_chg.loc[last_chg['Rank']==490]
        #    losssym5 = str(list(loss5.index)[0])
        #    self.ms_loser_sym5.setText(losssym5)
        #    lossname5 = str(list(stock_list.loc[stock_list['Symbol']==losssym5,'Name'])[0])
        #    self.ms_loser_name5.setText(lossname5)
        #    self.ms_loser_price5.setText(str(round(all_stocks[losssym5]['Close'][-1],2)))
        #    self.ms_loser_chg5.setText(str(list(last_chg.loc[last_chg.index==losssym5,0])[0]))

        #elif self.ms_gainer_filter.currentText() == 'Price % Change':
        #    gain1 = last_pchg.loc[last_pchg['Rank']==1]
        #    gainsym1 = str(list(gain1.index)[0])
        #    self.ms_gainer_sym1.setText(gainsym1)
        #    gainname1 = str(list(stock_list.loc[stock_list['Symbol']==gainsym1,'Name'])[0])
        #    self.ms_gainer_name1.setText(gainname1)
        #    self.ms_gainer_price1.setText(str(round(all_stocks[gainsym1]['Close'][-1],2)))
        #    self.ms_gainer_chg1.setText('+'+str(list(last_pchg.loc[last_pchg.index==gainsym1,0])[0])+'%')

        #    gain2 = last_pchg.loc[last_pchg['Rank']==2]
        #    gainsym2 = str(list(gain2.index)[0])
        #    self.ms_gainer_sym2.setText(gainsym2)
        #    gainname2 = str(list(stock_list.loc[stock_list['Symbol']==gainsym2,'Name'])[0])
        #    self.ms_gainer_name2.setText(gainname2)
        #    self.ms_gainer_price2.setText(str(round(all_stocks[gainsym2]['Close'][-1],2)))
        #    self.ms_gainer_chg2.setText('+'+str(list(last_pchg.loc[last_pchg.index==gainsym2,0])[0])+'%')

        #    gain3 = last_pchg.loc[last_pchg['Rank']==3]
        #    gainsym3 = str(list(gain3.index)[0])
        #    self.ms_gainer_sym3.setText(gainsym3)
        #    gainname3 = str(list(stock_list.loc[stock_list['Symbol']==gainsym3,'Name'])[0])
        #    self.ms_gainer_name3.setText(gainname3)
        #    self.ms_gainer_price3.setText(str(round(all_stocks[gainsym3]['Close'][-1],2)))
        #    self.ms_gainer_chg3.setText('+'+str(list(last_pchg.loc[last_pchg.index==gainsym3,0])[0])+'%')

        #    gain4 = last_pchg.loc[last_pchg['Rank']==4]
        #    gainsym4 = str(list(gain4.index)[0])
        #    self.ms_gainer_sym4.setText(gainsym4)
        #    gainname4 = str(list(stock_list.loc[stock_list['Symbol']==gainsym4,'Name'])[0])
        #    self.ms_gainer_name4.setText(gainname4)
        #    self.ms_gainer_price4.setText(str(round(all_stocks[gainsym4]['Close'][-1],2)))
        #    self.ms_gainer_chg4.setText('+'+str(list(last_pchg.loc[last_pchg.index==gainsym4,0])[0])+'%')

        #    gain5 = last_pchg.loc[last_pchg['Rank']==5]
        #    gainsym5 = str(list(gain5.index)[0])
        #    self.ms_gainer_sym5.setText(gainsym5)
        #    gainname5 = str(list(stock_list.loc[stock_list['Symbol']==gainsym5,'Name'])[0])
        #    self.ms_gainer_name5.setText(gainname5)
        #    self.ms_gainer_price5.setText(str(round(all_stocks[gainsym5]['Close'][-1],2)))
        #    self.ms_gainer_chg5.setText('+'+str(list(last_pchg.loc[last_pchg.index==gainsym5,0])[0])+'%')

        #    loss1 = last_pchg.loc[last_pchg['Rank']==494]
        #    losssym1 = str(list(loss1.index)[0])
        #    self.ms_loser_sym1.setText(losssym1)
        #    lossname1 = str(list(stock_list.loc[stock_list['Symbol']==losssym1,'Name'])[0])
        #    self.ms_loser_name1.setText(lossname1)
        #    self.ms_loser_price1.setText(str(round(all_stocks[losssym1]['Close'][-1],2)))
        #    self.ms_loser_chg1.setText(str(list(last_pchg.loc[last_pchg.index==losssym1,0])[0])+'%')

        #    loss2 = last_pchg.loc[last_pchg['Rank']==493]
        #    losssym2 = str(list(loss2.index)[0])
        #    self.ms_loser_sym2.setText(losssym2)
        #    lossname2 = str(list(stock_list.loc[stock_list['Symbol']==losssym2,'Name'])[0])
        #    self.ms_loser_name2.setText(lossname2)
        #    self.ms_loser_price2.setText(str(round(all_stocks[losssym2]['Close'][-1],2)))
        #    self.ms_loser_chg2.setText(str(list(last_pchg.loc[last_pchg.index==losssym2,0])[0])+'%')

        #    loss3 = last_pchg.loc[last_pchg['Rank']==492]
        #    losssym3 = str(list(loss3.index)[0])
        #    self.ms_loser_sym3.setText(losssym3)
        #    lossname3 = str(list(stock_list.loc[stock_list['Symbol']==losssym3,'Name'])[0])
        #    self.ms_loser_name3.setText(lossname3)
        #    self.ms_loser_price3.setText(str(round(all_stocks[losssym3]['Close'][-1],2)))
        #    self.ms_loser_chg3.setText(str(list(last_pchg.loc[last_pchg.index==losssym3,0])[0])+'%')

        #    loss4 = last_pchg.loc[last_pchg['Rank']==491]
        #    losssym4 = str(list(loss4.index)[0])
        #    self.ms_loser_sym4.setText(losssym4)
        #    lossname4 = str(list(stock_list.loc[stock_list['Symbol']==losssym4,'Name'])[0])
        #    self.ms_loser_name4.setText(lossname4)
        #    self.ms_loser_price4.setText(str(round(all_stocks[losssym4]['Close'][-1],2)))
        #    self.ms_loser_chg4.setText(str(list(last_pchg.loc[last_pchg.index==losssym4,0])[0])+'%')

        #    loss5 = last_pchg.loc[last_pchg['Rank']==490]
        #    losssym5 = str(list(loss5.index)[0])
        #    self.ms_loser_sym5.setText(losssym5)
        #    lossname5 = str(list(stock_list.loc[stock_list['Symbol']==losssym5,'Name'])[0])
        #    self.ms_loser_name5.setText(lossname5)
        #    self.ms_loser_price5.setText(str(round(all_stocks[losssym5]['Close'][-1],2)))
        #    self.ms_loser_chg5.setText(str(list(last_pchg.loc[last_pchg.index==losssym5,0])[0])+'%')

        #et = time.time()
        #print 'gainer/loser', et-st

    def company_summary(self):  
        st = time.time()
        symbol = str(self.cs_search.text())
        data = self.get_symbol_data(symbol)

        stock = Share(symbol)

        today_date = datetime.date.today()
        year_date = datetime.datetime(today_date.year-1,today_date.month,today_date.day)
        year_date = year_date.strftime('%Y-%m-%d')

        sym_yclose = round(data['Close'].loc[year_date:today_date][0],2)
        sym_yhigh = round(data['Close'].loc[year_date:today_date].max(),2)
        sym_ylow = round(data['Close'].loc[year_date:today_date].min(),2)
        sym_avgvol = round(data['Volume'].loc[year_date:today_date].mean(),2)

        sym_open = round(data['Open'][-1],2)
        sym_close = round(data['Close'][-1],2)
        sym_high = round(data['High'][-1],2)
        sym_low = round(data['Low'][-1],2)
        sym_vol = round(data['Volume'][-1],2)
        sym_chg = round(data['Change'][-1],2)
        sym_pchg = round(data['% Change'][-1],2)
        sym_ychg = round(((sym_close - sym_yclose)/sym_yclose)*100,2)
        sym_eps = str(stock.get_earnings_share())
        sym_pe = str(stock.get_price_earnings_ratio())
        sym_div = str(stock.get_dividend_share())
        sym_divy = str(stock.get_dividend_yield())
        sym_avgvol = str(stock.get_avg_daily_volume())
        sym_mrkcap = str(stock.get_market_cap())
        close_data = data['Close']

        self.cs_price.setText(str(sym_close))
        self.cs_change.setText(str(sym_chg)+' ('+str(sym_pchg)+'%)')
        self.cs_eps.setText(str(sym_eps))
        self.cs_peratio.setText(str(sym_pe))
        self.cs_div.setText(str(sym_div))
        self.cs_divyield.setText(str(sym_divy))
        self.cs_openprice.setText(str(sym_open))
        self.cs_dayhigh.setText(str(sym_high))
        self.cs_daylow.setText(str(sym_low))
        self.cs_yearlow.setText(str(sym_ylow))
        self.cs_yearhigh.setText(str(sym_yhigh))
        self.cs_dayvol.setText(str(sym_vol))
        self.cs_ytdchg.setText(str(sym_ychg))
        self.cs_avgvol.setText(str(sym_avgvol))
        self.cs_mrkcap.setText(str(sym_mrkcap))

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
        self.cs_chart_axis.yaxis.set_major_locator(LinearLocator(10))
        self.cs_chart_axis.xaxis.set_major_locator(LinearLocator(12))
        self.cs_chart_axis.yaxis.tick_right()
        self.cs_chart_axis.fill_between(data.index,close_data,facecolor='blue')
        self.cs_chart_axis.plot(data['Close'],lw=5,alpha=0.6,color='blue')
        dateform = mdates.DateFormatter('%m/%y')
        self.cs_chart_axis.xaxis.set_major_formatter(dateform)
        #self.cs_chart_axis.tick_params(axis='x',direction='out',pad=100)
    
        axis = self.cs_chart_axis
        fig = self.cs_chart_canvas
        series = 'Close'
        self.tc_set_axis(axis,symbol,fig,series)
        et = time.time()
        print 'company', et-st

    def sector_summary(self):
        basic_chg = basic_data[]

    def financial_window(self):
        if self.is_rb_2.isChecked():
            row = [self.is_emp_1,self.is_growth_1,self.is_31,self.is_32,self.is_33,self.is_34,self.is_35,self.is_36,self.is_37,self.is_38,self.is_39,self.is_310,self.label_2954]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_1,self.is_growth_1,self.is_31,self.is_32,self.is_33,self.is_34,self.is_35,self.is_36,self.is_37,self.is_38,self.is_39,self.is_310,self.label_2954]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_3.isChecked():
            row = [self.is_emp_2,self.is_growth_2,self.is_51,self.is_52,self.is_53,self.is_54,self.is_55,self.is_56,self.is_57,self.is_58,self.is_59,self.is_510,self.label_2956]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_2,self.is_growth_2,self.is_51,self.is_52,self.is_53,self.is_54,self.is_55,self.is_56,self.is_57,self.is_58,self.is_59,self.is_510,self.label_2956]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_4.isChecked():
            row = [self.is_emp_3,self.is_growth_3,self.is_71,self.is_72,self.is_73,self.is_74,self.is_75,self.is_76,self.is_77,self.is_78,self.is_79,self.is_710,self.label_2957]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_3,self.is_growth_3,self.is_71,self.is_72,self.is_73,self.is_74,self.is_75,self.is_76,self.is_77,self.is_78,self.is_79,self.is_710,self.label_2957]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_6.isChecked():
            row = [self.is_emp_4,self.is_growth_4,self.is_101,self.is_102,self.is_103,self.is_104,self.is_105,self.is_106,self.is_107,self.is_108,self.is_109,self.is_1010,self.label_2960]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_4,self.is_growth_4,self.is_101,self.is_102,self.is_103,self.is_104,self.is_105,self.is_106,self.is_107,self.is_108,self.is_109,self.is_1010,self.label_2960]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_7.isChecked():
            row = [self.is_emp_5,self.is_growth_5,self.is_121,self.is_122,self.is_123,self.is_124,self.is_125,self.is_126,self.is_127,self.is_128,self.is_129,self.is_1210,self.label_2962]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_5,self.is_growth_5,self.is_121,self.is_122,self.is_123,self.is_124,self.is_125,self.is_126,self.is_127,self.is_128,self.is_129,self.is_1210,self.label_2962]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_8.isChecked():
            row = [self.is_emp_6,self.is_growth_6,self.is_141,self.is_142,self.is_143,self.is_144,self.is_145,self.is_146,self.is_147,self.is_148,self.is_149,self.is_1410,self.label_2965]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_6,self.is_growth_6,self.is_141,self.is_142,self.is_143,self.is_144,self.is_145,self.is_146,self.is_147,self.is_148,self.is_149,self.is_1410,self.label_2965]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_9.isChecked():
            row = [self.is_emp_7,self.is_growth_7,self.is_161,self.is_162,self.is_163,self.is_164,self.is_165,self.is_166,self.is_167,self.is_168,self.is_169,self.is_1610,self.label_2967]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_7,self.is_growth_7,self.is_161,self.is_162,self.is_163,self.is_164,self.is_165,self.is_166,self.is_167,self.is_168,self.is_169,self.is_1610,self.label_2967]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_10.isChecked():
            row = [self.is_emp_8,self.is_growth_8,self.is_181,self.is_182,self.is_183,self.is_184,self.is_185,self.is_186,self.is_187,self.is_188,self.is_189,self.is_1810,self.label_2969]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_8,self.is_growth_8,self.is_181,self.is_182,self.is_183,self.is_184,self.is_185,self.is_186,self.is_187,self.is_188,self.is_189,self.is_1810,self.label_2969]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_11.isChecked():
            row = [self.is_emp_9,self.is_growth_9,self.is_201,self.is_202,self.is_203,self.is_204,self.is_205,self.is_206,self.is_207,self.is_208,self.is_209,self.is_2010,self.label_2970]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_9,self.is_growth_9,self.is_201,self.is_202,self.is_203,self.is_204,self.is_205,self.is_206,self.is_207,self.is_208,self.is_209,self.is_2010,self.label_2970]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)
            
        if self.is_rb_12.isChecked():
            row = [self.is_emp_10,self.is_growth_10,self.is_221,self.is_222,self.is_223,self.is_224,self.is_225,self.is_226,self.is_227,self.is_228,self.is_229,self.is_2210,self.label_2973]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_10,self.is_growth_10,self.is_221,self.is_222,self.is_223,self.is_224,self.is_225,self.is_226,self.is_227,self.is_228,self.is_229,self.is_2210,self.label_2973]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_13.isChecked():
            row = [self.is_emp_11,self.is_growth_11,self.is_241,self.is_242,self.is_243,self.is_244,self.is_245,self.is_246,self.is_247,self.is_248,self.is_249,self.is_2410,self.label_2974]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_11,self.is_growth_11,self.is_241,self.is_242,self.is_243,self.is_244,self.is_245,self.is_246,self.is_247,self.is_248,self.is_249,self.is_2410,self.label_2974]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_1.isChecked():
            row = [self.is_emp_1,self.is_growth_1,self.is_31,self.is_32,self.is_33,self.is_34,self.is_35,self.is_36,self.is_37,self.is_38,self.is_39,self.is_310,self.label_2954,
                   self.is_emp_2,self.is_growth_2,self.is_51,self.is_52,self.is_53,self.is_54,self.is_55,self.is_56,self.is_57,self.is_58,self.is_59,self.is_510,self.label_2956]
            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_1,self.is_growth_1,self.is_31,self.is_32,self.is_33,self.is_34,self.is_35,self.is_36,self.is_37,self.is_38,self.is_39,self.is_310,self.label_2954,
                   self.is_emp_2,self.is_growth_2,self.is_51,self.is_52,self.is_53,self.is_54,self.is_55,self.is_56,self.is_57,self.is_58,self.is_59,self.is_510,self.label_2956]
            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

        if self.is_rb_5.isChecked():
            row = [self.is_emp_4,self.is_growth_4,self.is_101,self.is_102,self.is_103,self.is_104,self.is_105,self.is_106,self.is_107,self.is_108,self.is_109,self.is_1010,self.label_2960,
                   self.is_emp_5,self.is_growth_5,self.is_121,self.is_122,self.is_123,self.is_124,self.is_125,self.is_126,self.is_127,self.is_128,self.is_129,self.is_1210,self.label_2962,
                   self.is_emp_6,self.is_growth_6,self.is_141,self.is_142,self.is_143,self.is_144,self.is_145,self.is_146,self.is_147,self.is_148,self.is_149,self.is_1410,self.label_2965]

            for w in row:
                w.setMaximumHeight(60)
                w.setMinimumHeight(60)
        else:
            row = [self.is_emp_4,self.is_growth_4,self.is_101,self.is_102,self.is_103,self.is_104,self.is_105,self.is_106,self.is_107,self.is_108,self.is_109,self.is_1010,self.label_2960,
                   self.is_emp_5,self.is_growth_5,self.is_121,self.is_122,self.is_123,self.is_124,self.is_125,self.is_126,self.is_127,self.is_128,self.is_129,self.is_1210,self.label_2962,
                   self.is_emp_6,self.is_growth_6,self.is_141,self.is_142,self.is_143,self.is_144,self.is_145,self.is_146,self.is_147,self.is_148,self.is_149,self.is_1410,self.label_2965]

            for w in row:
                w.setMaximumHeight(0)
                w.setMinimumHeight(0)

    def get_symbol_data(self,symbol):
        st = time.time()
        if str(symbol) in list(basic_data.columns.levels[0]):
            return basic_data[str(symbol)]
        elif str(symbol) in list(capgood_data.columns.levels[0]):
            return capgood_data[str(symbol)]
        elif str(symbol) in list(condur_data.columns.levels[0]):
            return condur_data[str(symbol)]
        elif str(symbol) in list(nondur_data.columns.levels[0]):
            return nondur_data[str(symbol)]
        elif str(symbol) in list(conserve_data.columns.levels[0]):
            return conserve_data[str(symbol)]
        elif str(symbol) in list(energy_data.columns.levels[0]):
            return energy_data[str(symbol)]
        elif str(symbol) in list(finance_data.columns.levels[0]):
            return finance_data[str(symbol)]
        elif str(symbol) in list(health_data.columns.levels[0]):
            return health_data[str(symbol)]
        elif str(symbol) in list(misc_data.columns.levels[0]):
            return misc_data[str(symbol)]
        elif str(symbol) in list(tech_data.columns.levels[0]):
            return tech_data[str(symbol)]
        elif str(symbol) in list(trans_data.columns.levels[0]):
            return trans_data[str(symbol)]
        elif str(symbol) in list(utility_data.columns.levels[0]):
            return utility_data[str(symbol)]
        et = time.time()
        print 'get symbol data', et-st

        




#str(list(gain1.index)[0])



if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet('QMainWindow{background-color: black;border: 1px solid black;}')
    main = Main()

    main.show()
    sys.exit(app.exec_())