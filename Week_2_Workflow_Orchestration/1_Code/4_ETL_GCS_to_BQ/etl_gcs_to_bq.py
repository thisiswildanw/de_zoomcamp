import os,errno
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


@task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_from_gcs(color, year, month ):
    gcs_path=f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block= GcsBucket.load("prefect-gcs")
    gcs_block.get_directory(from_path=f"{gcs_path}", local_path=f"../data/")
    return Path(f"../data/{gcs_path}")

@task(log_prints=True, retries=3)
def transform(path):
    df = pd.read_parquet(path)
    print (f"pre: missing passenger count : {df['passenger_count'].isna().sum()}")
    df['passenger_count'].fillna(0, inplace=True)
    print (f"post: missing passenger count : {df['passenger_count'].isna().sum()}")
    return df

@task(log_prints=True,retries=3)
def write_to_bq(df):
    gcp_credentials_block = GcpCredentials.load("prefect-bq")

    df.to_gbq(
        destination_table="test_bq.yellow_trips_21_01",
        credentials = gcp_credentials_block.get_credentials_from_service_account(),
        project_id = "dezoomcamp-376313",
        chunksize = 500000,
        if_exists="append"
    )


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