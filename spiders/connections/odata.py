import pandas as pd
import requests

def getOdata(target_url):
    data = pd.DataFrame()
    while target_url:
        r = requests.get(target_url).json()
        data = data.append(pd.DataFrame(r['value']))
        
        if '@odata.nextLink' in r:
            target_url = r['@odata.nextLink']
        else:
            target_url = None
            
    return data


# count row numbers
def odataCountRows(url, odata):
    ''' Counts the rows in data OData tables
    For more info on OData counting check:
    https://blogs.sap.com/2013/03/20/using-odatas-top-skip-and-count/
    '''
    odata_url = url # select the website that you whish to query
    odata_table = odata # select the disered table from the selected 
    target_url = odata_url + odata_table + '/$count'
    count = requests.get(target_url).json()

    return count


# load odata table
def odataToDataframe(url, odata, skip='',filters='',nr='', select=''):
    ''' Load data via an odata API, input gives the ability
    to skip, stop, and filter on different columns.
    For more info on filtering and selecting check:
    https://www.odata.org/documentation/odata-version-3-0/overview/
    For more info on stopping and skipping and counting check:
    https://blogs.sap.com/2013/03/20/using-odatas-top-skip-and-count/
    '''
    
    odata_url = url\
        # select the website that you whish to query
    odata_table = odata \
        # select the disered table from the selected 
    skip_row = '&$skip=' + str(skip) if skip != '' else '' \
        # select where to begin (in which row)
    filter_col = '&$filter=' + filters if filters != '' else '' \
        # can filter on column values (e.g. eq=equal to or gt=greather than) 
    select_col = '&$select=' + select if select != '' else '' \
        # select columns
    temp_nr = str(nr) if nr != '' else str(odataCountRows(odata_url,odata_table))
    nr_rows = '?$top=' + temp_nr 
        # standard all rows except specified differently 
    target_url = odata_url + odata_table + nr_rows + skip_row + filter_col + select_col  \
        # join all filter values together

    output = getOdata(target_url) # load data via OData
    
    return output


# overview sites
urls = {
    'cbs' : 'https://beta.opendata.cbs.nl/OData4/CBS/',
    'geo' : 'https://opendata.cbs.nl/ODataApi/odata/'
}


