#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asdbutil.pl";

require "asinstallation.pl";

$title = "The Assayer: Browse by Reviewer";

use CGI;
use DBI;


$co = new CGI;

PrintHTTPHeader();

PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$bogus = 0;
$connected = 0;
$count_members = 0;
$count_reviewers = 0;
$count_reviews = 0;



if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) 
    		or $bogus="Error connecting to database.";
}
if (! $bogus) {
    $connected = 1;
    my $stmt = "SELECT count(id) FROM users";
    my $sth = $dbh->prepare($stmt) or print "error";
  	$sth->execute() or print "error";
    my @row = $sth->fetchrow_array();
	  $count_members = $row[0];
}

if (! $bogus) {
   
	print "<h1>$title</h1>\n";
	
	
	if ($login = seems_loggedIn($co)) {
	  print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$login) . " logged in.";
	}
	else {
	  print "Not logged in.";
	}
	print "<p>\n";
  
  }

if (! $bogus) {
  $selectstmt = "SELECT user_id FROM review_tbl";
  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error (1)";
}
if (! $bogus) {
  $sth->execute() or $bogus="Error reading database.";
}
if (! $bogus) {
  @users = ();
  while (@row= $sth->fetchrow_array()) {
    push @users,$row[0];
  }
  # get rid of dups:
  %users = ();
  foreach $user_id(@users) {
    $users{$user_id} = 1;
  }
  %info = ();
  foreach $user_id(keys %users) {
    $r = user_id_to_full_name_and_login($dbh,$user_id);
    $name = $r->{'full'};
    if ($name=~m/((\w+\.?)\s+)(\w+)/) {
      $name = "$3, $1";
    }
    $cooked_login = $r->{'login'};
    $cooked_login =~ tr/ /+/;
    $user_link
          = "<a href=\"" . $cgi_full_path . "/asuser.cgi?login=" . $cooked_login . "\">" . $name . "</a>";
    $info{$name} = {'login'=>$r->{login},'link'=>$user_link,'id'=>$user_id};
  }
  foreach $name(sort keys %info) {
    next if $name eq '0';
    ++$count_reviewers;
    $r = $info{$name};
    $login = $r->{'login'};
    $link = $r->{'link'};
    $user_id = $r->{'id'};
    print "$link<br><ul>\n";
    $selectstmt2 = "SELECT bkref_id FROM review_tbl WHERE user_id LIKE '$user_id' ORDER BY bkref_id ";
	  $sth2 = $dbh->prepare($selectstmt2) or $bogus="Internal error (2)";
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
  print "</ul>\n";
  } # loop over users
}

if (!$bogus) {
  print "<h2>Totals</h2>\n";
  print "<table><tr><td>Total members</td><td>$count_members</td></tr>\n";
  print "<tr><td>Total members who have written reviews</td><td>$count_reviewers</td></tr>\n";
  print "<tr><td>Total reviews</td><td>$count_reviews</td></tr></table>\n";
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


