#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asdbutil.pl";
require "./asgetmethod.pl";
require "./asinstallation.pl";
require "./asuinfo.pl";
require "./aslog.pl";

use CGI;
use DBI;


$co = new CGI;

$title = 'The Assayer';

PrintHTTPHeader();
PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$bogus = 0;
$connected = 0;

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) 
    		or $bogus="Error connecting to database.";
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
  if (1) {
	if ($reader_login = seems_loggedIn($co)) {
	  print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$reader_login) . " logged in.";
	}
	else {
	  print "Not logged in.";
	}
	print "<p>\n";
  }
  
}




#---------------------------------------------------------------------------------------------

print '<table width="500"><tr><td>';
print &add_review_page_html;
print '</td></tr></table>';

#---------------------------------------------------------------------------------------------


PrintFooterHTML($homepath);

if ($connected) {
    $dbh->disconnect;
}

#---------------------------------------------------------------------------------------------

sub add_review_page_html {
return <<ADD_REVIEW_PAGE;
	<h1>Add a Review</h1>
	
	Unlike some systems (e.g. Amazon.com), The Assayer does not restrict users to reviewing
	books that are already in its database. Although a book can be added to the database without
	a review (<a href="help.html#authors">see guidelines</a>), in general the first user to review the
	book is expected to enter it into the database. To avoid creating duplicate book or author
	entries in the database, please read the following instructions carefully.<p>
	
	<ol>
	<li> First check if the book is already in the database using the
	<a href="http://www.theassayer.org/cgi-bin/asbrowsetitle.cgi">browse by title</a> page.
	If so, then you can add your own review by
	going to the book's page and clicking on the Add Review button. After that, you're done.
	
	<li> If the book is not currently in the database, click
	<a href="http://www.theassayer.org/cgi-bin/asreview1.cgi">here</a> to add the
	author, add the book, and then review it.
	</td></tr></table>
	
	</ol>
	
	
	
ADD_REVIEW_PAGE
}
