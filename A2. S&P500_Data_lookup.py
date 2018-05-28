
# -*- coding: utf-8 -*-
"""
Download data from Yahoo finance, pulling symbols from database.
"""

import datetime
import MySQLdb as mdb
import urllib.request
import certifi
import Mod_Yahoo_Download as MYD
import numpy as np


def connect_sec_db():
    # Database connection to MySQL instance
    db_host = "localhost"
    db_user = "root"
    db_pass = "password"
    db_name = "securities_master"
    con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
    
    return con


def obtain_list_of_db_tickers():
    """Obtain a list of the DB tickers in the database."""
    
    con = connect_sec_db()
    with con:
        cur = con.cursor()
        cur.execute("select id, ticker from symbol")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]
    

def get_daily_historic_data_yahoo(ticker, sDate, eDate):

    # Try connecting to Yahoo finance for the data
    # On failure, print error message
    
    
    ## Sample Parameters
    #sDate = (2017,5,1)
    #eDate = (2017,6,2)
    #ticker = "csl.ax"
    
    try:
        # Get data as dataframe
       prices_df = MYD.mod_Yahoo_downloader(ticker, sDate, eDate).fillna(method='bfill')
       # Get rid of null vlues by replacing them with nan and then using backfill
       # then forward fill to fill them with values.
       prices_df = prices_df.replace("null", np.nan).bfill().ffill()
       
       # Store data in list of lists for each day
       daily_data = []
       for index, row in prices_df.iterrows():
           daily_data.append(('NYSE', ticker, index, row['Open'], row['High'], 
                       row['Low'], row['Close'], row['Adj Close'], 
                       row['Volume']))
       return daily_data
    except Exception as e:
        print("Could not download Yahoo data: %s" % e)
    

def insert_daily_data_into_db(data_vendor_id, symbol_id, daily_data):
    """Takes a list of tuples of daily data and adds it to the mysql database. 
    Appends the vendor ID and symbol ID to the data.
    
    daily data List of tuples of the OHLC data (with adj_close and volume)"""
    
    con = connect_sec_db()
    
    # Create the time now
    now = datetime.datetime.utcnow()
    
    checked = 0
    
    # Ammend the data to include the vendor ID and symbol ID
    daily_data = [(data_vendor_id, symbol_id, d[2], now, now, d[3], d[4], d[5],
                   d[6], d[7], d[8], checked) for d in daily_data]

    
    # Create the insert strings
    column_str = """data_vendor_id, symbol_id, price_date, create_date,
                    last_updated_date, open_price, high_price, low_price,
                    close_price, adj_close_price, volume, checks"""
    insert_str = ("%s, " * 12)[:-2]                
    final_str = "INSERT INTO daily_price (%s) VALUES (%s)" % (column_str, insert_str)
    
    with con:
        cur = con.cursor()
        cur.executemany(final_str, daily_data)
        
def example_sample_sp500():
    # Set up
    con = connect_sec_db()
    cursor = con.cursor()
    #cursor.execute("show tables")
    #mysql_tbl_list = cursor.fetchall()
    cursor.execute("select * from symbol")
    all_ticks = cursor.fetchall()

    # Will only look up 5 symbols however long the list
    #tickers = all_ticks[:100]
    tickers = all_ticks

    undownloaded = []

    for t in tickers:
        print("#########################################")
        print("Adding data for %s" % t[2])
        yf_data = get_daily_historic_data_yahoo(t[2], (2008,5,1), (2018,5,1))
        if not yf_data:
            print("#########################################")
            print("%s unable to be downloaded" % t[2])
            print("#########################################")
            undownloaded.append(t[2])
        else:        
            insert_daily_data_into_db(1, t[0], yf_data)
            
example_sample_sp500()