from pathlib import Path
import os
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
    df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
    df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
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
    color   = "green"
    year    = 2019
    month   = 4
    dataset_file=f"{color}_tripdata_{year}-{month:02}"
    dataset_url= f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = get_data(dataset_url)
    cleaned_df = clean(df)
    print(f"row_size={len(cleaned_df)}")
    path = write_local(cleaned_df, color, dataset_file)


if __name__ == "__main__":
    etl_web_to_gcs()