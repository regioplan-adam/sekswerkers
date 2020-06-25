import pypyodbc
import pandas as pd
import re
import math

def dbConnect():
    cnxn = pypyodbc.connect(
        '''DRIVER={ODBC Driver 17 for SQL Server};
        SERVER=regioplantestserver.database.windows.net;
        PORT=1433;
        DATABASE=regioplantestdb;
        UID=regioadmin;
        PWD=Henk2200quid!'''
        )

    return cnxn

# load queries
def query(name):
    '''
    Load sql query from working dir 
    '''
    dir_path = os.path.dirname(os.path.abspath(__file__))
    query = dir_path + '\\sqls\\' + name
    with open(query) as dwh_query:
        query = dwh_query.read()

    return query


# load datafraem
def readDb(query):
    '''
    Connect to datawarehouse, read query and close connection
    '''
    conn = dbConnect()
    df =  pd.read_sql(con=conn, sql=query)
    conn.close()

    return df

# push into datawarehouse
def insertVariblesIntoTable(dwh_table,pandas_df,primary_key=''):
    ''' Push pandas dataframe records into a datawarehouse table'''
    try:     
        # define dwh columns
        if primary_key != '':
            cols = str(tuple(readDb('SELECT * FROM '+dwh_table).drop(columns={primary_key})))
        else:
            cols = str(tuple(readDb('SELECT * FROM '+dwh_table)))
        cols = re.sub(r"'", "", cols)
        # connect to the data ware house 
        conn = dbConnect()
        cursor = conn.dbConnect()

        # sql sever allows max 1000 rows input
        lim = 1000
        runs = int(math.ceil(len(pandas_df) / lim))
        for x in range(0,runs):
            # push into the dwh
            dfrecordstuple = str([tuple(x) for x in pandas_df[lim*x:lim+(lim*x)].to_numpy()])
            dfrecordstuple = re.sub(r'[\[\]]', '', dfrecordstuple)
            cursor.execute('SET IDENTITY_INSERT '+dwh_table+'OFF\nINSERT INTO '+ \
                dwh_table + ' ' + cols + ' VALUES ' + dfrecordstuple)                                
            conn.commit()
            print(str(x+1)+'/'+str(runs)+' uploaded!')
        
        cursor.close()
        conn.close()

        print('Records inserted successfully into dwh-table: '+dwh_table)
        
    except Exception as error:
        print("Failed to insert into sql serer with the followig error:\n")    
        print(error)
