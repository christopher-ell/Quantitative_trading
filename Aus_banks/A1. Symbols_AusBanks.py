# -*- coding: utf-8 -*-

"""
Look up Relevant Symbols for S&P500
"""

import datetime
import MySQLdb as mdb
import pandas as pd

from math import ceil

def obtain_banks():
    """Import table of bank symbol data."""
    
    # stores the current time, for the created_at record
    now = datetime.datetime.utcnow()
    
    # Use pandas to import and format table
    symbols = pd.read_table('V:\Staff\Chris\Programming\Python\Quant\Quantstart\Aus_Banks\Banks.txt')
    
    symbols['created_date'] = now
    symbols['last_update_date'] = now
           
#    symbols = [tuple(x) for x in symbols.values]
    
    return symbols


def insert_snp500_symbols(symbols):
    """insert the S&P500 into the MySQL database."""
    
    # Connect to the MySQL instance
    db_host = "localhost"
    db_user = "root"
    db_pass = "password"
    db_name = "securities_master"
    
    con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
    
    # Create the insert strings
    column_str = "ticker, instrument, name, sector, currency, created_date, last_update_date"
    insert_str = ("%s, " * 7)[:-2]
    final_str = "insert into symbol (%s) values (%s)" % (column_str, insert_str)
    #print(final_str, len(symbols))
    
    # Using the MySQL connection, carry out an insert into for every symbol
    with con:
        cur = con.cursor()
        # This line avoids the MySQL Max_PACKET_SIZE
        # Although of course it could be set larger!
        for i in range(0, int(ceil(len(symbols)/100.0))):
            cur.executemany(final_str, symbols[i*100:(i+1)*100-1])
            
#if __name__ == "__main__":
#    symbols = obtain_banks()
#    insert_snp500_symbols(symbols)

#print(symbols)

symbols = obtain_banks()

# Connect to the MySQL instance
db_host = "localhost"
db_user = "root"
db_pass = "password"
db_name = "securities_master"
    
con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
    
# Create the insert strings
column_str = "ticker, instrument, name, sector, currency, created_date, last_update_date"
insert_str = ("%s, " * 7)[:-2]
final_str = "insert into symbol (%s) values (%s)" % (column_str, insert_str)
#print(final_str, len(symbols))
    
# Using the MySQL connection, carry out an insert into for every symbol
with con:
    cur = con.cursor()
    # This line avoids the MySQL Max_PACKET_SIZE
    # Although of course it could be set larger!
    cur.executemany(final_str, symbols)
    