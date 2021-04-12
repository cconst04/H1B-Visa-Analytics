#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
import pandas as pd_real
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from unidecode import unidecode


# In[2]:


def get_bounds(x):
    matches = re.findall("\d+",x)
    matches = list(map(float,matches))

    if len(matches)==0:
        matches = [float("-inf"),float("inf")]

    if len(matches)==1:
        matches = matches+[float("inf")]

    return matches

def normalize_str_cols(df,include_cols = None, exclude_cols = None, casing = "upper"):

    df_2 = df.copy()

    if include_cols:
        str_cols = include_cols
    else:
        str_cols = df_2.dtypes[df_2.dtypes == 'object'].index

        if exclude_cols:
            str_cols =[i for i in str_cols if i not in exclude_cols]


    for c in str_cols:

        non_na_mask = ~df[c].isna()

        #Remove accents
        df_2.loc[non_na_mask,c] = df_2.loc[non_na_mask,c].apply(unidecode)

        #Convert columns to selected casing
        df_2.loc[non_na_mask,c] = df_2.loc[non_na_mask,c].apply(lambda x: x.lower() if casing == "lower" else x.upper())

        #Trim trailing and leading spaces
        df_2.loc[non_na_mask,c] = df_2.loc[non_na_mask,c].apply(lambda x: x.strip())


        # remove leading and trailing punctuation
        df_2.loc[non_na_mask,c] = df_2.loc[non_na_mask,c]            .apply(lambda x: x.strip('., '))


        # remove alone , and .
        df_2.loc[non_na_mask,c] = df_2.loc[non_na_mask,c]            .apply(lambda x: re.sub("( , )|( . )",' ',x))
        #remove multiple consecutive white spaces
        df_2.loc[non_na_mask,c] = df_2.loc[non_na_mask,c]            .apply(lambda x: re.sub(" +",' ',x))

    return df_2



# In[3]:


#Get data
year = 2020
df = pd.read_csv(f'../data/clean/lca/{year}.csv')
states = pd.read_csv("../data/raw/states.csv")
person_income = pd.read_csv("../data/raw/personal_income.csv")
soc_codes = pd.read_excel("../data/raw/soc_structure_2018.xlsx")
naics_sectors = pd.read_excel("../data/raw/2017_NAICS_Descriptions.xlsx")


# In[4]:


#Clean person income
person_income['group'] = person_income['group'].str.replace(',','').str.replace('$','')
person_income['frequency'] = person_income['frequency'].str.replace(',','').str.replace('$','').astype(int)
person_income[["lower_bound",
               "upper_bound"]] = pd.DataFrame(person_income['group']\
                                                            .apply(get_bounds)\
                                                            .to_list())


# In[5]:


#Clean Soc Codes
soc_codes.rename(columns={"Unnamed: 4":"job_category","Major Group":"SOC_CODE"},inplace = True)
soc_codes.dropna(subset=["SOC_CODE"],inplace = True)
soc_codes = soc_codes[["SOC_CODE","job_category"]]
soc_codes["SOC_CODE"] = soc_codes["SOC_CODE"].apply(lambda x: x[0:2])


# In[6]:


#Clean NAICS codes

naics_sectors = naics_sectors[["Code","Title"]]
naics_sectors["Code"] = naics_sectors["Code"].astype(str)
mask = naics_sectors["Code"].str.len()==4
naics_sectors = naics_sectors[mask]
naics_sectors["Title"] = naics_sectors["Title"].str.strip(' T')
naics_sectors.rename(columns={"Code":"industry_group"},inplace = True)


# In[7]:


#Normalize employer name
df = normalize_str_cols(df,include_cols=["EMPLOYER_NAME"])


# Saving csv's

# In[8]:


person_income[1:].to_csv("../data/processed/personal_income.csv",index=False)  
soc_codes.to_csv("../data/processed/soc_codes.csv",index=False)
naics_sectors.to_csv("../data/processed/naics_sectors.csv",index=False)  
df.to_csv(f'../data/processed/processed_{year}.csv',index = False)
