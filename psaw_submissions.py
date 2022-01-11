import requests
import datetime as dt
import json
import time
from datetime import timedelta
from datetime import datetime
import pandas as pd
import numpy as np


url_submission = "https://api.pushshift.io/reddit/search/submission"

subreddit_to_pull_submissions = ["HeartDisease"] #["skiing","progresspics","backpacking","loseit","EatCheapAndHealthy"]


def crawl_page(subreddit: str, last_page = None):
  """Crawl a page of results from a given subreddit.

  :param subreddit: The subreddit to crawl.
  :param last_page: The last downloaded page.

  :return: A page or results.
  """
  params_submission = {"subreddit": subreddit, "size": 10000, "sort": "desc", "sort_type": "created_utc", "before":"104d","after":"865d","filter":['url','author', 'title', 'created_utc','id','num_comments','permalink','score','subreddit','subreddit_id','selftext']}
  if last_page is not None:
    if len(last_page) > 0:
      # resume from where we left at the last page
      params_submission["before"] = last_page[-1]["created_utc"]
    else:
      # the last page was empty, we are past the last page
      return []
  results_submission = requests.get(url_submission, params_submission)
  if not results_submission.ok:
    # something wrong happened
    raise Exception("Server returned status code {}".format(results_submission.status_code))
  return results_submission.json()["data"]


def crawl_subreddit(subreddit, max_submissions = 500000): #1000000
  """
  Crawl submissions from a subreddit.

  :param subreddit: The subreddit to crawl.
  :param max_submissions: The maximum number of submissions to download.

  :return: A list of submissions.
  """
  submissions = []
  last_page = None
  while last_page != [] and len(submissions) < max_submissions:
    a = crawl_page(subreddit, last_page)
    last_page = a
    submissions += last_page
    time.sleep(3)
  return submissions[:max_submissions]
  

def crawl_comment(sub,link_id):
  """
  Crawl comments from specific subreddit posts.

  :param sub: The subreddit to crawl.
  :param link_id: The post id you need the comments made on.

  :return: A list of comments for that post.
  """
  params_comments = {"limit":1000, "filter":['author','body','created_utc','id','link_id','parent_id','permalink','score','subreddit','subreddit_id']}
  latest_comments = []
  for i in link_id:
    req = 'https://api.pushshift.io/reddit/comment/search/?subreddit='+sub+'&'+'link_id=t3_'+i
    try:
      js = requests.get(req,params_comments).json()
      if len(js['data'])!=0:
        for j in js['data']:
          latest_comments.append(j)
    except:
      # print(f'Response for {i} link id is not in JSON format.')
      pass
  return latest_comments

### Loop over multiple subs and formulate a table from jsons pulled from the API. Submissions and comment tables are then merged on link_id###
for sub in subreddit_to_pull_submissions:
    try:
        start = time.time()
        lastest_submissions = crawl_subreddit(sub)
        df_submission = pd.json_normalize(lastest_submissions)
        link_id = df_submission['id'].drop_duplicates().values

        df_comment = pd.json_normalize(crawl_comment(sub,link_id))
        df_comment['link_id'] = df_comment['link_id'].str.split('_').str[1]
        df_comment.to_csv(sub+'_comments.csv')
        df_comment_2 = df_comment.groupby('link_id').agg({'body': '************'.join})

        df = df_submission.merge(df_comment_2, how='left', left_on = 'id', right_on='link_id')
        try:
            df = df.drop(['body_x'], axis=1)
            df = df.rename(columns={'body_y': 'body'})
        except:
            pass
        df=df[df.columns.drop(list(df.filter(regex='Unnamed')))]
        df = df.loc[:,~df.columns.duplicated()]
        df['created_utc_local'] = df['created_utc'].map(lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x)))
        df.to_csv(sub+'.csv')
        end = time.time()
        elapsed = str(timedelta(seconds=(np.ceil(end - start))))
        print(f'{sub} completed and download time was {elapsed}')
    except:
        print(f'Problem with {sub} at server')
        pass