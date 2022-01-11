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
from matplotlib.ticker import AutoLocator, AutoMinorLocator


def revise_weeks(df):
    """
    Scans the dataframe for week numbers in dec 2019 - jan 2020 and dec 2020 - jan 2021
    and adds 52 to the number of weeks succeeding 52
    """
    minn = df['week'][(df['month']==12) & (df['year']==2019)].min()
    if minn==1:
        first = df['date'][(df['month']==12) & (df['year']==2019) & (df['week']==minn)].values[0]
        month = 12
        year = 2019
    else:
        minn = df['week'][(df['month']==1) & (df['year']==2020)].min()
        first = df['date'][(df['month']==1) & (df['year']==2020) & (df['week']==minn)].values[0]
        month = 1
        year = 2020
        
    maxx = df['week'][(df['month']==12) & (df['year']==2020)].min()
    if maxx==1:
        last = df['date'][(df['month']==12) & (df['year']==2020) & (df['week']==maxx)].values[0]
    else:
        maxx = df['week'][(df['month']==1) & (df['year']==2021)].min()
        last = df['date'][(df['month']==1) & (df['year']==2021) & (df['week']==maxx)].values[0]

    df['week'][(df['date']>=first)&(df['date']<last)] += df['week'][(df['month']==month) & (df['year']==year)].max()

    minn = df['week'][(df['month']==1) & (df['year']==2021)].min()
    if minn==1:
        first = df['date'][(df['month']==1) & (df['year']==2021) & (df['week']==minn)].values[0]
        month = 1
        year = 2021
    else:
        minn = df['week'][(df['month']==2) & (df['year']==2021)].min()
        first = df['date'][(df['month']==2) & (df['year']==2021) & (df['week']==minn)].values[0]
        month = 2
        year = 2021

    df['week'][df['date']>=first] += df['week'][(df['month']==month) & (df['year']==year)].max()
    
    return df

def new_users(data):
    engagement_topics_week = {'Drugs':0,'Diet':0,'Physical_Activity':0,'Smoking':0}
    plt.figure(figsize=(15,5))
    for i in engagement_topics_week.keys():
        x = data[['author','date','week','month','year']][(data['broader_topic']==i) & (data['date']<pd.to_datetime('15-01-2021').date())]
        x = revise_weeks(x.copy())
        x = x[x['date']<pd.to_datetime('01-04-2021').date()]
        
        y = x[['date','week']]
        week_series = y['week'].values
        date_series = y[['date','week']][y['week'].astype(str).isin(week_series.astype(str))].groupby('week').first().reset_index(drop=False)
        date_series.rename(columns={'date':'Date'},inplace=True)
        
        x = x[['author','week']].drop_duplicates()
        x.reset_index(inplace=True)
        user_win = 2
         ### first three weeks by index
        df2 = pd.DataFrame()
        week = []
        new_user_count = []
        status = True
        while status:
            seen_user_win = np.sort(x['week'].unique())[user_win]
            seen_user = set(x['author'][x['week']<=seen_user_win])
            
            current_user_win = np.sort(x['week'].unique())[user_win+1]
            current_user = set(x['author'][x['week']==current_user_win])
            
            new_user = current_user.difference(seen_user)
            
            week.append(current_user_win)
            new_user_count.append(len(new_user))
            
            user_win += 1
           
            if current_user_win < np.sort(x['week'].unique())[-1]:
                status = True
            else:
                status = False
        df2['week'] = week
        df2['new_user_counts'] = new_user_count
        df2 = pd.merge(df2,date_series,how='left',left_on='week',right_on='week')

        
        engagement_topics_week[i] = df2
        date_peaks_x = [pd.to_datetime('01-06-2020').date(),pd.to_datetime('03-23-2020').date()]
        plt.axvline(x=date_peaks_x[0], color='black',linestyle="--")
        plt.axvline(x=date_peaks_x[1], color='grey',linestyle="--")
        
        if i=='Drugs':
            lab = 'Substance Use'
        elif i=='Physical_Activity':
            lab = 'Physical Activity'
        else:
            lab = i
            
        plt.plot(engagement_topics_week[i]['Date'][1:-1], engagement_topics_week[i]['new_user_counts'][1:-1], linestyle="-", label=lab)
    plt.title('Weekly new user counts for all broader groups ', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Count of new users', fontsize=12)
    plt.legend()

    plt.show()
    
def msg_analysis(data):
    messages_pre_dt = {'Drugs':0,'Diet':0,'Physical_Activity':0,'Smoking':0}
    messages_post_dt = {'Drugs':0,'Diet':0,'Physical_Activity':0,'Smoking':0}
    messages_pre_week = {'Drugs':0,'Diet':0,'Physical_Activity':0,'Smoking':0}
    messages_post_week = {'Drugs':0,'Diet':0,'Physical_Activity':0,'Smoking':0}
    
    plt.figure(figsize=(15,5))
    for i in messages_pre_dt.keys():
        
        x = data[['message','date']][(data['broader_topic']==i) & (data['date']<=pd.to_datetime('01-05-2020').date())].fillna(0)
        messages_pre_dt[i] = x.groupby(['date']).size().reset_index(name='counts')
        plt.plot(messages_pre_dt[i]['date'], messages_pre_dt[i]['counts'], linestyle="-", label=[i if i!= 'Physical_Activity' else 'Physical Activity'][0])
    plt.title('Daily message counts for broader topics pre covid', fontsize=12)
    plt.xlabel('Date',fontsize=12)
    plt.ylabel('Count of messages',fontsize=12)
    plt.legend(loc='upper right',bbox_to_anchor=(1.15, 1))
    plt.show()
    
    plt.figure(figsize=(15,5))
    for i in messages_pre_week.keys():
        df = data[['message','date','week','month','year']][(data['broader_topic']==i) & (data['date']<pd.to_datetime('15-01-2021').date())]
        x = revise_weeks(df.copy())
        x = x[x['date']<pd.to_datetime('01-04-2021').date()]
        y = x[['message','week']].fillna(0)
        k = x[['date','week']].drop_duplicates().sort_values(by=['date'])

        week_series = k['week'].values
        date_series = k[['date','week']][k['week'].astype(str).isin(week_series.astype(str))].groupby('week').first().reset_index(drop=False)
        date_series = date_series[date_series['week']<=54]
        date_series.rename(columns={'date':'Date'},inplace=True)

        z = y.groupby(['week']).size().reset_index(name='counts')
        z = z[z['week'] <= 54]
        z = pd.merge(z,date_series,how='left',left_on='week',right_on='week')
        messages_pre_week[i] = z

        plt.plot(messages_pre_week[i]['week'], messages_pre_week[i]['counts'], linestyle="-", label=[i if i!= 'Physical_Activity' else 'Physical Activity'][0])
    plt.title('Weekly message counts for broader topics pre covid',fontsize=12)
    plt.xlabel('Weeks',fontsize=12)
    plt.ylabel('Count of messages',fontsize=12)
    plt.legend(loc='upper right',bbox_to_anchor=(1.15, 1))
    plt.show()
    
    plt.figure(figsize=(15,5))
    for i in messages_post_dt.keys():
        
        x = data[['message','date']][(data['broader_topic']==i) & (data['date']<pd.to_datetime('15-01-2021').date()) & (data['date']>pd.to_datetime('01-04-2020').date())].fillna(0)
        messages_post_dt[i] = x.groupby(['date']).size().reset_index(name='counts')

        plt.plot(messages_post_dt[i]['date'], messages_post_dt[i]['counts'], linestyle="-", label=[i if i!= 'Physical_Activity' else 'Physical Activity'][0])
    plt.title('Daily message counts for broader topics during covid', fontsize=12)
    plt.xlabel('Date',fontsize=12)
    plt.ylabel('Count of messages',fontsize=12)
    plt.legend(loc='upper right',bbox_to_anchor=(1.15, 1))
    plt.show()
    
    plt.figure(figsize=(15,5))
    for i in messages_post_week.keys():
        df = data[['message','date','week','month','year']][(data['broader_topic']==i) & (data['date']<pd.to_datetime('15-01-2021').date())]
        x = revise_weeks(df.copy())
        x = x[x['date']<pd.to_datetime('01-04-2021').date()]

        y = x[['message','week']].fillna(0)
        k = x[['date','week']].drop_duplicates().sort_values(by=['date'])

        week_series = k['week'].values
        date_series = k[['date','week']][k['week'].astype(str).isin(week_series.astype(str))].groupby('week').first().reset_index(drop=False)
        date_series = date_series[date_series['week']>53]
        date_series.rename(columns={'date':'Date'},inplace=True)
        
        z = y.groupby(['week']).size().reset_index(name='counts')
        
        z = z[z['week'] > 53]
        z = pd.merge(z,date_series,how='left',left_on='week',right_on='week')
        messages_post_week[i] = z

        plt.plot(messages_post_week[i]['week'], messages_post_week[i]['counts'], linestyle="-", label=[i if i!= 'Physical_Activity' else 'Physical Activity'][0])
    plt.title('Weekly message counts for broader topics during covid', fontsize=12)
    plt.xlabel('Weeks', fontsize=12)
    plt.ylabel('Count of messages',fontsize=12)
    plt.legend(loc='upper right',bbox_to_anchor=(1.15, 1))
    plt.show()
    
    return messages_pre_dt, messages_post_dt, messages_pre_week, messages_post_week
    
def plot_msgs(messages_pre_week,messages_post_week):
    plt.figure(figsize=(15,5))
    for i in messages_pre_week.keys():
        x_list = np.append(messages_pre_week[i]['Date'][2:].values,messages_post_week[i]['Date'][:-1].values)
        y_list = np.append(messages_pre_week[i]['counts'][2:].values,messages_post_week[i]['counts'][:-1].values)
        
        if i=='Drugs':
            lab = 'Substance Use'
        elif i=='Physical_Activity':
            lab = 'Physical Activity'
        else:
            lab = i
            
        plt.plot(x_list, y_list,  linestyle="-", label=lab)
    plt.title('Weekly message counts for broader groups', fontsize=14)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Count of messages', fontsize=14)
    date_peaks_x = [pd.to_datetime('01-06-2020').date(),pd.to_datetime('03-23-2020').date()]

    plt.axvline(x=date_peaks_x[0], color='black',linestyle="--")
    plt.axvline(x=date_peaks_x[1], color='grey',linestyle="--")
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(loc='upper right',bbox_to_anchor=(1.15, 1))
    plt.show()

def main():
    
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
    
    ###Engagement Analysis###
    new_users(data) #New user count plots
    messages_pre, messages_post, messages_pre_week, messages_post_week = msg_analysis(data)
    plot_msgs(messages_pre_week,messages_post_week) #messages count plots
    

if __name__ == "__main__":
    main()