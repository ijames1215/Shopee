# -*- coding: UTF-8 -*-

####################################
#             package              #
####################################

import time
import re
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

####################################
#            read csv              #
####################################

df = pd.read_csv('train.csv', index_col=0)

####################################
#        POI street拆解             #
####################################

df2 = df['POI/street'].str.split(pat="/")


####################################
#              資料檢視             #
####################################

df[['POI','street']] = pd.DataFrame(df['POI/street'].str.split(pat="/").tolist(), index= df.index)
# print('POI,Street都有資料' + str(len(df[(df.POI != "") | (df.street != "")])))
# print('只有POI有資料' + str(len(df[(df.POI != "") ])))
# print('只有Street有資料' + str(len(df[(df.street != "")])))

####################################
#              資料檢視             #
####################################


df_POI = df[(df.POI != "")].reset_index()

df_list = []

for run in range(len(df_POI)):

    ####################################
    #   取得id  raw_address 和 POI      #
    ####################################

    str_id = str(df_POI['id'][run])
    str_raw_address = str(df_POI['raw_address'][run])

    str_POI = str(df_POI['POI'][run])


    try:
        ##############################################
        #   First Try raw_address 和 POI 的詞一樣     #
        ##############################################

        try:
            str_match = re.findall(fr'{str_POI}', str_raw_address)[0]

        ################################################################################
        #   Second Try raw_address 和 POI 的詞不一樣 : 抓POI的頭 和 POI尾後兩碼的string   #
        ###############################################################################

        except:
            str_match = re.findall(fr'{str_POI[:1]}.*{str_POI[-2:]}', str_raw_address)[0]

        #####################################################################################
        #   Third Try 有可能會抓到較長的string 所以在做一次 抓POI的頭兩碼 和 POI尾後兩碼的string  #
        #####################################################################################


        if len(str_match) > len(str_POI):
            for match in range(len(str_POI)):

                str_match = re.findall(fr'{str_POI[:(match + 2)]}.*{str_POI[-(match + 2):]}', str_raw_address)[0]
                print(fr'{str_POI[:(match + 2)]}.*{str_POI[-(match + 2):]}')
                try:
                    str_match = str_match.replace(",", "")
                except:
                    pass

                #####################################################################################
                #                        會遇到如id 40的情況 所以利用空格的數量來取得POI                #
                #####################################################################################

                if len(str_match) > len(str_POI):
                    str_match = re.findall(fr'{str_POI[:(match + 2)]}.*{str_POI[-(match + 2):]}', str_raw_address)[0]
                    tab_count = str_POI.count(' ')
                    list_match = str_match.split(' ')[0:tab_count+1]
                    str_match = ' '.join(list_match)
                    break
                else:
                    break
    except:
        pass

    ############################################
    #             有些String有逗號              #
    ############################################

    try:
        str_match = str_match.replace(",", "")
    except:
        pass

    ############################################
    #    POI 和 Match POI 開頭字母不一樣的情況    #
    ############################################

    try:
        if str_POI[0] != str_match[0]:
            try:
                str_match = re.findall(fr'{str_POI}.split(' ')[0]', str_raw_address)[0]
            except:
                for i in range(len(str_POI)):
                    try:
                        str_match = re.findall(fr'{str_POI[0:i]}.*{str_POI[-(i+1):(-i)]}', str_raw_address)[0]
                    except:
                        continue

        #####################################################################################
        #                        會遇到如id 40的情況 所以利用空格的數量來取得POI                #
        #####################################################################################

        if len(str_match) > len(str_POI):
            tab_count = str_POI.count(' ')
            list_match = str_match.split(' ')[0:tab_count + 1]
            str_match = ' '.join(list_match)

        ############################################
        #             有些String有逗號              #
        ############################################

        try:
            str_match = str_match.replace(",", "")
        except:
            pass
    except:
        pass

    #####################################################################################
    #                             將四個資訊整合起來 建立DataFrame                        #
    #####################################################################################


    df_list.append([str_id,str_raw_address,str_POI,str_match])

    print(str_id)
    print(str_raw_address)
    print(str_POI)
    print(str_match)

    print('\\'*10)

df = pd.DataFrame(df_list,columns=['id', 'Raw_address', 'POI','Match_POI'])
df.to_csv(r'POI_Match.csv',index= False,encoding = 'utf-8-sig')





