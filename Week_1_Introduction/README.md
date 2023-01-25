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
    - Connecting pgAdmin and Postgres
    - Putting the ingestion script to Docker
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
[**Data Engineering**]is the practice of designing and building systems for collecting, storing, and analyzing data at scale. 


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







