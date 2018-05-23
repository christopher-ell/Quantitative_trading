# -*- coding: utf-8 -*-
"""
Basic Cointegration Mean Reversions Cointegration Testing
Fix
- Sometimes size of data doesn't match
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


all_coint_res = pd.DataFrame(columns = ['symbol_id1','symbol_id1','test type', 'p-value'])
row = 1


for symb1 in unique_symbols:
    
    for t in range(int(symb1), len(unique_symbols)):

        data1 = price_data[price_data.symbol_id == symb1]
        data2 = price_data[price_data.symbol_id == unique_symbols[t]]
    
        print("symbol 1: ", symb1)
        print("symbol 2: ", unique_symbols[t])
    
    
        if len(data1) == len(data2):
            for ttype in ['c', 'ct']:
                coint_res = ts.coint(data1['adj_close_price'], data2['adj_close_price'], regression = ttype)
                
                ## The null hypothesis is no cointegration so if the p-value is less than 5%
                ## this means we reject the null of no cointegration.
                if coint_res[1] < 0.05:
                    all_coint_res.loc[row] = [symb1, unique_symbols[t], ttype, coint_res[1]]
                    row += 1
    