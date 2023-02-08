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