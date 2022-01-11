"""
Author: Karan Wanchoo
Project: CVD_Reddit_NLP
Date: January 10, 2022
Affiliation: World Well-Being Project
"""

use covid_cv_reddit;

ALTER TABLE master_sub ADD COLUMN message_id BIGINT NOT NULL;
UPDATE master_sub SET message_id = unique_key;

ALTER TABLE master_sub ADD COLUMN broader_topic VARCHAR(250) NOT NULL;

UPDATE master_sub SET broader_topic = "Drugs" where subreddit = "Drugs";
UPDATE master_sub SET broader_topic = "Drugs" where subreddit = "Marijuana";
UPDATE master_sub SET broader_topic = "Drugs" where subreddit = "addiction";
UPDATE master_sub SET broader_topic = "Drugs" where subreddit = "DrugCombos";
UPDATE master_sub SET broader_topic = "Drugs" where subreddit = "1P_LSD";
UPDATE master_sub SET broader_topic = "Drugs" where subreddit = "stopdrinking";
UPDATE master_sub SET broader_topic = "Drugs" where subreddit = "alcoholism";
UPDATE master_sub SET broader_topic = "Physical_Activity" where subreddit = "trailrunning";
UPDATE master_sub SET broader_topic = "Physical_Activity" where subreddit = "gravelcycling";
UPDATE master_sub SET broader_topic = "Physical_Activity" where subreddit = "bicycling";
UPDATE master_sub SET broader_topic = "Physical_Activity" where subreddit = "skiing";
UPDATE master_sub SET broader_topic = "Physical_Activity" where subreddit = "backpacking";
UPDATE master_sub SET broader_topic = "Diet" where subreddit = "diet";
UPDATE master_sub SET broader_topic = "Diet" where subreddit = "EatCheapAndHealthy";
UPDATE master_sub SET broader_topic = "Diet" where subreddit = "progresspics";
UPDATE master_sub SET broader_topic = "Diet" where subreddit = "loseit";
UPDATE master_sub SET broader_topic = "Diet" where subreddit = "GettingShredded";
UPDATE master_sub SET broader_topic = "Diet" where subreddit = "GYM";
UPDATE master_sub SET broader_topic = "Smoking" where subreddit = "stopsmoking";
UPDATE master_sub SET broader_topic = "Smoking" where subreddit = "quittingsmoking";
UPDATE master_sub SET broader_topic = "Smoking" where subreddit = "smokingcessation";
UPDATE master_sub SET broader_topic = "Smoking" where subreddit = "electronic_cigarette";

ALTER TABLE master_sub ADD COLUMN user_sub VARCHAR(250) NOT NULL, ADD COLUMN is_post INT NOT NULL;

UPDATE master_sub SET is_post = 1 WHERE created_utc_local BETWEEN CAST('2020-01-05' AS DATE) AND CAST('2021-02-05' AS DATE);
UPDATE master_sub SET is_post = 0 WHERE created_utc_local BETWEEN CAST('2019-01-05' AS DATE) AND CAST('2020-01-05' AS DATE);

UPDATE master_sub SET user_sub = CONCAT(author,'_', subreddit,'_','pre') where is_post = 0;
UPDATE master_sub SET user_sub = CONCAT(author,'_', subreddit,'_','post') where is_post = 1;

CREATE INDEX message_id ON master_sub(message_id);
ALTER TABLE master_sub ADD PRIMARY KEY(message_id);

ALTER TABLE master_sub ADD COLUMN is_drugs INT NOT NULL, ADD COLUMN is_pa INT NOT NULL, ADD COLUMN is_diet INT NOT NULL, ADD COLUMN is_smoking INT NOT NULL;

UPDATE master_sub SET is_drugs = 1 WHERE broader_topic = 'Drugs';
UPDATE master_sub SET is_pa = 1 WHERE broader_topic = 'Physical_Activity';
UPDATE master_sub SET is_diet = 1 WHERE broader_topic = 'Diet';
UPDATE master_sub SET is_smoking = 1 WHERE broader_topic = 'Smoking';

ALTER TABLE master_sub ADD COLUMN user_s VARCHAR(250) NOT NULL;
UPDATE master_sub SET user_s = CONCAT(author, subreddit);
