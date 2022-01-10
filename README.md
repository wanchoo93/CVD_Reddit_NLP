# CVD_Reddit_NLP

This repository contains code for the paper:

**REDDIT LANGUAGE INDICATES CHANGES IN CARDIOVASCULAR HEALTH BEHAVIORS AROUND DIET, PHYSICAL ACTIVITY, SUBSTANCE USE, AND SMOKING DURING COVID-19**.

## Steps for running the code for regeneration:

### 1. PRAW/PSAW script to scrape Reddit data:
In the **psaw_submissions.py** enter subreddit names you wish to scrape in Line #13 assigning to **subreddit_to_pull_submissions**. Run the **psaw_submissions.py** file in terminal.
*subreddit_comments.csv* and *subreddit.csv* files shall be created for every subreddit where *"subreddit"* implies the subreddit names you have provided as input.
You could change **params_submission** variable in Line #24 to alter the mentioned parameters. Visit [Pushshift Reddit API Documentation](https://github.com/pushshift/api) for more details.

### 2. Data preparation:
It is recommended to append all individual subreddit output files in a single master file separately for posts and comments and upload it to your respective databases. In this documentation I have used database name **covid_cv_reddit** and table name **master_sub** that contains all the posts from 22 subreddits. MySQL server was used for our project.
Run **MySQL_data_prep.sql**

### 2. DLATK installation and requirements:
Please visit [DLATK](https://github.com/dlatk/dlatk) website for details.
```
cd ~/code/dlatk/
source activate dlatk
```

### 3. Performing topic modelling step by step using DLATK and MySQL:
* Generate standard unigram feature table on the complete master_sub table with message_id as the group id. The output is a 1to3gram feature table created in your home db
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id --add_ngrams -n 1 2 3 --combine_feat_tables 1to3gram
```

* Apply colocalization filter to the generated features. This yields feat$colloc$master_sub$message_id$5en05 output table
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id -f 'feat$1to3gram$master_sub$message_id$16to16' --feat_occ_filter --feat_colloc_filter
```

* Add “id” column in MySQL and run deleterows() procedure on feat$colloc$master_sub$message_id$5en05 to get rid of special character features
```
ALTER TABLE covid_cv_reddit.feat$1to3gram$master_sub$message_id$16to16$0_0001 ADD COLUMN id BIGINT NOT NULL;
UPDATE covid_cv_reddit.feat$1to3gram$master_sub$message_id$16to16$0_0001 CROSS JOIN ( SELECT @myid := 0) AS parameter SET id = @myid := (@myid +1);
```

* Create a table to store special characters that will be removed from the feature table
```
create table splchar (namee VARCHAR(20));
INSERT INTO splchar(namee)
VALUES ('%*%'),('%.%'),('%)%'),('%(%'),('%-%'),('%/%'),('%[%'),('%]%'),('%:%'),('%;%'),
('%?%'),('%!%'),('%"%'),('%*%'),('%=%'),('%#x200%'),('amp'),('&');
```

* Run deleterows() procedure file
```
call deleterows();
```

* Create collocation scores for message_id
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id  --create_collocation_scores -f ‘feat$1to3gram$master_sub$message_id$16to16$0_0001’ --word_table ‘feat$1to3gram$master_sub$message_id$16to16$0_0001’
```

### 3. 
