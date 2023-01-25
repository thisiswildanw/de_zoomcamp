#Docker image that we will build
FROM python:3.9

#Set up our image by installing pandas (in this case)
RUN pip install pandas

#Copy the script to the conainer ("source file" "destination")
COPY pipeline.py pipeline.py

#Define what to do when the container runs
ENTRYPOINT ["python", "pipeline.py"]