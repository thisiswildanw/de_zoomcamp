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