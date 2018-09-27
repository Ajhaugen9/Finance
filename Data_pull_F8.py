import pandas as pd
import pandas_datareader.data as web
import datetime
import sqlite3
import urllib2
from bs4 import BeautifulSoup
from random import randint
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

'''Python script to gather basic info, historical pricing data from yahoo finance and historical income statement, balance sheet,
   and statement of cash flow data from stockrow.com. Each SQL query has '###' next to it to make it easier to find.
   The data is first loaded into pandas which is a data structure and analysis tool for Pyhton. With pandas I can upload 
   data to the database using '.to_sql' or pull data from the database with '.read_sql_query'.'''

def company_info_to_db():
    
    #Get the list of symbols from csv and create pandas dataframe
    list_path = "C:/Users/ajhau/Desktop/Data_pull_F8/Data_pull_F8/companylist.csv"
    company_list = pd.read_csv(list_path, index_col=0)

    #add the new colums that we will get
    company_list['City/State'] = None
    company_list['Country'] = None
    company_list['Phone'] = None
    company_list['Website'] = None

    symbols = list(company_list.index)
    failed_sym = []

    for sym in symbols:
        try:
            #the company info is from yahoo finance
            _url = 'https://finance.yahoo.com/quote/'+sym+'/profile?p='+sym
            page = urllib2.urlopen(_url)
            soup = BeautifulSoup(page, 'html.parser')

            
            ad_info = soup.find('p', attrs={'class':'D(ib) W(47.727%) Pend(40px)'}).get_text(separator=u'%').split('%')

            company_list.loc[sym]['City/State'] = ad_info[-4]
            company_list.loc[sym]['Country'] = ad_info[-3]
            company_list.loc[sym]['Phone'] = ad_info[-2]
            company_list.loc[sym]['Website'] = ad_info[-1]

            print sym, str(symbols.index(sym))+' Out of '+str(len(symbols))

        except Exception as e:
            failed_sym.append(sym)

            company_list.loc[sym]['City/State'] = 'NA'
            company_list.loc[sym]['Country'] = 'NA'
            company_list.loc[sym]['Phone'] = 'NA'
            company_list.loc[sym]['Website'] = 'NA'

            print 'Failed: '+sym+' Number Failed: '+str(len(failed_sym))
            print e

    #connect to sql db and send the dataframe
    con = sqlite3.connect('Finance8_DB')
    company_list.to_sql('Company_Info', con, if_exists = 'replace') ###


def historical_price_data():

    #open database
    db_path = "C:/Users/ajhau/Desktop/Finance Program/Finance 8/Data_pull_F8/Finance8_DB"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    #Pulls the entire table from sql database. Includes company symbol, name, sector, industry, address, phone number, and website.
    cinfo = pd.read_sql_query('SELECT * FROM Company_Info',conn, index_col='Symbol') ###

    symbols = list(cinfo.index) #list of just the symbols

    #start and end dates for historical data
    sdate = datetime.datetime(1980,1,1)
    edate = datetime.date.today()

    failed = []

    #loop through every symbol
    for sym in symbols:

        try:
            #Get the sector for the symbol which will be the database table name  
            sector = str(c.execute("SELECT Sector FROM Company_Info WHERE Symbol = '%s'"%sym).fetchone()[0]) ###

            if sector == 'n/a':
                sector = 'No_Sector'
        
            #get data from yahoo
            hp_data = web.DataReader(sym,'yahoo',sdate,edate)

            #basic calculations for columns that will be added
            hp_data['Change'] = hp_data['Close'] - hp_data['Open']
            hp_data['PChange'] = hp_data['Change'] / hp_data['Open']
            hp_data['Symbol'] = sym
            hp_data = hp_data[['Symbol','Open','High','Low','Close','Adj Close','Change','PChange','Volume']] #rearange columns
            hp_data.index = [pd.to_datetime(d).date() for d in hp_data.index]

            #send to sql db
            hp_data.to_sql(str(sector)+'_hp',conn,if_exists='append') ###

            print 'Passed: '+sym, str(symbols.index(sym)+1)+'/'+str(len(symbols))+' Failed: '+str(len(failed)) 

        except Exception as e:
            failed.append(sym)

            print 'Failed: '+sym, str(symbols.index(sym)+1)+'/'+str(len(symbols))+' Failed: '+str(len(failed)) 


    failed = pd.Series(failed)
    failed.to_sql('Failed',conn,if_exists='replace')




def financial_stat_pull():
    st = time.time()

    #open database
    db_path = "C:/Users/ajhau/Desktop/Finance Program/Finance 8/Data_pull_F8/Finance8_DB"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    #open webdriver. Have to use this to gather data from websites that use java rather than html
    chromeOptions = Options()
    chromeOptions.add_argument("--kiosk")
    driver = webdriver.Chrome(r"C:/Users/ajhau/Downloads/chromedriver_win32/chromedriver.exe",chrome_options=chromeOptions)

    
    cinfo = pd.read_sql_query('SELECT * FROM Company_Info',conn, index_col='Symbol') ### 
    failed = pd.read_sql_query('SELECT * FROM Failed',conn) ### 
    failed = [str(x) for x in failed['0']]
    symbols = [sym for sym in cinfo.index if sym not in failed]

    failed = []
    statements = ['income','balance','cashflow']
    for symbol in symbols:
        try:
            for statement in statements:
                sector = str(c.execute("SELECT Sector FROM Company_Info WHERE Symbol = '%s'"%symbol).fetchone()[0]) ###
                if sector == 'n/a':
                    sector = 'No_Sector'
                sector = sector.replace(' ','').replace('-','')

                stat_to_db(symbol,sector,statement,driver,conn,st,symbols)

        except Exception as e:
            print e
            failed.append(symbol)
            print 'Failed: '+symbol, statement, str(symbols.index(symbol)+1)+'/'+str(len(symbols))+' Failed: '+str(len(failed)), time.time() - st 


    failed = pd.Series(failed)
    failed.to_sql('Failed_FS',conn,if_exists='replace')


    driver.quit()

            





def stat_to_db(symbol,sector,statement,driver,conn,st,symbols):

    #Stock row url for annual income statement data
    _url = 'https://stockrow.com/'+symbol+'/financials/'+statement+'/annual'
    driver.get(_url)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    data_list = soup.find('div', attrs={'class':'mainGridWrap'}).get_text(separator=u'%').split('%')

    #check the order of the dates. if previous years data is first the click 'reverse columns' button 
    if int(data_list[0][:4]) < int(data_list[1][:4]):
        x_path = '//*[@id="root"]/div/div/section/div/div[2]/div[1]/div[2]/section[4]/div/div[1]/div[1]/button'
        link = driver.find_element_by_xpath(x_path).click()
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        data_list = soup.find('div', attrs={'class':'mainGridWrap'}).get_text(separator=u'%').split('%')

    else:
        pass

    # replace unwanted unicode
    for i, item in enumerate(data_list):
        if item == u'\u2014':
            data_list[i] = '-'

    data_list = [str(x) for x in data_list if str(x) != '']
    data_list = ['Date'] + data_list

    #figure out how many column the data has
    n_col = []
    for item in data_list[:20]:
        try:
            date_ = datetime.datetime.strptime(item,'%Y-%m-%d').date()
            n_col.append(item)
        except:
            pass

    #convert the data list into dataframe
    col = [str(x[:4]) for x in data_list[1:len(n_col)+1]]
    data = pd.DataFrame(columns=col,index=data_list[::len(n_col)+1])
    for i in range(len(data.columns)):
        data[data.columns[i]] = data_list[i+1::len(n_col)+1]

    #add missing columns
    add_col = [str(x) for x in range(2005,2018)]
    add_col.reverse()
    data = pd.concat([data,pd.DataFrame(columns=add_col)])
    data['Symbol'] = symbol

    cols = data.columns.tolist()
    cols.reverse()
    data = data[cols]

    if statement == 'income':
        data.to_sql(str(sector)+'_inca',conn,if_exists='append') ###
        print 'Passed: '+symbol,statement, str(symbols.index(symbol)+1)+'/'+str(len(symbols)), time.time() - st 

    elif statement == 'balance':
        data.to_sql(str(sector)+'_bala',conn,if_exists='append') ###
        print 'Passed: '+symbol,statement, str(symbols.index(symbol)+1)+'/'+str(len(symbols)), time.time() - st 

    elif statement == 'cashflow':
        data.to_sql(str(sector)+'_casha',conn,if_exists='append') ###
        print 'Passed: '+symbol,statement, str(symbols.index(symbol)+1)+'/'+str(len(symbols)), time.time() - st 


financial_stat_pull()