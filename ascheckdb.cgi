#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asdbutil.pl";
require "./asinstallation.pl";
require "./asgetmethod.pl";
require "./asfreedom.pl";

PrintHTTPHeader();

$title = "The Assayer: Checking Consistency of the Database";

use CGI;
use DBI;


$co = new CGI;

PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$bogus = 0;
$connected = 0;

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
	print "<h1>$title</h1>\n";
	
	if ($login = seems_loggedIn($co)) {
	  print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$login) . " logged in.";
	}
	else {
	  print "Not logged in.";
	}
	print "<br>\n";
  }

  #-------------------------------------------------------------------------------------------

  print "<h2>Book IDs not referred to by any bkref_id</h2>\n";
	if (! $bogus) {
	  $sth = $dbh->prepare("SELECT title,bk_id FROM bk_tbl ORDER BY bk_id") or $bogus=4;
	}
	if (! $bogus) {
	  $sth->execute() or $bogus=5;
	}
	if (! $bogus) {
    $count = 0;
	  while (@row = $sth->fetchrow_array()) {
	    ($title,$bk_id) = @row;
	    $err = 0;
	    $sth2 = $dbh->prepare("SELECT bkref_id FROM bkref_tbl WHERE bk_id LIKE '$bk_id'") or $err=1;
	    if (! $err) {
	      $sth2->execute() or $err=2;
	    }
	    if (! $err) {
	      @row = $sth2->fetchrow_array();
	    }
	    if (!@row) {
        print "<p>$title, bk_id=$bk_id, not referred to by any bkref_id, <a href=\"http://www.theassayer.org/cgi-bin/asbook.cgi?book=-$bk_id\">link</a><br/>";
        ++$count;
    	  $sth3 = $dbh->prepare("SELECT title,bk_id FROM bk_tbl WHERE title LIKE '$title'") or $bogus=6;
        if (!$bogus) {$sth3->execute() or $bogus=7}
        if (!$bogus) {
          while (@row=$sth3->fetchrow_array()) {
            ($title,$bk_id2)=@row;
            if ($bk_id2 != $bk_id) {print " -- bk_id $bk_id2 refers to a similar title, $title<br/>"}
          }
        }
        if (ref $sth3) {$sth3->finish}
        print "</p>\n";
		  }
	  }
    print "Total found: $count<br/>\n";
    if (ref $sth) {$sth->finish}
    if (ref $sth2) {$sth2->finish}
	}

  #-------------------------------------------------------------------------------------------

  print "<h2>bkref_ids that refer to nonexistent bk_ids</h2>\n";
	if (! $bogus) {
	  $sth = $dbh->prepare("SELECT bkref_id FROM bkref_tbl") or $bogus=4;
	}
	if (! $bogus) {
	  $sth->execute() or $bogus=5;
	}
	if (! $bogus) {
	  @row = $sth->fetchrow_array();
    ($bkref_id,) = @row;
    $count = 0;
	  while (@row = $sth->fetchrow_array()) {
	    ($title,$bk_id) = @row;
	    $err = 0;
	    $sth2 = $dbh->prepare("SELECT bk_id FROM bkref_tbl WHERE bkref_id LIKE '$bkref_id'") or $err=1;
	    if (! $err) {
	      $sth2->execute() or $err=2;
	    }
	    if (! $err) {
	      @row = $sth2->fetchrow_array();
	    }
	    if (!@row) {
        print "bkref_id=$bkref_id refers to nonexistent bk_id=$bk_id<br/>\n";
        ++$count;
		  }
	  }
    print "Total found: $count<br/>\n";
    if (ref $sth) {$sth->finish}
    if (ref $sth2) {$sth2->finish}
	}

  #-------------------------------------------------------------------------------------------

  print "<h2>Author IDs not referred to by any auref_id</h2>\n";
	if (! $bogus) {
	  $sth = $dbh->prepare("SELECT au_id FROM auref_tbl") or $bogus=4;
	}
	if (! $bogus) {
	  $sth->execute() or $bogus=5;
	}
	if (! $bogus) {
    $count = 0;
	  while (@row = $sth->fetchrow_array()) {
	    ($au_id,) = @row;
	    $err = 0;
	    $sth2 = $dbh->prepare("SELECT auref_id FROM auref_tbl WHERE au_id LIKE '$au_id'") or $err=1;
	    if (! $err) {
	      $sth2->execute() or $err=2;
	    }
	    if (! $err) {
	      @row = $sth2->fetchrow_array();
	    }
	    if (!@row) {
        print "au_id=$au_id, not referred to by any auref_id<br/>\n";
        ++$count;
		  }
	  }
    print "Total found: $count<br/>\n";
    if (ref $sth) {$sth->finish}
    if (ref $sth2) {$sth2->finish}
	}

  #-------------------------------------------------------------------------------------------

  print "<h2>Books with no authors listed (not even anonymous)</h2>\n";
	if (! $bogus) {
	  $sth = $dbh->prepare("SELECT title,bk_id FROM bk_tbl ORDER BY bk_id") or $bogus=4;
	}
	if (! $bogus) {
	  $sth->execute() or $bogus=5;
	}
	if (! $bogus) {
    $count = 0;
	  while (@row = $sth->fetchrow_array()) {
	    ($title,$bk_id) = @row;
	    $err = 0;
      if (!get_aurefs($bk_id,$dbh)) {
        print "<p>$title, bk_id=$bk_id, gives an error in get_aurefs()</p>\n";
        ++$count;
      }
	  }
    print "Total found: $count<br/>\n";
    if (ref $sth) {$sth->finish}
    if (ref $sth2) {$sth2->finish}
	}

if ($bogus) {
	print "Sorry, error $bogus occurred.<p>\n ";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  if (ref $sth2) {$sth2->finish}
  $dbh->disconnect;
}

PrintFooterHTML($homepath);


