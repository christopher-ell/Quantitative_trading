# -*- coding: utf-8 -*-
"""

Problems:
    - Current program excludes all incomplete sets of data
    - A more automated way to get the maximum number of records than 756
"""


import datetime
import MySQLdb as mdb
import numpy as np
import pandas as pd

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




 
##########################################   
## 1. For finding data without all dates##
##########################################

#size_count = price_data.groupby('symbol_id').size()

## Get rid of all rows below 756 records (number of total stock dates in time 
## period)
date_filter = price_data.groupby('symbol_id').filter(lambda x: len(x) >= 756)

check_ids = date_filter.symbol_id.unique()

for t in range(0, len(check_ids)):
    q_str = 'update daily_price set checks = 1 where symbol_id = {}'.format(check_ids[t])
    cur = con.cursor()
    cur.execute(q_str)
    


#############################################   
## 2. For finding data with negative values##
#############################################

data_filter = price_data[price_data['adj_close_price'] < 0]

neg_ids = data_filter.symbol_id.unique()

for t in range(0, len(neg_ids)):
    q_str = 'update daily_price set checks = -1 where symbol_id = {}'.format(neg_ids[t])
    print(q_str)
    cur = con.cursor()
    cur.execute(q_str)


## Work on incorporating incomplete data
#    
#unique_dates = price_data.price_date.unique()
#
#unique_symbols = price_data.symbol_id.unique()
#
#
#
#stock_temp = price_data[price_data.symbol_id == 202].set_index('price_date').drop('id', axis=1)
#
#stock_df = pd.DataFrame(index=unique_dates)
#
#stock_df = stock_df.join(stock_temp, how='left')

