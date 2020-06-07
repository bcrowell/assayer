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
require "./asloc.pl";
require "./asfreedom.pl";
require "./asinstallation.pl";
require "./asgetmethod.pl";

PrintHTTPHeader();


use CGI;
use DBI;

$co = new CGI;

$debug = 0;
$describe_changes = "";
$did_header_stuff = 0;
$bogus = 0;
$auref_log = 0;

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}


%query_hash = decode_query_hash();
if (exists($query_hash{"book"})) {
  $bkref_id = $query_hash{"book"};
}
else {
  $bkref_id = 0;
  $bogus = "GET method book parameter not given.";
}


$new_book_title = $co->param('title');
$new_auref0 = $co->param('auref0');
$new_auref1 = $co->param('auref1');
$new_auref2 = $co->param('auref2');
$new_auref3 = $co->param('auref3');
$new_auref4 = $co->param('auref4');

$new_url = $co->param('url');
$new_lcc_class = $co->param('lcc_class');
$new_lcc_subclass = $co->param('lcc_subclass');
$new_subsubclass = $co->param('subsubclass');
$new_freedom = $co->param('freedom');

if (! $bogus) {
	if ($login = seems_loggedIn($co)) {
	}
	else {
	  $bogus = "Only logged-in users can edit book data.";
	}
}

if (!$bogus) {
    $do_what = $co->param('submit');

	if ((length $do_what)==0) {
	  $do_what = 1; # view
	  $pagetitle = "Editing book: ";
	}
	else {
	  $do_what = 2; # modify
	  $pagetitle = "Writing to Database: ";
	}
}

###################################################
## Get info about the book (first time)
###################################################
if (!$bogus) {
	$bk_id = bk_ref_to_raw_id($bkref_id,$dbh);
	if (!$bk_id) {$bogus="Error reading database (1)";}
	$book_title = get_title($bk_id,$dbh);
	if (!$book_title) {$bogus="Error reading database (2)";}
	@auref_id_array = get_aurefs($bk_id,$dbh);
	if (!@auref_id_array) {
    #$bogus="Error reading database (3)";
    @auref_id_array = ();
  }
	$auref0 = $auref_id_array[0];
	$auref1 = $auref_id_array[1];
	$auref2 = $auref_id_array[2];
	$auref3 = $auref_id_array[3];
	$auref4 = $auref_id_array[4];
	$url = get_book_info($dbh,$bk_id,"url");
	$lcc_class = get_book_info($dbh,$bk_id,"lcc_class");
	$lcc_subclass = get_book_info($dbh,$bk_id,"lcc_subclass");
	$subsubclass = get_book_info($dbh,$bk_id,"subsubclass");
	$freedom = get_book_info($dbh,$bk_id,"freedom");
	if ($freedom ne "") {$default_freedom=$freedom;}else{$default_freedom="1";}
}

###################################################
## Update database.
###################################################
if ($bk_id =~ m/[^0-9]/) {$bogus = "Book number contains illegal characters.";}
if ($do_what==2 && ($new_url ne '' && !($new_url =~ m@^(http|https|ftp)://@))) {$bogus = "Invalid URL."}
if ($do_what==2 && !$bogus) {
  if ($new_book_title ne $book_title) {
    $describe_changes = $describe_changes . "Changed title from $book_title to $new_book_title.";
    $tq = $dbh->quote($new_book_title);
    $stmt = "UPDATE bk_tbl SET title = $tq WHERE bk_id = '$bk_id'";
    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
    $sth->execute() or $bogus="Error writing to database, execute $stmt";
  }
  if ($new_freedom ne $freedom) {
    if ($new_freedom =~ m/[^0-9]/) {$bogus = "Freedom contains illegal characters.";}
    if (!$bogus) {
	    $describe_changes = $describe_changes . "Changed freedom from $freedom to $new_freedom.";
	    $stmt = "UPDATE bk_tbl SET freedom = '$new_freedom' WHERE bk_id = '$bk_id'";
	    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
	    $sth->execute() or $bogus="Error writing to database, execute $stmt";
    }
  }
  if ($new_url ne $url) {
    $describe_changes = $describe_changes . "Changed url from $url to $new_url.";
    $q = $dbh->quote($new_url);
    $stmt = "UPDATE bk_tbl SET url = $q WHERE bk_id = '$bk_id'";
    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
    $sth->execute() or $bogus="Error writing to database, execute $stmt";
  }
  if ($new_lcc_class ne $lcc_class) {
    if ($new_lcc_class =~ m/[^a-zA-Z]/) {$bogus = "new_lcc_class contains illegal characters.";}
    if (!$bogus) {
	    $describe_changes = $describe_changes . "Changed lcc_class from $lcc_class to $new_lcc_class.";
	    $stmt = "UPDATE bk_tbl SET lcc_class = '$new_lcc_class' WHERE bk_id = '$bk_id'";
	    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
	    $sth->execute() or $bogus="Error writing to database, execute $stmt";
    }
  }
  if ($new_lcc_subclass ne $lcc_subclass) {
    if ($new_lcc_subclass =~ m/[^a-zA-Z]/) {$bogus = "new_lcc_subclass contains illegal characters.";}
    if (!$bogus) {
	    $describe_changes = $describe_changes . "Changed lcc_subclass from $lcc_subclass to $new_lcc_subclass.";
	    $stmt = "UPDATE bk_tbl SET lcc_subclass = '$new_lcc_subclass' WHERE bk_id = '$bk_id'";
	    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
	    $sth->execute() or $bogus="Error writing to database, execute $stmt";
    }
  }
  if ($new_subsubclass ne $subsubclass) {
    if ($new_subsubclass =~ m/[^a-zA-Z]/) {$bogus = "new_subsubclass contains illegal characters.";}
    if (!$bogus) {
	    $describe_changes = $describe_changes . "Changed subsubclass from $subsubclass to $new_subsubclass.";
	    $stmt = "UPDATE bk_tbl SET subsubclass = '$new_subsubclass' WHERE bk_id = '$bk_id'";
	    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
	    $sth->execute() or $bogus="Error writing to database, execute $stmt";
    }
  }
  if (($new_auref0 =~ m/[^0-9]/) || ($new_auref1 =~ m/[^0-9]/) || ($new_auref2 =~ m/[^0-9]/) || 
  	($new_auref3 =~ m/[^0-9]/) || ($new_auref4 =~ m/[^0-9]/)) {$bogus = "Author number contains illegal characters.";}
  if ($new_auref0 ne $auref0 && !$bogus) {
    $describe_changes = $describe_changes . "Changed auref0 from $auref0 to $new_auref0.";
    $stmt = "UPDATE bk_tbl SET auref_id1 = '$new_auref0' WHERE bk_id = '$bk_id'";
    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
    $sth->execute() or $bogus="Error writing to database, execute $stmt";
  }
  if ($new_auref1 ne $auref1 && !$bogus) {
    $describe_changes = $describe_changes . "Changed auref1 from $auref1 to $new_auref1.";
    $stmt = "UPDATE bk_tbl SET auref_id2 = '$new_auref1' WHERE bk_id = '$bk_id'";
    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
    $sth->execute() or $bogus="Error writing to database, execute $stmt";
  }
  if ($new_auref2 ne $auref2 && !$bogus) {
    $describe_changes = $describe_changes . "Changed auref2 from $auref2 to $new_auref2.";
    $stmt = "UPDATE bk_tbl SET auref_id3 = '$new_auref2' WHERE bk_id = '$bk_id'";
    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
    $sth->execute() or $bogus="Error writing to database, execute $stmt";
  }
  if ($new_auref3 ne $auref3 && !$bogus) {
    $describe_changes = $describe_changes . "Changed auref3 from $auref3 to $new_auref3.";
    $stmt = "UPDATE bk_tbl SET auref_id4 = '$new_auref3' WHERE bk_id = '$bk_id'";
    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
    $sth->execute() or $bogus="Error writing to database, execute $stmt";
  }
  if ($new_auref4 ne $auref4 && !$bogus) {
    $describe_changes = $describe_changes . "Changed auref4 from $auref4 to $new_auref4.";
    $stmt = "UPDATE bk_tbl SET auref_id5 = '$new_auref4' WHERE bk_id = '$bk_id'";
    $sth = $dbh->prepare($stmt) or $bogus="Error writing to database, prepare $stmt";
    $sth->execute() or $bogus="Error writing to database, execute $stmt";
  }
  if (0) {
	print "@@@ $new_book_title<p>\n";
	print "@@@ $new_auref0<p>\n";
	print "@@@ $new_auref1<p>\n";
	print "@@@ $new_auref2<p>\n";
	print "@@@ $new_auref3<p>\n";
	print "@@@ $new_auref4<p>\n";
	
	print "@@@ $new_url<p>\n";
	print "@@@ $new_freedom<p>\n";
  }
  
}

###################################################
## Get info about the book (second time, after updating)
###################################################
if (!$bogus) {
	$bk_id = bk_ref_to_raw_id($bkref_id,$dbh);
	if (!$bk_id) {$bogus="Error reading database (1)";}
	$book_title = get_title($bk_id,$dbh);
	if (!$book_title) {$bogus="Error reading database (2)";}
	@auref_id_array = get_aurefs($bk_id,$dbh);
	if (!@auref_id_array) {
		@auref_id_array = ();
    #$bogus="Error reading database (3)"
  }
	$url = get_book_info($dbh,$bk_id,"url");
	$lcc_class = get_book_info($dbh,$bk_id,"lcc_class");
	$lcc_subclass = get_book_info($dbh,$bk_id,"lcc_subclass");
	$subsubclass = get_book_info($dbh,$bk_id,"subsubclass");
	$freedom = get_book_info($dbh,$bk_id,"freedom");
	if ($freedom ne "") {$default_freedom=$freedom;}else{$default_freedom="1";}
}


###################################################
## Print info about the book.
###################################################
if (!$bogus) {
	  $pagetitle = $pagetitle . $book_title;
	  PrintHeaderHTML($homepath,$pagetitle);
	  PrintBannerHTML($homepath);
	  print toolbar_HTML($homepath);
	  print "User $login logged in.<p>\n";
	  print "<b>Important -- read this!</b> "
	  	. "Although I've set this up so that any logged-in user can edit a book's information, "
	  	. "most users probably don't know enough to fiddle with this stuff. If in doubt, read the "
	  	. "<a href=\"".help_link($homepath)."\">help page</a>. You're safest just "
	  	. "e-mailing me to request a change rather than doing it yourself. Currently the only "
	  	. "security feature is that you must be logged in to use this page, and all changes are "
	  	. "logged in the <a href=\"asviewlog.cgi?n=10\">public log file</a>.<p>\n";
	  print "You can only put in preexisting author id numbers in this form. To create a new author by hand "
	  . "use <a href=\"asaddauthor.cgi\" target=\"window\">this page</a>.<p>";
	  print "To redirect an author ref., use <a href=\"asredirectau.cgi\" target=\"window\">this page</a>.<p>";
	  $did_header_stuff = 1;
	  print "<h1>$pagetitle</h1>\n";
      print "<a href=\"asbook.cgi?book=$bkref_id\">$book_title</a> / \n";
	  @auref_id_array = get_aurefs($bk_id,$dbh);
	  $very_first_one = 1;
	  foreach $auref_id(@auref_id_array) {
	        if ($very_first_one && !$auref_log) {
	          $auref_log = $auref_id;
	        }
		    my $au_id = au_ref_to_raw_id($auref_id,$dbh);
			#if ($au_id < 0) {$err=$au_id;} else {$err=0;}
		    my ($last,$first,$suffix) = get_name($au_id,$dbh);
		    if (!$very_first_one) {print ", ";}
		    $very_first_one = 0;
			print "<a href=\"asauthor.cgi?author=$auref_id\">" . printable_author($first,$last,$suffix,0) 
				. "</a>";
	  }
	  print " (#$bkref_id)<br>\n";
}
###################################################
## Form for editing
###################################################
if (!$bogus) {
	print  $co->start_form(-method=>'POST',
	    		-action=>"$cgi_full_path/aseditbook.cgi?book=$bkref_id") . "\n";

	print "<table>\n";
	
	print "<tr><td>title:</td><td colspan=\"2\">"
		. $co->textfield(-name=>'title',-value=>$book_title,-size=>70,-maxlength=>140) ."</td></tr>\n";

    for ($k=0; $k<=4; $k++) {
	    ($last,$first,$suffix) = ("","","");
	    $au_id = 0;
        $auref = $auref_id_array[$k];
	    $ak = "auref$k";
        if ($auref ne "" && $auref) {
	      $au_id = au_ref_to_raw_id($auref,$dbh);
	      ($last,$first,$suffix) = get_name($au_id,$dbh);
		  print "<tr><td>author$k</td>"
		    . "<td>" . $co->textfield(-name=>$ak,-value=>$auref,-size=>10,-maxlength=>10) ."</td>\n"
		    . "<td>$last, $first $suffix</td></tr>\n";
	    }
	    else {
		  print "<tr><td>author$k</td>"
		    . "<td>" . $co->textfield(-name=>$ak,-value=>"",-size=>10,-maxlength=>10) ."</td>\n"
		    . "</tr>\n";
	    }
    }

	print "<tr><td>URL:</td><td colspan=\"3\">" 
		. $co->textfield(-name=>'url',-value=>$url,-size=>70,-maxlength=>140) ."</td></tr>\n";
	print "<tr><td>LCC class:</td><td colspan=\"2\">" 
		. $co->textfield(-name=>'lcc_class',-value=>$lcc_class,-size=>70,-maxlength=>70) ."</td></tr>\n";
	print "<tr><td>LCC subclass:</td><td colspan=\"2\">" 
		. $co->textfield(-name=>'lcc_subclass',-value=>$lcc_subclass,-size=>70,-maxlength=>70) ."</td></tr>\n";
	print "<tr><td>subsubclass:</td><td colspan=\"2\">" 
		. $co->textfield(-name=>'subsubclass',-value=>$subsubclass,-size=>70,-maxlength=>70) ."</td></tr>\n";

  my @subsubs = ();
  foreach my $subsub(sort keys %subsubclass) {
    if ($subsub =~ m/$lcc_class$lcc_subclass/) {
      push @subsubs,$subsub;
    }
  }
  if (@subsubs) {
    print "<tr><td>possible subsubclasses:<br/>";
    foreach my $subsub(@subsubs) {
      my $stripped = $subsub;
      $stripped =~ s/^$lcc_class$lcc_subclass//; # strip off initial two LOC letters
      print "$stripped - $subsubclass{$subsub}<br/>\n";
    }
    print "</td></tr>\n";
  }

	print "<tr><td>Freedom:</td><td colspan=\"3\">" 
		. $co->popup_menu(
		  -name=>"freedom",
		  -values=>['0','1','2','3','4','5'],
		  -default=>$default_freedom,
		  -labels=>\%describe_freedom
		) . "</td></tr>\n";

	print "</table>\n";	


						
	print	$co->submit(-name=>'submit',-value=>'Submit');
	
	print	$co->end_form;
}

if ($bogus && !$did_header_stuff) {
	  PrintHeaderHTML($homepath,"Error");
	  PrintBannerHTML($homepath);
	  print toolbar_HTML($homepath);
}
if ($bogus) {
	  print "Error: $bogus<p>\n";
}

&PrintFooterHTML($homepath);

if (!$bogus && $connected && $describe_changes ne "") {
  make_log_entry($dbh,user_login_to_id($login,$dbh),"editbook",$bkref_id,0,$auref_log,0,0,0,$describe_changes);
}

if ($connected) {
  $dbh->disconnect;
}

