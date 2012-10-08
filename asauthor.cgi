#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asdbutil.pl";

require "asinstallation.pl";

PrintHTTPHeader();

use CGI;
use DBI;

$co = new CGI;

$bogus = 0;
$connected = 0;

	$did_header_and_banner = 0;



$my_query_string = $ENV{'QUERY_STRING'};

@query_key_pairs = split(/&/, $my_query_string);

if (! @query_key_pairs) {
  $bogus = "No GET method parameters given.";
}

# There's supposed be something called %in that cgi-lib makes for me,
# but it doesn't seem to work, so I reinvent the wheel:
%query_hash = ();
if (! $bogus) {
  foreach $par (@query_key_pairs) {
    @par_parts = split(/=/, $par);
    $query_hash{$par_parts[0]} = $par_parts[1];
  }
}

#print "--- query hash = @{[%query_hash]}<p>\n";
if (exists($query_hash{"author"})) {
  $auref_id = $query_hash{"author"};
}
else {
  $auref_id = 0;
  $bogus = "GET method book parameter not given.";
}
#print "--- bkref_id = $auref_id<p>\n";

if ($auref_id =~ m/[^0-9]/) {$bogus = "Author number contains illegal characters.";}


if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}

###################################################
## Get raw au_id.
###################################################
if (! $bogus) {
  $selectstmt = "SELECT au_id FROM auref_tbl WHERE auref_id LIKE '$auref_id'";
  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error (1)";
}
if (! $bogus) {
  $sth->execute() or $bogus="Error reading database (1)";
}
if (! $bogus) {
  @row = $sth->fetchrow_array();
  if (! @row) {
    $bogus = "Error reading database (2)";
  }
  else {
    $au_id = $row[0];
  }
}
 


###################################################
## Get author's name.
###################################################
if (! $bogus) {
  $selectstmt = "SELECT last_name, first_and_middle_names,suffix FROM au_tbl WHERE au_id LIKE '$au_id'";
  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error (3)";
}
if (! $bogus) {
  $sth->execute() or $bogus="Error reading database (3)";
}
if (! $bogus) {
  @row = $sth->fetchrow_array();
  if (! @row) {
    $bogus = "Error reading database (4)";
  }
  else {
    $this_last = $row[0];
    $this_first = $row[1];
    $this_suffix = $row[2];
  }
}

if (! $bogus) {

	$full_name = "$this_first $this_last ";
	if ((length $this_suffix)>0) {$full_name = $full_name . " $this_suffix";};
   
	$title = "The Assayer: $full_name";
	PrintHeaderHTML($homepath,$title);
	PrintBannerHTML($homepath);
	print toolbar_HTML($homepath);
	$did_header_and_banner = 1;
	print "<h1>$full_name</h1>\n";
	#print "author id #$auref_id<br>\n";
	  
	
	###################################################
	## Button to review a new book by this author.
	###################################################
	print 
	$co->startform(
		-method=>'POST',
		-action=>"$cgi_full_path/asreview2.cgi");
	
	print  	$co->hidden(-name=>'auref1',-default=>"$auref_id",-override=>1);

	print  	$co->hidden(-name=>'last1',-default=>"$this_last",-override=>1);
	print  	$co->hidden(-name=>'first1',-default=>"$this_first",-override=>1);
	print  	$co->hidden(-name=>'suffix1',-default=>"$this_suffix",-override=>1);
	print  	$co->hidden(-name=>'what',-default=>"3",-override=>1);
	print  	$co->hidden(-name=>'n',-default=>"1",-override=>1);
	
	#print "bkref_id = $bkref_id<br>";
	print	"Click on this button to review a book by this author that is not yet in the database: "
	   . $co->submit(-name=>'Add Book') . "<p>\n";
	
			
	print	$co->endform;
	
	###################################################
	## List books by this author.
	###################################################
	
	if (1) {
	    print "<h2>Books in the database by this author</h2>\n";
		if (! $bogus) {
		  @au_refs = all_au_refs($au_id,$dbh,\$err_ref);
		  if ($err_ref) {$bogus = 1;}
		  $au_refs_sql_clause = make_au_refs_sql_clause(\@au_refs);
		  #print "--- $au_refs_sql_clause ---<p>\n";
		}
		if (! $bogus) {
		  $selectstmt = "SELECT bk_id,title FROM bk_tbl WHERE $au_refs_sql_clause";
		  #print "---2 $selectstmt ---<p>\n";
		  $sth = $dbh->prepare($selectstmt) or $bogus="Internal error (5)";
		}
		if (! $bogus) {
		  $sth->execute() or $bogus="Error reading database (5)";
		}
		if (! $bogus) {
		  while (@row = $sth->fetchrow_array()) {
		    $bk_id = $row[0];
		    $this_title = $row[1];

		    $selectstmt2 = "SELECT bkref_id FROM bkref_tbl WHERE bk_id LIKE '$bk_id'";
		    $err2 = 0;
		    $sth2 = $dbh->prepare($selectstmt2) or $err2=1;
		    if (! $err2) {
		      $sth2->execute() or $err2=2;
		    }
		    if (! $err2) {
		      @row2 = $sth2->fetchrow_array();
		    }
		    if (@row2) {
		      $bkref_id = $row2[0];
		      print "<a href=\"asbook.cgi?book=$bkref_id\">$this_title</a>";
  			  $bk_id = bk_ref_to_raw_id($bkref_id,$dbh);
	  		  print freedom_img_tag($homepath,get_book_info($dbh,$bk_id,"freedom"));
		  	  print count_reviews_html($dbh,$bkref_id);
			    print "<br/>\n";
		    }
		    else {
		      #print "---zugwug<p>\n";
		      print "Internal error: book $bk_id not found, $selectstmt2<p>\n";
		    }
		    if ($err2) {print "err2=$err2<p>\n";}

		  }
		}
	}

}	


if ($bogus) {
    if (! 	$did_header_and_banner ) {
	$title = "The Assayer: Error Viewing Author Record";
	PrintHeaderHTML($homepath,$title);
	PrintBannerHTML($homepath);
	print toolbar_HTML($homepath);
	}
	print "<h1>Error</h1>\n";
	print "$bogus<p>\n ";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  if (ref $sth2) {$sth2->finish}
  $dbh->disconnect;
}

PrintFooterHTML($homepath);


