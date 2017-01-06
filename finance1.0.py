from PyQt4.uic import loadUiType
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas,NavigationToolbar2QT as NavigationToolbar)
import matplotlib.gridspec as gridspec
from matplotlib.widgets import *
import matplotlib.dates as mdates
import matplotlib.finance
from matplotlib.ticker import LinearLocator, MaxNLocator
from matplotlib.dates import AutoDateLocator
import numpy as np
import pandas as pd
from pandas_datareader import data as web
import datetime
from matplotlib.widgets import MultiCursor
import csv

#Sets the data frame for prices and info
all_stocks = pd.DataFrame.from_csv('all_stocks.csv',header=[0,1])
all_stocks.rename(columns={'MA50': 'MA_one'}, inplace=True)
all_stocks.rename(columns={'MA200': 'MA_two'}, inplace=True)
data = all_stocks.round(2)
info = pd.DataFrame.from_csv('stock_info.csv')
con = pd.DataFrame.from_csv('condis.csv',header=[0,1,2]).round(2)

other_search = ['US Bonds','US Economy','Currency','Portfolio']

#Creates a list of strings so search results have sybmol, name, and industry
info['keys'] = info[['Company','Name','Industry']].apply(lambda x: '   '.join(x), axis=1)
keys = list(info['keys'])
keywords = keys+other_search

#Creates a list of company symbols
symb = []
for sym in info['Company']:
    symb.append(sym)

#Creats dataframe of variables and sorted in ascending order
close = []
change = []
pchange = []
mrkcap = []
for com in symb:
    close.append(data[com]['Close'][-1])
    change.append(data[com]['Change'][-1])
    pchange.append(data[com]['% Change'][-1])
    mrkcap.append(data[com]['Mrk Cap'][-1])
gain_loss_dict = {'Close':close, 'Change':change, '% Change':pchange, 'Mrk Cap':mrkcap}
gain_loss_pd = pd.DataFrame(gain_loss_dict, index=symb).sort_values(by='Mrk Cap')
gainer_pd = gain_loss_pd.sort_values(by='% Change',ascending=False)
gainer_pd = gainer_pd.round(2)

loser_pd = gain_loss_pd.sort_values(by='% Change',ascending=True)
loser_pd = loser_pd.round(2)

#Gets the date of today/last row in data
date_e = data.index[-1].to_pydatetime()
year = date_e.year
month = date_e.month
day = date_e.day

start = datetime.date(1975,1,1)
end = datetime.date.today()

sp_index = web.DataReader('^GSPC','yahoo',start, end)
sp_index = sp_index.round(2)
nasdaq_index = web.DataReader('^IXIC','yahoo',start, end)
us_gdp = web.DataReader('GDP','fred',start, end) #quarterly

plottypes = ['Open','High','Low','Close','High/Low Shaded','OHLC Candlestick']

Ui_MainWindow, QMainWindow = loadUiType('new_finance.ui')
class Main(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(Main, self).__init__(parent)
        self.setupUi(self)        
        self.stackedWidget.setCurrentIndex(0)

        #top menu buttons
        self.filehome_pb.clicked.connect(self.startup_page)
        self.fileequity_pb.clicked.connect(self.equity_summary)
        self.filebond_pb.clicked.connect(self.bond_window)
        self.fileecon_pb.clicked.connect(self.econ_window)
        self.filecurrency_pb.clicked.connect(self.currency_window)
        self.fileportfolio_pb.clicked.connect(self.portfolio_window)
        self.fileindex_pb.clicked.connect(self.index_window)

        #start page (search bar,table/graph header buttons)
        searching = QtGui.QStringListModel()
        searching.setStringList(keywords)
        comkey = QtGui.QCompleter()
        comkey.setModel(searching)
        print comkey
        self.start_search_bar.setCompleter(comkey)
        self.start_search_bar.returnPressed.connect(self.searching) #search bar on start page
        self.stock_index_pb.clicked.connect(self.index_window)
        self.econ_graph_pb.clicked.connect(self.econ_window)
        self.currency_pb.clicked.connect(self.currency_window)
        self.bonds_pb.clicked.connect(self.bond_window)

        #Equity page
        self.equity_search_bar.setCompleter(comkey)
        self.equity_search_bar.returnPressed.connect(self.searching) # search bar on equity page
        self.price_chart_pb.clicked.connect(self.historical_chart)
        self.price_hist_pb.clicked.connect(self.historical_table)
        self.hist_graph_edit.clicked.connect(self.edit_hist_graph)

        #historical chart moving averages
        self.ma_one_plot.returnPressed.connect(self.hist_ma_one)
        self.ma_two_plot.returnPressed.connect(self.hist_ma_two)
        self.ma_three_plot.returnPressed.connect(self.hist_ma_three)

        #historical chart date buttons
        self.oned_pb.clicked.connect(self.hist_date_buttons)
        self.threed_pb.clicked.connect(self.hist_date_buttons)
        self.sevend_pb.clicked.connect(self.hist_date_buttons)
        self.onem_pb.clicked.connect(self.hist_date_buttons)
        self.sixm_pb.clicked.connect(self.hist_date_buttons)
        self.oney_pb.clicked.connect(self.hist_date_buttons)
        self.fivey_pb.clicked.connect(self.hist_date_buttons)
        self.teny_pb.clicked.connect(self.hist_date_buttons)
        self.max_range_pb.clicked.connect(self.hist_date_buttons)

        self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        self.hist_date_from.setDate(QtCore.QDate(year-1,month,day))
        self.hist_date_from.dateChanged.connect(self.hist_set_axis)
        self.hist_date_to.dateChanged.connect(self.hist_set_axis)

        #historical chart edit/add company
        ### autocomplete for plot type search bar
        plottypes = ['Open','High','Low','Close','High/Low Shaded','OHLC Candlestick']
        plot_type = QtGui.QStringListModel()
        plot_type.setStringList(plottypes)
        comkey1 = QtGui.QCompleter()
        comkey1.setModel(plot_type)

        studies = ['Bollinger Bands','Trend Lines','Volume','EMA (20d)']
        study = QtGui.QStringListModel()
        study.setStringList(studies)
        comkey2 = QtGui.QCompleter()
        comkey2.setModel(study)

        ###search bar in the hist chart edit to add a second company
        self.hedit_initial_ck.stateChanged.connect(self.hedit_first_company)
        self.hedit_plot_type.setCompleter(comkey1) #search bar for plot type 1
        self.hedit_plot_type.returnPressed.connect(self.hedit_first_company)
        self.hedit_plot_type_ck.stateChanged.connect(self.hedit_first_company)
        self.hedit_add_study.setCompleter(comkey2)
        self.hedit_add_study.returnPressed.connect(self.hedit_first_company)
        self.hedit_study_ck.stateChanged.connect(self.hedit_first_company) #search bar for study 1

        self.hedit_add_company.setCompleter(comkey)
        self.hedit_add_company.returnPressed.connect(self.hist_add_company) 
        self.hedit_add_ck.stateChanged.connect(self.hedit_second_company)
        self.hedit_add_study_2.setCompleter(comkey2)
        self.hedit_add_study_2.returnPressed.connect(self.hedit_second_company)
        self.hedit_plot_type_2.setCompleter(comkey1)
        self.hedit_plot_type_2.returnPressed.connect(self.hedit_second_company)
        #self.hedit_plot_type_ck_2.stateChanged.connect(self.hedit_first_company)
        self.hedit_study_ck_2.stateChanged.connect(self.hedit_second_company) 
        self.compare2.clicked.connect(self.sec_company_summary)

        #index page
        self.index_search_bar.returnPressed.connect(self.searching)
        #self.sp_index_ck.stateChanged.connect(self.index_plot_sp)
        #self.dow_index_ck.stateChanged.connect(self.index_plot_dow)
        #self.nasdaq_index_ck.stateChanged.connect(self.index_plot_nasdaq)

        self.startup_page()

    def searching(self):
        '''Called when something is searched on the start page. Takes what was searched and opens calls
           a function to open the appropriate window
        '''
        
        #If what was searched is not in other_search then its a company
        if str(self.start_search_bar.text()) not in other_search:
            self.equity_summary()
        elif str(self.start_search_bar.text()) == 'US Bonds':
            self.bonds_window()
        elif str(self.start_search_bar.text()) == 'US Economy':
            self.econ_window()        
        elif str(self.start_search_bar.text()) == 'Currency':
            self.currency_window()
        elif str(self.start_search_bar.text()) == 'Portfolio':
            self.portfolio_window()
        
    def startup_page(self):
        '''Start up page is called in _init_ and sets all the info for that page'''
       
        self.stackedWidget.setCurrentIndex(0)

        #Top left stock index graph 
        #Since its a twinx the axis tick had to be set for the second graph
        sindex_axis.plot(sp_index['Close'],color='green',lw=4)
        sindex_axis2 = sindex_axis.twinx()
        sindex_axis2.yaxis.label.set_color("w")
        sindex_axis2.xaxis.label.set_color('w')
        sindex_axis2.spines['bottom'].set_color("w")
        sindex_axis2.spines['top'].set_color("w")
        sindex_axis2.spines['left'].set_color("w")
        sindex_axis2.spines['right'].set_color("w")
        sindex_axis2.tick_params(axis='y', colors='w',labelsize=20)
        sindex_axis2.tick_params(axis='x', colors='w',labelsize=20)
        sindex_axis2.plot(nasdaq_index['Close'],color='orange',lw=4, alpha=0.6)
        sindex_axis.set_ylim([1750,2500])
        sindex_axis.set_xlim([datetime.datetime(year-1,month,day),datetime.datetime(year,month,day-1)])
        sindex_axis.xaxis.set_minor_formatter(mdates.DateFormatter('%m/&y'))

        #Bottom left econ graph
        secon_axis.plot(us_gdp['GDP'],color='green',lw=4,alpha=0.6)
        secon_axis.legend()
        secon_axis.yaxis.tick_right()
        secon_axis.set_xlim([datetime.datetime(year-1,month,day),datetime.datetime(year,month,day-1)])

        #Sets the Gainers Table
        gainers_pd = gainer_pd[:10]
        losers_pd = loser_pd[:10]
        gainHeaders = []
        for column in gainers_pd.columns:
            gainHeaders.append(column)
            self.gainers_table.setHorizontalHeaderLabels(gainHeaders)  
        self.gainers_table.setVerticalHeaderLabels(gainers_pd.index)          
        self.gainers_table.setColumnCount(len(gainers_pd.columns))
        self.gainers_table.setRowCount(len(symb))
        for r, key in enumerate(gainers_pd):
            for c, item in enumerate(gainers_pd[key]):
                newitem = QTableWidgetItem(str(item))
                newitem.setTextAlignment(Qt.AlignCenter)
                self.gainers_table.setItem(c,r, newitem)

        #Sets the Losers Tables
        loserHeaders = []
        for column in losers_pd.columns:
            loserHeaders.append(column)
            self.losers_table.setHorizontalHeaderLabels(loserHeaders)  
        self.losers_table.setVerticalHeaderLabels(losers_pd.index)          
        self.losers_table.setColumnCount(len(losers_pd.columns))
        self.losers_table.setRowCount(len(symb))
        for r, key in enumerate(losers_pd):
            for c, item in enumerate(losers_pd[key]):
                newitem = QTableWidgetItem(str(item))
                newitem.setTextAlignment(Qt.AlignCenter)
                self.losers_table.setItem(c,r, newitem)

    def equity_summary(self):
        '''Called when the start up page search is for a company and sets the Summary page and Chart page
           info for the company that was searched for
        '''
        self.stackedWidget.setCurrentIndex(1)
        
        #Gets each item in the search bar
        name, symbol, industry = self.symbolFunction(self.start_search_bar.text())

        #Sets the equity search bar to what was searched on start page
        self.equity_search_bar.setText(str(self.start_search_bar.text()))

        #Gets the date a year ago from most recent date in data
        one_year = datetime.date(year-1,month,day-1)
        one_yr_ind = one_year.strftime('%Y-%m-%d')
        today_date = data.index[-1].strftime('%m/%d/%y')

        #Data  for the price lables
        price = data[symbol]['Close'][-1]
        pchg = data[symbol]['% Change'][-1]
        volume = data[symbol]['Volume'][-1]
        open = data[symbol]['Open'][-1]
        high = data[symbol]['High'][-1]
        low = data[symbol]['Low'][-1]
        value = data[symbol]['Mrk Cap'][-1]
        yr_high = max(data[symbol]['Close'][-258:])
        yr_low = min(data[symbol]['Close'][-258:])
        price_chg = str(price)+'/'+str(pchg)
        year_price = data[symbol]['Close'].loc[one_yr_ind]
        ytd_chg = ((price-year_price)/year_price)*100.0

        #Fill in summary labels
        self.com_name.setText(name)
        self.com_price.setText(str(price))
        self.com_chg.setText(str(pchg))
        self.vol_label.setText(str(volume))
        self.open_label.setText(str(open))
        self.high_label.setText(str(high))
        self.low_label.setText(str(low))
        self.value_label.setText(str(value))

        #Change the color to green if positive, red if negative
        if pchg > 0:
            self.equity_updown_sign.setText('+')
            self.equity_updown_sign.setStyleSheet('color:green')
            self.com_price.setStyleSheet('color:green')
            self.com_chg.setStyleSheet('color:green')
            self.equity_percent_sign.setStyleSheet('color:green')
        else:
            self.equity_updown_sign.setText('-')
            self.equity_updown_sign.setStyleSheet('color:red')
            self.com_price.setStyleSheet('color:red')
            self.com_chg.setStyleSheet('color:red')
            self.equity_percent_sign.setStyleSheet('color:red')
        
        #Fill in bottom summary labels
        self.price_chg_label.setText(str(price_chg))
        self.day_high_label.setText(str(high))
        self.day_low_label.setText(str(low))
        self.year_low_label.setText(str(yr_low))
        self.year_high_label.setText(str(yr_high))
        self.year_chg_label.setText(str(ytd_chg))
        self.cap_label.setText(str(value))

        #Plot the closing price for the last year
        ##Change the number of ticks on the x and y axis
        esum_axis.xaxis.set_major_locator(AutoDateLocator(minticks=10))
        esum_axis.yaxis.set_major_locator(LinearLocator(10))
        date_form = mdates.DateFormatter('%m/%d/%y')
        esum_axis.xaxis.set_major_formatter(date_form)

        esum_axis.plot(data[symbol]['Close'],color='green',lw=4, alpha=0.6)
        esum_axis.yaxis.tick_right()
        esum_axis.set_xlim([datetime.datetime(year-1,month,day),datetime.datetime(year,month,day-1)])

        #Realign Y-axis to center the graph lines
        close_min = data[symbol]['Close'].loc[one_yr_ind:today_date].min()
        close_max = data[symbol]['Close'].loc[one_yr_ind:today_date].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        esum_axis.set_ylim([ax1_min,ax1_max])
        ehist_axis.set_ylim([ax1_min,ax1_max])
        self.ehist_canvas.draw()

        #Fill in company price table for last 10 days
        columns = ['Close','Change','Mrk Cap']
        self.price_hist_table.setHorizontalHeaderLabels(columns)   
        dates = data.index[-11:][::-1].strftime('%m/%d/%y')
        date_list = []
        for d in dates:
            date_list.append(d)
            self.price_hist_table.setVerticalHeaderLabels(date_list)          
        self.price_hist_table.setColumnCount(len(columns))
        self.price_hist_table.setRowCount(len(range(1,10)))
        for r, key in enumerate(data[symbol][['Close','% Change','Mrk Cap']][-11:]):
            for c, item in enumerate(data[symbol][key].iloc[::-1]):
                newitem = QTableWidgetItem(str(item))
                newitem.setTextAlignment(Qt.AlignCenter)
                self.price_hist_table.setItem(c,r, newitem)
        
        #Opens the equity summary page
        self.equity_tab.setCurrentIndex(0)

        #Sets the histotical chart page 
        self.historical_chart()

    def symbolFunction(self, search_bar):
        if search_bar != '':
            key = str(search_bar).split('   ')
            symbol = key[0]
            name= key[1]
            industry = key[2]

        return name, symbol, industry

    def historical_chart(self):
        '''Called in the equity_summary function. Plots the Histrical Chart'''

        self.equity_tab.setCurrentIndex(1)
        
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())

        #Sets the search bar and check buttons on the historical chart edit popup
        self.hedit_initial_company.setText(str(name))
        self.hedit_initial_ck.stateChanged.disconnect()
        self.hedit_plot_type_ck.stateChanged.disconnect()
        self.hedit_initial_ck.setChecked(True)
        self.hedit_plot_type_ck.setChecked(True)

        #Make plot and study search bar invisble for second company
        #Becomes visible when the second company is added
        self.hedit_plot_type_ck_2.setGeometry(110,395,31,0)
        self.hedit_plot_type_2.setGeometry(140,395,371,0)

        self.hedit_study_ck_2.setGeometry(110,435,31,0)
        self.hedit_add_study_2.setGeometry(140,440,371,0)

        ##Change the number of ticks on the x and y axis
        ehist_axis.xaxis.set_major_locator(AutoDateLocator(minticks=15))
        ehist_axis.yaxis.set_major_locator(LinearLocator(15))
        date_form = mdates.DateFormatter('%m/%d/%y')
        ehist_axis.xaxis.set_major_formatter(date_form)

        #Plots the closing price for the past year
        '''hist_stock_graph geometry(-65,85,3051,1581)'''
        ehist_axis.plot(data[symbol]['Close'],color='green',lw=5,alpha=0.6) # put try/except here for wrong symbol
        ehist_axis.yaxis.tick_right()
        ehist_axis.set_xlim([datetime.datetime(year-1,month,day),datetime.datetime(year,month,day-1)])

        #Hide the other Legend lines not plotted
        self.legend_box.setGeometry(2240,120,581,70)
        self.leg_two_color.setGeometry(0,0,0,0)
        self.leg_three_color.setGeometry(0,0,0,0)
        self.leg_four_color.setGeometry(0,0,0,0)

        self.legend_linetwo.setGeometry(0,0,0,0)
        self.legend_linethree.setGeometry(0,0,0,0)
        self.legend_linefour.setGeometry(0,0,0,0)

        self.legend_two_price.setGeometry(0,0,0,0)
        self.legend_three_price.setGeometry(0,0,0,0)
        self.legend_four_price.setGeometry(0,0,0,0)

        #Hide second company legend
        self.legend_second_name.setGeometry(0,0,0,0)
        self.legend_sec_pchg.setGeometry(0,0,0,0)

        self.leg_sec_one_color.setGeometry(0,0,0,0)
        self.leg_sec_two_color.setGeometry(0,0,0,0)
        self.leg_sec_three_color.setGeometry(0,0,0,0)
        self.leg_sec_four_color.setGeometry(0,0,0,0)

        self.legend_sec_lineone.setGeometry(0,0,0,0)
        self.legend_sec_linetwo.setGeometry(0,0,0,0)
        self.legend_sec_linethree.setGeometry(0,0,0,0)
        self.legend_sec_linefour.setGeometry(0,0,0,0)

        self.legend_sec_one_price.setGeometry(0,0,0,0)
        self.legend_sec_two_price.setGeometry(0,0,0,0)
        self.legend_sec_three_price.setGeometry(0,0,0,0)
        self.legend_sec_four_price.setGeometry(0,0,0,0)

        self.compare1.setText(str(symbol)+'+'+str(round(data[symbol]['Change'][-1],2)))
        self.hist_legend()
        self.ehist_canvas.draw()        

    def hist_legend(self):
        #Data for the first compant
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())
        closing = data[symbol]['Close'][-1]
        low = data[symbol]['Low'][-1]
        high = data[symbol]['High'][-1]
        open = data[symbol]['Open'][-1]
        pchg = data[symbol]['% Change'][-1]

        #Data for the second company
        #sec_name, sec_symbol, sec_industry = self.symbolFunction(self.hedit_add_company.text())
        #sec_closing = data[sec_symbol]['Close'][-1]
        #sec_low = data[sec_symbol]['Low'][-1]
        #sec_high = data[sec_symbol]['High'][-1]
        #sec_open = data[sec_symbol]['Open'][-1]
        #sec_pchg = data[sec_symbol]['% Change'][-1]

        '''The first company is always show so the first to lines in the legend will
           always be there, this is to change the label and price'''
        if self.hist_graph_edit.text() == '>>>':
            self.legend_box.setGeometry(1420,120,581,171)
        elif self.hist_graph_edit.text() == '<<<':
            self.legend_box.setGeometry(2240,120,581,171)

        if self.hedit_initial_ck.isChecked():
            self.legend_first_name.setText(str(name+' '+'('+symbol+')'))
            self.legend_pchg.setText(str(pchg))
            if self.hedit_plot_type.text() == 'Close':
                self.legend_lineone.setText('Closing Price')
                self.legend_one_price.setText(str(closing))
            elif self.hedit_plot_type.text() == 'Open':
                self.legend_lineone.setText('Opening Price')
                self.legend_one_price.setText(str(open))
            elif self.hedit_plot_type.text() == 'High':
                self.legend_lineone.setText('Highest Price')
                self.legend_one_price.setText(str(high))
            elif self.hedit_plot_type.text() == 'Low':
                self.legend_lineone.setText('Lowest Price')
                self.legend_one_price.setText(str(low))
            elif self.hedit_plot_type.text() == 'High/Low Shaded':
                self.legend_lineone.setText('High/Low Shaded')
                self.legend_one_price.setText('')
            else:
                pass

            '''If boll bands are selected then that takes 3 extra lines in the legend
                EMA is 1 extra line. If study check isnt checked then the legend box is 
                adjusted to fit just to top 2 lines'''
            if self.hedit_study_ck.isChecked():
                if self.hedit_add_study.text() == 'Bollinger Bands':
                    self.leg_two_color.setGeometry(60,73,25,25)
                    self.leg_three_color.setGeometry(60,103,25,25) 
                    self.leg_four_color.setGeometry(60,133,25,25)

                    self.legend_linetwo.setGeometry(100,70,341,30)
                    self.legend_linethree.setGeometry(100,100,341,30)
                    self.legend_linefour.setGeometry(100,130,341,30)

                    self.legend_two_price.setGeometry(450,70,101,30)
                    self.legend_three_price.setGeometry(450,100,101,30)
                    self.legend_four_price.setGeometry(450,130,101,30)

                elif self.hedit_add_study.text() == 'EMA (20d)':
                    #self.legend_box.setGeometry(1420,120,581,101)
                    self.leg_two_color.setGeometry(60,73,25,25)
                    self.leg_two_color.setStyleSheet('color:blue')
                    self.legend_linetwo.setGeometry(100,70,341,30)
                    self.legend_two_price.setGeometry(450,70,101,30)
                    self.legend_linetwo.setText('EMA (20d)')
                else:
                    pass
            else:
                if  self.hist_graph_edit.text() == '>>>':
                    self.leg_two_color.setGeometry(0,0,0,0)
                    self.leg_three_color.setGeometry(0,0,0,0)
                    self.leg_four_color.setGeometry(0,0,0,0)

                    self.legend_linetwo.setGeometry(0,0,0,0)
                    self.legend_linethree.setGeometry(0,0,0,0)
                    self.legend_linefour.setGeometry(0,0,0,0)

                    self.legend_two_price.setGeometry(0,0,0,0)
                    self.legend_three_price.setGeometry(0,0,0,0)
                    self.legend_four_price.setGeometry(0,0,0,0)
                else:
                    self.leg_two_color.setGeometry(0,0,0,0)
                    self.leg_three_color.setGeometry(0,0,0,0)
                    self.leg_four_color.setGeometry(0,0,0,0)

                    self.legend_linetwo.setGeometry(0,0,0,0)
                    self.legend_linethree.setGeometry(0,0,0,0)
                    self.legend_linefour.setGeometry(0,0,0,0)

                    self.legend_two_price.setGeometry(0,0,0,0)
                    self.legend_three_price.setGeometry(0,0,0,0)
                    self.legend_four_price.setGeometry(0,0,0,0)
        else:
            pass

    def hist_add_company(self):
        '''Called when a second company is searched for from the graph edit. Sets the plot and
           and study search bars and graph for the second company. Calls hedit_second_company to 
           plot the second comapny
        '''

        name, symbol, industry = self.symbolFunction(self.hedit_add_company.text())

        #Makes the plot type and study search bar visible for second company and checked
        #Setting add_ck to checked calls hedit_second_company to plot
        self.hedit_add_ck.stateChanged.disconnect()
        self.hedit_add_ck.setChecked(True)
        self.hedit_add_ck.stateChanged.connect(self.hedit_second_company)
        self.hedit_plot_type_ck_2.setChecked(True)
        self.hedit_plot_type_ck_2.setGeometry(110,395,31,40)
        self.hedit_plot_type_2.setGeometry(140,395,371,40)
        self.hedit_study_ck_2.setGeometry(110,435,31,40)
        self.hedit_add_study_2.setGeometry(140,440,371,40)

        #Plots close for new company
        ehist_axis2.plot(data[symbol]['Close'],color='yellow',lw=5,alpha=0.6) # put try/except here for wrong symbol
        ehist_axis2.set_xlim([datetime.datetime(year-1,month,day),datetime.datetime(year,month,day-1)])

        #Brings the second y axis to the right of the first company
        ehist_axis2.spines['right'].set_position(('outward', 80))
        ehist_axis2.set_frame_on(True)
        ehist_axis2.patch.set_visible(False)
        ehist_axis2.spines["right"].set_visible(True)
        ehist_axis2.spines['right'].set_color("w")
        ehist_axis2.yaxis.set_ticks_position('right')
        ehist_axis2.tick_params(axis='y', colors='yellow',labelsize=20)

        #Change the number of ticks on the x and y axis
        ehist_axis2.xaxis.set_major_locator(AutoDateLocator(minticks=15))
        ehist_axis2.yaxis.set_major_locator(LinearLocator(15))
        date_form = mdates.DateFormatter('%m/%d/%y')
        ehist_axis2.xaxis.set_major_formatter(date_form)

        #Create box with second company symbol and daily change
        self.compare2.setGeometry(780,70,150,46)
        if data[symbol]['Change'][-1] > 0:
            self.compare2.setText(str(symbol)+'+'+str(round(data[symbol]['Change'][-1],2)))
        else:
            self.compare2.setText(str(symbol)+'-'+str(round(data[symbol]['Change'][-1],2)))

        #Resize hist graph to fit the double y axis 
        self.hist_stock_graph.setGeometry(-23,93,2300,1581)
        self.hist_set_axis()
        self.ehist_canvas.draw()

    def sec_company_summary(self):
        company2 = str(self.hedit_add_company.text())
        #self.compare2.setGeometry(780,120,0,46)
        #self.hist_stock_graph.setGeometry(-65,135,3051,1531)
        self.start_search_bar.setText(str(company2))
        self.equity_summary()    
    
    def hist_date_buttons(self):
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())

        '''When a date button is pressed it changes the QtdateEdits to the date range 
           selected. Whenever the QtdateEdit is changed the set_axis function is called
           which sets the x axis to match the date range and then resizes the y axis to
           to center the graph lines
        '''
        if self.oned_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year,month,day-1))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.threed_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year,month,day-3))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.sevend_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year,month,day-7))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.onem_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year,month-1,day))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.sixm_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year,month-6,day))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.oney_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year-1,month,day))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.fivey_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year-5,month,day))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.teny_pb.isChecked():
            self.hist_date_from.setDate(QtCore.QDate(year-10,month,day))
            self.hist_date_to.setDate(QtCore.QDate(year,month,day))
        elif self.max_range_pb.isChecked():
            #gets the first data value is the dataframe
            start_date = data[symbol].first_valid_index().to_pydatetime()
            start_year = start_date.year
            start_month = start_date.month
            start_day = start_date.day
            self.hist_date_from.setDate(QtCore.QDate(start_year,start_month,start_day))

    def edit_hist_graph(self):
        '''When the graph edit is click it opens the side window when its clicked again
           the side window is closed
        '''
        if self.hist_graph_edit.isChecked():
            self.hist_spacer.setGeometry(630,70,1611,46)
            self.hist_stock_graph.setGeometry(-23,93,2260,1581)
            self.hist_graph_edit.setGeometry(2150,70,81,41)
            self.tree_frame.setGeometry(2240,110,731,1551)
            self.graph_edit_header.setGeometry(2240,70,731,46)
            self.hist_graph_edit.setText('>>>')

            date_form = mdates.DateFormatter('%m/%y')
            ehist_axis.xaxis.set_major_formatter(date_form)
        else:
            self.hist_spacer.setGeometry(630,70,2341,46)
            self.hist_graph_edit.setGeometry(2870,70,81,41)
            self.hist_stock_graph.setGeometry(-23,93,3010,1581)
            self.tree_frame.setGeometry(2240,110,0,0)
            self.graph_edit_header.setGeometry(2260,70,0,0)
            self.hist_graph_edit.setText('<<<')

            date_form = mdates.DateFormatter('%m/%d/%y')
            ehist_axis.xaxis.set_major_formatter(date_form)

        self.hist_legend()

    def hedit_first_company(self):
        '''Called when any of the first company search bars or check buttons are changed
           in the graph edit side window. Plots what ever is in each of the search bars
        '''
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())

        ehist_axis.clear()
        ehist_axis.xaxis.set_major_locator(AutoDateLocator(minticks=15))
        ehist_axis.yaxis.set_major_locator(LinearLocator(15))
        ehist_axis.grid(True, which='major', color='w', linestyle='--')  
        #If the top two search bars are checked then it will plot whats in the plot type search bar
        #If either of the top two search bars arw unchecked then the first company plots are deleted
        if self.hedit_initial_ck.isChecked():
            if self.hedit_plot_type_ck.isChecked():
                if self.hedit_plot_type.text() == 'Close':
                    ehist_axis.plot(data[symbol]['Close'],color='green',lw=5,alpha=0.6)
                elif self.hedit_plot_type.text() == 'Open':
                    ehist_axis.plot(data[symbol]['Open'],color='green',lw=5,alpha=0.6)
                elif self.hedit_plot_type.text() == 'High':
                    ehist_axis.plot(data[symbol]['High'],color='green',lw=5,alpha=0.6)
                elif self.hedit_plot_type.text() == 'Low':
                    ehist_axis.plot(data[symbol]['Low'],color='green',lw=5,alpha=0.6)
                elif self.hedit_plot_type.text() == 'High/Low Shaded':
                    ehist_axis.plot(data[symbol]['Close'],color='green',lw=5,alpha=0.6)
                    ehist_axis.plot(data[symbol]['High'],color='green',lw=3, alpha=0.5)
                    ehist_axis.plot(data[symbol]['Low'],color='red',lw=3, alpha=0.5)
                    ehist_axis.fill_between(data.index, data[symbol]['High'], data[symbol]['Close'], facecolor='green', alpha=0.4)
                    ehist_axis.fill_between(data.index, data[symbol]['Low'], data[symbol]['Close'], facecolor='red', alpha=0.4)
                elif self.hedit_plot_type.text() == 'OHLC Candlestick':
                    matplotlib.finance.candlestick_ohlc(ehist_axis,data[symbol]['Open'],data[symbol]['High'],data[symbol]['Low'],data[symbol]['Close'], width=6, colorup='green', colordown='red', alpha=0.75)
            else:
                del ehist_axis.lines[0:]
                self.hist_replot()

            #Adds as study when selected
            if self.hedit_study_ck.isChecked():
                if self.hedit_add_study.text() == 'Bollinger Bands':
                    self.hist_boll_bands(ehist_axis,symbol)
                elif self.hedit_add_study.text() == 'EMA (20d)':
                    ema = pd.ewma(data[symbol]['Close'],com=9.5)
                    ehist_axis.plot(ema,color='blue',lw=3, alpha=0.5)
                #elif self.hedit_add_study.text() == 'Volume':
                #    self.hist_stock_bgraph()
                #    ehist_baxis.plot(data[symbol]['Volume'],color='green',lw=5,alpha=0.6)
                #else:
                #    self.hist_stock_graph.setGeometry(-65,135,3051,1531)
                #    self.hist_bottom_graph.setGeometry(-65,1259,3051,0)
            else:
                del ehist_axis.lines[0:]
                self.hist_replot()
        else:
            del ehist_axis.lines[0:]
            self.hist_replot()

        #Sets the axis so graph lines are centered
        self.hist_legend()
        self.hist_set_axis()
        self.ehist_canvas.draw()        

    def hedit_second_company(self):
        '''Same logic as hedit_first_company'''
        name, symbol, industry = self.symbolFunction(self.hedit_add_company.text())

        ehist_axis2.clear()

        #Set the tick lines and grid
        ehist_axis2.xaxis.set_major_locator(AutoDateLocator(minticks=15))
        ehist_axis2.yaxis.set_major_locator(LinearLocator(15))
        ehist_axis2.grid(True, which='major', color='w', linestyle='--')  

        if self.hedit_add_ck.isChecked():
            if self.hedit_plot_type_ck_2.isChecked():
                if self.hedit_plot_type_2.text() == 'Close':
                    ehist_axis2.plot(data[symbol]['Close'],color='yellow',lw=5,alpha=0.6)
                elif self.hedit_plot_type_2.text() == 'Open':
                    ehist_axis2.plot(data[symbol]['Open'],color='yellow',lw=5,alpha=0.6)
                elif self.hedit_plot_type_2.text() == 'High':
                    ehist_axis2.plot(data[symbol]['High'],color='yellow',lw=5,alpha=0.6)
                elif self.hedit_plot_type_2.text() == 'Low':
                    ehist_axis2.plot(data[symbol]['Low'],color='yellow',lw=5,alpha=0.6)
                elif self.hedit_plot_type_2.text() == 'High/Low Shaded':
                    ehist_axis2.plot(data[symbol]['Close'],color='yellow',lw=5,alpha=0.6)
                    ehist_axis2.plot(data[symbol]['High'],color='green',lw=3, alpha=0.5)
                    ehist_axis2.plot(data[symbol]['Low'],color='red',lw=3, alpha=0.5)
                    ehist_axis2.fill_between(data.index, data[symbol]['High'], data[symbol]['Close'], facecolor='green', alpha=0.4)
                    ehist_axis2.fill_between(data.index, data[symbol]['Low'], data[symbol]['Close'], facecolor='red', alpha=0.4)
            else:
                del ehist_axis2.lines[0:]
                self.hist_replot()

            if self.hedit_study_ck_2.isChecked():
                if self.hedit_add_study_2.text() == 'Bollinger Bands':
                    self.hist_boll_bands(ehist_axis2,symbol)
                elif self.hedit_add_study_2.text() == 'EMA (20d)':
                    ema = pd.ewma(data[symbol]['Close'],com=9.5)
                    ehist_axis2.plot(ema,color='blue',lw=3, alpha=0.5)
                #elif self.hedit_add_study.text() == 'Volume':
                #    self.hist_stock_bgraph()
                #    ehist_baxis.plot(data[symbol]['Volume'],color='green',lw=5,alpha=0.6)
                #else:
                #    self.hist_stock_graph.setGeometry(-65,135,3051,1531)
                #    self.hist_bottom_graph.setGeometry(-65,1259,3051,0)
            else:
                pass
        else:
            del ehist_axis2.lines[0:]

            self.hedit_plot_type_ck_2.setChecked(False)
            self.hedit_add_company.setText('')
            self.hedit_plot_type_ck_2.setGeometry(110,395,31,0)
            self.hedit_plot_type_2.setGeometry(140,395,371,0)
            self.hedit_study_ck_2.setGeometry(110,435,31,0)
            self.hedit_add_study_2.setGeometry(140,440,371,0)

            self.hist_stock_graph.setGeometry(-23,93,3051,1581)
            ehist_axis2.axes.get_xaxis().set_ticklabels([])
            ehist_axis2.axes.get_yaxis().set_ticklabels([])
            
            self.hist_replot()
        self.hist_set_axis()
        self.ehist_canvas.draw()   

    def hist_ma_one(self):
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())
        if self.ma_one_plot.text() != '':
            ma1 = self.ma_one_plot.text()
            ma_one = data[symbol]['Close'].rolling(window=int(ma1)).mean()
            ehist_axis.plot(ma_one,color='orange',lw=3,alpha=0.5)
            self.ehist_canvas.draw()
        else:
            self.hist_replot()

    def hist_ma_two(self):
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())

        if self.ma_two_plot.text() != '':
            ma2 = self.ma_two_plot.text()
            ma_two = data[symbol]['Close'].rolling(window=int(ma2)).mean()
            ehist_axis.plot(ma_two,color='yellow',lw=3,alpha=0.5)
            self.ehist_canvas.draw()
        else:
            self.hist_replot()

    def hist_ma_three(self):
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())

        if self.ma_three_plot.text() != '':
            ma3 = self.ma_three_plot.text()
            ma_three = data[symbol]['Close'].rolling(window=int(ma3)).mean()
            ehist_axis.plot(ma_three,color='red',lw=3,alpha=0.5)
            self.ehist_canvas.draw()
        else:
            self.hist_replot()

    def hist_boll_bands(self,axis,symbol):
        #std dev of the last 20 days
        std_dev = data[symbol]['Close'][-20:].std()
        sma = data[symbol]['Close'].rolling(window=20).mean()
        upper_band = sma + (std_dev*2)
        lower_band = sma - (std_dev*2)
        axis.plot(sma,color='white',lw=4,alpha=0.5)
        axis.plot(upper_band,color='purple',lw=2,alpha=0.5)
        axis.plot(lower_band,color='yellow',lw=2,alpha=0.5)
        self.ehist_canvas.draw()

    def hist_set_axis(self):
        '''Centers the grpah lines and sets the date range x axis when ever changed'''
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())

        key = str(self.hedit_add_company.text())

        #Gets the dates from the QtdateEdits
        from_year = self.hist_date_from.date().year()
        from_month = self.hist_date_from.date().month()
        from_day = self.hist_date_from.date().day()
        to_year = self.hist_date_to.date().year()
        to_month = self.hist_date_to.date().month()
        to_day = self.hist_date_to.date().day()

        #Sets the x axis on the greaph
        ehist_axis.set_xlim([datetime.datetime(from_year,from_month,from_day,9,0,0),datetime.datetime(to_year,to_month,to_day-1,17,0,0)])

        #Format the QtdateEdit to us in index
        from_ = datetime.date(from_year,from_month,from_day)
        to_ = datetime.datetime(to_year,to_month,to_day)
        from_index = from_.strftime('%Y-%m-%d')
        to_index = to_.strftime('%Y-%m-%d')

        #Sets the y-axis max and min based on high and low
        close_min = data[symbol]['Close'].loc[from_index:to_index].min()
        close_max = data[symbol]['Close'].loc[from_index:to_index].max()
        close_diff = float(close_max - close_min)
        ax1_min = float(close_min - (close_diff*0.10))
        ax1_max = float(close_max + (close_diff*0.10))
        ehist_axis.set_ylim([ax1_min,ax1_max])

        #Sets the y-axis for second company if searched for
        if self.hedit_add_company.text() != '':
            #Gets the symbol and name from search bar
            key = str(self.hedit_add_company.text()).split('   ')
            symbol2 = key[0]
            name= key[1]
            print 'something'
            close_min2 = data[symbol2]['Close'].loc[from_index:to_index].min()
            close_max2 = data[symbol2]['Close'].loc[from_index:to_index].max()
            close_diff2 = float(close_max2 - close_min2)
            ax1_min2 = float(close_min2 - (close_diff2*0.10))
            ax1_max2 = float(close_max2 + (close_diff2*0.10))
            ehist_axis2.set_ylim([ax1_min2,ax1_max2])
            ehist_axis2.set_xlim([datetime.datetime(from_year,from_month,from_day,9,0,0),datetime.datetime(to_year,to_month,to_day-1,17,0,0)])
        else:
            pass

        #Unchecks all the date buttons so another can be selected
        date_buttons = [self.oned_pb,self.threed_pb,self.sevend_pb,self.onem_pb,self.sixm_pb,self.oney_pb,self.fivey_pb,self.teny_pb,self.max_range_pb]
        for b in date_buttons:
            b.setChecked(False)
        self.ehist_canvas.draw() 

    def hist_replot(self):
        '''When a graph line has to be deleted, all the lines are deleted then this is called so
           whatever wasnt suppose to be deleted is re plotted
        '''
        name, symbol, industry = self.symbolFunction(self.equity_search_bar.text())

        #Delete everything
        del ehist_axis.lines[0:]
        del ehist_axis2.lines[0:]

        #Checks if the fisrt company should be plotted
        if self.hedit_plot_type_ck.isChecked():
            if self.hedit_plot_type.text() == 'Close':
                ehist_axis.plot(data[symbol]['Close'],color='green',lw=5,alpha=0.6)
            elif self.hedit_plot_type.text() == 'Open':
                ehist_axis.plot(data[symbol]['Open'],color='green',lw=5,alpha=0.6)
            elif self.hedit_plot_type.text() == 'High':
                ehist_axis.plot(data[symbol]['High'],color='green',lw=5,alpha=0.6)
            elif self.hedit_plot_type.text() == 'Low':
                ehist_axis.plot(data[symbol]['Low'],color='green',lw=5,alpha=0.6)
            elif self.hedit_plot_type.text() == 'High/Low Shaded':
                ehist_axis.plot(data[symbol]['Close'],color='green',lw=5,alpha=0.6)
                ehist_axis.plot(data[symbol]['High'],color='green',lw=3, alpha=0.5)
                ehist_axis.plot(data[symbol]['Low'],color='red',lw=3, alpha=0.5)
                ehist_axis.fill_between(data.index, data[symbol]['High'], data[symbol]['Close'], facecolor='green', alpha=0.4)
                ehist_axis.fill_between(data.index, data[symbol]['Low'], data[symbol]['Close'], facecolor='red', alpha=0.4)
            elif self.hedit_plot_type.text() == 'OHLC Candlestick':
                matplotlib.finance.candlestick_ohlc(ehist_axis,data[symbol]['Open'],data[symbol]['High'],data[symbol]['Low'],data[symbol]['Close'], width=6, colorup='green', colordown='red', alpha=0.75)
        else:
            pass           

        #Checks if the second company should be plotted
        if self.hedit_plot_type_ck_2.isChecked():
            name, symbol, industry = self.symbolFunction(self.hedit_add_company.text())
            if self.hedit_plot_type_2.text() == 'Close':
                ehist_axis2.plot(data[symbol]['Close'],color='yellow',lw=5,alpha=0.6)
            elif self.hedit_plot_type_2.text() == 'Open':
                ehist_axis2.plot(data[symbol]['Open'],color='yellow',lw=5,alpha=0.6)
            elif self.hedit_plot_type_2.text() == 'High':
                ehist_axis2.plot(data[symbol]['High'],color='yellow',lw=5,alpha=0.6)
            elif self.hedit_plot_type_2.text() == 'Low':
                ehist_axis2.plot(data[symbol]['Low'],color='yellow',lw=5,alpha=0.6)
            elif self.hedit_plot_type_2.text() == 'High/Low Shaded':
                ehist_axis2.plot(data[symbol]['Close'],color='yellow',lw=5,alpha=0.6)
                ehist_axis2.plot(data[symbol]['High'],color='green',lw=3, alpha=0.5)
                ehist_axis2.plot(data[symbol]['Low'],color='red',lw=3, alpha=0.5)
                ehist_axis2.fill_between(data.index, data[symbol]['High'], data[symbol]['Close'], facecolor='green', alpha=0.4)
                ehist_axis2.fill_between(data.index, data[symbol]['Low'], data[symbol]['Close'], facecolor='red', alpha=0.4)
        else:
            pass          

        #Checks if the moving averages should be plotted
        if self.ma_one_plot.text() != '':
            ma1 = self.ma_one_plot.text()
            ma_one = data[symbol]['Close'].rolling(window=int(ma1)).mean()
            ehist_axis.plot(ma_one,color='orange',lw=3,alpha=0.5)
        else:
            self.ma_one_plot.setText('')
        if self.ma_two_plot.text() != '':
            ma2 = self.ma_two_plot.text()
            ma_two = data[symbol]['Close'].rolling(window=int(ma2)).mean()
            ehist_axis.plot(ma_two,color='orange',lw=3,alpha=0.5)
        else:
            self.ma_two_plot.setText('')
        if self.ma_two_plot.text() != '':
            ma3 = self.ma_three_plot.text()
            ma_three = data[symbol]['Close'].rolling(window=int(ma3)).mean()
            ehist_axis.plot(ma_three,color='orange',lw=3,alpha=0.5)
        else:
            self.ma_three_plot.setText('')
        if self.hedit_add_company.text() != '':
            self.hist_add_company()
        else:
            pass
        self.hist_set_axis()
        self.ehist_canvas.draw()
            
    def index_window(self):
        self.stackedWidget.setCurrentIndex(2)

        one_year = datetime.date(year-1,month,day-1)
        one_yr_ind = one_year.strftime('%Y-%m-%d')
        today_date = sp_index.index[-1].strftime('%m/%d/%y')

        sp_close = sp_index['Close'][-1]
        sp_yrclose = sp_index['Close'].loc[one_yr_ind]
        sp_open = sp_index['Open'][-1]
        sp_high = sp_index['High'][-1]
        sp_yrhigh = sp_index['High'].loc[one_yr_ind]

        sp_low = sp_index['Low'][-1]
        sp_yrlow = sp_index['Low'].loc[one_yr_ind]
        sp_chg = sp_close - sp_open
        sp_pchg = sp_chg/sp_close
        sp_vol = sp_index['Volume'][-1]
        
        self.sp_chg.setText(str(sp_chg))
        self.sp_pchg.setText(str(sp_pchg))

        self.sp_rlow.setText(str(sp_low))
        self.sp_rhigh.setText(str(sp_high))

        self.sp_yrlow.setText(str(sp_yrlow))
        self.sp_yrhigh.setText(str(sp_yrhigh))
        self.sp_open.setText(str(sp_open))
        self.sp_volume.setText(str(sp_vol))

    #def hist_stock_bgraph(self):
    #    if self.equity_search_bar.text() in symb or com_names:
    #        if len(self.equity_search_bar.text()) <= 5:
    #            symbol = str(self.equity_search_bar.text())
    #            symbol_index = symb.index(symbol)       
    #            name = com_names[symbol_index]
    #        elif len(self.equity_search_bar.text()) > 5:
    #            name = str(self.equity_search_bar.text())
    #            company_index = com_names.index(name)
    #            symbol = symb[company_index]
    #    self.hist_stock_graph.setGeometry(-65,135,3051,1221)
    #    self.hist_bottom_graph.setGeometry(-65,1259,2301,410)
    #    esum_axis.yaxis.tick_right()
    #    self.hist_set_axis()
    #    self.ehist_bcanvas.draw()        

    def historical_table(self):
        self.equity_tab.setCurrentIndex(2)

    def econ_window(self):
        self.stackedWidget.setCurrentIndex(3)

    def bond_window(self):
        self.stackedWidget.setCurrentIndex(4)

    def currency_window(self):
        self.stackedWidget.setCurrentIndex(5)

    def portfolio_window(self):
        self.stackedWidget.setCurrentIndex(6)

    def addmpl(self, sindex_fig):
        self.sindex_canvas = FigureCanvas(sindex_fig)
        self.mplvl_sindex_graph.addWidget(self.sindex_canvas)
        self.sindex_canvas.draw()

    def addmpl2(self, esum_fig):
        self.esum_canvas = FigureCanvas(esum_fig)
        self.mplvl_sum_graph.addWidget(self.esum_canvas)
        self.esum_canvas.draw()

    def addmpl3(self, ehist_fig):
        self.ehist_canvas = FigureCanvas(ehist_fig)
        self.mplvl_hist_graph.addWidget(self.ehist_canvas)
        self.ehist_canvas.draw()

    def addmpl4(self, secon_fig):
        self.secon_canvas = FigureCanvas(secon_fig)
        self.mplvl_secon_graph.addWidget(self.secon_canvas)
        self.secon_canvas.draw()

        #def addmpl5(self, ehist_bfig):
        #    self.ehist_bcanvas = FigureCanvas(ehist_bfig)
        #    self.mplvl_hist_bgraph.addWidget(self.ehist_bcanvas)
        #    self.ehist_bcanvas.draw()

if __name__ == '__main__':
    import sys

    #Index graph on start up
    sindex_fig = Figure(facecolor='#07000d') 
    sindex_fig.set_tight_layout(tight=True)
    sindex_axis = sindex_fig.add_subplot(111,axisbg='#07000d') 
    sindex_axis.grid(True, color='w')
    sindex_axis.yaxis.label.set_color("w")
    sindex_axis.xaxis.label.set_color('w')
    sindex_axis.spines['bottom'].set_color("w")
    sindex_axis.spines['top'].set_color("w")
    sindex_axis.spines['left'].set_color("w")
    sindex_axis.spines['right'].set_color("w")
    sindex_axis.tick_params(axis='y', colors='w',labelsize=20)
    sindex_axis.tick_params(axis='x', colors='w',labelsize=20)

    #Closing price graph on equity summary page
    esum_fig = Figure(facecolor='#07000d') 
    esum_fig.set_tight_layout(tight=True)
    esum_axis = esum_fig.add_subplot(111,axisbg='#07000d') 
    esum_axis.grid(True, which='minor', color='w', linestyle='--')
    esum_axis.grid(True, which='major', color='w', linestyle='--') 
    esum_axis.yaxis.label.set_color("green")
    esum_axis.xaxis.label.set_color('w')
    esum_axis.spines['bottom'].set_color("w")
    esum_axis.spines['top'].set_color("w")
    esum_axis.spines['left'].set_color("w")
    esum_axis.spines['right'].set_color("w")
    esum_axis.tick_params(axis='y', colors='w',labelsize=20)
    esum_axis.tick_params(axis='x', colors='w',labelsize=20)

    #Equity historical graph
    ehist_fig = Figure(facecolor='#07000d') 
    ehist_fig.set_tight_layout(tight=True)
    ehist_axis = ehist_fig.add_subplot(111,axisbg='#07000d') 
    ehist_axis.grid(True, which='minor', color='w', linestyle='--')
    ehist_axis.grid(True, which='major', color='w', linestyle='--')  
    ehist_axis.yaxis.label.set_color("green")
    ehist_axis.xaxis.label.set_color('w')
    ehist_axis.spines['bottom'].set_color("w")
    ehist_axis.spines['top'].set_color("w")
    ehist_axis.spines['left'].set_color("w")
    ehist_axis.spines['right'].set_color("w")
    ehist_axis.tick_params(axis='y', colors='green',labelsize=20)
    ehist_axis.tick_params(axis='x', colors='w',labelsize=20)

    ehist_axis2 = ehist_axis.twinx()

    #ehist_bfig = Figure(facecolor='#07000d') 
    #ehist_bfig.set_tight_layout(tight=True)
    #ehist_baxis = ehist_bfig.add_subplot(111,axisbg='#07000d') 
    #ehist_baxis.grid(True, color='w')
    #ehist_baxis.yaxis.label.set_color("green")
    #ehist_baxis.xaxis.label.set_color('w')
    #ehist_baxis.spines['bottom'].set_color("w")
    #ehist_baxis.spines['top'].set_color("w")
    #ehist_baxis.spines['left'].set_color("w")
    #ehist_baxis.spines['right'].set_color("w")
    #ehist_baxis.tick_params(axis='y', colors='green',labelsize=20)
    #ehist_baxis.tick_params(axis='x', colors='w',labelsize=20)

    secon_fig = Figure(facecolor='#07000d') 
    secon_fig.set_tight_layout(tight=True)
    secon_axis = secon_fig.add_subplot(111,axisbg='#07000d') 
    secon_axis.grid(True, color='w')
    secon_axis.yaxis.label.set_color("w")
    secon_axis.xaxis.label.set_color('w')
    secon_axis.spines['bottom'].set_color("w")
    secon_axis.spines['top'].set_color("w")
    secon_axis.spines['left'].set_color("w")
    secon_axis.spines['right'].set_color("w")
    secon_axis.tick_params(axis='y', colors='w',labelsize=20)
    secon_axis.tick_params(axis='x', colors='w',labelsize=20)

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet('QMainWindow{background-color: black;border: 1px solid black;}')
    main = Main()
    main.addmpl(sindex_fig)
    main.addmpl2(esum_fig)
    main.addmpl3(ehist_fig)
    main.addmpl4(secon_fig)
    #main.addmpl5(ehist_bfig)

    main.show()
    sys.exit(app.exec_())



