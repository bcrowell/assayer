#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asinstallation.pl";

PrintHTTPHeader();

$title = "The Assayer: Email Login Information";

use CGI;
use DBI;


$co = new CGI;


PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);


print "<h1>E-mail Login Information</h1>\n";
print "Please enter the same e-mail address you used when you registered as a member. Your ";
print "username and password will be e-mailed to you at that address.<p>";

print 
	$co->startform(
		-method=>'POST',
		-action=>"$cgi_full_path/asforgot2.cgi");
		
print "E-mail: " . $co->textfield(-name=>'email',-value=>'',-size=>50) . "<p>";

print	$co->submit(-name=>'Submit');

		
print	$co->endform;

print "<p/>The <i>Home</i> link above will take you back to The Assayer's home page.<p>\n";
&PrintFooterHTML($homepath);
