#Docker image that we will build
FROM python:3.9

#Set up our image by installing pandas (in this case)
RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2-binary pyArrow

#Copy the script to the conainer ("source file" "destination")
COPY ingest_data.py ingest_data.py

#Define what to do when the container runs
ENTRYPOINT ["python", "ingest_data.py"]