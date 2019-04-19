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

$title = "The Assayer: Browse by Author";

use CGI;
use DBI;

$co = new CGI;

%query_hash = decode_query_hash();
$search = $co->param('search');
if (exists($query_hash{"search"})) {
  $search = $query_hash{"search"};
}

$do_it = ($co->param('submit') ne "") || ($search ne "");



PrintHTTPHeader();

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
	print "<p>\n";
  
  }

	  print  $co->startform(-method=>'POST',-action=>"$cgi_full_path/asbrowseauthor.cgi") . "\n";
	
	print "Enter one or more letters from the beginning of the author's last name,<br> or leave this space blank to view the "
	   . "entire list of authors.<br>\n"
	   .  $co->textfield(-name=>'search',-value=>$search,-size=>20,-maxlength=>30) 
	.	$co->submit(-name=>'submit',-value=>'Submit')
	.	$co->endform;

if ($do_it) {
	if (! $bogus) {
	  $selectstmt = "SELECT au_id, last_name, first_and_middle_names, suffix FROM au_tbl WHERE last_name LIKE "
	  	. $dbh->quote($search . "%") . " ORDER BY last_name, first_and_middle_names, suffix";
	  $sth = $dbh->prepare($selectstmt) or $bogus=4;
	}
	if (! $bogus) {
	  $sth->execute() or $bogus=5;
	}
	if (! $bogus) {
	  $count = 0;
	  while (@row = $sth->fetchrow_array()) { # for each author id...
	    $au_id = $row[0];
	    $this_last = $row[1];
	    $this_first = $row[2];
	    $this_suffix = $row[3];
	    $selectstmt2 = "SELECT auref_id FROM auref_tbl WHERE au_id LIKE '$au_id'";
	    $err = 0;
	    $sth2 = $dbh->prepare($selectstmt2) or $err=1;
	    if (! $err) {
	      $sth2->execute() or $err=2;
	    }
	    # No loop here. We just want the first auref that refers to this author id.
	    if (! $err) {
	      @row = $sth2->fetchrow_array();
	    }
	    if (@row) {
	      $auref_id = $row[0];
	      ++$count;
	      if ((length $this_suffix)>0) {
	        print "<a href=\"asauthor.cgi?author=$auref_id\">$this_last, $this_first, $this_suffix</a><br>\n";
	      }
	      else {
	        print "<a href=\"asauthor.cgi?author=$auref_id\">$this_last, $this_first</a><br>\n";
	      }
	    }
	  }
	}
}

if (!$bogus && $do_it) {
  print "<p>Total matches: $count<p>\n";
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


