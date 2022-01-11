CREATE DEFINER=`kwanchoo`@`%` PROCEDURE `delete_covid_keys`()
BEGIN
    DECLARE counter INT;
    DECLARE counterend int;
	set counter := 1;
	set counterend := (select count(*) from covid_char);
    WHILE (counter <= counterend) do
        delete from covid_cv_reddit.feat$1to3gram$master_sub$user_sub$0_01$pmi3_0 where feat like 
        (select namee from covid_char limit 1 offset counter);
		set counter := counter + 1;
    END WHILE;
END