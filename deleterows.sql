CREATE DEFINER=`kwanchoo`@`%` PROCEDURE `deleterows`()
BEGIN
    DECLARE counter INT;
    DECLARE counterend int;
	set counter := 1;
	set counterend := (select count(*) from splchar);
    WHILE (counter <= counterend) do
        delete from covid_cv_reddit.feat$1to3gram$master_sub$message_id$16to16$0_0001 where feat like 
        (select namee from splchar limit 1 offset counter);
		set counter := counter + 1;
    END WHILE;
END