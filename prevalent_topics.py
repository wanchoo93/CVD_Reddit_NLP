"""
Author: Karan Wanchoo
Project: CVD_Reddit_NLP
Date: January 10, 2022
Affiliation: World Well-Being Project
"""
import pandas as pd
import numpy as np
import sqlalchemy
from pandas.io import sql
import matplotlib.pyplot as plt
import datetime
import nltk
from nltk.corpus import stopwords
import time
from datetime import timedelta
from datetime import datetime, date
import seaborn as sns
import statsmodels.formula.api as smf
import os
import sys
import scipy
from scipy import signal
import matplotlib.dates as mdates
from matplotlib.transforms import Transform
from matplotlib.ticker import (
    AutoLocator, AutoMinorLocator)


def get_data():

    ###Specify your db and engine###
    conn = sqlalchemy.create_engine('mysql://127.0.0.1/covid_cv_reddit?read_default_file=~/.my.cnf')
    
    query0 = """Select * from master_sub"""
    start = time.time()
    data = pd.read_sql(query0,conn)
    end = time.time()
    elapsed = str(timedelta(seconds=(np.ceil(end - start))))
    print(f'master_sub data read in {elapsed} seconds')
    data['date'] = data['created_utc_local'].dt.date
    data['week'] = data['created_utc_local'].dt.week
    data['month'] = data['created_utc_local'].dt.month
    data['year'] = data['created_utc_local'].dt.year
    
    query1 = """ SELECT * FROM covid_cv_reddit.feat$cat_covid_cv_200_cp_w$master_sub$message_id$coll"""
    start = time.time()
    lda_table = pd.read_sql(query1,conn)
    end = time.time()
    elapsed = str(timedelta(seconds=(np.ceil(end - start))))
    print(f'group norm data read in {elapsed} seconds')
    lda_table_transposed = pd.pivot_table(lda_table, values='group_norm', index=['group_id'],columns=['feat'], aggfunc=np.sum).drop('_intercept',axis=1)
    lda_table_transposed.sort_index(axis=1)
    lda_table_transposed.reset_index(drop=False, inplace=True)
    lda_table_transposed_2 = pd.merge(lda_table_transposed,data[['message_id','created_utc_local','broader_topic','subreddit']], how='left',left_on='group_id',right_on='message_id').drop(['message_id'],axis=1).sort_values('created_utc_local')
    lda_table_transposed_2['date'] = lda_table_transposed_2['created_utc_local'].dt.date
    lda_table_transposed_2['week'] = lda_table_transposed_2['created_utc_local'].dt.week
    lda_table_transposed_2['month'] = lda_table_transposed_2['created_utc_local'].dt.month
    lda_table_transposed_2['year'] = lda_table_transposed_2['created_utc_local'].dt.year
    
    return lda_table_transposed_2

def get_correlations():
    ### for 1 file with all topics ###
    prefix = 'Phase2_200_reattempt'
    sub = ['is_diet','is_drugs','is_pa','is_smoking']
    main_data = pd.read_csv('/home/kwanchoo/code/dlatk/'+prefix+'_topic_tagcloud_wordclouds/'+prefix+'.csv',skiprows=3)

    col_indices = [i for i in range(len(main_data.columns)) if main_data.columns[i] in sub]
    col_indices = [0] + col_indices + [i+1 for i in col_indices]
    col_indices.sort()
    main_data_2 = main_data.iloc[:,col_indices]

    ###Average across selective topics###

    rda_overall_topics = {'Drugs':0,'Diet':0,'Physical_Activity':0,'Smoking':0}
    cols = {'Diet':[str(i) for i in main_data_2['feature'][(main_data_2['is_diet']>0)&(main_data_2['p']<0.01)&(main_data_2['feature']!='_intercept')]],'Drugs':[str(i) for i in main_data_2['feature'][(main_data_2['is_drugs']>0)&(main_data_2['p.1']<0.01)&(main_data_2['feature']!='_intercept')]],'Physical_Activity':[str(i) for i in main_data_2['feature'][(main_data_2['is_pa']>0)&(main_data_2['p.2']<0.01)&(main_data_2['feature']!='_intercept')]],'Smoking':[str(i) for i in main_data_2['feature'][(main_data_2['is_smoking']>0)&(main_data_2['p.3']<0.01)&(main_data_2['feature']!='_intercept')]]}
    for i in cols:
        print('Positively Corr and Sig topics for '+i,': ',len(cols[i]))
    return cols

def get_plots(cols,lda_table_transposed_2):
    for broader_topic in cols.keys():
        print(broader_topic)
        topic_list = cols[broader_topic]
        for topic in topic_list:
            print(topic)
            boo_1 = lda_table_transposed_2[[topic,'date','week','month','year']][(lda_table_transposed_2['broader_topic']==broader_topic) & (lda_table_transposed_2['date']<pd.to_datetime('15-01-2021').date())].fillna(0)

            boo_2 = revise_weeks(boo_1.copy())
            week_series = boo_2['week'].values
            date_series = boo_2[['date','week']][boo_2['week'].astype(str).isin(week_series.astype(str))].groupby('week').first().reset_index(drop=False)
            date_series.rename(columns={'date':'Date'},inplace=True)
            boo_2 = pd.merge(boo_2,date_series,how='left',left_on='week',right_on='week')
            boo_3 = boo_1[[topic,'date']]

            path = make_dir(os.getcwd(),broader_topic+'_corr_topics')

            plt.figure(figsize=(15,5))
            sns.lineplot(data=boo_2, x="Date", y=topic)
 
            date_peaks_x = [pd.to_datetime('01-06-2020').date(),pd.to_datetime('03-23-2020').date()]
    
            plt.axvline(x=date_peaks_x[0], color='black',linestyle="--")
            plt.axvline(x=date_peaks_x[1], color='grey',linestyle="--")
            plt.xlabel('Date', fontsize=17)
            plt.ylabel('Topic distribution', fontsize=17)
            plt.xticks(fontsize=15)
            plt.yticks(fontsize=15)
            plt.title('7 day rolling average for Topic '+topic, fontsize=17)
            plt.savefig(path+'/topic_'+topic+'.png')
            plt.show()
            
def main():
	lda_table_transposed_2 = get_data()
	cols = get_correlations()
	get_plots(cols,lda_table_transposed_2)
    
    
if __name__ == "__main__":
	main()
