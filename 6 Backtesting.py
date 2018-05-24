# -*- coding: utf-8 -*-
"""
Backtesting Cointegration Pairs Trading
Fix
- 
"""
import datetime
import MySQLdb as mdb
import numpy as np
import pandas as pd
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm
from pandas.stats.api import ols


def connect_sec_db():
    # Database connection to MySQL instance
    db_host = "localhost"
    db_user = "root"
    db_pass = "password"
    db_name = "securities_master"
    con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name, 
                      autocommit=True)
    
    return con

def hedge_ratio(x, y, add_const=True):
    if add_const:
        x = sm.add_constant(x)
        model = sm.OLS(y, x).fit()
        return model.params[1]
    model = sm.OLS(y, x).fit()
    return model.params.values




con = connect_sec_db()

symbol_id1 = 1
symbol_id2 = 2
look = 10
band = 2


price_data = pd.read_sql("select * from daily_price;", con=con)




price_data = price_data[price_data.checks == 1]

data1 = price_data[price_data.symbol_id == symbol_id1].rename(columns={'adj_close_price':'adj_close_price_'+str(symbol_id1)})
data2 = price_data[price_data.symbol_id == symbol_id2].rename(columns={'adj_close_price':'adj_close_price_'+str(symbol_id2)})

backtester = pd.merge(data1[['adj_close_price_'+str(symbol_id1), 'price_date']], data2[['adj_close_price_'+str(symbol_id2), 'price_date']], how='inner', on='price_date')

backtester['return_'+str(symbol_id1)] = backtester['adj_close_price_'+str(symbol_id1)].pct_change()
backtester['return_'+str(symbol_id2)] = backtester['adj_close_price_'+str(symbol_id2)].pct_change()

hedge = hedge_ratio(backtester['adj_close_price_'+str(symbol_id1)], backtester['adj_close_price_'+str(symbol_id2)])

backtester['SPREAD'] = backtester['adj_close_price_'+str(symbol_id2)] - hedge * backtester['adj_close_price_'+str(symbol_id1)]

backtester['z-score'] = (backtester["SPREAD"] - pd.rolling_mean(backtester["SPREAD"], window = look))/pd.rolling_std(backtester["SPREAD"], window = look)

backtester['long/short'] = 0
          
backtester = backtester.dropna()

backtester.loc[backtester['z-score'] >= band, 'long/short'] = 1 ## Want to buy 1/beta of 2 and short 1

backtester.loc[backtester['z-score'] <= -band, 'long/short'] = -1 ## Want to buy 1 short 1/beta of 2

backtester['holding_'+str(symbol_id1)] = backtester['long/short'] * -1

backtester['holding_'+str(symbol_id2)] = backtester['long/short'] * hedge

backtester['return'] = backtester['holding_'+str(symbol_id1)].shift(1) * backtester['return_'+str(symbol_id1)] + backtester['holding_'+str(symbol_id2)].shift(1) * backtester['return_'+str(symbol_id2)]