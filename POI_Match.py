# -*- coding: UTF-8 -*-

####################################
#             package              #
####################################

import pandas as pd

####################################
#            read csv              #
####################################

df = pd.read_csv('POI_Match.csv', low_memory = False)

####################################
#          list 轉成字典            #
####################################

#####  Hint : POI欄位是Train Data 裡的 POI     Match_POI欄位是擷取Raw Address可能的 POI資訊  #####

POI_list = df['POI'].tolist()
Match_list = df['Match_POI'].tolist()
dict_Match = dict(zip(Match_list,POI_list))
