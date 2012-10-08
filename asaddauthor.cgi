#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################
# bug: when setting defaults of score menus, doesn't handle values
# that aren't integers

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asdbutil.pl";
require "aslog.pl";
require "asinstallation.pl";
require "asgetmethod.pl";

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

$last = $co->param('last');
$first = $co->param('first');
$suffix = $co->param('suffix');

$last =~ s/<//; #strip html
$first =~ s/<//; #strip html
$suffix =~ s/<//; #strip html


$pagetitle = "Adding an Author";
PrintHeaderHTML($homepath,$pagetitle);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

print "<h1>$pagetitle</h1>\n";
print "<b>Warning -- read this:</b> You should not normally need to use this page. The normal way to"
	. " add authors is at the start of the process of putting a new book in the database. The only reason"
	. " this page exists is to handle situations where a book with multiple authors was entered without"
	. " all the authors. Be sure to read the entire help page before messing with this. It's probably a better"
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
	
###################################################
## Form 
###################################################
if (!$bogus) {
	if (!$debug) {
	  print  $co->startform(-method=>'POST',
	    		-action=>"$cgi_full_path/asaddauthor.cgi") . "\n";
	}
	else {
	  print  $co->startform(-method=>'POST',
	    		-action=>"$cgi_full_path/asaddauthor.cgi?debug=true") . "\n";
	}
	
	print "<table>\n";
	
	print "<tr><td>last:</td><td>" 
		. $co->textfield(-name=>'last',-value=>$last,-size=>70,-maxlength=>70) ."</td></tr>\n";
	print "<tr><td>first:</td><td>" 
		. $co->textfield(-name=>'first',-value=>$first,-size=>70,-maxlength=>70) ."</td></tr>\n";
	print "<tr><td>suffix:</td><td>" 
		. $co->textfield(-name=>'suffix',-value=>$suffix,-size=>70,-maxlength=>70) ."</td></tr>\n";
	print "</table>\n";	


						
	print	$co->submit(-name=>'submit',-value=>'Submit');
	
	print	$co->endform;
}
	if (!$bogus && $last ne "" && $user_id) {
		#########################################################
		###### Add author record
		#########################################################
			      $ql = $dbh->quote($last);
			      $qf = $dbh->quote($first);
			      $qs = $dbh->quote($suffix);
				  $insertstmt = "INSERT INTO au_tbl (
				    last_name,
				    first_and_middle_names,
				    suffix,
				    created_by_user_id,
				    date_created
				  )
				  VALUES (
				    $ql,
				    $qf,
				    $qs,
				    \'$user_id\',
				    NOW()
				  )";
				  $sth = $dbh->prepare($insertstmt) or $bogus="Internal error (2).";
				  if (! $bogus) {
				    if (!$debug) {
				      $sth->execute() or $bogus="Error writing to database (2).";
				    }
				    else {
				      print "SQL: $insertstmt<p>\n";
				    }
				  }
				  if (! $bogus) {
					  $insertstmt = "INSERT INTO auref_tbl (
					    au_id,
					    created_by_user_id,
					    date_created
					  )
					  VALUES (
					    LAST_INSERT_ID(),
					    \'$user_id\',
					    NOW()
					  )";
					  $sth = $dbh->prepare($insertstmt) or $bogus="Internal error (3).";
				  }
				  if (! $bogus) {
				    if (! $debug) {
				      $sth->execute() or $bogus="Error writing to database (3).";
				    }
				    else {
				      print "SQL: $insertstmt<p>\n";
				    }
				  }
				  if (! $bogus) {
				    $selectstmt = "SELECT auref_id FROM auref_tbl WHERE auref_id LIKE LAST_INSERT_ID()";
				    $sth = $dbh->prepare($selectstmt) or $bogus="Internal error.";
				  }
				  if (! $bogus) {
				    $sth->execute() or $bogus="Error updating database (4).";
				  }
				  if (! $bogus) {
				    @row = $sth->fetchrow_array();
				    if (! @row) {
				      $bogus = "Error reading database (4).";
				    }
				    else {
				      $auref = $row[0];
				      $inserted_author = 1;
				      print "auref=$auref<p>\n";
                      if (!$debug) {make_log_entry($dbh,$user_id,"addaubyhand",0,0,$auref,0,0,0,"");}
				    }
				 }

	}
	
	if ($bogus) {
	  print "Error: $bogus<p>\n";
	}
	
	


&PrintFooterHTML($homepath);


if ($connected) {
  if (ref $sth) {$sth->finish}
  $dbh->disconnect;
}

