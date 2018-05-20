#%pylab inline   https://github.com/sjev/trading-with-python
def mod_Yahoo_downloader(ticker, sDate, eDate):
    import requests # interaction with the web
    import os  #  file system operations
    import yaml # human-friendly data format
    import re  # regular expressions
    import pandas as pd # pandas... the best time series library out there
    import datetime as dt # date and time functions
    import io

    #############################################################################
    ########################### Get Cookie and Token ############################
    #############################################################################

    # search with regular expressions

    # "CrumbStore":\{"crumb":"(?<crumb>[^"]+)"\}

    url = 'https://uk.finance.yahoo.com/quote/AAPL/history' # url for a ticker symbol, with a download link
    r = requests.get(url)  # download page

    txt = r.text # extract html

    cookie = r.cookies['B'] # the cooke we're looking for is named 'B'
                      #print('Cookie: ', cookie)

    # Now we need to extract the token from html. 
    # the string we need looks like this: "CrumbStore":{"crumb":"lQHxbbYOBCq"}
    # regular expressions will do the trick!

    pattern = re.compile('.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')

    for line in txt.splitlines():
        m = pattern.match(line)
        if m is not None:
            crumb = m.groupdict()['crumb']


    ##############################################################################
    ################################ Store Cookie ################################
    ##############################################################################

    # create data directory in the user folder
    dataDir = os.path.expanduser('~')+'/twpData'

    if not os.path.exists(dataDir):
        os.mkdir(dataDir)


    # save data to YAML file
    data = {'cookie':cookie,'crumb':crumb}

    dataFile = os.path.join(dataDir,'yahoo_cookie.yml')

    with open(dataFile,'w') as fid:
        yaml.dump(data,fid)
    
    ##############################################################################
    ########################## Get Actual Required Data ##########################
    ##############################################################################

    ## Required Parameters
    #sDate = (2017,5,1)
    #eDate = (2017,6,2)
    #ticker = "csl.ax"


    ## Get Data    
    # prepare input data as a tuple
    data = (int(dt.datetime(*sDate).timestamp()),
            int(dt.datetime(*eDate).timestamp()), 
               crumb)

    url = "https://query1.finance.yahoo.com/v7/finance/download/" + ticker + "?period1={0}&period2={1}&interval=1d&events=history&crumb={2}".format(*data)

    # Request actual data you want with cookie and changing certificate 
    # verification to false
    # Data comes out referenceable in difficult way
    data = requests.get(url, cookies={'B':cookie}, verify=False)
    p = data.text.strip().split(",")


    ## Reformat data
    dt.datetime(*sDate).timestamp() # convert to seconds since epoch  
    # io.string converts data 
    buf = io.StringIO(data.text) # create a buffer
    df = pd.read_csv(buf,index_col=0) # convert to pandas DataFrame
    df.head()
    
    return df

test_data = mod_Yahoo_downloader("RE", (2014,5,1), (2017,6,2))

#print(test_data[:3])