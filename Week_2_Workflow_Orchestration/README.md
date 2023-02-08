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
- [Week 2 Homework](#week-2-homework)


Data Lake
=========

**Data lake** is a central repository that holds big data from many source & type of data (structured, semi-structured & unstructured). The main idea this concept is to ingest data *as quickly as* possible and *make it avalable* for many roles in organization.

_[back to the top](#table-of-contents)_

<br></br>

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

_[back to the top](#table-of-contents)_

<br></br>


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

If you have installed Perfect, Lets try it to orchestrate `ingest_data.py` on [previous](https://github.com/thisiswildanw/de_zoomcamp/tree/master/Week_1_Introduction#ingesting-nyc-taxi-data-to-postgres-with-python) lesson by following this step : 

1. Modify our `ingest_data.py`:
    -  First, split the ingestion process script into three function (`extract_data()` , `transform_data()` and `ingest_data()`). 
    -  Import new function: 
        - `prefect.task` : represents a discrate action in a Prefect workflow. 
        - `prefect.flow` : is a container for task. It represents an entire workflow or application by describing the dependencies between tasks. 
        - `prefect.tasks.task_input_hash` : required to for task caching. 
        - `datetime.timedelta` : required to calculating difference date in task caching.
        - `prefect_sqlalchemy.SqlAlchemyConnector` : required to create connection with databases.
    -  For `extract_data()` function, we modify it as Prefect task using `@task` with 4 parameter setting : 
        - `log_print` as `True` to enable the loggin of print task statements. 
        - `retries=3`. This tasks runs 3 times before the flow fails. 
        - `cache_key_fn=task_input_hash` to create specify the cache key function in task caching. Prefect task can be cached which case the outputs will be reused for future runs. For example, you might want to make sure that a database is loaded before generating reports, but you might not want to run the load task every time the flow is run. No problem: just cache the load task for 24 hours, and future runs will reuse its successful output.
        -  `cache_expiration=timedelta(days=1)` to set 1 day or 24 hours as expiration time in this task.
    
        Besides using Prefect to orchestrate and observe this task, there 3 main process in this script. First, we get file from url. Then, set file name by getting last `string` from splited url . Finally, read the `parquet` file and return it as `dataframe`. 

    -  `transform_data()` is new function in `ingest_data.py`. This function is required to remove and count all data with **zero passenger**. We also using `@task` to orchestrate and observe this function with parameter (`log_print`= `True` and `retries=3`).

    -   Create **Prefect Block** to store postgres configuration by following this step:
        - Run this command in terminal. 
            ``` prefect orion start ```
            <p align="center">
            <img src="2_Images/2_Introduction_to_Prefect/1.png" >
            </p>
            <br>

        - Check out the dashboard at `https://127.0.0.1:4200`.
            
            <p align="center">
            <img src="2_Images/2_Introduction_to_Prefect/2.png" >
            </p>
            <br>

        - Click `Hamburger Button` >  `Block` > `Add Block +`.
        - Select `SQLAlchemy Connector`.
            <p align="center">
            <img src="2_Images/2_Introduction_to_Prefect/3.png" >
            </p>
            <br>
        
        - Fill the `Block Name` form as "postgres-connector".
        - Click `SyncDriver`.
        - Select `postgre+psycopg2`.
        - Fill other form : 
            - `Database` : ny_taxi.
            - `Username` : root.
            - `Password` : root.
            - `Host`     : localhost.
            - `Port`     : 8080:80.
        - Keep empty for other `optional` form. 
        - Click `Create`.

            <p align="center">
            <img src="2_Images/2_Introduction_to_Prefect/4.png" >
            </p>
            <br>

        >Note : Username and Password in this project are meant for testing. Please give more appropriate Username and Password for daily production. 

    - After creating connection block, we can use it to simplify `ingest_data()` parameter using `SqlAlchemyConnector.load("postgres-connector")`. In addition fuction, we create `log_subflow` to print `table_name`.
    - In the end, we keep the rest of `ingest_data.py` functionally similiar with previous lesson. 
    - Here completed version of modified `ingest_data.py`: 

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
        
  ```
  <br>

2. Run modified `ingest_data.py` using following this command

   ``` python ingest_data.py ```
    
    <p align="center">
    <img src="2_Images/2_Introduction_to_Prefect/5.png" >
    </p>
    <br>



3. Lets check in pgAdmin. It shouldn't have data with zero passenger. 

    
    <p align="center">
    <img src="2_Images/2_Introduction_to_Prefect/6.png" >
    </p>
    <br>

4. Then, check how many data *more than* zero passenger. Its **1,244,691** row.

    <p align="center">
    <img src="2_Images/2_Introduction_to_Prefect/7.png" >
    </p>
    <br>

5. In the end, check the flow run in Prefect UI. Well, `ingest_flow` take 21 minutes to complete, while `sub_flow` almost near 0 minutes. 
    <p align="center">
    <img src="2_Images/2_Introduction_to_Prefect/8.png" >
    </p>
    <br>

_[back to the top](#table-of-contents)_

<br></br>


ETL with GCP & Perfect
======================

In this lesson, we will try to implement ETL (extract, transform, load) process to Google Cloud (Storage) using Python & Prefect by following this step:

1. Intstall required libraries on [requirements.txt](/Week_2_Workflow_Orchestration/1_Code/3_ETL_GCP_Prefect/requirements.txt) using `pip install -r requirements.txt`.

2. Run Prefect on terminal using `prefect orion start`. Dont forget to check out Prefect dashboard at `https://127.0.0.1:4200`.

3. Open VScode or another code editor. We will using `Python` as basic programming language. 

4. Create new python tab, and name it as `etl_web_to_gcs.py`. 

5. Import required function: profobuf
5. Import required function: profobuf

    ```python
    from pathlib import Path
    import pandas as pd
    from prefect import flow, task
    from prefect_gcp.cloud_storage import GcsBucket
    ```

6. Create Prefect `task` to get dataset from repositories, then read and return it as `dataframe`.
    In this lesson, we are using Januray 2021 NYC Yellow Taxi data with (`.csv`) format from [Data Engineering Zoomcamp repository](https://github.com/DataTalksClub/nyc-tlc-data). 
    
    The url : ```https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz```

    Python code:
    ```python
    @task(retries=3)
    def get_data(url:str):
        df = pd.read_csv()
        return df 
    ```

7. Create Prefect `task` to fix data types issue of `tpep_pickup_datetime` and `tpep_dropoff_datetime"`columns, then return it as cleaned `dataframe`. 

    Python code:
    ```python
    @task()
    def clean(df = pd.DataFrame):
        df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"] )
        df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"] )
        return df
    ```

8. Create Prefect `task` to export our cleaned `dataframe` and write it to `.parquet` file and store it to our local storage.

    Python code:
    ```python
    @task(log_prints=True)
    def write_local(df, color, dataset_file):
        path = Path(f"data/{color}/{dataset_file}.parquet")

        df.to_parquet(path, compression="gzip")
        return path
    ```


9. Setting up Google Cloud Storage. 
    - Go to ```concole.cloud.google.com```.
    - Click `Navigation Bar` (The Hamburger Icon), Click `Cloud Storage` > `Bucket`.
    <p align="center">
    <img src="2_Images/3_ETL_GCP_Prefect/1.png" >
    </p>
    <br>

    - Select `+ Create`, if you dont have any cloud buckets.
        - Fill the first form with your bucket name, we choice `prefect-test-de`
        - Keep it default for the rest form.
        - Click `CREATE`. 

        <p align="center">
        <img src="2_Images/3_ETL_GCP_Prefect/2.png" >
        </p>
        <br>


10. Access configuration. We have created  `google service account` on [previous lesson](#introduction-to-perfect-concepts). Let use it. 

    >Note : Make sure that you have given `Biguery Admin`, `Storage Admin` role permission to your `service account`. 

12. GCS Bucket Block configuration on Prefect UI. 
    Lets make a block: 
    - Check out the dashboard at `https://127.0.0.1:4200`.
    - Click `Navigation Bar` (The Hamburger Button), then click `Blocks` > `+`.
    - Find `GCS Bucket` on search form. Click `Add +`.
    - Fill first form with your block name. 
    - Name the scond form with your bucket name. 
    - On GCP Credentials menu, copy-paste all your `service account` information as `dictionaries` to `service account info` form. 
    - Keep the rest empty, then click `Create`.
        <p align="center">
        <img src="2_Images/3_ETL_GCP_Prefect/3.png" >
        </p>
        <br>

13. Create Prefect `task` to upload `parquet` file to Google Cloud Storage.
    Python code:
    ```Python
    @task()
    def write_gcs(path):
        gcs_block = GcsBucket.load("prefect-gcs")
        gcs_block.upload_from_path(
            from_path=f"{path}",
            to_path=path
    )
    ```

14. Combine all task and create Prefect flow using `@flow` as main function `etl_web_gcs()` . 
    
    Python code:
    ```Python

    @flow(log_prints=True)
    def etl_web_to_gcs():
        color   = "yellow"
        year    = 2021
        month   = 1
        dataset_file=f"{color}_tripdata_{year}-{month:02}"
        dataset_url= f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
        
        df = get_data(dataset_url)
        cleaned_df = clean(df)
        path = write_local(cleaned_df, color, dataset_file)
        write_gcs(path)
    
    if __name__ == "__main__":
    etl_web_to_gcs()
    ```

15. Execute [`etl_web_to_gcs.py`](/Week_2_Workflow_Orchestration/1_Code/3_ETL_GCP_Prefect/etl_web_to_gcs.py) by following this command : `python etl_web_to_gcs.py`.

    <p align="center">
    <img src="2_Images/3_ETL_GCP_Prefect/4.png" >
    </p>
    <br>

16. Check the result on cloud bucket in images below and you can see `parquet` file was **successfully** uploaded to GCS via Prefect & Python. 

    <p align="center">
    <img src="2_Images/3_ETL_GCP_Prefect/5.png" >
    </p>

_[back to the top](#table-of-contents)_

<br></br>

From Google Cloud Storage to Big Query 
======================================

We have learned how to extract, transform data and load it to Google Cloud Storage. In this lesson we will try to extract data from Google Cloud Storage, transform it and load it directly to Google BigQuery using Python and Prefect by following this step: 

1. Open VScode or another code editor. We will using `Python` as basic programming language. 

2. Create new python tab, and name it as `etl_gcs_to_bq.py`. 

3. Import required function.

    Python Code: 

    ```python
    from pathlib import Path
    import pandas as pd
    from prefect import flow, task
    from prefect_gcp.cloud_storage import GcsBucket
    from prefect_gcp import GcpCredentials
    ```

4. Create Prefect `task` to extract `parquet` data from google cloud storage that was uploaded in the previous lesson, save it to local storage and return it as `file path`. 

    Python Code:

    ```Python
    @task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
    def extract_from_gcs(color, year, month ):
        gcs_path=f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
        gcs_block= GcsBucket.load("prefect-gcs")
        gcs_block.get_directory(from_path=f"{gcs_path}", local_path=f"../data/")
        return Path(f"../data/{gcs_path}")
    ```

5. Create Prefect `task` to convert `null` value in `passenger_count` column and count it rows before and after converted, then return it as `dataframe`.

    ```Python
    @task(log_prints=True, retries=3)
    def transform(path):
        df = pd.read_parquet(path)
        print (f"pre: missing passenger count : {df['passenger_count'].isna().sum()}")
        df['passenger_count'].fillna(0, inplace=True)
        print (f"post: missing passenger count : {df['passenger_count'].isna().sum()}")
        return df
    ```

6. Setting up Google Big Query. We need it to create empty table as fast as posible for new data.  
    - Go to ```concole.cloud.google.com```.
    - Click `Navigation Bar` (The Hamburger Icon), Click `Google BigQuery`.
    - If you don have any database, click 3 dots button on the right project id. Then click `Create dataset`.
        <p align="center">
        <img src="2_Images/4_ETL_GCS_to_BQ/1.png" >
        </p>
        <br>


    - Name it whatever you want. We choose `test_bq`.
        <p align="center">
        <img src="2_Images/4_ETL_GCS_to_BQ/2.png" >
        </p>
        <br>
    - On the right `test_bq` click 3 dots button, then click `Create table`.
        - Name it whatever you want. We choose `test_bq`.
        <p align="center">
        <img src="2_Images/4_ETL_GCS_to_BQ/3.png" >
        </p>from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_gcp.cloud_storage import GcsBucket

@task(retries=3,log_prints=True, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def get_data(url:str):
    df = pd.read_csv(url)
    return df 


@task(log_prints=True, )
def clean(df = pd.DataFrame):
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    return df

@task(log_prints=True)
def write_local(df, color, dataset_file):
    path = Path(f"data/{color}/{dataset_file}.parquet")

    df.to_parquet(path, compression="gzip")
    return path

@task()
def write_gcs(path):
    gcs_block = GcsBucket.load("prefect-gcs")
    gcs_block.upload_from_path(
        from_path=f"{path}",
        to_path=path
    )

@flow(log_prints=True)
def etl_web_to_gcs():
    color   = "yellow"
    year    = 2021
    month   = 1
    dataset_file=f"{color}_tripdata_{year}-{month:02}"
    dataset_url= f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
    
    df = get_data(dataset_url)
    cleaned_df = clean(df)
    path = write_local(cleaned_df, color, dataset_file)
    write_gcs(path)


if __name__ == "__main__":
    etl_web_to_gcs()
        <br>

        - Select `Google Cloud Storage` on first form. 
        - In the next selection form, Select `browser` > `prefect-test-de` bucket > `data` > `yellow` > select `yellow_tripdata_2021-01.parquet` filename. 
        - Fill table name whatever you want. We choose `yellow_trips_21_01`.
        - Keep other form as default, then click `Create Table`.
             <p align="center">
             <img src="2_Images/4_ETL_GCS_to_BQ/4.png" >
             </p>
             <br>

7. The current `yellow_trips_21_01` table has null value on `passenger_count` column. We will truncate the table using `SQL Query` and write new table value to `yellow_trips_21_01` on BigQuery via Prefect `task`.
    - Open `Query Editor` by click 3 dots button on the right table name. 
      <p align="center">
      <img src="2_Images/4_ETL_GCS_to_BQ/5.png" >
      </p>
      <br>
    - Run this `SQL Query` : `TRUNCATE TABLE 'test_bq.yellow_trips_21_01'`.
      <p align="center">
      <img src="2_Images/4_ETL_GCS_to_BQ/6.png" >
      </p>
      <br>
    - Create Prefect `task` on `etl_gcs_to_bq.py` to write modified `dataframe` and load it to `BigQuery` as end point.

        Python Code: 
        ```Python 
        @task(log_prints=True,retries=3)
        def write_to_bq(df):
            gcp_credentials_block = GcpCredentials.load("prefect-bq")

            df.to_gbq(
                destination_table="test_bq.yellow_trips_21_01",
                credentials = gcp_credentials_block.get_credentials_from_service_account(),
                project_id = "dezoomcamp-376313",
                chunksize = 500000,
                if_exist="append"
            )
        ```
8. Create Prefect `flow` to run all Prefect `task` from `extract_from_gcs()` > `transform()` > `write_to_bq`. 

    ```Python
    @flow(log_prints=True, retries=3)
    def etl_gcs_to_bq():
        color   = "yellow"
        year    = 2021
        month   = 1

        path = extract_from_gcs(color, year, month)
        df = transform(path)
        write_to_bq(df)

    if __name__ == "__main__":
        etl_gcs_to_bq()
    ```

9. Execute [`etl_gcs_to_bq.py`](/Week_2_Workflow_Orchestration/1_Code/4_ETL_GCS_to_BQ/etl_gcs_to_bq.py) by following this command : `python etl_gcs_to_bq.py`.
      <p align="center">
      <img src="2_Images/4_ETL_GCS_to_BQ/7.png" >
      </p>
      <br>

10. Check out load process on Bigquery `Query Editor` by run following query below. Its succesfully showing **1,369,765** row size.

    ```SQL
    SELECT
        COUNT(1) ROW_SIZE
    FROM
        `test_bq.yellow_trips_21_01`
    WHERE 
        passenger_count IS NOT NULL;
    ```
    Query Result: 

    <p align="center">
    <img src="2_Images/4_ETL_GCS_to_BQ/8.png" >
    </p>
    <br>

_[back to the top](#table-of-contents)_

<br></br>


Parameterizing Flow & Deployments with ETL into GCS Flow 
========================================================

In this lesson, We are going to learn how to add parameterization to Prefect flows and create deployment. 

What is parameterizing? It means allowing your prefect flow to take parameters, so when we actually schedule it, it's not hard to coded anymore. 

Here step-by-step using Python: 

1. Create copy of [`etl_web_gcs.py`](/Week_2_Workflow_Orchestration/1_Code/3_ETL_GCP_Prefect/etl_web_to_gcs.py) and name it as [`parameterizing_flow.py`](/Week_2_Workflow_Orchestration/1_Code/5_Parameterizing_Flow/parameterized_flow.py). 

2. On the first step, of course we add parameter to main function `etl_web_gcs()`.

    Before : 
    ```Python 
    def etl_web_gcs():
    ```

    After : 
    
    ```Python 
    def etl_web_gcs(year:int, month:int, color:str)-> None:
    ``` 

3. Let create parent flow that's going to trigger `etl_web_gcs()` and repeat it three times for three different months.  
    Pyhton Code:
    ```Python
    @flow()
    def etl_parent_flow(
        year:int, months: list[int], color:str
        ):
        for month in months:
            etl_web_to_gcs(year, month, color)

    if __name__ == "__main__":
        color = "yellow"
        months = [1,2,3]
        year=2021
        etl_parent_flow()
    ```

4. Run [`parameterized_flow.py`](/Week_2_Workflow_Orchestration/1_Code/5_Parameterizing_Flow/parameterized_flow.py) by following this command:
    ```Python parameterized_flow.py ```

6. Check out Prefect dashboard on `http://127.0.0.1:4200/flow-runs`. You see, `etl_parent_flow()` and all `etl_web_to_gcs()` function has successfully executed. 

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/1.png" >
    </p>
    <br>

7. Go to Google Storage> `prefect-test-de` (my bucket)> `data` > `yellow`. You see in image below, that we have 3 different months yellow trip data in bucket. It mean, that `parameterized_flow.py` with additional parameter successfully uploading 3 `parquet` data (based of our input) to Google Storage. 

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/2.png" >
    </p>
    <br>

We have learn how to `add parameterization` to `Prefect flow`, but running process is still manual and it is not a best practice. So, we need to learn how to create `Prefect deployment`. 

What is it?. 

Creating a `deployment` for a `Prefect` workflow means packaging workflow code, settings, and infrastructure configuration so that the workflow can be managed via the Prefect API and run it remotely.

In this section, we will create Prefect deployement for `parameterized_flow.py` by following this step:

1. Open directory where `paramerized_flow.py` stored via terminal. 

2. Build a prefect deployment by running this command: 
    `prefect deployment build parameterized_flow.py:etl_parent_flow -n "Parameterized ETL"`

    You see, in image below that a `yaml` file has created. `yaml` file in this project store all of `parameterized_flow.py` metadata.  

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/3.png" >
    </p>
    <br>

    Add year, months and color parameter in `etl_parent_flow-deployment.yaml`. Here the complete `yaml` file : 

    ```Yaml
        ###
        ### A complete description of a Prefect Deployment for flow 'etl-parent-flow'
        ###
        name: Parameterized ETL
        description: null
        version: a3c49c225ec46af4f93b83257ed3516c
        # The work queue that will handle this deployment's runs
        work_queue_name: default
        tags: []
        parameters: {"color":"yellow", "months":[1,2,3], "year": 2021}
        schedule: null
        infra_overrides: {}
        infrastructure:
        type: process
        env: {}
        labels: {}
        name: null
        command: null
        stream_output: true
        working_dir: null
        block_type_slug: process
        _block_type_slug: process

        ###
        ### DO NOT EDIT BELOW THIS LINE
        ###
        flow_name: etl-parent-flow
        manifest_path: null
        storage: null
        path: /home/thisiswildanw/project/de_zoomcamp/Week_2_Workflow_Orchestration/1_Code/5_Parameterizing_Flow
        entrypoint: parameterized_flow.py:etl_parent_flow
        parameter_openapi_schema:
        title: Parameters
        type: object
        properties:
            year:
            title: year
            position: 0
            type: integer
            months:
            title: months
            position: 1
            type: array
            items:
                type: integer
            color:
            title: color
            position: 2
            type: string
        required:
        - year
        - months
        - color
        definitions: null
    ```
3. Run `etl_parrent_flow-deployment.yaml` by following this command:
    `prefect deployment apply etl_parent_flow-deployment.yaml`
    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/4.png" >
    </p>
    <br>
3. Run `etl_parrent_flow-deployment.yaml` by following this command:
    `prefect deployment apply etl_parent_flow-deployment.yaml`
    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/4.png" >
    </p>
    <br>

4. Ahha, lets check out our prefect deployment dashboard on `http://127.0.0.1:4200/deployments`, then select `etl-parent-flow/Parameterized ETL`. 
    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/5.png" >
    </p>
    <br>
4. Ahha, lets check out our prefect deployment dashboard on `http://127.0.0.1:4200/deployments`, then select `etl-parent-flow/Parameterized ETL`. 
    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/5.png" >
    </p>
    <br>

5. The Prefect deployment has been running, but if you check `Work Queues` menu, it is in waiting state and not started yet. 
    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/6.png" >
    </p>
    <br>

    Lets start deployment job by following this command `prefect agent start --work-queue "default"`.

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/7.png" >
    </p>
    <br>

    Open `Work Queues` menu. Well, it takes `5 minute 19 second` to complete `etl-parent-flow`.

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/8.png" >
    </p>
    <br>



6. Dont forget to check our Google Storage Bucket. You see, that 3 different months yellow taxi data has stored. It meant, our Prefect successfully executed. 

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/9.png" >
    </p>
    <br>

_[back to the top](#table-of-contents)_

<br></br>

5. The Prefect deployment has been running, but if you check `Work Queues` menu, it is in waiting state and not started yet. 
    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/6.png" >
    </p>
    <br>

    Lets start deployment job by following this command `prefect agent start --work-queue "default"`.

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/7.png" >
    </p>
    <br>

    Open `Work Queues` menu. Well, it takes `5 minute 19 second` to complete `etl-parent-flow`.

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/8.png" >
    </p>
    <br>



6. Dont forget to check our Google Storage Bucket. You see, that 3 different months yellow taxi data has stored. It meant, our Prefect successfully executed. 

    <p align="center">
    <img src="2_Images/5_Parameterizing_Flow/9.png" >
    </p>
    <br>

_[back to the top](#table-of-contents)_

<br></br>


Schedules & Docker Storage with Infrastructure
===============================================

In this lesson, we will learn how to schedulling flows and also running flow in docker containers. 
In this lesson, we will learn how to schedulling flows and also running flow in docker containers. 

#### Schedule Flow via UI
#### Schedule Flow via UI

So, first we will learn about schedulling flows by following step below: 

1. Check out Prefect deployment dashboard at `http://127.0.0.1:4200/deployments`. Click `Parameterized ETL`, then `Add` schedule. 

    <p align="center">
    <img src="2_Images/6_Schedulling_and_Containerizing/1.png" >
    </p>
    <br>

    In add schedule menu below, you see that we can manage schedule type based `Interval`, `Cron` and `Rrule`. Moreover, we can set time zone and it really helpful to schedule flow wherever country we are. 
    
    <p align="center">
    <img src="2_Images/6_Schedulling_and_Containerizing/2.png" >
    </p>
    <br>

    In this section, we try to set every five minute to run this prefect deployment. You can change it whatever you want.
    
    <p align="center">
    <img src="2_Images/6_Schedulling_and_Containerizing/3.png" >
    </p>
    <br>

2.  You can also schedule flow when creating deployment. Check this [link](https://docs.prefect.io/concepts/schedules/) for more information.

<br>

#### Running Flows In Docker Container

We can put our Prefect flow code in lots of different place, so far we have running locally on our machine and that's been nice for getting started. But, if we want to make things a little bit more production ready and have other people be able to access our flow code storage we could put it on version control system (github, gitlab, etc), we could do it with Cloud (AWS S3, Google Cloud Storage, Azure Blob Storage) so we have a lot of options. 

In this section, we going to store our code in a Docker image and put it up on Docker Hub and then when we run a Docker container that code will be right there by following this step: 

1. Create `Dockerfile`. 
    ```Dockerfile
    FROM prefecthq/prefect:2.7.7-python3.9

    COPY requirements.txt .

    RUN pip install -r requirements.txt --trusted-host pypi.python.org --no-cache-dir

    COPY flows /opt/prefect/flows
    COPY data /opt/prefect/data

    ```
2. Create requirements.txt
    
    ```
    pandas==1.5.2
    prefect==2.7.7
    prefect-gcp[cloud_storage]==0.2.3
    profobuf==4.21.11
    pyarrow==10.0.1
    ```

3. Build `Dockerfile` image by following this command `docker image build -t try/prefect:zoomcamp .`

4. Let's push that all up to Docker Hub, so anyone can access it there. 
    - Create docker container block:
        - Go to prefect block in navigation manu.
        - Add new block, select `Docker Container`.
        - Name your block, whatever you want. 
        - Add Docker Tage of your docker image.
        - Select `ALWAYS` in your image pull policy form.
        - Click `Create`.
    
    - We also can craete docker block via pyton programming by following this code:
        ```Pyhton
        from prefect.infrastucture.docker import DockerContainer

        docker_block = DockerContainer(
            image="try/prefect:zoomcamp
            image_pull_policy="ALWAYS"
            auto_remove=True
        )

        docker_block.save("zoom", overwrite=True)

        ```
5. Create prefect deployment, in this section we will create it via python:
    ```Python
    from prefect.deployments import Deployment
    from prefect.infrastructure.docker import DockerContainer
    from parameterized_flow import etl_parent_flow

    docker_block= DockerContainer.load("zoomcamp")

    docker_dep = Deployment.build_from_flow(
        flow=etl_parent_flow,
        name="docker-flow",
        infrastructure=docker_block
    )
    if __name__ == "__main__":
        docker_dep.apply()
    ```
6. Start `default` agent by following this command on CLI:
    `prefect agent start -q default`

7. Run the deployement queue: 
    `prefect deployment run etl-parent-flow/docker-flow`


_[back to the top](#table-of-contents)_

<br></br>

So, first we will learn about schedulling flows by following step below: 

1. Check out Prefect deployment dashboard at `http://127.0.0.1:4200/deployments`. Click `Parameterized ETL`, then `Add` schedule. 

    <p align="center">
    <img src="2_Images/6_Schedulling_and_Containerizing/1.png" >
    </p>
    <br>

    In add schedule menu below, you see that we can manage schedule type based `Interval`, `Cron` and `Rrule`. Moreover, we can set time zone and it really helpful to schedule flow wherever country we are. 
    
    <p align="center">
    <img src="2_Images/6_Schedulling_and_Containerizing/2.png" >
    </p>
    <br>

    In this section, we try to set every five minute to run this prefect deployment. You can change it whatever you want.
    
    <p align="center">
    <img src="2_Images/6_Schedulling_and_Containerizing/3.png" >
    </p>
    <br>

2.  You can also schedule flow when creating deployment. Check this [link](https://docs.prefect.io/concepts/schedules/) for more information.

<br>

#### Running Flows In Docker Container

We can put our Prefect flow code in lots of different place, so far we have running locally on our machine and that's been nice for getting started. But, if we want to make things a little bit more production ready and have other people be able to access our flow code storage we could put it on version control system (github, gitlab, etc), we could do it with Cloud (AWS S3, Google Cloud Storage, Azure Blob Storage) so we have a lot of options. 

In this section, we going to store our code in a Docker image and put it up on Docker Hub and then when we run a Docker container that code will be right there by following this step: 

1. Create `Dockerfile`. 
    ```Dockerfile
    FROM prefecthq/prefect:2.7.7-python3.9

    COPY requirements.txt .

    RUN pip install -r requirements.txt --trusted-host pypi.python.org --no-cache-dir

    COPY flows /opt/prefect/flows
    COPY data /opt/prefect/data

    ```
2. Create requirements.txt
    
    ```
    pandas==1.5.2
    prefect==2.7.7
    prefect-gcp[cloud_storage]==0.2.3
    profobuf==4.21.11
    pyarrow==10.0.1
    ```

3. Build `Dockerfile` image by following this command `docker image build -t try/prefect:zoomcamp .`

4. Let's push that all up to Docker Hub, so anyone can access it there. 
    - Create docker container block:
        - Go to prefect block in navigation manu.
        - Add new block, select `Docker Container`.
        - Name your block, whatever you want. 
        - Add Docker Tage of your docker image.
        - Select `ALWAYS` in your image pull policy form.
        - Click `Create`.
    
    - We also can craete docker block via pyton programming by following this code:
        ```Pyhton
        from prefect.infrastucture.docker import DockerContainer

        docker_block = DockerContainer(
            image="try/prefect:zoomcamp
            image_pull_policy="ALWAYS"
            auto_remove=True
        )

        docker_block.save("zoom", overwrite=True)

        ```
5. Create prefect deployment, in this section we will create it via python:
    ```Python
    from prefect.deployments import Deployment
    from prefect.infrastructure.docker import DockerContainer
    from parameterized_flow import etl_parent_flow

    docker_block= DockerContainer.load("zoomcamp")

    docker_dep = Deployment.build_from_flow(
        flow=etl_parent_flow,
        name="docker-flow",
        infrastructure=docker_block
    )
    if __name__ == "__main__":
        docker_dep.apply()
    ```
6. Start `default` agent by following this command on CLI:
    `prefect agent start -q default`

7. Run the deployement queue: 
    `prefect deployment run etl-parent-flow/docker-flow`


_[back to the top](#table-of-contents)_

<br></br>


Perfect Cloud/Additional Resource
=================================

(Comming Soon)


Week 2 Homework
===============


#### Question 1. Load January 2020 data
Using the `etl_web_to_gcs.py` flow that loads taxi data into GCS as a guide, create a flow that loads the green taxi CSV dataset for January 2020 into GCS and run it. Look at the logs to find out how many rows the dataset has.

How many rows does that dataset have?
#### Answer : 447,770 (A)

<p align="center">
<img src="3_Homework/images/1.png" >
</p>
<br>


#### Question 2. Scheduling with Cron
Cron is a common scheduling specification for workflows.

Using the flow in etl_web_to_gcs.py, create a deployment to run on the first of every month at 5am UTC. What’s the cron schedule for that?
#### Answer : 0 5 1 * * (A)


<p align="center">
<img src="3_Homework/images/2.png" >
</p>
<br>

<p align="center">
<img src="3_Homework/images/9.png" >
</p>
<br>

#### Question 3. Loading data to BigQuer
Using etl_gcs_to_bq.py as a starting point, modify the script for extracting data from GCS and loading it into BigQuery. This new script should not fill or remove rows with missing values. (The script is really just doing the E and L parts of ETL).

The main flow should print the total number of rows processed by the script. Set the flow decorator to log the print statement.

Parametrize the entrypoint flow to accept a list of months, a year, and a taxi color.

Make any other necessary changes to the code for it to function as required.

Create a deployment for this flow to run in a local subprocess with local flow code storage (the defaults).

Make sure you have the parquet data files for Yellow taxi data for Feb. 2019 and March 2019 loaded in GCS. Run your deployment to append this data to your BiqQuery table. How many rows did your flow code process?
#### Answer : 14,851,920

- Python Code:
    ```Python
    import os
    import pandas as pd
    from pathlib import Path
    from prefect import task, flow
    from prefect.tasks import task_input_hash
    from datetime import timedelta
    from prefect_gcp.cloud_storage import GcsBucket
    from prefect_gcp import GcpCredentials


    @task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
    def get_url_write_local(url, color):
        file_name = url.split("/")[-1]
        os.system(f" wget -P data/{color} {url}" )
        
        path = Path(f"data/{color}/{file_name}")
        return path

    @task()
    def write_gcs(chunk_path, gcs_path):
        gcs_block = GcsBucket.load("prefect-gcs")
        gcs_block.upload_from_path(
            from_path=f"{chunk_path}",
            to_path=f"{gcs_path}"
        )

    @task(log_prints=True,retries=3)
    def write_to_bq(chunk_path):
        gcp_credentials_block = GcpCredentials.load("prefect-bq")
        df = pd.read_parquet(chunk_path)
        df.to_gbq(
            destination_table="test_bq.yellow_trips",
            credentials = gcp_credentials_block.get_credentials_from_service_account(),
            project_id = "dezoomcamp-376313",
            chunksize = 50000,
            if_exists="append"
        )

    @flow()
    def child_el_1(color, url, gcs_path, folder_name_file):
        #get file from url, create csv path and write it to local
        if os.path.exists(f"data/{color}/temp"):
            pass
        else:
            os.makedirs(f"data/{color}/temp")


        file_path = get_url_write_local(url, color)

        #read csv file by chunk
        with pd.read_csv(file_path, chunksize=1e6) as reader:
            i =1
            for chunk in reader:
                #create path for chunk in local temp
                if os.path.exists(f"data/{color}/temp/{folder_name_file}"):
                    pass
                else:
                    os.mkdir(f"data/{color}/temp/{folder_name_file}") 

                chunk_path = Path(f"data/{color}/temp/{folder_name_file}/part_{i}.parquet")
                
                #write chunks to local
                if chunk_path.is_file():
                    print(f"Your chunk path is exists!")
                    pass
                else:
                    chunk.to_parquet(chunk_path, compression="gzip")
                
                #write chunks to gcs 
                gcs_file_path = Path(f"{gcs_path}/part_{i}.parquet")
                write_gcs(chunk_path, gcs_file_path)

                #write chunks to bq
                write_to_bq(chunk_path)

                #delete chunk file in local temp
                os.remove(chunk_path)

                #incremental for chunk 
                i+=1


    @flow()
    def parent_el(color,year, months):

        for month in months: 
            folder_name_file=f"{color}_tripdata_{year}-{month:02}"
            url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{folder_name_file}.csv.gz"
            gcs_path = f"data/{color}/{folder_name_file}"
            child_el_1(color, url,gcs_path, folder_name_file)

    if __name__ == "__main__":
        color = "yellow"
        year = "2019"
        months = [2,3]
        parent_el(color, year, months)
    ```
- Prefcect Deployment
    - Build: 
    <p align="center">
    <img src="3_Homework/images/6.png" >
    </p>
    <br>

    - `parent_el-deployment.yaml` with additional parameter

    ```yaml
    ###
    ### A complete description of a Prefect Deployment for flow 'parent-el'
    ###
    name: Extract Load
    description: null
    version: 5fd1a9f2adefb7385c8ea9d276d2baaa
    # The work queue that will handle this deployment's runs
    work_queue_name: default
    tags: []
    parameters: {"color":"yellow", "months":[2,3], "year":2019}
    schedule: null
    infra_overrides: {}
    infrastructure:
    type: process
    env: {}
    labels: {}
    name: null
    command: null
    stream_output: true
    working_dir: null
    block_type_slug: process
    _block_type_slug: process

    ###
    ### DO NOT EDIT BELOW THIS LINE
    ###
    flow_name: parent-el
    manifest_path: null
    storage: null
    path: /home/thisiswildanw/project/de_zoomcamp/Week_2_Workflow_Orchestration/3_Homework/Question_3
    entrypoint: el.py:parent_el
    parameter_openapi_schema:
    title: Parameters
    type: object
    properties:
        color:
        title: color
        position: 0
        year:
        title: year
        position: 1
        months:
        title: months
        position: 2
    required:
    - color
    - year
    - months
    definitions: null

    ```
    
    - Run `parent_el-deployment.yaml`
    <p align="center">
    <img src="3_Homework/images/7.png" >
    </p>
    <br>


    - Execute flow runs from this deployment: 
    <p align="center">
    <img src="3_Homework/images/8.png" >
    </p>
    <br>


- GCP File
    <p align="center">
    <img src="3_Homework/images/3.png" >
    </p>
    <br>

    <p align="center">
    <img src="3_Homework/images/4.png" >
    </p>
    <br>

- Big Query
    <p align="center">
    <img src="3_Homework/images/5.png" >
    </p>
    <br>


#### Question 4. Github Storage Block

Using the web_to_gcs script from the videos as a guide, you want to store your flow code in a GitHub repository for collaboration with your team. Prefect can look in the GitHub repo to find your flow code and read it. Create a GitHub storage block from the UI or in Python code and use that in your Deployment instead of storing your flow code locally or baking your flow code into a Docker image.

Note that you will have to push your code to GitHub, Prefect will not push it for you.

Run your deployment in a local subprocess (the default if you don’t specify an infrastructure). Use the Green taxi data for the month of November 2020.

How many rows were processed by the script?

#### Answer : 88,605 (C)

- Push `etl_web_to_gcs_q4.py` to GitHub.
- Create GitHub block via Prefect UI\
    <p align="center">
    <img src="3_Homework/images/10.png" >
    </p>
    <br>
- Create and Run deployment
    <p align="center">
    <img src="3_Homework/images/11.png" >
    </p>
    <br>
- Result : 88605

    <p align="center">
    <img src="3_Homework/images/12.png" >
    </p>
    <br>



#### Question 5. Email or Slack notifications
Q5. It’s often helpful to be notified when something with your dataflow doesn’t work as planned. Choose one of the options below for creating email or slack notifications.

The hosted Prefect Cloud lets you avoid running your own server and has Automations that allow you to get notifications when certain events occur or don’t occur.

Create a free forever Prefect Cloud account at app.prefect.cloud and connect your workspace to it following the steps in the UI when you sign up.

Set up an Automation that will send yourself an email when a flow run completes. Run the deployment used in Q4 for the Green taxi data for April 2019. Check your email to see the notification.

Alternatively, use a Prefect Cloud Automation or a self-hosted Orion server Notification to get notifications in a Slack workspace via an incoming webhook.

Join my temporary Slack workspace with this [link](https://join.slack.com/t/temp-notify/shared_invite/zt-1odklt4wh-hH~b89HN8MjMrPGEaOlxIw). 400 people can use this link and it expires in 90 days.

In the Prefect Cloud UI create an [Automation](https://docs.prefect.io/ui/automations) or in the Prefect Orion UI create a [Notification](https://docs.prefect.io/ui/notifications/) to send a Slack message when a flow run enters a Completed state. Here is the Webhook URL to use: https://hooks.slack.com/services/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

Test the functionality.

Alternatively, you can grab the webhook URL from your own Slack workspace and Slack App that you create.

How many rows were processed by the script?

#### Answer : 514,392
- Create prefect cloud account and workspace [here](https://app.prefect.cloud/)
- Go to `Profile` > `settings` > `API Keys`, Select `add new api keys`.
    <p align="center">
    <img src="3_Homework/images/13.png" >
    </p>
    <br>

- Setting up prefect cloud on CLI: 
    - `prefect cloud login <API KEY>`
    - `prefect config set PREFECT_API_URL="https://api.prefect.cloud/api/accounts/[ACCOUNT-ID]/workspaces/[WORKSPACE-ID]"`
    - `prefect config set PREFECT_API_KEY=<API KEY>`
- Go to `Navigation Menu` on Prefect Cloud UI > `Automation`. Select `Add Automation`

- On `Trigger Menu` we select `Failed` and `Compeleted` Trigger for `etl-web-to-gcs` flow. Click `Next`

- On `Action Menu` we select `Send a Notification` to email block. 

- Create a `Automation Name` for `Details Menu`.

- Run `etl_web_to_gcs_q5.py`.

    <p align="center">
    <img src="3_Homework/images/14.png" >
    </p>
    <br>

-Row Size = 154,392
    <p align="center">
    <img src="3_Homework/images/15.png" >
    </p>
    <br>


### Question 6. Secrets
Prefect Secret blocks provide secure, encrypted storage in the database and obfuscation in the UI. Create a secret block in the UI that stores a fake 10-digit password to connect to a third-party service. Once you’ve created your block in the UI, how many characters are shown as asterisks (*) on the next page of the UI?

#### Answer : 8
    <p align="center">
    <img src="3_Homework/images/16.png" >
    </p>
    <br>




