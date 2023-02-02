Week 2 Workflow Orchestration
=============================

> Next: (Comming Soon)

> Previous: [Week 1 Introduction](https://github.com/thisiswildanw/de_zoomcamp/tree/master/Week_1_Introduction)

> [Back to Start Page](https://github.com/thisiswildanw/de_zoomcamp)

Table of Contents: 
=================
- [Data Lake](#data-lake)
- [Introduction to Workflow Orchestration](#introduction-to-workflow-orchestration)
- [Introduction to Perfect Concepts](#introduction-to-perfect-concepts)
- [ETL with GCP & Perfect](#etl-with-gcp--perfect)
- [From Google Cloud Storage to Big Query](#from-google-cloud-storage-to-big-query)
- [Parameterizing Flow & Deployments with ETL Into GCS Flow](#parameterizing-flow--deployments-with-etl-into-gcs-flow)
- [Schedules & Docker Storage with Infrastructure](#schedules--docker-storage-with-infrastructure) 
- [Perfect Cloud/Additional Resource](#perfect-cloudadditional-resource)


Data Lake
=========

**Data lake** is a central repository that holds big data from many source & type of data (structured, semi-structured & unstructured). The main idea this concept is to ingest data *as quickly as* possible and *make it avalable* for many roles in organization.

Introduction to Workflow Orchestration
======================================

**Workflow orchestration** means gouvering your *data flow* in way that respects orchestration rules and business logic. 

Now what is this **data flow**? 

**Data flow** is what binds and otherwise, *disparate set of application together*. So, workflow orchestration tools is allow you to turn any code into a workflow that can scheduled and observed. 

Here core feature of workflow orchestration:
- Remote execution.
- Scheduling.
- Retries.
- Caching.
- Integrated with external systems (APIs, databases).
- Support ad-hoc runs. 
- Allowing parameterization or alerting when something fails.

Introduction to Perfect Concepts
================================
  
In this lesson, we use [**Prefect**](https:www.prefect.io) as workflow orchestration tool. 

Why **Prefect**?
- It's an *open-source* data flow platform.
- It allow you to add observability and orchestration using *Python* as code. 
- It let us build, run and monitor at scale. 

If you haven't installed **Prefect** yet, follow this [link](https://docs.prefect.io/getting-started/installation/)

<Blockquote>

We recommend this version to install: 
- prefect==2.7.7
- prefect-sqlalchemy==0.2.2
- prefect-gcp[cloud_storage]==0.2.3

</Blockquote>

If you have installed Perfect, Lets try it to orchestrate `ingest_data.py` on [previous](https://github.com/thisiswildanw/de_zoomcamp/tree/master/Week_1_Introduction#ingesting-nyc-taxi-data-to-postgres-with-python) lesson : 

- First lets modify our `ingest_data.py` :
  ```python

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
    def ingest_data(user, password, host, port, db, table_name, df):
        #create engine variable
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

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
        user = "root"
        password = "root"
        host = "localhost"
        port = "5432"
        db = "ny_taxi"
        table_name = "yellow_taxi_data"
        url="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"

        log_subflow(table_name)
        raw_data = extract_data(url)
        data = transform_data(raw_data)
        ingest_data(user,password, host, port, db, table_name, data)

    if __name__ == '__main__':
        main_flow()
        
  ```

#### 



ETL with GCP & Perfect
======================


From Google Cloud Storage to Big Query 
======================================

Parameterizing Flow & Deployments with ETL into GCS Flow 
========================================================


Schedules & Docker Storage with Infrastructure
===============================================

Perfect Cloud/Additional Resource
=================================