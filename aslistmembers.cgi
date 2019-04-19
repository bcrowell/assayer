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
PrintHTTPHeader();

$title = "The Assayer: Membership List";

use CGI;
use DBI;


$co = new CGI;


PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);

$bogus = 0;
$connected = 0;

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
	print "<h1>Assayer Membership List</h1>\n";
	if ($login = seems_loggedIn($co)) {
	  print "User $login logged in.";
	}
	else {
	  print "Not logged in.";
	}
	print "<p>\n";
  
  }

if (! $bogus) {
  $selectstmt = "SELECT login FROM users ORDER BY login";
  $sth = $dbh->prepare($selectstmt) or $bogus=4;
}
if (! $bogus) {
  $sth->execute() or $bogus=5;
}
if (! $bogus) {
  while (@row = $sth->fetchrow_array()) {
    print " " . $row[0] . "<br>\n";
  }
}


if ($bogus) {
	print "Sorry, error $bogus occurred.<p>\n ";
}
if ($connected) {
  $dbh->disconnect;
}

print "<p>The <i>Home</i> link above will take you back to The Assayer's home page.<p>";
PrintFooterHTML($homepath);


