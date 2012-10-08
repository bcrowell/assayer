use CGI;
use DBI;

require "db_password.pl";

sub count_reviews_html($$)
{
  my ($dbh,$bkref_id) = @_;
    
	my $err_ref;
	my $bk_id = bk_ref_to_raw_id($bkref_id,$dbh);
	
	my @bk_refs = all_bk_refs($bk_id,$dbh,\$err_ref);
	if ($err_ref) {return "e1";}
	my $bk_refs_sql_clause = make_bk_refs_sql_clause(\@bk_refs);

    my $stmt = "SELECT count( user_id) FROM review_tbl WHERE ($bk_refs_sql_clause)";
          # ...count (distinct user_id) causes error...not implemented in mySQL?
    my $sth = $dbh->prepare($stmt) or return "e2";
	$sth->execute() or return "$stmt";
    my @row = $sth->fetchrow_array();
	if (!@row) {
	  return "e4";
	}
	if (@row) {
	  if ($row[0]==0) {
	    return " (no reviews) ";
	  }
	  else {
	    return "";
	  }
	}
  
}


sub get_book_info($$$)
{
    my ($dbh,$bk_id,$what) = @_;

    my $selectstmt2 = "SELECT $what FROM bk_tbl WHERE bk_id LIKE " . $dbh->quote($bk_id);
    #print "--- $selectstmt2<p>\n";
    my $sth2 = $dbh->prepare($selectstmt2) or return 0;
    $sth2->execute() or return 0;
    my @row2 = $sth2->fetchrow_array();
    if (!@row2) {return 0;}
    return $row2[0];
}

sub get_user_info($$$)
{
    my ($dbh,$user_id,$what) = @_;

    my $selectstmt = "SELECT $what FROM users WHERE id LIKE " . $dbh->quote($user_id);
    my $sth = $dbh->prepare($selectstmt) or return 0;
    $sth->execute() or return 0;
    my @row = $sth->fetchrow_array();
    if (!@row) {return 0;}
    return $row[0];
}

sub get_login_of_other_user($$)
{
    my ($reviewer_user_id,$dbh) = @_;

    my $selectstmt2 = "SELECT login FROM users WHERE id LIKE " . $dbh->quote($reviewer_user_id);
    my $sth2 = $dbh->prepare($selectstmt2) or return 0;
    $sth2->execute() or return 0;
    my @row2 = $sth2->fetchrow_array();
    if (!@row2) {return 0;}
    return $row2[0];
}

sub user_login_to_id($$)
{
    my ($login,$dbh) = @_;

    my $selectstmt2 = "SELECT id FROM users WHERE login LIKE " . $dbh->quote($login);
    my $sth2 = $dbh->prepare($selectstmt2) or return 0;
    $sth2->execute() or return 0;
    my @row2 = $sth2->fetchrow_array();
    if (!@row2) {return 0;}
    return $row2[0];
}


sub get_name($$)
{
	my ($au_id,$dbh) = @_;
	my @err_result = ("","","");
	my $selectstmt = "SELECT last_name,first_and_middle_names,suffix FROM au_tbl WHERE au_id LIKE '$au_id'";
	my $sth = $dbh->prepare($selectstmt) or return @err_result;
	$sth->execute() or return @err_result;
	my @row = $sth->fetchrow_array();
	if (! @row) {return @err_result;}
	return @row;
}


sub get_title($$)
{
	my ($bk_id,$dbh) = @_;
    my $selectstmt = "SELECT title FROM bk_tbl WHERE bk_id LIKE '$bk_id'";
    my $sth = $dbh->prepare($selectstmt) or return 0;
    $sth->execute() or return 0;
    my @row = $sth->fetchrow_array();
    if (! @row) {return 0;}
    return $row[0];

}

sub get_aurefs($$)
{
	my ($bk_id,$dbh) = @_;
    my $selectstmt = "SELECT auref_id1,auref_id2,auref_id3,auref_id4,auref_id5 FROM bk_tbl WHERE bk_id LIKE '$bk_id'";
    my $sth = $dbh->prepare($selectstmt) or return 0;
    $sth->execute() or return 0;
    my @row = $sth->fetchrow_array();
    if (! @row) {return 0;}
    my @result = ();
    if ($row[0]>0) {push @result,$row[0];}
    if ($row[1]>0) {push @result,$row[1];}
    if ($row[2]>0) {push @result,$row[2];}
    if ($row[3]>0) {push @result,$row[3];}
    if ($row[4]>0) {push @result,$row[4];}
    return @result;

}

# Returns the raw book id associated with this book ref. If a negative
# number is input, it just supplies the positive; this allows you to
# access books whose database info has been corrupted and have no ref pointing
# to them.
sub bk_ref_to_raw_id($$)
{
	my ($bkref_id,$dbh) = @_;
  if ($bkref_id<0) {return -$bkref_id}
	my $selectstmt = "SELECT bk_id FROM bkref_tbl WHERE bkref_id LIKE '$bkref_id'";
	my $sth = $dbh->prepare($selectstmt) or return 0;
	$sth->execute() or return 0;
	my @row = $sth->fetchrow_array();
	if (! @row) {return 0;}
	return $row[0];
}

sub au_ref_to_raw_id($$)
{
	my ($auref_id,$dbh) = @_;
	my $err = 0;
	my ($au_id,@row,$selectstmt,$sth);
	my @row;


	$selectstmt = "SELECT au_id FROM auref_tbl WHERE auref_id LIKE '$auref_id'";
	$sth = $dbh->prepare($selectstmt) or $err = -2;
	if (! $err) {
	  $sth->execute() or $err= -3;
	}
	if (! $err) {
	  @row = $sth->fetchrow_array();
	  if (! @row) {
	    $err = -4;
	  }
	  else {
	    $au_id = $row[0];
	  }
	}
	if ($err) {
	  return $err;
	}
	else {
	  return $au_id;
	}
}

sub make_au_refs_sql_clause()
	# pass array by reference
{
	
	my ($aaa) = @_; # $aaa holds reference to the array
	my @au_refs = @$aaa;
	my $auref_id;
	my $result = "";
	foreach $auref_id(@au_refs) {
	  for ($i=1; $i<=5; $i++) {
	    if ((length $result)!=0) {
	      $result = $result . "OR ";
	    }
	    $result = $result . "auref_id$i LIKE $auref_id ";
	  }
	}
	return $result;
}

sub make_bk_refs_sql_clause($)
	# pass array by reference
{
	
	my ($aaa) = @_; # $aaa holds reference to the array
	my @bk_refs = @$aaa;
	my $bkref_id;
	my $result = "";
	foreach $bkref_id(@bk_refs) {
	  if ((length $result)!=0) {
	    $result = $result . "OR ";
	  }
	  $result = $result . "bkref_id LIKE $bkref_id ";
	}
	return $result;
}

sub all_au_refs()
{
	my ($au_id,$dbh,$err_ref) = @_;
	my @refs = ();
	my ($sth,$selectstmt,@row);
    $$err_ref = 0;
	my $selectstmt = "SELECT auref_id FROM auref_tbl WHERE au_id LIKE '$au_id'";
	my $sth = $dbh->prepare($selectstmt) or $$err_ref = 1;
	if ($$err_ref) { return 0;  }
	$sth->execute() or $$err_ref = 2;
	if ($$err_ref) { return 0;  }
	while (@row = $sth->fetchrow_array()) {
	  push @refs,$row[0];
	}
	return @refs;
}

sub all_bk_refs($$$)
{
	my ($bk_id,$dbh,$err_ref) = @_;
	my @refs = ();
	my ($sth,$selectstmt,@row);
    $$err_ref = 0;
	my $selectstmt = "SELECT bkref_id FROM bkref_tbl WHERE bk_id LIKE '$bk_id'";
	my $sth = $dbh->prepare($selectstmt) or $$err_ref = 1;
	if ($$err_ref) { return 0;  }
	$sth->execute() or $$err_ref = 2;
	if ($$err_ref) { return 0;  }
	while (@row = $sth->fetchrow_array()) {
	  push @refs,$row[0];
	}
	return @refs;
}

sub printable_form_of_license_code()
{
	my ($code,$want_link) = @_;
	my ($license_name,$link);
	$license_name = "";
	
	# 100's are OPL
	if ($code == 110) {
	  $license_name =  "Open Publication License 1.0 without options A or B";
	  $link = "http://opencontent.org/openpub/";
	}
	# 200's are GFDL
	if ($code == 211) {
	  $license_name =  "GFDL 1.1";
	  $link = "http://www.gnu.org/copyleft/fdl.html";
	}
	if ($code == 310) {
          $license_name =  "Free Word 1.0";
          $link = "http://www.theassayer.org/freeword.txt";
 	}
        if ($code == 410) {
          $license_name =  "Soapbox 1.0";
          $link = "http://www.theassayer.org/soapbox.txt";
        }

	if ($want_link && (length $license_name)>0) {
	  return "<a href=\"$link\">$license_name</a>";
	}
	else {
	  return $license_name;
	}
}

# Has bug related to www.theassayer.org versus theassayer.org.
# Internal links always get generated with www. on the front, but if I type theassayer.org
# in the url bar, I get to a url withuot the www, so the cookie doesn't work.
sub bake_a_cookie {
  my $co = shift;
  my $path = cookie_path();
  return $co->cookie(-name=>'assayerlogin',-path=>cookie_path());

}

sub cookie_path {
  return '/'; # not just /cgi, because that breaks cookies on the home page
}

sub seems_loggedIn() # has bug related to www.theassayer.org versus theassayer.org -- see above at bake_a_cookie
{
	my ($co) = @_;
	my $the_cookie = bake_a_cookie($co);
	if ((length $the_cookie)>=1) {
	  my $login = (split /,/,$the_cookie)[0];
	  return $login;
	}
	else {
	  return 0;
	}
}

sub loggedIn() # has bug related to www.theassayer.org versus theassayer.org -- see above at bake_a_cookie
{
	my ($co,$dbh,$err_ref) = @_;
    $$err_ref = 0;
	my $the_cookie = bake_a_cookie($co);
	if ((length $the_cookie)<1) { return 0; }
	my $login = (split /,/,$the_cookie)[0];
	my $special_sauce = (split /,/,$the_cookie)[1];
	my $selectstmt = "SELECT login FROM users WHERE login LIKE "
					. $dbh->quote($login) . " AND special_sauce LIKE "
					. $dbh->quote($special_sauce);
	my $sth = $dbh->prepare($selectstmt) or $$err_ref = 1;
	if ($$err_ref) { return 0;  }
	$sth->execute() or $$err_ref = 2;
	if ($$err_ref) { return 0;  }
	my @row = $sth->fetchrow_array();
	if (! @row) {
	  return 0;
	}
	else {
	  return $row[0];
	}
}

sub loggedIn_user_id($$$)
{
	my ($co,$dbh,$err_ref) = @_;
    $$err_ref = 0;
	my $the_cookie = bake_a_cookie($co);
	if ((length $the_cookie)<1) { return 0; }
	my $login = (split /,/,$the_cookie)[0];
	my $special_sauce = (split /,/,$the_cookie)[1];
	my $selectstmt = "SELECT id FROM users WHERE login LIKE "
					. $dbh->quote($login) . " AND special_sauce LIKE "
					. $dbh->quote($special_sauce);
	my $sth = $dbh->prepare($selectstmt) or $$err_ref = 1;
	if ($$err_ref) { return 0;  }
	$sth->execute() or $$err_ref = 2;
	if ($$err_ref) { return 0;  }
	my @row = $sth->fetchrow_array();
	if (! @row) {
	  #print "---- $login $special_sauce";
	  return 0;
	  
	}
	else {
	  return $row[0];
	}
}

return 1;
