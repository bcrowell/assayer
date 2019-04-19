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
$title = "The Assayer: Add a Review: Step 1";

use CGI;
use DBI;

#$who_am_i = "asreview1x.cgi"; # for debugging
$who_am_i = "asreview1.cgi"; # normal

$co = new CGI;

$what = $co->param('what');
if ($what eq "") {$what=1;}

# n = number of authors
$n = $co->param('n');
if ($n eq "") {$n=1;}

$search = $co->param('search');

for ($k=0; $k<$max_authors; $k++) {
  $m = $k+1;
  $last[$k] = $co->param("last$m");
  $first[$k] = $co->param("first$m");
  $suffix[$k] = $co->param("suffix$m");
  $auref[$k] = $co->param("auref$m");
  #Strip HTML out to avoid security problems.
  $last[$k] =~ s/<//; # strip html
  $first[$k] =~ s/<//;
  $suffix[$k] =~ s/<//;

}

PrintHTTPHeader();
PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);
if (! seems_loggedIn($co)) {$bogus = "Not logged in. Only members can review books.";}

if (!$bogus) {
  if ($login = seems_loggedIn($co)) { print "User $login logged in.<p>"; }
  print "<h1>$title</h1>\n";
  if ($what==1) {$bogus = do1($co,$homepath,$n,\@last,\@first,\@suffix,\@auref);}
  if ($what==2) {$bogus = do2($co,$homepath,$n,\@last,\@first,\@suffix,\@auref,$search);}
  if ($what==3) {$bogus = do3($co,$homepath,$n,\@last,\@first,\@suffix,\@auref);}
}

if ($bogus) {
  print "Error: $bogus<p>\n";
}

&PrintFooterHTML($homepath);

########################################################################
# what=1
########################################################################
sub do1($$$$$$$)
{
	my ($co,$homepath,$n,$last_ref,$first_ref,$suffix_ref,$auref_ref) = @_;
	my $bogus = 0;
    print $co->start_form( -method=>'POST',
		-action=>($cgi_full_path . "/" . $who_am_i));
	print completed_authors($co,$n-1,$last_ref,$first_ref,$suffix_ref,$auref_ref,"",0);
	print "<b>" . ordinal($n,1) . " author:</b><br>\n";
	print "Please enter this author's last name (or the first few letters of it):<br>"
		.$co->textfield(-name=>"search",-value=>'') ;
	print	$co->submit(-name=>'Continue');
	print  	$co->hidden(-name=>'what',-default=>"2",-override=>1);
	print  	$co->hidden(-name=>'n',-default=>$n,-override=>1);
	print	$co->end_form;
	print guidelines();
	return $bogus;
}
########################################################################
# what=2
########################################################################
sub do2($$$$$$$$)
{
	my ($co,$homepath,$n,$last_ref,$first_ref,$suffix_ref,$auref_ref,$search) = @_;
	my $bogus = 0;
	my ($dbh,$stmt,$sth,$stmt2,$sth2);
	my @row;
	my @row2;
	my $connected = 0;
	my $count;
	my ($au_id,$last,$first,$suffix);
  # Strip leading and trailing whitespace from author's name, and do other cleanup stuff:
    $search =~ s/^\s+//;
    $search =~ s/\s+$//;
  	if ($search eq uc($search)) {$search=lc($search)}
  	if ($search eq lc($search)) {substr($search,0,1)=uc(substr($search,0,1))}
	if (! $bogus) {
	    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
	}
	if (! $bogus) { $connected = 1; }
	if (! $bogus) {
		$stmt = "SELECT au_id,last_name,first_and_middle_names,suffix FROM au_tbl WHERE last_name LIKE '$search%'";
	    $sth = $dbh->prepare($stmt) or $bogus = "Internal error (1)";
	}
	if (! $bogus) {
	    $sth->execute() or $bogus = "Internal error (2)";
	}
	if (! $bogus) {
	
		print "<table><tr><td width=\"245\" bgcolor=\"#dddddd\">Finish entering the author's name</td>\n";
		print "<td width=\"8\"><b>OR</b></td><td width=\"245\" bgcolor=\"#dddddd\">select an author who is already in the database</td></tr>\n";
	    print "<tr><td valign=\"top\">\n";
	    print $co->start_form( -method=>'POST',
			-action=>($cgi_full_path . "/" . $who_am_i));
		print completed_authors($co,$n,$last_ref,$first_ref,$suffix_ref,$auref_ref,$search,0);
		print	$co->submit(-name=>"submit",-value=>"submit");
		print  	$co->hidden(-name=>'what',-default=>"3",-override=>1);
	    print  	$co->hidden(-name=>'n',-default=>$n,-override=>1);
		print	$co->end_form;
		
	    print "</td><td></td><td valign=\"top\">\n";
		
		$count = 0;
		while (@row = $sth->fetchrow_array()) {
		  ($au_id,$last,$first,$suffix) = @row;
		  print printable_author($first,$last,$suffix,1);
		  if (! $bogus) {
			$stmt2 = "SELECT auref_id FROM auref_tbl WHERE au_id LIKE '$au_id'";
		    $sth2 = $dbh->prepare($stmt2) or $bogus = "Internal error (3)";
		  }
		  if (! $bogus) {
		    $sth2->execute() or $bogus = "Internal error (4)";
		  }
		  @row2 = $sth2->fetchrow_array();
		  if (@row2) {
		    ++$count;
		    $au_ref = $row2[0];
		    $o = ordinal($n,0);
	        print $co->start_form( -method=>'POST',-action=>($cgi_full_path . "/" . $who_am_i));
		    print completed_authors($co,$n-1,$last_ref,$first_ref,$suffix_ref,$auref_ref,"",1);
	  	    print $co->hidden(-name=>"last$n",-default=>$last,-override=>1) . "\n";
		  	print $co->hidden(-name=>"first$n",-default=>$first,-override=>1) . "\n";
		  	print $co->hidden(-name=>"suffix$n",-default=>$suffix,-override=>1) . "\n";
		  	print $co->hidden(-name=>"auref$n",-default=>$au_ref,-override=>1) . "\n";
		    print	$co->submit(-name=>"submit",-value=>"Author #$au_ref") . "<br>\n";
			print  	$co->hidden(-name=>'what',-default=>"3",-override=>1);
		    print  	$co->hidden(-name=>'n',-default=>$n,-override=>1);
			print	$co->end_form;
		  }
		}
		if (!$count) {
		  print "(There are no authors already in the database whose last names begin with \"$search\".)<p>\n";
		}
		print "</td></tr></table>\n";
	}
	if ($connected) {
   $dbh->disconnect;
   if (ref $sth) {$sth->finish}
   if (ref $sth2) {$sth2->finish}
  }
	print guidelines();
	return $bogus;
}


########################################################################
# what=3
########################################################################
sub do3($$$$$$$)
{
	my ($co,$homepath,$n,$last_ref,$first_ref,$suffix_ref,$auref_ref) = @_;
	my $bogus = 0;
	
    print $co->start_form( -method=>'POST',
		-action=>($cgi_full_path . "/asreview2.cgi") );
	print completed_authors($co,$n,$last_ref,$first_ref,$suffix_ref,$auref_ref,"",0);
	print	$co->submit(-name=>'Done');
	print  	$co->hidden(-name=>'n',-default=>$n,-override=>1);
	print	$co->end_form;
	
	if ($n+1<=$max_authors) {
		print $co->start_form( -method=>'POST',
				-action=>($cgi_full_path . "/" . $who_am_i));
		print completed_authors($co,$n,$last_ref,$first_ref,$suffix_ref,$auref_ref,"",1);
		print  	$co->hidden(-name=>'what',-default=>"1",-override=>1);
		$o = ordinal($n+1,0);
		print	$co->submit(-name=>"Add a $o author");
		print  	$co->hidden(-name=>'n',-default=>($n+1),-override=>1);
		print	$co->end_form;
	}
	
	return $bogus;
}
########################################################################
# completed_authors
########################################################################
sub completed_authors($$$$$$$$)
{
	my ($co,$n,$last_ref,$first_ref,$suffix_ref,$auref_ref,$search,$silent) = @_;
	my @last = @$last_ref;
	my @first = @$first_ref;
	my @suffix = @$suffix_ref;
	my @auref = @$auref_ref;
	my $result;
	$result = "";
	for ($k=0; $k<$n; $k++) {
	  $current_one = ($k==$n-1 && $search ne "");
	  if ($current_one) {$last[$k]=$search; $first[$k]=""; $suffix[$k]="";}
	  $m=$k+1;
	  if (!$silent) {$result = $result . "<b>" . ordinal($k+1,1) . " author:</b> ";}
	  if (! $current_one && !$silent) {
	    $result = $result . printable_author($first[$k],$last[$k],$suffix[$k],1);
	    if ($auref[$k] ne "") {$result = $result . " (author id #" . $auref[$k] . ")";}
	  }
	  if (! $current_one) {
		  	$result = $result .  $co->hidden(-name=>"last$m",-default=>$last[$k],-override=>1) . "\n"
		  	. $co->hidden(-name=>"first$m",-default=>$first[$k],-override=>1) . "\n"
		  	. $co->hidden(-name=>"suffix$m",-default=>$suffix[$k],-override=>1) . "\n";
		  	if ($auref[$k] ne "") {
		  	  $result = $result . $co->hidden(-name=>"auref$m",-default=>$auref[$k],-override=>1) . "\n";
		  	}
	  }
	  else {
	    if (!$silent) {$result = $result . authorblanks($m,$search) . "<p>\n";}
	  }
	  if (!$silent) {$result = $result . "<p>\n";}
	}
	return $result;
}
########################################################################
# authorblanks
########################################################################
sub authorblanks($$)
{
	my ($k,$search) = @_;
	return "<table><tr><td valign=\"bottom\">last name</td><td valign=\"bottom\">first and middle<br>names or initials</td><td valign=\"bottom\">suffix</td></tr>\n"
	 . "<tr>"
	 . "<td>" . $co->textfield(-name=>"last$k",-value=>$search) . "</td>"
	 . "<td>" . $co->textfield(-name=>"first$k",-value=>'') . "</td>"
	 . "<td>" . $co->textfield(-name=>"suffix$k",-value=>'') . "</td>"
	 . "</tr>"
	 . "<tr><td>Example: Wells</td><td>Example: H.G.</td><td>Example: Jr.</td></tr>"
	 . "</table>";

}
########################################################################
# ordinal
########################################################################
sub ordinal($$)
{
	my ($k,$caps) = @_;
	my $result;
	$result = "";
	if ($k==1) {$result = "first";}
	if ($k==2) {$result = "second";}
	if ($k==3) {$result = "third";}
	if ($k==4) {$result = "fourth";}
	if ($k==5) {$result = "fifth";}
	if ($result eq "") {$result = $k . "th";}
	if ($caps) {
	  return ucfirst($result);
	}
	else {
	  return $result;
	}
}
########################################################################
# guidelines
########################################################################
sub guidelines()
{
	return "<h3>Guidelines for Entering Authors' Names</h3><ul>"
		. "<li> There is a special author called 'anonymous'."
		. "<li> Names that start with a preposition have the preposition at the end, after a comma:"
		. "<ul> Carmo, Joao Batista do, <i>not</i> Do Carmo, Joao Batista</ul>"
		. "<li> Names that start with an article have the article at the beginning:"
		. "<ul> L'Hoste, Jacques</ul>"
		. "</ul>";
}
