use CGI;
use DBI;

require "./asdbutil.pl";
require "./asinstallation.pl";

# 	  user_id INTEGER NOT NULL,
# 	  bkref_id INTEGER NOT NULL,
# 	  notify_sauce VARCHAR(20)

#		if ($deactivate ne "") {deactivate_notification($dbh,$reader_id,$bk_refs_sql_clause);}
#		if ($activate ne "") {activate_notification($dbh,$reader_id,$bkref_id);}

sub notification_is_activated($$$)
	#returns notify_sauce or 0
{
    my ($dbh,$user_id,$bk_refs_sql_clause) = @_;

    my $selectstmt = "SELECT notify_sauce FROM notify_tbl WHERE user_id LIKE '$user_id' AND ($bk_refs_sql_clause)";
    #print "--- $selectstmt<p>\n";
    $sth = $dbh->prepare($selectstmt) or return 0;
    $sth->execute() or return 0;
    @row = $sth->fetchrow_array();
    if (!@row) {return 0;}
    return $row[0];
}


sub deactivate_notification($$$)
{
    my ($dbh,$user_id,$bk_refs_sql_clause) = @_;

    my $stmt = "DELETE FROM notify_tbl WHERE user_id LIKE '$user_id' AND ($bk_refs_sql_clause)";
    #print "--- $selectstmt<p>\n";
    $sth = $dbh->prepare($stmt) or return 0;
    $sth->execute() or return 0;
 }

sub activate_notification($$$$)
{
    my ($dbh,$user_id,$bkref_id,$bk_refs_sql_clause) = @_;
    deactivate_notification($dbh,$user_id,$bk_refs_sql_clause);
    $sauce = int (10000. * rand) . int (10000. * rand);
    my $stmt = "INSERT INTO notify_tbl(user_id,bkref_id,notify_sauce) VALUES('$user_id','$bkref_id','$sauce')";
    $sth = $dbh->prepare($stmt) or return 0;
    $sth->execute() or return 0;
 }
 
sub send_notifications()
{
 	my ($dbh,$bkref) = @_;
 	my $err_ref;
 	my @row;
	my $bk_id = bk_ref_to_raw_id($bkref,$dbh);
	if (!$bk_id) {return 0;}
	$title = get_book_info($dbh,$bk_id,"title");
	my @bk_refs = all_bk_refs($bk_id,$dbh,\$err_ref);
	if ($err_ref) {return 0;}
	my $bk_refs_sql_clause = make_bk_refs_sql_clause(\@bk_refs);
    my $selectstmt = "SELECT user_id,notify_sauce FROM notify_tbl WHERE ($bk_refs_sql_clause)";
    #print "--- $selectstmt<p>\n";
    my $sth = $dbh->prepare($selectstmt) or return 0;
    $sth->execute() or return 0;
    while (@row = $sth->fetchrow_array()) {
      my ($user_id,$notify_sauce) = @row;

      my $selectstmt2 = "SELECT email FROM users WHERE id LIKE '$user_id'";
      my $sth2 = $dbh->prepare($selectstmt2) or return 0;
      $sth2->execute() or return 0;
      if (@row2 = $sth2->fetchrow_array()) {
        $email = $row2[0];
		$message_text = "
Discussion has been posted on The Assayer about the following book:
  $title
This automated e-mail was sent because you asked to be notified of
discussion of this book.
To read the latest discussion, go to the following Web address:
  $cgi_full_path/asbook.cgi?book=$bkref
If you want to stop receiving e-mail notifications about discussion
of this book, go to the same discussion page and click Deactivate.";

      send_email(TO=>$email,REASON=>'You requested notification of discussion on this book.',SUBJECT=>"discussion of $title on The Assayer",
										 BODY=>$message_text);


	  }#end if row2

    }#end while row
    return 1;
}#end sub send_notifications

return 1;
