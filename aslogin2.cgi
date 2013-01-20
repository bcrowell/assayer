#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asgetmethod.pl";
require "asinstallation.pl";
require "asdbutil.pl";

use Digest::SHA;

$title = "The Assayer: Log In";

use CGI;
use DBI;


$co = new CGI;


$login = $co->param('login');
$pwd = $co->param('pwd');
$hash = Digest::SHA::sha1_base64($pwd."theassayer");

%query_hash = decode_query_hash();
if (exists($query_hash{"x"})) {
  $try_x_version = "x";
}
else {
  $try_x_version = "";
}


$bogus = 0;
$connected = 0;
if ((length $login)<3) {$bogus=1;}
if ((length $pwd)<3) {$bogus=2;}

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}

if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
  $selectstmt = "SELECT login,pwd_hash,special_sauce FROM users WHERE login = "
  	. $dbh->quote($login) . " AND pwd_hash = " . $dbh->quote($hash);
  $sth = $dbh->prepare($selectstmt) or $bogus=4;
}
if (! $bogus) {
  $sth->execute() or $bogus=5;
}
if (! $bogus) {
   @row = $sth->fetchrow_array();
   if (! @row) {$bogus="Invalid login name or password.";}
}
if (! $bogus) {
   $special_sauce = $row[2];
   $logincookietext = $login . "," . $special_sauce;
   $logincookie = $co->cookie(
      -name=>'assayerlogin',
      -value=>$logincookietext,
      -expires=>("+" . $login_period . "d"),
      -path=>cookie_path(),
    );
	print $co->header(-cookie=>$logincookie);
	&PrintHeaderHTML($homepath,"Logged In");
	&PrintBannerHTML($homepath);
	print toolbar_HTML($homepath);
	print "<h1>Logged In</h1>\n";
	print "Welcome, $login! You will remain logged in on this computer for the next $login_period days."
		. " If other people use this computer, you may wish to log out at the end of each session on the site.<p>";


	#print "---" . $co->header(-cookie=>$logincookie) . "---";

	
	print "<h2>Changing your password</h2>\n";
	print 
		$co->startform(
			-method=>'POST',
			-action=>"$cgi_full_path/aschangeuserinfo.cgi");
			
	print "New password: <INPUT TYPE=\"PASSWORD\" NAME=\"newpwd1\" SIZE=\"12\" MAXLENGTH=\"12\"><p>";
	print "Type new password again: <INPUT TYPE=\"PASSWORD\" NAME=\"newpwd2\" SIZE=\"12\" MAXLENGTH=\"12\"><p>";
	
	print  	$co->hidden(-name=>'login',-default=>"$login",-override=>1);
	print  	$co->hidden(-name=>'pwd',-default=>"$pwd",-override=>1);
	print	$co->submit(-name=>'Change Password');
	
			
	print	$co->endform;

	print "<h2>Changing other user information</h2>\n";
	print 
		$co->startform(
			-method=>'POST',
			-action=>"$cgi_full_path/aschangeuserinfo.cgi");
			
	
	print  	$co->hidden(-name=>'login',-default=>"$login",-override=>1);
	print  	$co->hidden(-name=>'pwd',-default=>"$pwd",-override=>1);
	print	$co->submit(-name=>'Go');
	

	&PrintFooterHTML($homepath);
  
  }
if ($connected) {
  if (ref $sth) {$sth->finish}
  $dbh->disconnect;
}

if ($bogus) {
	PrintHTTPHeader();
	&PrintHeaderHTML($homepath,"Error Logging In");
	&PrintBannerHTML;
	print "<h1>Error Logging In</h1>\n";
	print "$bogus<p>\n";
	&PrintFooterHTML($homepath);
}
