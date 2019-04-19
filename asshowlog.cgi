#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################
# Bug: Doesn't handle parent_review when revising or looking at multiple versions...argh!!!

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asdbutil.pl";
require "./asinstallation.pl";
require "./asgetmethod.pl";
require "./asnotifyutil.pl";
require "./aslog.pl";

PrintHTTPHeader();

use CGI;
use DBI;


$co = new CGI;

$bogus = 0;
$connected = 0;

$title = "The Assayer: View Log File";


$debug = 0;


if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
	print "<h1>The Assayer: Browse by Title</h1>\n";
	
	
	if ($login = seems_loggedIn($co)) {
	  print "User $login logged in.";
	}
	else {
	  print "Not logged in.";
	}
	print "<p>\n";
  
  }

if (! $bogus) {
  $selectstmt = "SELECT title,bk_id FROM bk_tbl ORDER BY title";
  $sth = $dbh->prepare($selectstmt) or $bogus=4;
}
if (! $bogus) {
  $sth->execute() or $bogus=5;
}
if (! $bogus) {
  while (@row = $sth->fetchrow_array()) {
    $this_title = $row[0];
}
if ($bogus) {
	$title = "The Assayer: Error Viewing Log";
	PrintHeaderHTML($homepath,$title);
	PrintBannerHTML($homepath);
	print "<h1>Error</h1>\n";
	print "$bogus<p>\n ";
}
if ($connected) {
  $dbh->disconnect;
}

PrintFooterHTML($homepath);

