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

### 3. DLATK installation and requirements:
Please visit [DLATK](https://github.com/dlatk/dlatk) website for details.
```
cd ~/code/dlatk/
source activate dlatk
```

### 4. User engagement analysis on Reddit:
Run **engagement.py** for the generating new user count plots and message count plots over time across four broader groups.
```
python engagement.py
```

### 5. Language Feature Extraction using DLATK and MySQL:
* Generate standard unigram feature table on the complete master_sub table with message_id as the group id. The output is a 1to3gram feature table created in your home db
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id --add_ngrams -n 1 2 3 --combine_feat_tables 1to3gram
```

* Apply colocalization filter to the generated features. This yields *feat$colloc$master_sub$message_id$5en05* output table
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id -f 'feat$1to3gram$master_sub$message_id$16to16' --feat_occ_filter --feat_colloc_filter
```

* Add “id” column in MySQL on *feat$1to3gram$master_sub$message_id$16to16$0_0001*
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

* Run deleterows() procedure file to get rid of features containing above mentioned special characters
```
call deleterows();
```

* Create collocation scores for message_id
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id  --create_collocation_scores -f ‘feat$1to3gram$master_sub$message_id$16to16$0_0001’ --word_table ‘feat$1to3gram$master_sub$message_id$16to16$0_0001’
```

* Extract collocation feature table. You could change the --set_p_occ and --colloc_pmi_thresh thresholds as per your data. This generates *feat$colloc$master_sub$message_id$5en05* table as output.
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id --add_ngrams -n 1 2 3 --use_collocs --colloc_table covid_cv_reddit.ufeat\$master_sub_herc --lexicondb=covid_cv_reddit --colloc_pmi_thresh 6.0 --feat_occ_filter --set_p_occ 0.0001
```

### 6. Topic Modelling using DLATK and MySQL:
* Estimate LDA topics using Mallet from these 1to3grams. Specify the number of topics you want, lexicon name and path of folder and the 1to3gram table name
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id -f 'feat$colloc$master_sub$message_id$5en05' \
--estimate_lda_topics \
--lda_lexicon_name covid_cv_200 \
--mallet_path /home/sharath/mallet-2.0.8/bin/mallet \
--num_topics 200 \
--num_stopwords 100 \
--save_lda_files /sandata/kwanchoo/lda_200/
```

* Check the output tables *covid_cv_200_cp* and *covid_cv_200_freq_t50ll*

* Now create 1to3grams at *user_subreddit_pandemicflag* level (i.e Alex_Marijuana_pre or Alex_Marijuana_post implying the post was made by user Alex in Marijuana subreddit pre-pandemic or during pandemic. This column has been named as **user_sub** in the table **master_sub**
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c user_sub --add_ngrams -n 1 2 3 --combine_feat_tables 1to3gram --feat_occ_filter --feat_colloc_filter
```

* Now use the lexica created on the entire document list to extract topic norms at user_subreddit level
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c user_sub --add_lex_table -l covid_cv_200_cp --weighted_lexicon --lexicondb=covid_cv_reddit --word_table ‘feat$1to3gram$master_sub$user_sub$0_01’
```

* In MySQL create the outcome table **post_outcome** before running correlations between features and pandemic flag
```
CREATE INDEX user_sub ON master_sub(user_sub);
CREATE TABLE post_outcome SELECT DISTINCT broader_topic, user_sub, is_post FROM master_sub;
CREATE INDEX user_sub ON post_outcome(user_sub);
```

* In MySQL delete the features having covid related stopwords
```
create table covid_char (namee VARCHAR(20));
INSERT INTO covid_char(namee)
VALUES ('%covid%'),('%quarantine%'),('%lockdown%'),('%coronavirus%'),('%covid-19%'),('%pandemic%'),('%corona%'),('amp'),('%& amp%'),('amp ;'),('. for example'),('%covid%'),('%#x200%'),('; &'),(';'),(','),('.'),('. * *'),('. ] ('),('%https%'),('%[removed]%'),('nan'),('! nan'),(') nan'),('? nan');
```
* Run delete_covid_keys() procedure on *feat$1to3gram$master_sub$user_sub$0_01$pmi3_0* to get rid of features containing above mentioned covid related stopwords
```
call delete_covid_keys();
```

### 7. Change in Language Markers Pre- and During COVID-19 using DLATK and MySQL:
* Language correlations to highlight fluctuation pre vs post covid. Change the broader_topic name (Diet, Physical_Activity, Drugs, Smoking). Pandemic indicator flag in the **master_sub** dataset has the name **is_post** that indicates whether the post was made during pandemic (is_post = 1) or pre-pandemic (is_post=0)
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -g user_sub \
-f 'feat$1to3gram$master_sub$user_sub$0_01$pmi3_0' \
--outcome_table post_outcome  --group_freq_thresh 400 \
--outcomes is_post --output_name Drugs_ngram_new \
--tagcloud --make_wordclouds \
--tagcloud_colorscheme bluered \
--lexicondb=covid_cv_reddit \
--csv \
--where "broader_topic like '%Drugs%'"
```

* Create tag-clouds and get correlations that shall highlight topics for each subreddit undergone fluctuation pre vs post covid. Change the broader_topic name (Diet, Physical_Activity, Drugs, Smoking)
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -g user_sub \
-f ‘feat$cat_covid_cv_200_cp_w$master_sub$user_sub$1to3’ \
--outcome_table post_outcome  --group_freq_thresh 400 \
--outcomes is_post --output_name Smoking_200 \
--topic_tagcloud --make_topic_wordcloud --topic_lexicon covid_cv_200_freq_t50ll \
--tagcloud_colorscheme bluered \
--lexicondb=covid_cv_reddit \
--csv \
--where "broader_topic like '%Smoking%'"
```

* Get top messages for every topic
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -f 'feat$cat_covid_cv_200_cp_w$master_sub$message_id$coll' --output top_msgs_master_sub --whitelist --top_messages 20 --group_freq_thresh 4 --topic_lexicon covid_cv_200_freq_t50ll
```

### 8. Identify significantly positively correlated topics associated with the four broader groups:
* **user_s** in the column name in **master_sub** that has been created by concatenating user and subreddit values. Posts are aggregated at user_subreddit levels and correlations are found with broader group indicator flags such as **is_drugs**, **is_smoking**, etc similar to **is_post**.
```
CREATE TABLE post_outcome_2 SELECT DISTINCT broader_topic, user_s, is_drugs, is_pa, is_diet, is_smoking from master_sub;
CREATE INDEX user_s ON post_outcome_2(user_s);
```
* Broader group correlations. This gives a list of topics with their correlations with four broader groups. We then use the positively and significantly correlated topics to perform Prevalent Topic Analysis
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -g user_s \
-f ‘feat$cat_covid_200_cp_w$master_sub$user_s$1to3’ \
--outcome_table post_outcome_2  --group_freq_thresh 400 \
--outcomes is_drugs is_pa is_diet is_smoking --output_name Group_correlations \
--topic_tagcloud --make_topic_wordcloud --topic_lexicon covid_cv_200_freq_t50ll \
--tagcloud_colorscheme bluered \
--lexicondb=covid_cv_reddit \
--csv \
```
### 9. Prevalent Topic Analysis:

* Get the probability distribution (group_norm distribution) for each message across all (200) topics such that we get a 200 dimensional vector across all messages. The output table is *cat_covid_cv_post_200_cp_w$master_sub$message_id$1to3*
```
python dlatkInterface.py -d covid_cv_reddit -t master_sub -c message_id --add_lex_table -l covid_cv_200_cp --weighted_lexicon --lexicondb=covid_cv_reddit --word_table ‘feat$colloc$master_sub$message_id$5en05’
```

* Run **prevalent_topics.py** for the generating new user count plots and message count plots over time across four broader groups.
```
python prevalent_topics.py
```
