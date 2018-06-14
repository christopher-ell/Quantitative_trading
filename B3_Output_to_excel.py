# -*- coding: utf-8 -*-
"""
Publish output for each working strategy into an Excel file

@author: Christopher Ell
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import openpyxl

filepath = 'V:\Staff\Chris\Programming\Python\Quant\Quantstart\Outputs\Template.xlsx'

writer = pd.ExcelWriter(filepath, engine='xlsxwriter')

sheet_name='test'

## Chart 1

def plot_results(writer, df, ts1, ts2, sheet_name, filepath, cell):
    
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
            'categories': '=test!$D$3:$D502',
            'values':'=test!$C$3:$C502'
            })

    chart.add_series({
            'name':ts2,
            'categories': '=test!$D$3:$D502',
            'values':'=test!$E$3:$E502'
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
    chart.set_title({'name':'%s and %s Cumulative Percent Growth' % (ts1, ts2)})
    
    chart.set_legend({'position':'bottom'})
    chart.set_chartarea({'border':{'none':True}})

    ## Insert chart into worksheet
    worksheet.insert_chart(cell, chart)

#    writer.save()




## Chart 2
def plot_scatter_ts(writer, df, ts1, ts2, sheet_name, filepath, cell):

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
            'categories': 'test!$E$3:$E502',
            'values':'=test!$C$3:$C502'
            })


    ## Configure chart axis
    chart.set_x_axis({'name':ts1,
                          'min':min_x2,
                          'max':max_x2})
    chart.set_y_axis({'name':ts2,
                          'min':min_x1,
                          'max':max_x1})
    
    chart.set_title({'name':'%s and %s Price Scatterplot' % (ts1, ts2)})
    
    chart.set_legend({'none':True})
    chart.set_chartarea({'border':{'none':True}})

    ## Insert chart into worksheet
    worksheet.insert_chart(cell, chart)
    
#    writer.save()

    
    
plot_scatter_ts(writer, back, 'adj_close_price4.0', 'adj_close_price26.0', sheet_name, filepath, 'Q18')

plot_results(writer, back, 'adj_close_price4.0', 'adj_close_price26.0', sheet_name, filepath, 'Q2')

writer.save()