import pandas as pd
df = pd.read_csv(r'test.csv')
df= df[['id','POI/street']]
df.to_csv(r'test.csv',index = False,encoding = 'utf-8-sig')