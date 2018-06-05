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

back.to_excel(writer, sheet_name='test')

writer.save()




## PLOTS
## ts1 is company 1 and ts2 is company 2
## 
def plot_results(df, ts1, ts2, filepath, cell):
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.plot(df['price_date'], df[ts1], label=ts1)
    ax.plot(df['price_date'], df[ts2], label=ts2)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
#    ax.set_xlim(datetime.datetime(start_year, start_month_num, start_day_num), datetime.datetime(end_year, end_month_num, end_day_num))
    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel('Month/Year')
    plt.ylabel('Cumulative Percent Growth')
    plt.title('%s and %s Cumulative Percent Growth' % (ts1, ts2))
    plt.legend()
    plt.savefig('plot.png', dpi=150)
    
    plt.show()
    
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active    
    img = openpyxl.drawing.image.Image('plot.png')
    img.anchor(ws.cell(cell))
    ws.add_image(img)
    wb.save(filepath)

    



def plot_scatter_ts(df, ts1, ts2, filepath, cell):
    plt.xlabel('%s Price ($)' % ts1)
    plt.ylabel('%s Price ($)' % ts2)
    plt.title('%s and %s Price Scatterplot' % (ts1, ts2))
    plt.scatter(df[ts1], df[ts2])
    
#    plt.show()
    
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    plt.savefig('plot.png', dpi=150)    
    img = openpyxl.drawing.image.Image('plot.png')
    img.anchor(ws.cell(cell))
    ws.add_image(img)
    wb.save(filepath)

    

plot_results(back, 'adj_close_price4.0', 'adj_close_price26.0', filepath, 'P2')

plot_scatter_ts(back, 'adj_close_price4.0', 'adj_close_price26.0', filepath, 'P34')
    




    



