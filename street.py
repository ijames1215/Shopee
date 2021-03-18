import pandas as pd


def address_filter(df, key, distance=2):
    '''

    :param df: pandas
    :param key: 搜尋關鍵字
    :param distance: 允許存在關鍵字前後的幾個字 每個字用一個空白區分
    :return: filter result pandas
    '''
    df = df.loc[df['street'] != '']
    df = df.loc[df['raw_address'].str.contains(key)]
    result_pd = pd.DataFrame()
    count = 0
    for index, row in df.iterrows():
        row = row.copy()
        if key in row['raw_address']:
            count += 1
            front = ''.join(row['raw_address'].split(key, 1)[0].strip().split(' ')[-distance:])
            back = ''.join(row['raw_address'].split(key, 1)[-1].strip().split(' ')[:distance])
            street = ''.join(row['street'].split(key)[-1]).strip()
            if street in front or street in back:
                result_pd = result_pd.append(row)
    return result_pd, count

df = pd.read_csv('train.csv', index_col=0)
df2 = df['POI/street'].str.split('/')

df[['POI','street']] = pd.DataFrame(df['POI/street'].str.split('/', 1).tolist(), index=df.index)
keys = ['jl.', 'jalan', 'jln', 'gg.', 'gang']

for key in keys:
    result, count = address_filter(df.copy(), key)
    print(len(result))
    print(key)
    print(count)

