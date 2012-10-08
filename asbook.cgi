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
require "asgetmethod.pl";
require "asnotifyutil.pl";
require "asfreedom.pl";
require "aslog.pl";
require "asloc.pl";

PrintHTTPHeader();

use CGI;
use DBI;


$co = new CGI;

$bogus = 0;
$connected = 0;


$debug = 0;

%query_hash = decode_query_hash();
if (exists($query_hash{"book"})) {
  $bkref_id = $query_hash{"book"};
}
else {
  $bkref_id = 0;
  $bogus = "GET method book parameter not given.";
}

if (!($bkref_id =~ m/\-?\d+/)) {$bogus = "Book number contains illegal characters.";}

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}

$reader_id = loggedIn_user_id($co,$dbh,\$err_zz);
if (!$bogus) {
	$bk_id = bk_ref_to_raw_id($bkref_id,$dbh);
}

###################################################
## Broken link reports
###################################################
if (!$bogus) {
  $text_about_url_ok = "";
  if ($co->param('broken') ne "") {$text_about_url_ok = report_url_ok($dbh,$reader_id,$bkref_id,$bk_id,0);}
  if ($co->param('not broken') ne "") {$text_about_url_ok = report_url_ok($dbh,$reader_id,$bkref_id,$bk_id,1);}
}


###################################################
## Get info about the book.
###################################################
if (!$bogus) {
	$bk_id = bk_ref_to_raw_id($bkref_id,$dbh);
	if (!$bk_id) {$bogus="Error reading database (1)";}
	$book_title = get_title($bk_id,$dbh);
	if (!$book_title) {$bogus="Error reading database (2)";}
	@auref_id_array = get_aurefs($bk_id,$dbh);
	#if (!@auref_id_array) {$bogus="Error reading database (3)";}
	$url = get_book_info($dbh,$bk_id,"url");
	$lccclass = get_book_info($dbh,$bk_id,"lcc_class");
	$lccsubclass = get_book_info($dbh,$bk_id,"lcc_subclass");
	$subsubclass = get_book_info($dbh,$bk_id,"subsubclass");
	$freedom = get_book_info($dbh,$bk_id,"freedom");
	$url_ok = get_book_info($dbh,$bk_id,"url_ok");
	$url_ok_user_id = get_book_info($dbh,$bk_id,"url_ok_user_id");
	$url_ok_date = get_book_info($dbh,$bk_id,"url_ok_date");
}

###################################################
## Make a time-ordered list of all reviewers who have reviewed this
## book (not just replied to a review). A reviewer may have done more
## than one revision.
###################################################
$already_reviewed = 0;
if (!$bogus) {
	$this_bkref_id = $bkref_id;
	@reviewers_array = ();
	%reviewers_hash = ();
	$err = 0;
	
	@bk_refs = all_bk_refs($bk_id,$dbh,\$err_ref);
	if ($err_ref) {$err = 1;}
	$bk_refs_sql_clause = make_bk_refs_sql_clause(\@bk_refs);
	#print "--- $bk_refs_sql_clause --- <p>\n";
	if (! $err) {
	  $selectstmt = "SELECT user_id FROM review_tbl WHERE ($bk_refs_sql_clause) AND ((parent_review_id IS NULL) OR (parent_review_id < '1')) ORDER BY review_id";
			#...make this an OR condition when implementing many-to-one refs
	  $sth = $dbh->prepare($selectstmt) or $err=4;
	}
	if (! $err) {
	  $sth->execute() or $err=5;
	}
	if (! $err) {
	  while (@row = $sth->fetchrow_array()) {
	    if (!exists ($reviewers_hash{$row[0]})) {
	      $reviewers_hash{$row[0]} = 1;
	      push @reviewers_array,$row[0];
	      if ($reader_id==$row[0]) {$already_reviewed = 1;}
	    }
	  }
	}
}


###################################################
## Print stuff.
###################################################
if (! $bogus) {
   
	$title = "The Assayer: $book_title";
	PrintHeaderHTML($homepath,$title);
	PrintBannerHTML($homepath);
	print toolbar_HTML($homepath);
	print "<h1>$book_title</h1>\n";
	
	print $text_about_url_ok;

	print "<table width=\"$default_screen_width\"><tr><td bgcolor=\"#dddddd\">";
	if ($#auref_id_array==0) {print "Author";} else {print "Authors";}
	print "</td><td width=\"250\" >";
	$first_author = 1;
	foreach $auref_id(@auref_id_array) {
	    $au_id = au_ref_to_raw_id($auref_id,$dbh);
		if ($au_id < 0) {$err=$au_id;} else {$err=0;}
	    ($last,$first,$suffix) = get_name($au_id,$dbh);
		if (! $first_author) {
		      print ", ";
		 }
		 else {
		      ($last1,$first1,$suffix1) = ($last,$first,$suffix);
		      $first_author = 0;
		 }
		 print "<a href=\"asauthor.cgi?author=$auref_id\">" . printable_author($first,$last,$suffix,0) . "</a>";
	}
	$auref1 = $auref_id_array[0];
	print "</td>\n";
	print "<td bgcolor=\"#dddddd\">Entered</td><td width=\"250\" >" . get_book_info($dbh,$bk_id,"date_created") . " by " 
		. user_id_to_hyperlinked_login_name($dbh,$cgi_full_path,get_book_info($dbh,$bk_id,"created_by_user_id"))
		. "\n";
	print "</td></tr>\n";
	print "<tr><td bgcolor=\"#dddddd\">Edit</td><td><a href=\"aseditbook.cgi?book=$bkref_id\">"
		. "edit data record</a></td>\n";
	print "<td bgcolor=\"#dddddd\">Freedom</td><td>";
	if ($freedom ne "") {
	  print $describe_freedom{$freedom}
	   . " <a href=\"".help_link($homepath,"freedomdisclaimer")."\">(disclaimer)</a>";
	}
	else {print "?";}
	print "</td></tr>\n";
        if ($lccclass ne '') {
	    print "<tr><td bgcolor=\"#dddddd\">Subject</td><td colspan=\"3\">";
	    print "<a href=\"asbrowsesubject.cgi?class=$lccclass\">$lccclass.$lccsubclass - ";
	    if ($lccsubclass eq '') {
        print $loc_class{$lccclass};
	    }
	    else {
        print $loc_subclass{$lccclass.$lccsubclass};
	    }
      if ($subsubclass ne '') {
        my $aaa = $lccclass.$lccsubclass.$subsubclass;
        if (exists $subsubclass{$aaa}) {
          print " ($subsubclass{$aaa})";
        }
      }
      print "</a>";
	    print "</td></tr>\n";
    }
	if ($url ne "" && $freedom>=2) {
	  print "<tr><td bgcolor=\"#dddddd\">Read</td><td colspan=\"3\">\n"
	  	. $co->startform(-method=>'POST',-action=>"$cgi_full_path/asbook.cgi?book=$bkref_id")
	  	. "<a href=\"$url\">$url</a>";
	  if ($url_ok eq "0" || $url_ok eq "1") {
	    print "<br>\nThis link was reported to be ";
	    if ($url_ok eq "0") {print "broken";} else {print "OK";}
	    print " by user " . user_id_to_hyperlinked_full_name($dbh,$url_ok_user_id,$cgi_full_path)
	       . " on " . $url_ok_date; 
	  }
	  if ($reader_id=="" || $reader_id=="0") {
	    print "<br>\nYou can't update this URL or report it OK or broken because you aren't logged in.";
	  }
	  else {
	    print "<br>\n"
	      . "<a href=\"aseditbook.cgi?book=$bkref_id\">update this link</a> | report it";
	    if ($url_ok ne "0") {
			print	" " . $co->submit(-name=>'broken',-value=>'broken');
	    }
	    if ($url_ok ne "1") {
			print	" " . $co->submit(-name=>'not broken',-value=>'not broken');
	    }
	    print	$co->endform;
	    print "</td></tr>";
	  }
	} 

	
	###################################################
	## Button to do another review of this book:
	###################################################
	print "<tr><td bgcolor=\"#dddddd\">Review</td><td colspan=\"3\">";
	if (!$already_reviewed && $reader_id) {
		print  review_button($co,$auref1,$bkref_id,$book_title,"",$last1,$first1,$suffix1);
	}
	if (!$reader_id) {
	  print "You can't add a review of this book right now because you're not logged in.";
	}
	print "</td></tr>\n";


	###################################################
	## E-mail notifications
	###################################################
	print "<tr><td bgcolor=\"#dddddd\">Notify</td><td colspan=\"3\">";
	if ($reader_id) {
		$deactivate = $co->param('Deactivate');
		$activate = $co->param('Activate');
		if ($deactivate ne "") {deactivate_notification($dbh,$reader_id,$bk_refs_sql_clause);}
		if ($activate ne "") {activate_notification($dbh,$reader_id,$bkref_id,$bk_refs_sql_clause);}
		$notify_sauce = notification_is_activated($dbh,$reader_id,$bk_refs_sql_clause);
		if ($notify_sauce) {
		    print $co->startform(-method=>'POST',-action=>"$cgi_full_path/asbook.cgi?book=$bkref_id");
			print "You are currently receiving e-mail notifications whenever this book is discussed.<br>";
			print "Press this button to deactivate notification for this book: ";
			print	$co->submit(-name=>'Deactivate',-value=>'Deactivate');
			print	$co->endform;
		}
		else {
		    print $co->startform(-method=>'POST',-action=>"$cgi_full_path/asbook.cgi?book=$bkref_id");
			print "Press this button to receive e-mail notifications whenever this book is discussed: ";
			print	$co->submit(-name=>'Activate',-value=>'Activate');
			print	$co->endform;
		}
	}
	print "</td></tr>\n";
	

	print "</table>";

	
	###################################################
	## Show reviews.
	###################################################
	$auref1 = $auref_id_array[0];
	foreach $reviewer_user_id (@reviewers_array) { # loop over reviewers
		$this_review_sql_clause = display_review($dbh,$homepath,$co,$reviewer_user_id,$bk_refs_sql_clause,
				0,$last1,$first1,$suffix1,$auref1,0,0,$titlebgcolor);
		if ($this_review_sql_clause) { # never false unless it's an error
		  @parent_stack = ($this_review_sql_clause);
		  $n_loops = 0;
		  while (@parent_stack && $n_loops<1000) { 
		    $this_review_sql_clause = display_review($dbh,$homepath,$co,0,$bk_refs_sql_clause,
				    $parent_stack[$#parent_stack],$last1,$first1,$suffix1,$auref1,$#parent_stack+1,1,
				    $titlebgcolor);
			#print "<p>---came back, $this_review_sql_clause<p>\n";
			if (!$this_review_sql_clause  || $depth>50) {
			  pop @parent_stack;
			}
		    else {
		      push @parent_stack,$this_review_sql_clause;
		    }
		    ++$n_loops;
		  }
		}
	}#end loop over reviewers
	if (scalar(@reviewers_array)==0) {
	  print "<h2>This book has not yet been reviewed.</h2><p>\n";
	}
}

if ($bogus) {
	$title = "The Assayer: Error Viewing Book Record";
	PrintHeaderHTML($homepath,$title);
	PrintBannerHTML($homepath);
	print "<h1>Error</h1>\n";
	print "$bogus<p>\n ";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  # Probably don't need to finish() sth_stack, since its elements have presumably been popped
  # off and garbage-collected.
  $dbh->disconnect;
}

PrintFooterHTML($homepath);

##########################################################################################
# Ugh-- design flaw: basically I can't support revisions of replies within my current
# database design. (Multiple replies are simply assumed to be separate replies.)
{
my @sth_stack = ();

sub display_review()
	# Returns 0 or sql clause for selecting any version of this review.
	{
		  my ($dbh,$homepath,$co,$reviewer_user_id,$bk_refs_sql_clause,$parent_sql,
		  		$last1,$first1,$suffix1,$auref1,$depth,$is_reply,$titlebgcolor) = @_;
		  my ($selectstmt,$err_zz,$latest_text,$latest_subj);
		  my $result = "";
		  my $found_any = 0;
		  my $reader_id = loggedIn_user_id($co,$dbh,\$err_zz);
		  my $debug = 0;
		  if (!$is_reply) {@sth_stack = ();}
		  if ($debug) {print "<br>--1-sth stack size=$#sth_stack, depth=$depth<br>\n";}
		  if ($#sth_stack<=$depth) { ###### create a new select
			  if (!$parent_sql) {
			    $selectstmt = "SELECT review_id,subject,review,score_content,score_writing,license,user_id,date FROM review_tbl WHERE ($bk_refs_sql_clause) AND user_id LIKE $reviewer_user_id AND ((parent_review_id IS NULL) OR (parent_review_id < '1')) ORDER BY review_id DESC";
			  }
			  else {
			    $selectstmt = "SELECT review_id,subject,review,score_content,score_writing,license,user_id,date FROM review_tbl WHERE ($bk_refs_sql_clause) AND $parent_sql ORDER BY review_id";
			  }
			  #print $selectstmt; 
			  my $sth = $dbh->prepare($selectstmt) or return 0;
			  $sth->execute() or return 0;
			  push @sth_stack,$sth;
		  }
		  if ($#sth_stack>$depth+1) { 
		    pop @sth_stack;
		  }
		  if ($debug) {print "<br>--2-sth stack size=$#sth_stack, depth=$depth<br>\n";}
		  my $rev_label = 0; # 0=latest, -1=second most recent, ...
		  REV_LOOP: while (@row = $sth_stack[$#sth_stack]->fetchrow_array()) { 
		  			#If this is a review, loop over a particular reviewer's revisions of a review.
		  			#If it's a reply, loop over all replies to a particular post.
		    $found_any = 1;
		    #my ($review_id,$subject,$review,$score_content,$score_writing,$license);
		    ($review_id,$subject,$review,$score_content,$score_writing,$license
		    		,$reviewer_user_id,$date) = @row;
		    	#...May overwrite $reviewer_user_id
		    if ($parent<0) {$parent=0;}
		    $score_content = $score_content / 10;
		    $score_writing = $score_writing / 10;
		    if ($is_reply || $rev_label == 0) {
		    	$result = "parent_review_id LIKE '$review_id'";
			    $latest_text = $review;
			    $latest_subj = $subject;
			    $reviewer_login = get_login_of_other_user($reviewer_user_id,$dbh);
			    if ($debug) {print "---review_id=$review_id<p>\n";}
			    print displayable_review($subject,$reviewer_login,$score_content,$score_writing,
						$review,$license,$is_reply,$homepath,$depth,$titlebgcolor,$date,$review_id,$dbh);
		    } # end if latest review
		    else { # not latest review
		      $result = $result . " OR parent_review_id LIKE '$review_id'";
		      if ($rev_label == -1) {
		        print "<br>This review has been revised. Earlier versions (viewing not yet implemented): ";
		      }
		      else {
		        print " ";
		      }
		      print $rev_label;
		      	# ...no link yet, because I haven't written the relevant cgi
		    } # end if not latest review
		    $rev_label = $rev_label - 1;
		    #if ($is_reply) {last REV_LOOP;}
		  }# end loop over a particular reviewer's revisions of a review
		  if ($found_any) {
		      if (!$reader_id) {
		      	print "<br>You cannot revise or reply to this post because you are not logged in.";
		      }
		      else {
				  if ($reviewer_user_id == $reader_id) {
				    # Viewing their own review. Give them the option of revising.
				    if (!$is_reply) { # I don't support revision of replies.
				      print revise_button($co,$auref1,$bkref_id,$book_title,"",$last1,$first1,$suffix1,
				    	$latest_subj,$latest_text,$license,$score_content,$score_writing);
				    }
				  } # end if own review
				  else { # someone else's review
				    print reply_button($co,$auref1,$bkref_id,$book_title,$review_id,$last1,$first1,$suffix1,
				    	$latest_subj,$license,$score_content,$score_writing);
				  }
			  }
			  print "<p>";
		  }

		  if ($result eq "") {
		    return 0;
		  }
		  else {
		    return "( " . $result . " )";
		  }
	}#end sub
}#end block
##########################################################################################

sub review_button()
{
	my ($co,$auref1,$bkref_id,$book_title,$parent_review,$last1,$first1,$suffix1) = @_;
	return  $co->startform( -method=>'POST', -action=>"$cgi_full_path/asreview3.cgi")
	. $co->hidden(-name=>'auref1',-default=>"$auref1",-override=>1)
	. 	$co->hidden(-name=>'bkref',-default=>"$bkref_id",-override=>1)
	. 	$co->hidden(-name=>'title',-default=>"$book_title",-override=>1)
	. 	$co->hidden(-name=>'parent_review',-default=>"",-override=>1)
	. 	$co->hidden(-name=>'last1',-default=>"$last1",-override=>1)
	. 	$co->hidden(-name=>'first1',-default=>"$first1",-override=>1)
	. 	$co->hidden(-name=>'suffix1',-default=>"$suffix1",-override=>1)
	. "Click on this button to add your own review of this book: "
	. $co->submit(-name=>'Add Review') . "<p>\n"
	. $co->endform;
}

##########################################################################################

sub revise_button()
{
	my ($co,$auref1,$bkref_id,$book_title,$parent_review,$last1,$first1,$suffix1,
    	$latest_subj,$latest_text,$license,$score_content,$score_writing
		) = @_;
    return  $co->startform(-method=>'POST', -action=>"$cgi_full_path/asreview3.cgi")
	.	"You can revise this review, but the earlier versions will still be in the "
	.   "database: " . $co->submit(-name=>'submit',-value=>'Revise')
	. 	$co->hidden(-name=>'last1',-default=>"$last1",-override=>1)
	. 	$co->hidden(-name=>'first1',-default=>"$first1",-override=>1)
	. 	$co->hidden(-name=>'suffix1',-default=>"$suffix1",-override=>1)
	. 	$co->hidden(-name=>'auref1',-default=>"$auref1",-override=>1)
	. 	$co->hidden(-name=>'title',-default=>"$book_title",-override=>1)
	. 	$co->hidden(-name=>'bkref',-default=>"$bkref_id",-override=>1)
	. 	$co->hidden(-name=>'parent_review',-default=>"",-override=>1)
	. 	$co->hidden(-name=>'subject',-default=>"$latest_subj",-override=>1)
	. 	$co->hidden(-name=>'review',-default=>"$latest_text",-override=>1)
	. 	$co->hidden(-name=>'license',-default=>"$license",-override=>1)
	. 	$co->hidden(-name=>'revising',-default=>"1",-override=>1)
	. 	$co->hidden(-name=>'content',-default=>"$score_content",-override=>1)
	. 	$co->hidden(-name=>'writing',-default=>"$score_writing",-override=>1)
	.   $co->endform;
}

##########################################################################################

sub reply_button()
	{
		my ($co,$auref1,$bkref_id,$book_title,$review_id,$last1,$first1,$suffix1,
		    	$latest_subj,$license,$score_content,$score_writing) = @_;
		return $co->startform(-method=>'POST', -action=>"$cgi_full_path/asreview3.cgi")
		. "Write a comment in reply to this review: " . $co->submit(-name=>'submit',-value=>'Reply')
		. 	$co->hidden(-name=>'last1',-default=>"$last1",-override=>1)
		. 	$co->hidden(-name=>'first1',-default=>"$first1",-override=>1)
		. 	$co->hidden(-name=>'suffix1',-default=>"$suffix1",-override=>1)
		. 	$co->hidden(-name=>'auref1',-default=>"$auref1",-override=>1)
		. 	$co->hidden(-name=>'title',-default=>"$book_title",-override=>1)
		. 	$co->hidden(-name=>'bkref',-default=>"$bkref_id",-override=>1)
		. 	$co->hidden(-name=>'parent_review',-default=>"$review_id",-override=>1)
		. 	$co->hidden(-name=>'subject',-default=>"Re: $latest_subj",-override=>1)
		. 	$co->hidden(-name=>'review',-default=>"",-override=>1)
		. 	$co->hidden(-name=>'license',-default=>"$license",-override=>1)
		. 	$co->hidden(-name=>'revising',-default=>"0",-override=>1)
		. 	$co->hidden(-name=>'content',-default=>"",-override=>1)
		. 	$co->hidden(-name=>'writing',-default=>"",-override=>1)
		. $co->endform;
	}

##########################################################################################

sub report_url_ok($$$$$)
{
	my ($dbh,$reader_id,$bkref_id,$bk_id,$ok) = @_;
    my $stmt = "UPDATE bk_tbl SET url_ok = '$ok', url_ok_user_id='$reader_id',url_ok_date=NOW() WHERE bk_id='$bk_id'";
    $sth = $dbh->prepare($stmt) or return "Error updating database";
    $sth->execute() or return "Error updating database";
    if (! $ok) {
      $description="broken";
      $saywhat = "Thank you for reporting this broken URL. Our staff of bibliographic leprechauns will try "
      . "to track down the correct URL. If this is a case where the author or publisher has stopped "
      . "allowing the book to be downloaded or read for free, please use the link below to edit information "
      . "about this book and set the book's freedom level to 1 and make its URL blank. If you know "
      . "a correct URL for this book, please feel free to go ahead and fix it.<p>";
    }
    else {
      $saywhat =  "Thank you for reporting that this URL is valid.<p>";
      $description="not broken";
    }
    make_log_entry($dbh,$reader_id,"urlreport",$bkref_id,$bk_id,0,0,0,0,$description);
    return $saywhat;
 }

