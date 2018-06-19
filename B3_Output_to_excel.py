# -*- coding: utf-8 -*-
"""
Publish output for each working strategy into an Excel file

@author: Christopher Ell
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import openpyxl

#filepath = 'V:\Staff\Chris\Programming\Python\Quant\Quantstart\Outputs\test.xlsx'

## Connect to MySQL database
def connect_sec_db():
    import MySQLdb as mdb
    # Database connection to MySQL instance
    db_host = "localhost"
    db_user = "root"
    db_pass = "password"
    db_name = "securities_master"
    ## Connection string
    con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name, 
                      ## Set autocommit equal to True so you can make changes 
                      ## to the database
                      autocommit=True)
    
    return con

## Look up ticker of symbol_id
def symb_id_lookup(symbol_id):
    con = connect_sec_db()
    query = "select ticker from symbol where id = {};".format(symbol_id)
    ticker = pd.read_sql(query, con=con)
    return ticker['ticker'][0]

def plot_results(writer, df, symbol_id1, symbol_id2, sheet_name, filepath, cell):    
    
    ts1 = 'adj_close_price' + str(symbol_id1) + '.0'
    ts2 = 'adj_close_price' + str(symbol_id2) + '.0'
    
    ## Create Pandas Excel writer using Xlswriter as the engine
    df.to_excel(writer, sheet_name=sheet_name, startrow=1, startcol=1)
    
    ## Access the Xlswriter workbook and worksheets objects from the dataframe.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    ## Create a chart object 
    chart = workbook.add_chart({'type':'line'})

    ## Calculate extremes for axes
    min_x1 = df[ts1].min()
    max_x1 = df[ts1].max()
    min_x2 = df[ts2].min()
    max_x2 = df[ts2].max()    
    min_x = min(min_x1, min_x2)
    max_x = max(max_x1, max_x2)

    ## Configure the series of the chart from the dataframe data
    chart.add_series({
            'name':ts1,
            'categories': '=coint_analysis!$D$3:$D502',
            'values':'=coint_analysis!$C$3:$C502'
            })

    chart.add_series({
            'name':ts2,
            'categories': '=coint_analysis!$D$3:$D502',
            'values':'=coint_analysis!$E$3:$E502'
            })

    ## Configure chart axis
    chart.set_x_axis({'name':'Month/Year',
                      'date_axis':True,
                      'num_format': 'mm/yy', 
                      'major_gridlines':{
                              'visible':True,
                              'line':{'width':1, 'dash_type':'dash'}
                              }})
    chart.set_y_axis({'name':'Cumulative Percent Growth',
                      'min':min_x,
                      'max':max_x,
                      'major_gridlines':{
                              'visible':True,
                              'line':{'width':1, 'dash_type':'dash'}
                              }                  
                      })
    chart.set_title({'name':'%s and %s Cumulative Percent Growth' % (symb_id_lookup(symbol_id1), symb_id_lookup(symbol_id2))})
        
    chart.set_legend({'position':'bottom'})
    chart.set_chartarea({'border':{'none':True}})

    ## Insert chart into worksheet
    worksheet.insert_chart(cell, chart)
        

def plot_scatter_ts(writer, df, symbol_id1, symbol_id2, sheet_name, filepath, cell):
    
    ts1 = 'adj_close_price' + str(symbol_id1) + '.0'
    ts2 = 'adj_close_price' + str(symbol_id2) + '.0'
        
    ## Create Pandas Excel writer using Xlswriter as the engine
    df.to_excel(writer, sheet_name=sheet_name, startrow=1, startcol=1)
        
    ## Access the Xlswriter workbook and worksheets objects from the dataframe.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    ## Create a chart object 
    chart = workbook.add_chart({'type':'scatter'})

    min_x1 = df[ts1].min()
    max_x1 = df[ts1].max()
    min_x2 = df[ts2].min()
    max_x2 = df[ts2].max()    

    ## Configure the series of the chart from the dataframe data
    chart.add_series({
            #        'name':'Series1',
            'categories': 'coint_analysis!$E$3:$E502',
            'values':'=coint_analysis!$C$3:$C502'
            })


    ## Configure chart axis
    chart.set_x_axis({'name':ts1,
                         'min':min_x2,
                         'max':max_x2})
    chart.set_y_axis({'name':ts2,
                          'min':min_x1,
                          'max':max_x1})
    
    chart.set_title({'name':'%s and %s Price Scatterplot' % (symb_id_lookup(symbol_id1), symb_id_lookup(symbol_id2))})
    
    chart.set_legend({'none':True})
    chart.set_chartarea({'border':{'none':True}})

    ## Insert chart into worksheet
    worksheet.insert_chart(cell, chart)
        
def plot_spread(writer, df, symbol_id1, symbol_id2, sheet_name, filepath, cell):
    
    ## Create Pandas Excel writer using Xlswriter as the engine
    df.to_excel(writer, sheet_name=sheet_name, startrow=1, startcol=1)
    
    ## Access the Xlswriter workbook and worksheets objects from the dataframe.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    ## Create a chart object 
    chart = workbook.add_chart({'type':'line'})

    ## Calculate extremes for axes
    min_x = df['SPREAD'].min()
    max_x = df['SPREAD'].max()

    ## Configure the series of the chart from the dataframe data
    chart.add_series({
            'name':'SPREAD',
            'categories': '=coint_analysis!$D$3:$D502',
            'values':'=coint_analysis!$H$3:$H502'
            })

    ## Configure chart axis
    chart.set_x_axis({'name':'Month/Year',
                      'date_axis':True,
                      'num_format': 'mm/yy', 
                      'major_gridlines':{
                              'visible':True,
                              'line':{'width':1, 'dash_type':'dash'}
                              }})
    chart.set_y_axis({'name':'Cumulative Percent Growth',
                      'min':min_x,
                      'max':max_x,
                      'major_gridlines':{
                              'visible':True,
                              'line':{'width':1, 'dash_type':'dash'}
                              }                  
                      })
    chart.set_title({'name':'Daily Price Spread between %s and %s' % (symb_id_lookup(symbol_id1), symb_id_lookup(symbol_id2))})
        
    chart.set_legend({'position':'bottom'})
    chart.set_chartarea({'border':{'none':True}})

    ## Insert chart into worksheet
    worksheet.insert_chart(cell, chart)
        

def plot_returns(writer, df, symbol_id1, symbol_id2, sheet_name, filepath, cell):
    
    ## Create Pandas Excel writer using Xlswriter as the engine
    df.to_excel(writer, sheet_name=sheet_name, startrow=1, startcol=1)
    
    ## Access the Xlswriter workbook and worksheets objects from the dataframe.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    ## Create a chart object 
    chart = workbook.add_chart({'type':'line'})

    ## Calculate extremes for axes
    min_x = df['cum_return'].min()
    max_x = df['cum_return'].max()

    ## Configure the series of the chart from the dataframe data
    chart.add_series({
            'name':'SPREAD',
            'categories': '=coint_analysis!$D$3:$D502',
            'values':'=coint_analysis!$N$3:$N502'
            })

    ## Configure chart axis
    chart.set_x_axis({'name':'Month/Year',
                     'date_axis':True,
                     'num_format': 'mm/yy', 
                     'major_gridlines':{
                              'visible':True,
                              'line':{'width':1, 'dash_type':'dash'}
                              }})
    chart.set_y_axis({'name':'Cumulative Percent Growth',
                      'min':min_x,
                      'max':max_x,
                      'major_gridlines':{
                              'visible':True,
                              'line':{'width':1, 'dash_type':'dash'}
                              }                  
                      })
    chart.set_title({'name':'Returns between %s and %s' % (symb_id_lookup(symbol_id1), symb_id_lookup(symbol_id2))})
        
    chart.set_legend({'position':'bottom'})
    chart.set_chartarea({'border':{'none':True}})

    ## Insert chart into worksheet
    worksheet.insert_chart(cell, chart)


def excel_export(back, symbol_id1, symbol_id2, filepath): 
    

    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    sheet_name='coint_analysis'

    plot_results(writer, back, symbol_id1, symbol_id2, sheet_name, filepath, 'Q2')
    
    plot_scatter_ts(writer, back, symbol_id1, symbol_id2, sheet_name, filepath, 'Q18')

    plot_spread(writer, back, symbol_id1, symbol_id2, sheet_name, filepath, 'Z2')

    plot_returns(writer, back, symbol_id1, symbol_id2, sheet_name, filepath, 'Z18')


    writer.save()
    
filename = 'V:/Staff/Chris/Programming/Python/Quant/Quantstart/Outputs/test.xlsx';

excel_export(back, 4, 13, filename)
