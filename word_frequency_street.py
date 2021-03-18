import pandas as pd

# (棄用)
# 抄來的 https://blog.csdn.net/buster2014/article/details/50939892
# def sortedDictValues3(adict):
#     keys = adict.keys()
#     keys.sort()
#     return map(adict.get, keys)
#
# 一行语句搞定：
# [(k, di[k]) for k in sorted (di.keys())]

df = pd.read_csv('train.csv', index_col=0)
df.head()

df2 = df['POI/street'].str.split(pat="/")

df[['POI', 'street']] = pd.DataFrame(df['POI/street'].str.split(pat="/").tolist(), index=df.index)

# print(len(df[(df.POI != "") | (df.street != "")]))
# print(len(df[(df.POI != "")]))
# print(len(df[(df.street != "")]))
# print(df.POI.nunique())
# print(df.street.nunique())

street_word_dict = {}

street_data = df['street'].tolist()

#把空格跟'.'拿掉
for street in street_data:
    temp = street.replace('.', ' ')
    temp = temp.split(' ')
    for word in temp:
        if len(word.strip()) > 0:
            if word not in street_word_dict:
                street_word_dict[word] = 1
            else:
                street_word_dict[word] += 1

# 刪除字頻率小於100
del_key = []
for word in street_word_dict:
    if street_word_dict[word] < 100:
        del_key.append(word)
        # print(word, ' : ', street_word_dict[word])

for word in del_key:
    del street_word_dict[word]

# sortedDictValues3(street_word_dict)
a = sorted(street_word_dict.items(), key=lambda x: x[1], reverse=True)

with open('street_word_frequency.csv', 'w') as f:
    for row in a:
        f.write(str(row[0]) + ' , ' + str(row[1]) + '\n')
