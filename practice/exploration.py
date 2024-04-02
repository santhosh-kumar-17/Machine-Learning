import pandas as pd
import numpy as np

df = pd.read_csv('MSFT.csv')
print(df.describe())

def findz_score(data):
    meanu=10
    sdd=12
    
    for i  in data['Close']:
        data['z_score']=i-meanu//sdd
    
    return data

badas=findz_score(df)
print(df)
print('gumtha')
print(badas)