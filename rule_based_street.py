# -*- coding: UTF-8 -*-
import pandas as pd
from collections import Counter

# load trainning data
test = pd.read_csv("test.csv",low_memory=False)
print(test.columns)
# seperate POI/street
#train[["POI", "street"]] = train["POI/street"].str.split("/").tolist()

# build up corpus and frequecy of bigram
def bigram_counter(corpus):
    bigram_list = []
    for text in corpus:
        token = normalize_and_tokenize(text)
        bigram = [tuple([a, b]) for a, b in zip(token, token[1:])]
        bigram_list.append(bigram)
    bigram_list = [inner for outter in bigram_list for inner in outter]
    return Counter(bigram_list)

def normalize_and_tokenize(text):
    t = text.replace(",", "")
    token = t.split(" ")
    return token

GRAM_SIZE = 2
corpus = test.raw_address.tolist()
bigram = bigram_counter(corpus)
print(80*"=")
print("@ count of bigram:", len(bigram))
print(80*"=")
print("@ top 100 common bigram:\n", bigram.most_common(100))

# matching street by rules:
# noted --> jl. ... / jalan ... / jln ... / ... raya / ... gang / ... gg.
## senario 1: hit the rules and extract the neighbor word
BIGRAM_THRESHOLD = 10
keywords_for_street = {'jl.':1, 'jalan':1, 'jln':1, 'raya':-1, 'gg.':-1, 'gang':-1}

def merge_street_list(street_list):
    return "need to be merged"

def street_extract(address):
    token = normalize_and_tokenize(address)
    street_list = []
    for k in keywords_for_street.keys():
        if k in token:
            street_name_index = token.index(k) + keywords_for_street[k]
            if street_name_index >= 0:
                street_name = token[street_name_index]
                street = (k, street_name) if keywords_for_street[k] > 0 else (street_name, k)
                street_list.append(street)
            else:
                break
    if len(street_list) == 0:
        return ""
    elif len(street_list) == 1:
        return " ".join(street_list[0])
    else:
        return merge_street_list(street_list)

####################################
#            read csv              #
####################################

df = pd.read_csv('POI_Match.csv', low_memory = False)

####################################
#          list 轉成字典            #
####################################

#####  Hint : POI欄位是Train Data 裡的 POI     Match_POI欄位是擷取Raw Address可能的 POI資訊  #####
import re
POI_list = df['POI'].tolist()
Match_list = df['Match_POI'].tolist()
dict_Match = dict(zip(Match_list,POI_list))

test['POI\Street'] = r'\''
for match in range(len(test)):

    key = str(test['raw_address'][match])

    matching = [str(s) for s in Match_list if key in str(s)]

    print(match)
    print(matching)
    print(street_extract(corpus[match]))
    if matching == []:
        matching = [str(s) for s in Match_list if key in str(s)]

    if matching != [] and street_extract(corpus[match]) != '':
        test.loc[test.index == match,'POI\Street'] = fr'{matching[0]}\'{street_extract(corpus[match])}'

    elif matching == [] and street_extract(corpus[match]) != '':
        test.loc[test.index == match,'POI\Street'] = fr'\'{street_extract(corpus[match])}'

    elif matching != [] and street_extract(corpus[match]) == '':
        test.loc[test.index == match,'POI\Street'] = fr'{matching[0]}\''
    else:
        pass
test.to_csv("test_test.csv",index = False,encoding = 'utf-8-sig')



    # for x in dict_Match.values():
    #     try:
    #         str_match = re.findall(fr'{x}', key)[0]
    #         print(key)
    #         print(str_match)
    #     except:
    #         pass
        # if str(x) in key:
        #     print(key)
        #     print(dict_Match[x])
        #     print('//'*10)
# for i in range(100):
#     print(40*"=", i, 40*"=")
#     #print("real street:", train.street[i])
#     print("my street:", street_extract(corpus[i]))

# matching POI
