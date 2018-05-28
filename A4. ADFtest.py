# -*- coding: utf-8 -*-
"""
Basic Cointegration Mean Reversions Unit Root Testing
Fix
- Check if the log difference is better to use than the absolute value of the series
"""


import datetime
import MySQLdb as mdb
import numpy as np
import pandas as pd
import statsmodels.tsa.stattools as ts


def connect_sec_db():
    # Database connection to MySQL instance
    db_host = "localhost"
    db_user = "root"
    db_pass = "password"
    db_name = "securities_master"
    con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name, 
                      autocommit=True)
    
    return con


con = connect_sec_db()


price_data = pd.read_sql("select * from daily_price;", con=con)

price_data = price_data[price_data.checks == 1]


unique_symbols = price_data.symbol_id.unique().tolist()

presults = pd.DataFrame(columns = ['symbol_id','test type', 'p-value'])
row = 1

## Test all datasets for a unit root
for t in unique_symbols:    
    
    data = price_data[price_data.symbol_id == t]
    #data['lreturn'] = np.log(price_data.adj_close_price) - np.log(price_data.adj_close_price).shift(1)
    #data = data.iloc[1:]
    
    ## ADF test statistic on data
    ## First value is test-statistic, second value is p-value
    ## Fourth value is data points in the sample
    ## Fifth dict contains critival values at different percentages 1%, 5% & 10%
    ## If test stat is larger than critical value then cannot reject null gamma = 0
    ## and unlikely to have found mean reverting time series
    ## If test stat is less than critical value then reject null that gamma = 0
    ## and have found mean reverting time series.
    ## p-value gives probability of not rejecting null.
    for ttype in ['nc', 'c', 'ct']:
        adfuller_res = ts.adfuller_res = ts.adfuller(data['adj_close_price'],
                                                     regression = ttype)
    
        ## We are testing for a unit root so we want the data at level to be 
        ## non-stationary, so we want to not reject the null. Hence if the  p-value
        ## is greater than 5% we do not reject the null of non-stationarity
        if adfuller_res[1] > 0.05:      
            presults.loc[row] = [t, ttype, adfuller_res[1]]
            row += 1
    
dpresults = pd.DataFrame(columns = ['symbol_id','test type', 'p-value'])
unique_symbols = presults.symbol_id.unique().tolist()

for t in unique_symbols:
    data = price_data[price_data.symbol_id == t]
    data['dlreturn'] = price_data.adj_close_price - price_data.adj_close_price.shift(1)
    data = data.iloc[1:]
    for ttype in ['nc', 'c', 'ct']:
        adfuller_res = ts.adfuller_res = ts.adfuller(data['dlreturn'],
                                                     regression = ttype)
        
        ## We are testing for a unit root so now we want to reject the null of
        ## non-stationarity after taking the difference of the data. So we want
        ## a low p-value less than 5%
        if adfuller_res[1] < 0.05:      
            dpresults.loc[row] = [t, ttype, adfuller_res[1]]
            row += 1
    

unit_roots = dpresults.symbol_id.unique().tolist()
    