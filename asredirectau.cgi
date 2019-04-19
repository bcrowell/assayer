#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################
# bug: when setting defaults of score menus, doesn't handle values
# that aren't integers

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asdbutil.pl";
require "./aslog.pl";
require "./asinstallation.pl";
require "./asgetmethod.pl";

PrintHTTPHeader();


%query_hash = decode_query_hash();
$debug = exists($query_hash{"debug"});

use CGI;
use DBI;

$co = new CGI;


if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}

$keep = $co->param('keep');
$redirect = $co->param('redirect');
$do_what = 1;
if ($co->param('submit') ne "") {
  $do_what = $co->param('submit');
}


$pagetitle = "Redirecting an Author";
PrintHeaderHTML($homepath,$pagetitle);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

print "<h1>$pagetitle</h1>\n";
print "<b>Warning -- read this:</b> You should not normally need to use this page. "
	. " The only reason"
	. " this page exists is to handle situations where the same author has been entered into the database"
	. " twice. Be sure to read the entire help page before messing with this. It's probably a better"
	. " idea to e-mail the webmaster instead of doing it yourself, unless you're sure you understand"
	. " what you're doing.<p>";
if ($debug) {print "Debugging mode on<p>\n";}
$bogus = 0;


if (! $bogus) {
	if ($login = seems_loggedIn($co)) {
	}
	else {
	  $bogus = "Only logged-in users can edit book data.";
	}
}
	
	if (!$bogus) {
		#########################################################
		###### Get this person's user ID
		#########################################################
		if (! $bogus) {
		  $selectstmt = "SELECT id FROM users WHERE login LIKE '$login'";
		  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error.";
		}
		if (! $bogus) {
		  $sth->execute() or $bogus="Error searching database (1).";
		}
		if (! $bogus) {
		  @row = $sth->fetchrow_array();
		  if (! @row) {
		    $bogus = "Error reading database --$selectstmt--(1).";
		  }
		  else {
		    $user_id = $row[0];
		    #print "User $login, user id $user_id<p>\n";
		  }
		}
	}
	
	
	
if (!$bogus && $keep ne "" && $user_id) {
  $keep_raw = au_ref_to_raw_id($keep,$dbh);
}
else {
  $keep_raw = "";
}
if (!$bogus && $redirect ne "" && $user_id) {
  $redirect_raw = au_ref_to_raw_id($redirect,$dbh);
}
else {
  $redirect_raw = "";
}
	

###################################################
## Form 
###################################################
if (!$bogus) {
	if (!$debug) {
	  print  $co->startform(-method=>'POST',
	    		-action=>"$cgi_full_path/asredirectau.cgi") . "\n";
	}
	else {
	  print  $co->startform(-method=>'POST',
	    		-action=>"$cgi_full_path/asredirectau.cgi?debug=true") . "\n";
	}
	print "step $do_what<p>\n";
	
	print "<table>\n";
	
	print "<tr><td>keep:</td><td>" 
		. $co->textfield(-name=>'keep',-value=>$keep,-size=>70,-maxlength=>70) ."</td><td>->$keep_raw</td></tr>\n";
	print "<tr><td>redirect:</td><td>" 
		. $co->textfield(-name=>'redirect',-value=>$redirect,-size=>70,-maxlength=>70) ."</td><td>->$redirect_raw</td></tr>\n";
	print "</table>\n";	
	if ($do_what == 1) {
	  print	$co->submit(-name=>'submit',-value=>'2');
	}
	if ($do_what == 2) {
	  print	$co->submit(-name=>'submit',-value=>'3');
	}
	if ($do_what == 3) {
	  print	$co->submit(-name=>'submit',-value=>'1');
	}
	
	print	$co->endform;
}

###################################################
## Do the deed. 
###################################################
if (!$bogus && $keep ne "" && $redirect ne "" && $user_id && $keep_raw ne "" && $do_what==3) {
  print "Redirecting<p>\n";
	  $stmt = "UPDATE auref_tbl SET au_id = '$keep_raw' WHERE auref_id = '$redirect'";
	   $sth = $dbh->prepare($stmt) or $bogus=4;
	if (! $bogus) {
	  $sth->execute() or $bogus=5;
	}
}

&PrintFooterHTML($homepath);

	if ($bogus) {
	  print "Error: $bogus<p>\n";
	}

if ($connected) {
  $dbh->disconnect;
}

