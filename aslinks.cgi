#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asdbutil.pl";
require "asgetmethod.pl";
require "asinstallation.pl";
require "asuinfo.pl";
require "aslog.pl";

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
print &links_page_html;
print '</td></tr></table>';

#---------------------------------------------------------------------------------------------


PrintFooterHTML($homepath);

if ($connected) {
    $dbh->disconnect;
}

#---------------------------------------------------------------------------------------------

sub links_page_html {
return <<LINKSPAGE;
	<h1>The Assayer: Links</h1>
	
        <h2>General Links Relating to Free Books</h2>
	<ul>
    <li> <a href="http://commoncontent.org/">commoncontent.org</a> - licenses, and a directory of open-content
			works
		<li> <a href="http://www.gnu.org/">Gnu.org</a> - creators of the GFDL license for free books
		<li> <a href="http://www.ipl.org/">Internet Public Library</a>
		<li> <a href="http://www.gutenberg.org/">Project Gutenberg</a>
		<li> <a href="http://www.ibiblio.org/">ibiblio</a> - an archive of free information
		<li> <a href="http://digital.library.upenn.edu/books/">On-Line Books Page</a>
			and <a href="http://digital.library.upenn.edu/books/bplist/index.html">Book People mailing list</a>
			- has an emphasis on old books that have fallen into the public domain
		<li> <a href="http://www.samizdat.com/readers.html">Samizdat.com</a> hosts a bunch of free books, plus lots of good articles and links
		<li> <a href="http://abu.cnam.fr/">Association des Bibliophiles Universels</a> - hosts PD texts in French
	</ul>	

	<h2>Publishers Who Do Free Books</h2>
	Print publishers who make all of their books available for free in digital form:
	<ul>
                <li> 	<a href="http://greenteapress.com/">Green Tea Press</a> - computer science textbooks
                <li> 	<a href="http://www.lightandmatter.com/">Light and Matter</a> - science textbooks (my own operation)
	</ul>
        Print publishers who make some of their books available for free in digital form:
        <ul>
                <li> <a href="http://baen.com">Baen Books</a> - science fiction (see their <a href="http://baen.com/library/">Baen 
                          Free Library</a>)
                <li> <a href="http://newriders.com">New Riders</a> - computer books (GNU Autoconf, Automake, and Libtool)
                <li> <a href="http://oreilly.com">O'Reilly</a> - computer books (see their <a href="http://www.oreilly.com/openbook">
                              Open Books Project</a>)
                <li> <a href="http://www.nostarch.com/plg.htm">No Starch Press</a> - computer books (Programming Linux Games,...)
                <li> <a href="http://aw.com">Addison Wesley</a> - publishes Programming Ruby
        </ul>

	</td></tr></table>
	
LINKSPAGE
}
