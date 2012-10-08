#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asinstallation.pl";
require "asemail.pl";

PrintHTTPHeader();

$title = "The Assayer: E-mail Login Information";

use CGI;
use DBI;


$co = new CGI;


PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);



$email = $co->param('email');


$bogus = 0;
$connected = 0;
if ((length $email)<3) {$bogus=1;}

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}

if (! $bogus) {
    $connected = 1;
}

if (! $bogus) {
  $selectstmt = "SELECT login,pwd FROM users WHERE email LIKE '$email'";
  $sth = $dbh->prepare($selectstmt) or $bogus=4;
}
if (! $bogus) {
  $sth->execute() or $bogus=5;
}
if (! $bogus) {
  @row = $sth->fetchrow_array();
  if (! @row) {
    $bogus = "No user found with e-mail address $email.";
  }
}
if (! $bogus) {
   
  my $result = 
    send_email(TO=>$email,REASON=>'requested reminder of forgotten password',SUBJECT=>'Assayer login information',
             BODY=><<__BODY__
Here is the reminder you requested of your Assayer
login name and password. To log in, go to
	   http://theassayer.org
	
Login name: $row[0]
Password:   $row[1]
__BODY__
						 );
  if ($result eq '') {
  	print "<h1>Login Information Has Been E-Mailed</h1>\n";
  	print "Your login name and password have been e-mailed to $email.<p>";
  }
  else {
    print "Error: $result<p>";
  }
}


if ($bogus) {
    print "Error: $bogus\n";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  $dbh->disconnect;
}


&PrintFooterHTML($homepath);

