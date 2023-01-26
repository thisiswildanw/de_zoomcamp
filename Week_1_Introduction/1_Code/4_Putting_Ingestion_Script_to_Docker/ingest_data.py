
import os
import argparse
import pandas as pd
import numpy as np


from sqlalchemy import create_engine
from time import time

def main(params):
    


engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')


#create batch ingestion function with dataframe input, chunksize or batch and engine name
def batch_ingest(data, chunksize, engine):
    list_df = np.array_split(data, chunksize)
    for i in range (chunksize):
        try:
            t_start = time()
            list_df[i].to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
            t_end = time()
            j =i+1
            print('Inserted chunk no-' + str(j) +' took %.3f second' % (t_end - t_start) + ', it has '+ str(len(list_df[i])) + ' rows')
        except StopIteration:
            print('Failed!')
            break

