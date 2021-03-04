#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asdbutil.pl";
require "./asinstallation.pl";
require "./asgetmethod.pl";
require "./asfreedom.pl";

PrintHTTPHeader();

$title = "The Assayer: Browse by Title";

use CGI;
use DBI;


$co = new CGI;

%query_hash = decode_query_hash();
$search = $co->param('search');
if (exists($query_hash{"search"})) {
  $search = $query_hash{"search"};
}

$do_it = ($search ne "") || ($co->param('submit') ne "") || (exists($query_hash{"search"}));




$minfree = 1;
%query_hash = decode_query_hash();
if (exists($query_hash{"minfree"})) {
  $minfree = $query_hash{"minfree"};
}
if ($co->param('minfree') ne "") {
  $minfree = $co->param('minfree');
}
if ($minfree =~ m/[^0-9 ]/) {$bogus = "Minfree contains illegal characters.";}


if (exists($query_hash{"countrev"})) {
  if ($query_hash{"countrev"} eq "false") {
    $countrev = 0;
  }
  else {
    $countrev = 1;
  }
}
else {
  $countrev = 1;
}
if ($minfree =~ m/[^0-9 ]/) {$bogus = "Countrev contains illegal characters.";}


PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$bogus = 0;
$connected = 0;

$count_em = 0;

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
	print "<h1>The Assayer: Browse by Title</h1>\n";
	
	if ($login = seems_loggedIn($co)) {
	  print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$login) . " logged in.";
	}
	else {
	  print "Not logged in.";
	}
	print "<br>\n";
  }

	print  $co->start_form(-method=>'POST',-action=>"$cgi_full_path/asbrowsetitle.cgi") . "\n";
	
	print "<table><tr><td bgcolor=\"#dddddd\">Title</td>"
	   .  "<td>" . $co->textfield(-name=>'search',-value=>$search,-size=>20,-maxlength=>30) . "</td>"
		. "<td>Enter the beginning of the title, or leave this space blank to view the<br>"
	   . "entire list of books. Omit the words 'a' or 'the' if the title begins with them.</td></tr>\n"
	   .  "<tr><td bgcolor=\"#dddddd\">Minimum <a href=\"".help_link($homepath,"free")."\">freedom level</a></td>"
	   .  "<td colspan=\"2\">" . $co->popup_menu(
		  -name=>'minfree',
		  -values=>['0','1','2','3','4','5'],
		  -default=>$minfree,
		  -labels=>\%describe_freedom
		) . "</td></tr></table>\n"
	.	$co->submit(-name=>'submit',-value=>'Submit')
	.	$co->end_form;

if ($do_it) {
	if (! $bogus) {
	  $selectstmt = "SELECT title,bk_id,freedom,url FROM bk_tbl WHERE title LIKE "
	  	. $dbh->quote($search . "%") . " AND freedom >= '$minfree' ORDER BY title";
	  $sth = $dbh->prepare($selectstmt) or $bogus=4;
	}
	if (! $bogus) {
	  $sth->execute() or $bogus=5;
	}
	if (! $bogus) {
	  print "<h2>Search Results</h2>\n";
	  print explain_icons($homepath);
	  while (@row = $sth->fetchrow_array()) {
	    ($this_title,$bk_id,$freedom,$url) = @row;
	    $selectstmt2 = "SELECT bkref_id FROM bkref_tbl WHERE bk_id LIKE '$bk_id'";
	    $err = 0;
	    $sth2 = $dbh->prepare($selectstmt2) or $err=1;
	    if (! $err) {
	      $sth2->execute() or $err=2;
	    }
	    if (! $err) {
	      @row = $sth2->fetchrow_array();
	    }
	    if (@row && $this_title ne '') {
	      $bkref_id = $row[0];
	      my $very_first_author = 1;
	      print "<a href=\"asbook.cgi?book=$bkref_id\">$this_title</a> / \n";
		  @auref_id_array = get_aurefs($bk_id,$dbh);
		  foreach $auref_id(@auref_id_array) {
			    my $au_id = au_ref_to_raw_id($auref_id,$dbh);
				#if ($au_id < 0) {$err=$au_id;} else {$err=0;}
			    my ($last,$first,$suffix) = get_name($au_id,$dbh);
			    if (! $very_first_author) {print ", ";}
			    $very_first_author = 0;
				print "<a href=\"asauthor.cgi?author=$auref_id\">" . printable_author($first,$last,$suffix,0) . "</a>";
		  }
			print  freedom_img_tag_with_link($homepath,$freedom,$url);
		  if ($countrev) { print count_reviews_html($dbh,$bkref_id); }
		  print "<br>\n";
		  ++$count_em;
	    }
	  }
	  print "<p>$count_em books found<p>\n";
	}
}
if ($bogus) {
	print "Sorry, error $bogus occurred.<p>\n ";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  if (ref $sth2) {$sth2->finish}
  $dbh->disconnect;
}

PrintFooterHTML($homepath);


