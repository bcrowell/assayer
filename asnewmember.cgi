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

$title = "The Assayer: New Member";

use CGI;
use DBI;


$co = new CGI;


PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);

print "<h1>New Member</h1>\n";
    print 
	$co->startform(
		-method=>'POST',
		-action=>"$cgi_full_path/asnewmember2.cgi");
		
		
print "\nPlease enter your desired login name here. You can use upper- and lower-case ";
print "letters, digits, and spaces. If in doubt, we recommend  ";
print "using your initials plus your last name, e.g. inewton. (Don't make it too long, ";
print "since you'll have to type it in every time you log in.)<br>";

print "Login name: " . $co->textfield(-name=>'login',-value=>'') . '<p>';
print "Real name: " .  $co->textfield(-name=>'realname',-value=>'') . '<br>';
print "<p>You will also need to supply a valid e-mail address, to which we can send your ";
print "registration information. By default, this address is not displayed publicly on ";
print "The Assayer.<br>\n";


print "E-mail: " . $co->textfield(-name=>'email',-value=>'');



print "<p>Privacy information: The Assayer will not supply your e-mail address to anybody ";
print "without your permission, except if we are forced to do so by law. We will not send you ";
print "e-mail unless you request it, or as required in order to maintain your account.<p>";
print	$co->submit(-name=>'Submit');

		
print	$co->endform;

&PrintFooterHTML($homepath);
