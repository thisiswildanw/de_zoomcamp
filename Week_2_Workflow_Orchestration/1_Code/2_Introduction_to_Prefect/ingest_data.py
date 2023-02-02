#Import libraries
import os
import argparse
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from time import time
from datetime import timedelta
from prefect import flow, task
from prefect.tasks import task_input_hash
from prefect_sqlalchemy import SqlAlchemyConnector

@task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_data(url):
    #download parquet file
    os.system(f"wget {url}")

    #extract file_name
    #WARNING: script below is used only for this specific url
    file_name = url.split("/")[-1] 

    #read parquet using pandas
    df = pd.read_parquet(file_name)

    return df

@task(log_prints=True)
def transform_data(df):
    print(f"pre:missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] !=0]
    print(f"pre:missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    return df


@task(log_prints=True, retries=3)
def ingest_data(table_name, df):
    #create engine using prefect_alchemy
    connection_block = SqlAlchemyConnector.load("postgres-connector")
    with connection_block.get_connection(begin=False) as engine:
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

@flow(name="Subflow", log_prints=True)
def log_subflow(table_name:str):
    print("Logging Subflow for: {table_name}")

@flow(name="Ingest Flow")
def main_flow(): 
    table_name = "yellow_taxi_data"
    url="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"

    log_subflow(table_name)
    raw_data = extract_data(url)
    data = transform_data(raw_data)
    ingest_data(table_name, data)

if __name__ == '__main__':
    main_flow()