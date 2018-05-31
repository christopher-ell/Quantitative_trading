# -*- coding: utf-8 -*-
"""
Backtest single cointegration pairs trade given hyperparameters model type and
lookback period.

problems
- Not sure if I should append the validation data to the training data when 
  estimating test parameters
- Always chooses 'nc' trend for some reason?
- Overall relationships make negative returns
"""


import datetime
import MySQLdb as mdb
import numpy as np
import pandas as pd
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm
#from pandas.stats.api import ols


def connect_sec_db():
    # Database connection to MySQL instance
    db_host = "localhost"
    db_user = "root"
    db_pass = "password"
    db_name = "securities_master"
    con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name, 
                      autocommit=True)
    
    return con

def hedge_ratio(x, y, trend='NC'):
    if trend.upper() == 'C':
        ## Create field of just 1 for constant
        x = sm.add_constant(x)
        #print("Here1")
        model = sm.OLS(y, x).fit()
        ## Extract both parameters into dictionary
        params = [model.params[0], model.params[1]]
        return params
    if trend.upper() == 'T':
        x=x.to_frame()
        ## Create numbers from 1 to length of data for time trend
        x.insert(0, 'trend', range(1,1+len(x)))
        #print("Here2")
        model = sm.OLS(y, x).fit()
        ## Extract both parameters into dictionary
        params = [model.params[0], model.params[1]]
        return params
    model = sm.OLS(y, x).fit()
    #print("Here3")
    return model.params.values



def ml_data_split(data):
    
    import pandas as pd

    train_data = data[0:int(len(data)*0.6)]

    val_data = data[int(len(data)*0.6):int(len(data)*0.8)]

    test_data = data[int(len(data)*0.8):]
    
    return train_data, val_data, test_data



con = connect_sec_db()




def Backtester_ml(symbol_id1, symbol_id2, look, trend, band, stage):

    ## Import data from symbol 1 and rename the price column uniquely for later merging
    query = "select symbol_id, price_date, adj_close_price from daily_price where symbol_id = {};".format(symbol_id1)
    data1 = pd.read_sql(query, con=con)
    data1 = data1.rename(columns={"adj_close_price":"adj_close_price"+str(symbol_id1)})
    data1_train, data1_val, data1_test = ml_data_split(data1)

    ## Import data from symbol 2 and rename the price column uniquely for later merging
    query = "select symbol_id, price_date, adj_close_price from daily_price where symbol_id = {};".format(symbol_id2)
    data2 = pd.read_sql(query, con=con)
    data2 = data2.rename(columns={"adj_close_price":"adj_close_price"+str(symbol_id2)})
    data2_train, data2_val, data2_test = ml_data_split(data2)

    ## Merge data for symbols 1 and 2 into backtester data
    ## If the model is in the validation stage use the validation dataset 
    ## If the model is in the test stage use the test dataset 
    if stage.upper() == 'VAL':
#        print("here1")
        backtester = pd.merge(data1_val[['adj_close_price'+str(symbol_id1), 'price_date']], data2_val[['adj_close_price'+str(symbol_id2), 'price_date']], how='inner', on='price_date')
    elif stage.upper() == 'TEST':
#        print("here2")
        backtester = pd.merge(data1_test[['adj_close_price'+str(symbol_id1), 'price_date']], data2_test[['adj_close_price'+str(symbol_id2), 'price_date']], how='inner', on='price_date')
    else:
        print("Invalid stage, please use 'VAL' or 'TEST'")

    ## Calculate returns between each period for each stock price
    backtester['return_'+str(symbol_id1)] = backtester['adj_close_price'+str(symbol_id1)].pct_change()
    backtester['return_'+str(symbol_id2)] = backtester['adj_close_price'+str(symbol_id2)].pct_change()

    ## If the model has a trend or a constant estimate and use it.
    if trend.upper() == 'C':
        ## Calculate the hedge ratio between the two prices
        if stage.upper() == "VAL":
            hedge = hedge_ratio(data1_train['adj_close_price'+str(symbol_id1)], data2_train['adj_close_price'+str(symbol_id2)], 'C')
        else:
            ## When estimating the test parameters use all the data by appending validation set to train
            hedge = hedge_ratio(data1_train['adj_close_price'+str(symbol_id1)].append(data1_val['adj_close_price'+str(symbol_id1)]), data2_train['adj_close_price'+str(symbol_id2)].append(data2_val['adj_close_price'+str(symbol_id2)]), 'C')
        ## Calculate difference between predicted value and actual value
        backtester['SPREAD'] = hedge[0] + backtester['adj_close_price'+str(symbol_id2)] - hedge[1] * backtester['adj_close_price'+str(symbol_id1)]
        hedgev = hedge[1]
    elif trend.upper() == 'T':
        ## Calculate the hedge ratio between the two prices
        if stage.upper() == "VAL":
            hedge = hedge_ratio(data1_train['adj_close_price'+str(symbol_id1)], data2_train['adj_close_price'+str(symbol_id2)], 'T')
        else:
#            print("herehere")
#            print(data2_val.columns.values)
            ## When estimating the test parameters use all the data by appending validation set to train
            hedge = hedge_ratio(data1_train['adj_close_price'+str(symbol_id1)].append(data1_val['adj_close_price'+str(symbol_id1)]), data2_train['adj_close_price'+str(symbol_id2)].append(data2_val['adj_close_price'+str(symbol_id2)]), 'T')
        backtester.insert(0, 'trend', range(1,1+len(backtester)))
        ## Calculate difference between predicted value and actual value
        backtester['SPREAD'] = hedge[0]*backtester['trend'] + backtester['adj_close_price'+str(symbol_id2)] - hedge[1] * backtester['adj_close_price'+str(symbol_id1)]
        
        hedgev = hedge[1]
    else:
        ## Calculate the hedge ratio between the two prices
        if stage.upper() == "VAL":
            hedge = hedge_ratio(data1_train['adj_close_price'+str(symbol_id1)], data2_train['adj_close_price'+str(symbol_id2)], 'NC')
        else:
            ## When estimating the test parameters use all the data by appending validation set to train
            hedge = hedge_ratio(data1_train['adj_close_price'+str(symbol_id1)].append(data1_val['adj_close_price'+str(symbol_id1)]), data2_train['adj_close_price'+str(symbol_id2)].append(data2_val['adj_close_price'+str(symbol_id2)]), 'NC')
        ## Calculate difference between predicted value and actual value
        backtester['SPREAD'] = backtester['adj_close_price'+str(symbol_id2)] - hedge * backtester['adj_close_price'+str(symbol_id1)]
        hedgev = hedge

    ## Calculate Z value to see whether trade should be made
    backtester['z-score'] = (backtester["SPREAD"] - pd.rolling_mean(backtester["SPREAD"], window = look))/pd.rolling_std(backtester["SPREAD"], window = look)

    ## Initialise long/short values setting default 0
    backtester['long/short'] = 0
          
    ## Drop out values where percentage change has left na values
    backtester = backtester.dropna()
              
    ## If Z score is greater than or equal to band buy 1 unit of stock 1 and sell 
    ## 1/beta units of 2
    backtester.loc[backtester['z-score'] >= band, 'long/short'] = 1 ## Want to buy 1/beta of 2 and short 1

    ## If Z score is less than or equal to -band sell 1 unit of stock 1 and buy 
    ## 1/beta units of stock 2
    backtester.loc[backtester['z-score'] <= -band, 'long/short'] = -1 ## Want to buy 1 short 1/beta of 2

    ## Calculate holdings of stock 1by multiplying by -1
    backtester['holding_'+str(symbol_id1)] = backtester['long/short']

    ## Calculate holdings of stock 2 by multiplying by the hedge ratio
    backtester['holding_'+str(symbol_id2)] = backtester['long/short'] * -hedgev

    ## Calculate returns by multiplying percentage change in each stock by holdings           
    backtester['return'] = backtester['holding_'+str(symbol_id1)].shift(1) * backtester['return_'+str(symbol_id1)] + backtester['holding_'+str(symbol_id2)].shift(1) * backtester['return_'+str(symbol_id2)]

    ## Sum total returns from each period and annualise by working days 240/total 
    ## days in data
    ret = backtester['return'].sum()*(240/len(backtester))
    
    return ret, backtester



symbol_id1 = 4
symbol_id2 = 13

parameters = pd.DataFrame(columns = ['symbol_id1','symbol_id2', 'trend', 'look', 'annual_test_return'])


coint_rels=all_coint_res.groupby(["symbol_id1", "symbol_id2"]).count().reset_index()


#for i in range(0, len(coint_rels)):
for i in range(0, 50):
    
    symbol_id1 = coint_rels.iloc[i]['symbol_id1']
    symbol_id2 = coint_rels.iloc[i]['symbol_id2']

    datasize = 753
    look = 5
    #trend = 'nc'
    band = 1.5
    #stage = 'val'
    select_trend = 'nc'
    best_return = -99

    ## Decide on best trend to use

    ## Test no constant or trend
    ret_v_nc, _ = Backtester_ml(symbol_id1, symbol_id2, look, 'nc', band, 'test')

    best_return = ret_v_nc

    ## Test only constant
    ret_v_c, _ = Backtester_ml(symbol_id1, symbol_id2, look, 'c', band, 'val')

    # If only constant return is better than best return so far replace
    if ret_v_c > best_return:
        select_trend = 'c'
        best_return = ret_v_c

    ## Test only trend
    ret_v_t, _ = Backtester_ml(symbol_id1, symbol_id2, look, 't', band, 'val')

    # If only trend return is better than best return so far replace
    if ret_v_t > best_return:
        select_trend = 't'
        best_return = ret_v_t

    #ret_t = Backtester_ml(symbol_id1, symbol_id2, look, select_trend, band, 'test')



    ## Decide on best lookback period

    ## Test and validation period are 20% and 10% is half that
    for lookback in range(5,int(0.1*datasize)):
        ret_lb, _ = Backtester_ml(symbol_id1, symbol_id2, lookback, select_trend, band, 'val')
        if ret_lb > best_return:
            best_return = ret_lb
            look = lookback
        
    ret_t, back = Backtester_ml(symbol_id1, symbol_id2, look, select_trend, band, 'test')
    
    parameters.loc[i+1]=[symbol_id1, symbol_id2, select_trend, look, ret_t]
    
    print("This value: ", i)

    