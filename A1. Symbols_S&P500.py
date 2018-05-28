# -*- coding: utf-8 -*-

"""
Look up Relevant Symbols for S&P500
"""

import datetime
import lxml.html as lh
import urllib.request
import MySQLdb as mdb

from math import ceil

def obtain_parse_wiki_snp500():
    """Download and parse the wikipedia list of S&P500
    constituents using requests and libxml.
    
    Returns a list of tuples for to add to MySQL."""
    
    # stores the current time, for the created_at record
    now = datetime.datetime.utcnow()
    
    # Use libxml to download the list of S&P500 companies and obtain symbol table
    url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    doc = lh.parse(urllib.request.urlopen(url))
    symbolslist = doc.xpath('//table[1]/tr')[1:]

    
    #obtain the symbole information for each row in the S&P500 constituent table
    symbols = []
    for symbol in symbolslist:
        tds = symbol.getchildren()
        sd = {'ticker': tds[0].getchildren()[0].text,
              'name': tds[1].getchildren()[0].text,
                'sector': tds[3].text}
        
        # Create a tuple (for the DB format) and append to grand list
        symbols.append((sd['ticker'], 'stock', sd['name'],
                        sd['sector'], 'USD', now, now))
    
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
            
if __name__ == "__main__":
    symbols = obtain_parse_wiki_snp500()
    insert_snp500_symbols(symbols)

#print(symbols)
    