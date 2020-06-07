#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asdbutil.pl";
require "./asgetmethod.pl";
require "./asinstallation.pl";
require "./asuinfo.pl";

use Digest::SHA;


use CGI;
use DBI;


$co = new CGI;

$login = "";
%query_hash = decode_query_hash();
if (exists($query_hash{"login"})) {
  $login = $query_hash{"login"};
  $login =~ tr/+/ /;
  $title = "The Assayer: User $login";
}
else {
  $bogus = "GET method parameter not given.";
  $title = "The Assayer: User";
}

if ($login =~ m/[^A-Za-z0-9 ]/) {$bogus="Login names can only contain letters, digits, and spaces.";}

  
PrintHTTPHeader();
PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$bogus = 0;
$connected = 0;
$count_reviews = 0;

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) 
    		or $bogus="Error connecting to database.";
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
	print "<h1>$title</h1>\n";
	
	
	if ($reader_login = seems_loggedIn($co)) {
	  print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$reader_login) . " logged in.";
	  if ($reader_login eq $login) {
	    print "<br>Click on <i>log in</i> above to edit your own user information.";
	  }
	}
	else {
	  print "Not logged in.";
	}
	print "<p>\n";
  
  }

if (! $bogus) {
  $read_stuff = "";
  foreach $uinfo_key(@uinfo_order) {
      if ($read_stuff eq "") {
        $read_stuff = $read_stuff . $uinfo_key;
      }
      else {
        $read_stuff = $read_stuff . "," . $uinfo_key;
      }
  }
  $selectstmt = "SELECT " . $read_stuff . " FROM users WHERE login = '$login'";
  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error (1)";
}
if (! $bogus) {
  $sth->execute() or $bogus="Error reading database (1).";
}
if (! $bogus) {
  @row = $sth->fetchrow_array();
  if (!@row) {
     $bogus = "No such user";
  }
}
if (! $bogus) {
  print "<h2>About This User</h2>\n";
  print "<table>";
  $k = 0;
  foreach $uinfo_key(@uinfo_order) {
    $value = $row[$k];
    $op = "";
    if (!$uinfo_private{$uinfo_key}) {
      if ($uinfo_optional{$uinfo_key}) {$op=" (optional)";}
      print "<tr><td bgcolor=\"#dddddd\" valign=\"top\">"
    	. "<b>" . $uinfo_name{$uinfo_key} . "</b>"
    	. $op
    	. "</td><td>"
    	. $value
    	. "</td></tr>";
    }
    ++$k;
  }
  print "</table>";
}
if (! $bogus) {
    print "<h2>Reviews by This User</h2>\n";
	if (! $bogus) {
	  $user_id = user_login_to_id($login,$dbh);
	  $selectstmt2 = "SELECT bkref_id FROM review_tbl WHERE user_id LIKE '$user_id' ORDER BY bkref_id ";
	  $sth2 = $dbh->prepare($selectstmt2) or $bogus="Internal error (2)";
	}
	if (! $bogus) {
	  $sth2->execute() or $bogus="Error reading database (2).";
	}
	if (! $bogus) {
	  $previous_bkref = 0;
	  while (@row2 = $sth2->fetchrow_array()) {
	    ($bkref) = @row2;
	    
	    if ($bkref != $previous_bkref) {

			if (! $bogus) {
			  $selectstmt3 = "SELECT subject,review_id FROM review_tbl WHERE bkref_id LIKE '$bkref' AND user_id LIKE '$user_id' ORDER BY review_id DESC";
			  $sth3 = $dbh->prepare($selectstmt3) or $bogus="Internal error (3)";
			}
			if (! $bogus) {
			  $sth3->execute() or $bogus="Error reading database (3).";
			}
			if (! $bogus) {
			  if (@row3 = $sth3->fetchrow_array()) {
			    ($subject,$review_id) = @row3;

				if (! $bogus) {
				  $selectstmt4 = "SELECT bk_id FROM bkref_tbl WHERE bkref_id LIKE '$bkref'";
				  $sth4 = $dbh->prepare($selectstmt4) or $bogus="Internal error (4)";
				}
				if (! $bogus) {
				  $sth4->execute() or $bogus="Error reading database (4).";
				}
				if (! $bogus) {
				  if (@row4 = $sth4->fetchrow_array()) {
				        ($bk_id) = @row4;
						if (! $bogus) {
						  $selectstmt5 = "SELECT title FROM bk_tbl WHERE bk_id LIKE '$bk_id'";
						  $sth5 = $dbh->prepare($selectstmt5) or $bogus="Internal error (5)";
						}
						if (! $bogus) {
						  $sth5->execute() or $bogus="Error reading database (5).";
						}
						if (! $bogus) {
						  if (@row5 = $sth5->fetchrow_array()) {
						    ($title) = @row5;
						    print "<a href=\"asbook.cgi?book=$bkref\">$title</a> - $subject<br>\n";
						    $this_member_has_reviewed = 1;
						    ++$count_reviews;
						  }
						}
				  }
				}
			  }
			}
		
		}
	
	    $previous_bkref = $bkref;

	  }
	}
}

if (!$bogus) {
  print "<table><tr><td bgcolor=\"#dddddd\">Total reviews</td><td>$count_reviews</td></tr></table>\n";
}

if ($bogus) {
	print "<h1>Error</h1><br>$bogus<p>\n ";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  if (ref $sth2) {$sth2->finish}
  if (ref $sth3) {$sth3->finish}
  if (ref $sth4) {$sth4->finish}
  if (ref $sth5) {$sth5->finish}
  $dbh->disconnect;
}

PrintFooterHTML($homepath);
