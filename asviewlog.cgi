#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################
# Bug: Doesn't handle parent_review when revising or looking at multiple versions...argh!!!

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asdbutil.pl";
require "asinstallation.pl";
require "asgetmethod.pl";
require "asnotifyutil.pl";
require "aslog.pl";

PrintHTTPHeader();

use CGI;
use DBI;

$bogus = 0;


%query_hash = decode_query_hash();
if (exists($query_hash{"n"})) {
  $n = $query_hash{"n"};
}
else {
  $n = 20;
}
if ($n =~ m/[^0-9]/) {$bogus = "Parameter n contains illegal characters.";}

$co = new CGI;

$connected = 0;

$title = "The Assayer: View Log File";
PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);


$debug = 0;


if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
	print "<h1>$title</h1>\n";
	
	
	if (($login = seems_loggedIn($co))) {
	  print "User $login logged in.";
	}
	else {
	  print "Not logged in.";
	  $bogus = "Only logged-in users can view the log file.";
	}
	print "<p>\n";
  
  }

if (! $bogus) {
  $selectstmt = "SELECT log_key,user_id,what,bkref_id,bk_id,auref_id,au_id,review_id,user_id_affected,description,clock FROM log_tbl ORDER BY log_key DESC";
  $sth = $dbh->prepare($selectstmt) or $bogus=4;
}
if (! $bogus) {
  $sth->execute() or $bogus=5;
}
if (! $bogus) {
  print "<table>\n";
  $count = 0;
  while ((@row = $sth->fetchrow_array()) && $count<$n) {
    ++$count;
    ($log_key,$user_id,$what,$bkref_id,$bk_id,$auref_id,$au_id,$review_id,$user_id_affected,$description,$when) = @row;
	$login = get_login_of_other_user($user_id,$dbh);
	$stuff = $description;
	if ($bkref_id ne "" && $bkref_id) {
	  $stuff = $stuff . " <a href=\"asbook.cgi?book=$bkref_id\">book $bkref_id</a>";
	}
	if ($auref_id ne "" && $auref_id) {
	  $stuff = $stuff . " <a href=\"asauthor.cgi?author=$auref_id\">author $auref_id</a>";
	}
	if ($review_id ne "" && $review_id) {
	  $stuff = $stuff . " review $review_id";
	}
    print "<tr><td>$log_key</td><td>$what</td><td>$login</td><td>$when</td><td>$stuff</td></tr>\n";
  }
  print "</table>\n";
}
if ($bogus) {
	print "Error $bogus<p>\n ";
}
if ($connected) {
    if (ref $sth) {$sth->finish}
  $dbh->disconnect;
}

PrintFooterHTML($homepath);

