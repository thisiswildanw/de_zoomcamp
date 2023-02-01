#Import libraries
import os
import argparse
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from time import time

def main(params):
    #get parameter
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    file_name = 'yellow_tripdata_2021-01.parquet'

    #download parquet file
    os.system(f"wget {url}")

    #create engine variable
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    #read parquet using pandas
    df = pd.read_parquet(file_name)


    #try to create schema if exist, then replace it
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    #create batch size using floor division
    batch_size = len(df) // 100000 
    
    #batch spliting dataframe
    list_df = np.array_split(df, batch_size)

    #Create batch ingestion
    for i in range(batch_size):
        try:
            t_start = time()
            list_df[i].to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            j =i+1
            print('Batch data no-' + str(j) +' inserted to database, it took %.3f second' % (t_end - t_start))
        except StopIteration:
            print("Ingestion Failed!")


if __name__ == '__main__':
    # Parse the command line arguments and calls the main program
    parser = argparse.ArgumentParser(description='Ingest Parquet data to Postgres')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name', help='name of the table where we will write the results to')
    parser.add_argument('--url', help='url of parquet file')

    args = parser.parse_args()

    main(args)