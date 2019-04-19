#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";



require "./ashtmlutil.pl";
require "./asgetmethod.pl";
require "./asinstallation.pl";


PrintHTTPHeader();

$title = "The Assayer: Log In";

use CGI;
use DBI;


$co = new CGI;

%query_hash = decode_query_hash();
if (exists($query_hash{"x"})) {
  $try_x_version = "?x";
}
else {
  $try_x_version = "";
}

PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);


$bogus = 0;


if (! $bogus) {
   
	print "<h1>Log In</h1>\n";
  
  }

print 
	$co->start_form(-method=>'POST',-action=>"$cgi_full_path/aslogin2.cgi$try_x_version");
		
print "Login name: " . $co->textfield(-name=>'login',-value=>'') . "<br>";


#print "Password: " . $co->textfield(-name=>'pwd',-value=>'') . "<p>";
print "Password: <INPUT TYPE=\"PASSWORD\" NAME=\"pwd\" SIZE=\"12\" MAXLENGTH=\"12\"><p>";

print	$co->submit(-name=>'Log In');

print "<p>Don't have an account? <a href=\"asnewmember.cgi\">Click here</a> to get one!<p>\n";
print "If you've forgotten your username or password, <a href=\"asforgot.cgi\">click here</a>.<p>\n";
		
print	$co->end_form;

&PrintFooterHTML($homepath);
