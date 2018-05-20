# -*- coding: utf-8 -*-
"""
Basic Cointegration Mean Reversions

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


unique_symbols = price_data.symbol_id.unique()

presults = []

## Test all datasets for a unit root
for t in unique_symbols:

    data = price_data[price_data.symbol_id == t]
    data['lreturn'] = np.log(price_data.adj_close_price) - np.log(price_data.adj_close_price).shift(1)
    data = data.iloc[1:]
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
        adfuller_res = ts.adfuller_res = ts.adfuller(data['lreturn'],
                                                     regression = ttype, 
                                                     autolag = 'AIC')
    
        if adfuller_res[1] < 0.05:    
            temp = [t, ttype, adfuller_res[1]]    
            presults.append(temp)
    



