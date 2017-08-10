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
#from matplotlib.finance import candlestick_ohlc, candlestick2_ohlc
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
import StringIO
import time
from datetime import timedelta
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


Ui_MainWindow, QMainWindow = loadUiType('Finance_temp.ui')
class Main(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        st = time.time()
        super(Main, self).__init__(parent)
        self.setupUi(self)   

        self.mdiArea.addSubWindow(self.tech_chart)
        #self.mdiArea.addSubWindow(self.sector_summary)
        self.mdiArea.addSubWindow(self.companysummary)
        #self.mdiArea.addSubWindow(self.financials_window)
        #self.mdiArea.addSubWindow(self.market_summary)

        #Set up technical chart
        '''Sets up the main tech charts'''
        gs1 = gridspec.GridSpec(4, 1)
        gs1.update(left=0.01, right=0.95, top=.98, bottom=0.03,wspace=0,hspace=0)
        self.tech_chart_fig = Figure(facecolor='#191919') 
        self.tech_chart_canvas = FigureCanvas(self.tech_chart_fig)
        self.techchart_layout.addWidget(self.tech_chart_canvas)  
        self.tech_chart_axis = self.tech_chart_fig.add_subplot(gs1[:, :],facecolor='#191919') 
        self.tc_main_search.setText('AAPL')
        self.tc_sec_search1.setText('AAPL')

        gs2 = gridspec.GridSpec(4, 1)
        gs2.update(left=0.01, right=0.95, top=1.0, bottom=0.09,wspace=0,hspace=0)
        self.tech_chart_fig2 = Figure(facecolor='#191919') 
        self.tech_chart_canvas2 = FigureCanvas(self.tech_chart_fig2)
        self.techchart_layout2.addWidget(self.tech_chart_canvas2)  
        self.tech_chart_axis2 = self.tech_chart_fig2.add_subplot(gs2[:, :],facecolor='#191919') 

        gs3 = gridspec.GridSpec(4, 1)
        gs3.update(left=0.01, right=0.95, top=.98, bottom=0.035,wspace=0,hspace=0)
        self.tech_chart_fig3 = Figure(facecolor='#191919') 
        self.tech_chart_canvas3 = FigureCanvas(self.tech_chart_fig3)
        self.techchart_layout3.addWidget(self.tech_chart_canvas3)  
        self.tech_chart_axis3 = self.tech_chart_fig3.add_subplot(gs3[:, :],facecolor='#191919') 

        gs4 = gridspec.GridSpec(4, 1)
        gs4.update(left=0.00, right=0.925, top=1.00, bottom=0.0675,wspace=0,hspace=0)
        self.cs_chart_fig = Figure(facecolor='#323232') 
        self.cs_chart_canvas = FigureCanvas(self.cs_chart_fig)
        self.cs_chart_layout.addWidget(self.cs_chart_canvas)  
        self.cs_chart_axis = self.cs_chart_fig.add_subplot(gs4[:, :],facecolor='#323232') 

        gs5 = gridspec.GridSpec(4, 1)
        gs5.update(left=0.00, right=0.925, top=1.00, bottom=0.0675,wspace=0,hspace=0)
        self.ss_pie_fig = Figure(facecolor='#323232') 
        self.ss_pie_canvas = FigureCanvas(self.ss_pie_fig)
        self.ss_pie_layout.addWidget(self.ss_pie_canvas)  
        self.ss_pie_axis = self.ss_pie_fig.add_subplot(gs5[:, :],facecolor='#323232') 

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

        #Technical chart date buttons
        date_buttons = [self.tc_one_day,self.tc_five_day,self.tc_one_month,self.tc_three_month, self.tc_six_month,
                        self.tc_one_year,self.tc_five_year,self.tc_max_date]
        for b in date_buttons:
            b.clicked.connect(self.tc_date_buttons)

        #Market Summary
        self.ms_gainer_filter.currentIndexChanged.connect(self.ms_gainlose_table)

        #Fiancials Window
        #self.is_rb_1.clicked.connect(self.financial_window)
        #self.is_rb_2.clicked.connect(self.financial_window)
        #self.is_rb_3.clicked.connect(self.financial_window)
        #self.is_rb_4.clicked.connect(self.financial_window)
        #self.is_rb_5.clicked.connect(self.financial_window)
        #self.is_rb_6.clicked.connect(self.financial_window)
        #self.is_rb_7.clicked.connect(self.financial_window)
        #self.is_rb_8.clicked.connect(self.financial_window)
        #self.is_rb_9.clicked.connect(self.financial_window)
        #self.is_rb_10.clicked.connect(self.financial_window)
        #self.is_rb_11.clicked.connect(self.financial_window)
        #self.is_rb_12.clicked.connect(self.financial_window)
        #self.is_rb_13.clicked.connect(self.financial_window)

        #Company Summary 
        self.cs_search.returnPressed.connect(self.company_summary)

        '''comptetitors table'''
        cs_comp_header = [self.cs_sym_0,self.cs_name_0,self.cs_price_0,self.cs_chg_0,self.cs_mrk_0]
        for header in cs_comp_header:
            header.currentIndexChanged.connect(self.cs_competitor_table)
        et = time.time()
        print 'GUI Setup Time:', et-st

        '''historical table edit page'''
        self.cs_hist_edit.setMinimumHeight(0)
        self.cs_hist_edit.setMaximumHeight(0)
        self.cs_hist_oedit.clicked.connect(self.cs_hist_openedit)

        date_buttons = [self.cs_histedit_daily,self.cs_histedit_weekly,self.cs_histedit_monthly,
                        self.cs_histedit_quarterly,self.cs_histedit_yearly]
        for d in date_buttons:
            d.clicked.connect(self.cs_hist_table)

        data = self.get_symbol_data('TSLA')
        recdate = pd.to_datetime(data.index[-1])
        self.cs_hedit_datet.setDate(QtCore.QDate(recdate.year,recdate.month,recdate.day))
        self.cs_hedit_datef.setDate(QtCore.QDate(recdate.year-1,recdate.month,recdate.day))

        hedit_columns = [self.cs_hsearch0,self.cs_hsearch1,self.cs_hsearch2,self.cs_hsearch3,self.cs_hsearch4,
                        self.cs_hsearch5,self.cs_hsearch6,self.cs_hsearch7,self.cs_hsearch8,self.cs_hsearch9,
                        self.cs_hsearch10,self.cs_hsearch11,self.cs_hsearch12,self.cs_hsearch13,self.cs_hsearch14,
                        self.cs_hsearch15,self.cs_hsearch16,self.cs_hsearch17,self.cs_hsearch18,self.cs_hsearch19]
        for h in hedit_columns:
            h.returnPressed.connect(self.cs_hist_table)
        self.cs_hedit_datef.dateChanged.connect(self.cs_hist_table)
        self.cs_hedit_datet.dateChanged.connect(self.cs_hist_table)

        cs_pagesb = [self.cs_smryb,self.cs_histb,self.cs_ratiob,self.cs_finstatb,self.cs_corpinfob]
        for p in cs_pagesb:
            p.clicked.connect(self.cs_pages)

        #start functions
        self.tc_mainsearch() #clears all graph data and plots just the default data
        #self.ms_gainers_loser()
        self.company_summary()
        #self.financial_window()

    def tc_search1(self):
        st = time.time()
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
        et = time.time()
        print 'tc_search1', et-st
        self.tc_mainsearch() ###

    def tc_search2(self):
        st = time.time()
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
        et = time.time()
        print 'tc_search2', et-st

        self.tc_mainsearch()

    def tc_search3(self):
        st = time.time()
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
        et = time.time()
        print 'tc_search3', et-st
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
        print 'tc_compare', et-st

    def tc_mainsearch(self):
        st = time.time()
        '''Fisrt function to be called. sets up the main charts axis and grid then plots 
           the most recent years stock prices of a default company. Called whenever the 
           tech chart main search is used and deletes lines on edit page, and study tab'''

        #hides the search filters and clear the text
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
        dateform = mdates.DateFormatter('%m/%y')
        self.tech_chart_axis.xaxis.set_major_formatter(dateform)
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

        symbol = str(self.tc_main_search.text())
        data = self.get_symbol_data(symbol)

        '''still need to add candlestick'''
        #candlestick2_ohlc(self.tech_chart_axis,data['Open'],data['High'],data['Low'],data['Close'])
        #candlestick_ohlc(self.tech_chart_axis,data[['Open','High','Low','Close','Volume']])

        #sets the graph so the highest and lowest point on the line is 10% away from the edge
        close_min = data['Close'].loc[from_:to_].min()
        close_max = data['Close'].loc[from_:to_].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        self.tech_chart_axis.set_ylim([round(ax1_min,2),round(ax1_max,2)])
        self.tech_chart_axis.plot(data['Close'].loc[from_:to_],lw=5,alpha=0.75,color='#57bcff',linestyle='-')
        self.tech_chart_canvas.draw()

        name = stock_list.loc[stock_list['Symbol']==symbol,'Name']
        name = list(name)
        self.tc_legend_name.setText(str(name[0])+' ('+symbol+')')
        self.tc_legend_price.setText(str(round(data['Close'][-1],2)))
        self.tc_legend_change.setText(str(round(data['Change'][-1],2))+' '+str(round(data['% Change'][-1],3))+'%')
        self.tc_legend_prevclose.setText(str(round(data['Close'][-2],2)))
        self.tc_legend_open.setText(str(round(data['Open'][-1],2)))
        self.tc_legend_high.setText(str(round(data['High'][-1],2)))
        self.tc_legend_low.setText(str(round(data['Low'][-1],2)))
        et = time.time()
        print 'tc_mainsearch', et-st
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
        print 'tc_study1', et-st

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
        print 'tc_study2', et-st
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
        print 'tc_editline1', et-st
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
        print 'tc_editline2', et-st
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
        print 'tc_editline3', et-st
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
        self.tc_set_axis(axis,symbol,fig,'Close',data)
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
        self.tc_set_axis(axis,symbol,fig,'Volume',data)
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
        self.tech_chart_axis = self.tech_chart_fig.add_subplot(gs1[:, :],facecolor=bgcolor) 
        self.tc_main_search.setText('AAPL')
        self.tc_sec_search1.setText('AAPL')

    def tc_set_axis(self,axis,symbol,fig,series,data):
        st = time.time()

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
        print 'tc_set_axis', et-st
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
        #path = "C:\\Users\\ajhau\\Desktop\\Finance Program\\finance5\\program\\Sector_data" #- real
        path = "C:\\Users\\ajhau\\Desktop\\Sector_data" #-test
        if symbol in loaded_symbol_data.keys(): 
            data = loaded_symbol_data[symbol]
            et0 = time.time()
            return data
            print 'get_symbol_data','time0', et0-st0
        else:
            sector = list(stock_list.loc[stock_list['Symbol']==symbol,'Sector'])[0] #get the sector for the symbol
            index_num = sectors.index(sector) #index number for that sector

            #opens the csv for that sector and makes a list for the first row symbols 
            with open(path+'\\'+sec_file_names[index_num]) as f:
                reader = csv.reader(f)
                sec_symbols = next(reader)

            #from that list return the position of the symbols
            sym_ind = [0]
            for i, s in enumerate(sec_symbols):
                if s == symbol:
                    sym_ind.append(i)
                else:
                    pass
            sym_ind = np.array(sym_ind)

            data = pd.read_csv(path+'\\'+sec_file_names[index_num],header=1,index_col=0,usecols=sym_ind)[1:] #load the data for just the symbol called
            data.index = pd.to_datetime(data.index, infer_datetime_format=True) #format='%m/%d/%Y')
            data.columns = [x.split('.')[0] for x in data.columns]
            loaded_symbol_data[symbol] = data

            et0 = time.time()
            print 'get_symbol_data', et0-st0
            return data

    def company_summary(self):  
        st = time.time()
        self.cs_stackedwidget.setCurrentIndex(0)

        symbol = str(self.cs_search.text())
        data = self.get_symbol_data(symbol)

        self.cs_competitors(symbol)
        stock = Share(symbol)
        today_date = datetime.date.today()
        year_date = datetime.datetime(today_date.year-1,today_date.month,today_date.day)
        year_date = year_date.strftime('%Y-%m-%d')

        sym_yclose = round(data['Close'].loc[year_date:today_date][0],2)
        sym_yhigh = round(data['Close'].loc[year_date:today_date].max(),2)
        sym_ylow = round(data['Close'].loc[year_date:today_date].min(),2)
        sym_avgvol = round(data['Volume'].loc[year_date:today_date].mean(),2)
        sym_avgvol = "{:,.0f}".format(int(sym_avgvol))

        sym_open = round(data['Open'][-1],2)
        sym_close = round(data['Close'][-1],2)
        sym_high = round(data['High'][-1],2)
        sym_low = round(data['Low'][-1],2)
        sym_vol = round(data['Volume'][-1],2)
        sym_vol = "{:,.0f}".format(int(sym_vol))

        sym_chg = round(data['Change'][-1],2)
        sym_pchg = round(data['% Change'][-1],2)
        sym_ychg = round(((sym_close - sym_yclose)/sym_yclose)*100,2)
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
        self.cs_ytdchg.setText(str(sym_ychg)+'%')
        self.cs_avgvol.setText(str(sym_avgvol))
        self.cs_mrkcap.setText(str(sym_mrkcap))
        self.cs_sharesout.setText(sym_shares)

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
        self.cs_chart_axis.plot(data['Close'],lw=5,alpha=0.6,color='blue')
        dateform = mdates.DateFormatter('%m/%y')
        self.cs_chart_axis.xaxis.set_major_formatter(dateform)
        #self.cs_chart_axis.tick_params(axis='x',direction='out',pad=100)
    
        axis = self.cs_chart_axis
        fig = self.cs_chart_canvas
        et = time.time()
        print 'company_summary', et-st
        series = 'Close'
        self.tc_set_axis(axis,symbol,fig,series,data)
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
        symbol = str(self.cs_search.text())
        data = self.cs_histable_sort()

        edit_columns = [self.cs_hsearch0,self.cs_hsearch1,self.cs_hsearch2,self.cs_hsearch3,self.cs_hsearch4,
                        self.cs_hsearch5,self.cs_hsearch6,self.cs_hsearch7,self.cs_hsearch8,self.cs_hsearch9,
                        self.cs_hsearch10,self.cs_hsearch11,self.cs_hsearch12,self.cs_hsearch13,self.cs_hsearch14,
                        self.cs_hsearch15,self.cs_hsearch16,self.cs_hsearch17,self.cs_hsearch18,self.cs_hsearch19]
        headers = [str(x.text()) for x in edit_columns]
        col = [x for x in headers if x != '']
        data = data[col]
        self.cs_histable.setRowCount(len(data.index))
        #fill headers
        for d, date in enumerate(data.index):
            item = QtGui.QTableWidgetItem(str(data.index[d]))
            self.cs_histable.setVerticalHeaderItem(d,item)
        for h, header in enumerate(data.columns):
            item = QtGui.QTableWidgetItem(str(data.columns[h]))
            self.cs_histable.setHorizontalHeaderItem(h,item)
        #fill table data
        for c in range(len(col)):
            #replace old/empty data with new data
            for r in range(len(data.index)):
                item = QtGui.QTableWidgetItem('     '+str(data[data.columns[c]][r]))
                self.cs_histable.setItem(r,c,item)
        et = time.time()
        print 'cs_hist_table', et-st

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

    def cs_histable_sort(self):
        '''sorts the data to fit the chosen date range, then formats the data depending
           on if daily weekly monthly quarterly or yearly averages is requested'''
        st = time.time()
        symbol = str(self.cs_search.text())
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
            self.cs_hist_edit.setMinimumHeight(450)
            self.cs_hist_edit.setMaximumHeight(450)
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

        #losers = [[self.ms_loser_sym1,self.ms_loser_sym2,self.ms_loser_sym3,self.ms_loser_sym4,self.ms_loser_sym5],
        #          [self.ms_loser_name1,self.ms_loser_name2,self.ms_loser_name3,self.ms_loser_name4,self.ms_loser_name5],
        #          [self.ms_loser_price1,self.ms_loser_price2,self.ms_loser_price3,self.ms_loser_price4,self.ms_loser_price5]
        #          [self.ms_loser_chg1,ms_loser_chg2,ms_loser_chg3,ms_loser_chg4,ms_loser_chg5]]

        #bottom_five = gain_loss.sort_values('% Change', ascending=False).tail(5)



if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet('QMainWindow{background-color: black;border: 1px solid black;}')
    main = Main()

    main.show()
    sys.exit(app.exec_())









