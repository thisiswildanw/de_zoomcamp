Week 1 Basic Docker-Postgres and GCP-Terraform
======================

> Next Week: (Comming Soon)

> [Back to Start Page](https://github.com/thisiswildanw/de_zoomcamp)

Table of Contents: 
=================
- [Introduction to Data Engineering](#introduction-to-data-engineering)
- [Docker and Postgres](#docker-and-postgres)
    - [Introduction to Docker](#introduction-to-docker)
    - [Creating a Simple Data Pipeline using Python](#creating-a-simple-data-pipeline-in-docker)
    - [Ingesting NYC Taxi Data to Postgres with Python](#ingesting-nyc-taxi-data-to-postgres-with-python) 
    - [Connecting pgAdmin and Postgres with Docker](#connecting-pgadmin-and-postgres-with-docker)
    - [Putting Ingestion Script with Docker](#putting-ingestion-script-with-docker)
    - Running Postgres and pgAdmin with Docker-Compose
    - SQL refresher
- GCP and Terraform
    - GCP initial setup
    - GCP setup for access
    - Terraform basics
    - Creating GCP infrastructure with Terraform
- Homework


Introduction to Data Engineering
================================
[**Data Engineering**](hhttps://www.coursera.org/articles/what-does-a-data-engineer-do-and-how-do-i-become-one)is the practice of designing and building systems for collecting, storing, and analyzing data at scale. 


Docker and Postgres
===================

### Introduction to Docker

**Docker** is a software platform to create, deploy and manage virtualized application containers on server or cloud. In our case, we use docker to isolate our data pipelines. 

Why data engineers should we care about Docker: 
- Local experiments
- Integration test (CI/CD)
- Reproducibility
- Cloud deployment (GCP, AWS od Azure)
- Compatible with Spark and serverless application (AWS Lambda, Google Fuction)

>Note : Docker containers are ***stateless***: any changes done inside a container will **NOT** be saved when the container is killed and started again. This is an advantage because it allows us to restore any container to its initial state in a reproducible manner, but you will have to store data elsewhere if you need to do so; a common way to do so is with _volumes_.

### Creating a Simple Data Pipeline in Docker

**Data pipeline** is a fancy name of process service that gets in data and produces more data. 

Let's create an example pipeline. We will create a dummy `pipeline.py`. A python script that receives an input argument and prints it.

```python

#import library that we need 
import sys
import pandas as pd

#print arguments
print(sys.argv)

#argument 1 contain the actual first argument that we input/write
day = sys.argv[1]

#print sentence with the argument and print pandas version
print(f'job finished successfully for day = {day}')
print('pandas version = ', pd.__version__)

```

We can try running this script with `python pipeline.py <input_argument>`, and it print 3 lines as expected :
- `[pipeline.py, '<input_argument>`
- `job finished successfully for day = <input_argument>`
- `pandas version = '<pandas version on this local env>'`

The result : 

<p align="center">
  <img src="2_Images/1_Introduction_to_Docker/0_python_run.png" alt="Pipeline.py_running on python" >
  <p align="center"> Pipeline.py is Running Via Python3</p>
</p>


OK, let's try to containerize `Pipeline.py` via Docker image (`dockerfile`).

```docker
#Docker image that we will build
FROM python:3.9

#Set up our image by installing pandas (in this case)
RUN pip install pandas

#Copy the script to the conainer ("source file" "destination")
COPY pipeline.py pipeline.py

#Define what to do when the container runs
ENTRYPOINT ["python", "pipeline.py"]
```


Let's build the image by following this command:

```docker
docker build -t test:pandas .
```

<blockquote>
Note: 

- 'test' is the image name and 'pandas' its tag. 
- `pipeline.py` and `dockerfile` should in the same directory.
- The Docker commands should also be run from the same directory as these files.
</blockquote>

The Result:

<p align="center">
  <img src="2_Images/1_Introduction_to_Docker/1_docker_build.png" alt="Pipeline.py_running on python" >
  <p align="center"> Test:Pandas Image was Builded Using Docker </p>
</p>

We can run the container and pass an argument to it with this command: 

```docker
docker run -it test:pandas <input argument>
```

The result:
<p align="center">
  <img src="2_Images/1_Introduction_to_Docker/2_docker_run.png" alt="Pipeline.py_running on Docker" >
  <p align="center"> Pipeline.py is Running Via Docker Container</p>
</p>

_[back to the top](#table-of-contents)_

<br></br>

### Ingesting NYC Taxi Data to Postgres with Python

Before ingesting NYC Taxi Data, we need to know how to running Postgres in a container by following this command: 

```
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:13
```
> Note : Containerized version of postgres doesn't require any building or installation steps. We only need provide few environtment variable, volume for storing data and port mapping. 

- There are 3 needed enviroment variables (`-e`): 
  - `POSTGRES_USER` : the username for logging into database.
  - `POSTGRES_PASSWORD` : the password for the database. 
  - `POSTGRES_DB` : the name that we will give to the database.
  >Note : Username and Password in this project are meant for testing. Please give more appropriate Username and Password for daily production. 

- `-v` points to the volume directory. The colon `:` separates the first part (path to the folder in the host computer) from the second part (path to the folder inside the container). Path names must be absolute. If you're in a UNIX-like system, you can use `($pwd)` to print local folder as a shortcut.
  >Note: This command will only work if you run it from a directory which contains the ny_taxi_postgres_data subdirectory we created above.

- `p` is for port mapping. We choice `5432` as default Postgres port and host for this project. 
- The last argument is the image name and tag. We run `postgres` image on its version `13`.  


<p align="center">
  <img src="2_Images/2_Ingesting_NYC_Data_to_Postgres/1_postgre_is_running.png" alt="Postgre is runnning" >
  <p align="center">Postgre is Running Via Docker Container</p>
</p>


Once container is running, open new terminal and log into our database using [`pgcli`](https://www.pgcli.com/) by following this command :

```docker
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

- `-h` is the host. Since we runinng locally we can use localhost.
- `-p` is the port. We use `5432` as default postgres port for this project.
- `-u` is the username.
- `-d` is the database name.
>Note: Password is requested after running the command.


<p align="center">
  <img src="2_Images/2_Ingesting_NYC_Data_to_Postgres/2_using_pgcli_to_access_postgre_database.png" alt="Using pgcli" >
  <p align="center">Using pgcli to Access a Postgre Database (ny_taxi)</p>
</p>

<br></br>

We have learned how to run postgre in a docker container. Next, we will use data from [NYC TLC Trip Record Data website](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), specifically [Yellow Taxi Trip Record Parquet file for January 2021](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet) and ingest it to postgre database using Jupyter NoteBook.

<p align="center">
  <img src="2_Images/2_Ingesting_NYC_Data_to_Postgres/3_data_ingestion_architecture.png" alt="Using pgcli" >
  <p align="center">Ingestion Process</p>
</p>

Here, summary of NYC Data ingestion process via Jupyter Notebook in this project:
- Download parquet data using following command: 
  ```
  wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet
  ```
- Import python libraries that we needed (like Pandas & SQLAlchemy). 
- Create Schema for Yellow Taxi Trip database 
- Test NY_taxi Connection using SQLAlchemy
- Batch Ingestion from Yellow Taxi Trip Parquet Data to NY_Taxi Database 
- Create SQL Query to Access Postgre via Jupyter Notebook

>Note: Follow this Jupyter Notebook [*link*](1_Code/2_Ingesting_NYC_Data_to_Postgres/explore_ingest_data.ipynb) for detailed guide. 

_[back to the top](#table-of-contents)_

<br></br>

### Connecting pgAdmin and Postgres with Docker 

`pgAdmin` is a web-based tool to access and manage database. Its possible to run pgAdmin as container along with Postgre container, but both containers will have to be in the same *virtual network* so they can connect each other. 

First, create a virtual Docker network `pg-network`:
```
docker network create pg-network 
```

Use `docker network ls` to show existed network. 

<p align="center">
  <img src="2_Images/3_Connecting_pgAdmin_and_Postgre_with_Docker/0_existed_docker_net.png" >
  <p align="center">Existed Docker Network</p>
</p>

We will now re-run our Postgres container with the added network name and the container network name, so that the pgAdmin container can find it (we'll use `pg-database` for the container name):

```
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name pg-database \
    postgres:13

```

Then, run pgAdmin container on another terminal:

```
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    --network=pg-network \
    --name pgadmin \
    dpage/pgadmin4
```
- The container needs 2 environment variables: a login email and a password. We use `admin@admin.com` and root in this example.
>Note : Username and Password in this project are meant for testing. Please give more appropriate Username and Password for daily production. 
- `pgAdmin` is a web app and its default port is `80`; we map it to `8080` in our localhost to avoid any possible conflicts.
- Just like with the Postgres container, we specify a network and a name. However, the name in this example isn't really necessary because there won't be any containers trying to access this particular container.
- The actual image name is `dpage/pgadmin4`.

We now able to load pgAdmin on a web browser by browsing to `localhost:8080`. Use the same email and password you used for running the container to log in.

<p align="center">
  <img src="2_Images/3_Connecting_pgAdmin_and_Postgre_with_Docker/1_pgAdmin_login.png" >
  <p align="center">pgAdmin Login Page</p>
</p>

Right-click on Servers on the left sidebar and select Register > Server...

<p align="center">
  <img src="2_Images/3_Connecting_pgAdmin_and_Postgre_with_Docker/2_create_server.png" >
  <p align="center">Create Server</p>
</p>

Under *General* setting give the Server a name and under *Connection* add the same host name, user and password you used when running the container.

<p align="center">
  <img src="2_Images/3_Connecting_pgAdmin_and_Postgre_with_Docker/3_register_general.png" >
  <p align="center">General Setting</p>
</p>

<p align="center">
  <img src="2_Images/3_Connecting_pgAdmin_and_Postgre_with_Docker/4_register_connection.png" >
  <p align="center">Connection Setting</p>
</p>

Click on **Save**. Now, we should connected to the database.

We will explore using pgAdmin in next lessons.

_[back to the top](#table-of-contents)_

<br></br>


### Putting Ingestion Script with Docker

First, we need to export our existed Jupyter Notebook `explore_ingest_data.ipynb`(1_Code/4_Putting_Ingestion_Script_to_Docker/explore_ingest_data.ipynb) with this following command:

```
jupyter nbconvert --to=script explore_ingest_data.ipynb
```

Clean up the script by removing everything we don't need. We will also rename it to `ingest_data.py` and add a few modifications:

- Use argparse to handle the following command line arguments:
  - Username
  - Password
  - Host
  - Port
  - Database name
  - Table name
  - URL for the `parquet` file
- The engine we created for connecting to Postgres will be tweaked so that we pass the parameters and build the URL from them, like this: 
```
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
```
- We will also download `parquet` file using the provided URL argument.