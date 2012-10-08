#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asinstallation.pl";
require "aslog.pl";
require "asemail.pl";

PrintHTTPHeader();

$title = "The Assayer: New Member";

use CGI;
use DBI;


$co = new CGI;


PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);


$email = $co->param('email');
$email =~ s/^\s+//; # trim leading whitespace
$email =~ s/\s+$//; # trim trailing whitespace
$login = $co->param('login');
$login =~ s/^\s+//; # trim leading whitespace
$login =~ s/\s+$//; # trim trailing whitespace
$realname = $co->param('realname');
$realname =~ s/^\s+//; # trim leading whitespace
$realname =~ s/\s+$//; # trim trailing whitespace

$bogus = 0;
$connected = 0;

if ((length $login)<3) {$bogus="Login names must be at least three characters long.";}
if ((length $login)>20) {$bogus="Login names cannot be more than 20 characters long.";}
if ($login =~ m/[^A-Za-z0-9 ]/) {$bogus="Login names can only contain letters, digits, and spaces.";}
if ((length $email)<3 || !($email =~ m/\@/)) {$bogus="Invalid e-mail address.";}
if ((length $email)>50) {$bogus="E-mail addresses cannot be more than 50 characters long.";}
if (!(
     length($realname)>=5
     && $realname=~m/\s/
     && $realname=~m/[a-zA-Z]{2,30}.*[a-zA-Z]{2,30}/
     && !($realname=~m/[^a-zA-Z\-\.\' ]/)
    )) {
  $bogus="You must supply your real name $realname.";
}

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus="Database unavailable.";
}
###### Is the username already taken?
if (! $bogus) {
  $selectstmt = "SELECT login FROM users WHERE login LIKE '$login'";
  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error.";
}
if (! $bogus) {
  $sth->execute() or $bogus="Error searching database.";
}
if (! $bogus) {
  @row = $sth->fetchrow_array();
  if (@row) {
    $bogus = "That login name is already taken.";
  }
}
###### Is there already an account with this e-mail address?
if (! $bogus) {
  $selectstmt = "SELECT email FROM users WHERE email LIKE '$email'";
  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error (2).";
}
if (! $bogus) {
  $sth->execute() or $bogus="Error searching database (2).";
}
if (! $bogus) {
  @row = $sth->fetchrow_array();
  if (@row) {
    $bogus = "There is already a member with that e-mail address.";
  }
}
###### Make new account.
if (! $bogus) {
    $connected = 1;
    $pwd = int (10000. * rand) . "-" . int (10000. * rand);
    $special_sauce = int (10000. * rand) . "-" . int (10000. * rand);
}
if (! $bogus) {
  $insertstmt = "INSERT INTO
  users (
    login,
    pwd,
    email,
    special_sauce,
    real_name
  )
  VALUES (
    \'$login\',
    \'$pwd\',
    \'$email\',
    \'$special_sauce\',
    \'$realname\'
  )";
  $sth = $dbh->prepare($insertstmt) or $bogus="Internal error (3).";
}
if (! $bogus) {
  $sth->execute() or $bogus="Error writing to database.";

}

if (! $bogus) {
   
	print "<h1>New Member Account Has Been Created</h1>\n";
	print "Welcome! You will receive an e-mail giving you ";
	print "your registration information. The Home link above will take you back to The Assayer's home page.<p>";
	print "<p>If you don't get the e-mail within the usual time interval, ";
	print "it's probably because you made a typo when you entered your address -- ";
	print "in this situation, please use the bug report form to get your account deleted, so that you ";
	print "can start over again.";
  my $result = 
    send_email(TO=>$email,REASON=>'asked to become a member',SUBJECT=>'Assayer membership',
             BODY=><<__BODY__
Welcome to The Assayer! We suggest that you log in at
	   http://theassayer.org
using the login name and password shown below, and
change your password to something else. Do not use a
valuable password, since it will be transmitted over
connections that are not secure.
	
Login name: $login
Password:   $pwd
E-mail:     $email
__BODY__
						 );
  if ($result eq '') {
  	print "Your password has been e-mailed to $email.<p>";
  }
  else {
    print "Error: $result<p>";
  }

}

if ($bogus) {
	print "<h1>Error</h1>\n";
	print "$bogus<p>\n";
	print "If you already have an account but have forgotten your username or password, \n";
	print "go to the log-in page, and ask to have your log-in information e-mailed to you.<p>\n ";
}


&PrintFooterHTML($homepath);

if (!$bogus && $connected) {
  make_log_entry($dbh,user_login_to_id($login,$dbh),"newmember",0,0,0,0,0,0,"");
}


if ($connected) {
  $dbh->disconnect;
}

