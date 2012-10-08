use DBI;

require "asdbutil.pl";
require "db_password.pl";

#    CREATE TABLE log_tbl (
# 	  user_id INTEGER NOT NULL,
# 	  clock DATETIME DEFAULT '0000-00-00 00:00:00' NOT NULL,
# 	  what VARCHAR(50) NOT NULL,
# 	  bkref_id INTEGER,
# 	  bk_id INTEGER,
# 	  auref_id INTEGER,
# 	  au_id INTEGER,
# 	  review_id INTEGER,
# 	  user_id_affected INTEGER,
# 	  description TEXT


sub make_log_entry($$$$$$$$$$)
{
    my ($dbh,$user_id,$what,$bkref_id,$bk_id,$auref_id,$au_id,$review_id,$user_id_affected,$description) = @_;
		# args are same as record, except dbh on front for "when"
		# pass zeroes if unknown or not relevant
		# if you pass 0 for bk_id or au_id, it gets filled in
	if ($bk_id==0 && $bkref_id) {$bk_id = bk_ref_to_raw_id($bkref_id,$dbh);}
	if ($au_id==0 && $auref_id) {$au_id = au_ref_to_raw_id($auref_id,$dbh);}
    my $stmt = "
    	INSERT INTO 
    	log_tbl (user_id,clock,what,bkref_id,bk_id,auref_id,au_id,review_id,user_id_affected,description)
    	VALUES('$user_id',NOW()," 
    		. $dbh->quote($what) 
    		. ",'$bkref_id','$bk_id','$auref_id','$au_id','$review_id','$user_id_affected',"
    		. $dbh->quote($description) . ")";
    #print "--- $stmt<p>\n";
    $sth = $dbh->prepare($stmt) or return 0;
    $sth->execute() or return 0;
    #print "did it<p>";
    return 1;
}


return 1;
