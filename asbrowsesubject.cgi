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
require "./asloc.pl";

$title = "The Assayer: Browse by Subject";

use CGI;
use DBI;

use Time::HiRes qw( usleep ualarm gettimeofday tv_interval nanosleep
										clock_gettime clock_getres clock );
     # for profiling

$co = new CGI;

PrintHTTPHeader();

PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$bogus = 0;
$connected = 0;

%query_hash = decode_query_hash();
if (exists($query_hash{"class"})) {
  $class_requested = $query_hash{"class"};
}
else {
  $class_requested = 0;
}
if ($class_requested && ($class_requested =~ m/[^a-zA-Z]/)) {$bogus = "class_requested contains illegal characters.";}
if ($class_requested && (length($class_requested)>12)) {$bogus = "class_requested is too long";}

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


if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
        print "<h1>$title</h1>\n";
        
        
        if ($login = seems_loggedIn($co)) {
          print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$login) . " logged in.";
        }
        else {
          print "Not logged in.";
        }
        print "<p>\n";
  
  }

if (! $class_requested) {
  print "<table><tr><td>\n";
  for ($class_ascii = ord("A"); $class_ascii<=ord("Z"); $class_ascii++) {
    $class = chr($class_ascii);
    if ($class eq "M") {print "</td><td>\n";}
        $selectstmt = "SELECT count(*) FROM bk_tbl WHERE lcc_class LIKE '$class'";
        $sth = $dbh->prepare($selectstmt) or $bogus=4;
        if (! $bogus) {
          $sth->execute() or $bogus=5;
        }
        if (! $bogus) {
        @row = $sth->fetchrow_array();
            if (exists $loc_class{$class}) {
                    if ($row[0]) {
                      print "<a href=\"asbrowsesubject.cgi?class=$class\">";
                           }
                  print "$class - $loc_class{$class}";
                    if ($row[0]) {
                      print "</a>";
                           }
                        if ($row[0]==0) {print " (no books)<br>\n";}
                        if ($row[0]==1) {print " (1 books)<br>\n";}
                        if ($row[0]>1) {print " ($row[0] books)<br>\n";}
            }
        }
  }
  print "</td></tr></table>\n";

}

# We want to print out a table of contents, and then a listing of all the books. In a large category,
# the listing of the books may be very long, so to give them something to look at, we print the TOC
# on the fly, while storing up the listing in the string $body. To avoid doing every database access
# twice, we only go through the loop once.
my $body = '';
sub add_body {my $x = shift; $body = $body . $x}
sub add_toc {my $x = shift; print $x}
sub add_linked {
  my $text = shift;
  my $link_name = shift;
  my $body_style = shift;
  my $toc_style = $body_style;
  if (@_) {$toc_style = shift}
  my $extra_toc_prefix = '';
  if (@_) {$extra_toc_prefix = shift}
  my $toc_text = $extra_toc_prefix . $text;
  my $body_text = $text;
  if ($toc_style) {$toc_text = "<$toc_style>$toc_text</$toc_style>"}
  if ($body_style) {$body_text = "<$body_style>$body_text</$body_style>"}
  my $toc = '<a href="#'.$link_name.'">'.$toc_text.'</a>';
  my $body = '<a name="'.$link_name.'"/>'.$body_text;
  add_body($body);
  add_toc($toc);
}
if ($class_requested && !$bogus) {
  print  "<a href=\"asbrowsesubject.cgi\">General subject index</a><p>\n";
  print  explain_icons($homepath);
  add_toc('<h1>Contents</h1>');
  my $toc_prefix = '';
  my $hdr_note = '';
  for (my $freedom_loop=1; $freedom_loop<=1; ++$freedom_loop) { # used to loop up to 2, no longer do that because no non-free books
    my $freedom_clause;
    if ($freedom_loop==1) {
      $freedom_clause = "freedom >= '2'";
      $toc_prefix = 'free';
      #add_linked( "<h2>Free Books</h2>\n",$toc_prefix);
    }
    else {
      $freedom_clause = "freedom < '2'";
      $toc_prefix = 'nonfree';
      $hdr_note = ' (non-free books)';
      #add_linked( "<h2>Non-Free Books</h2>\n", $toc_prefix);
    }
    $selectstmt = "SELECT bk_id, lcc_class,lcc_subclass, subsubclass, title, freedom, url "
                 ."FROM bk_tbl WHERE lcc_class LIKE '$class_requested' AND $freedom_clause ORDER BY lcc_subclass, subsubclass, title";
    $sth = $dbh->prepare($selectstmt) or $bogus=4;
    if (! $bogus) {
      start_timer('execute initial select');
      $sth->execute() or $bogus=5;
      end_timer();
    }
    if (! $bogus) {
      $last_class = "-";
      $last_subclass = "-";
      $last_subsubclass = "-";
      my $count_book_loop = 0;
      while (@row = $sth->fetchrow_array()) { # for each book...
        ++$count_book_loop;
        start_timer("top of loop over books, $count_book_loop");
        ($bk_id,$lcc_class,$lcc_subclass,$subsubclass,$title,$freedom,$url) = @row;
        $selectstmt2 = "SELECT bkref_id FROM bkref_tbl WHERE bk_id LIKE '$bk_id'";
        $err = 0;
        $sth2 = $dbh->prepare($selectstmt2) or $err=1;
        if (! $err) {
          start_timer('execute select 2');
          $sth2->execute() or $err=2;
          end_timer();
        }
        # No loop here. We just want the first bkref that refers to this book id.
        if (! $err) {
          start_timer('fetchrow, one book');
          @row = $sth2->fetchrow_array();
          end_timer();
        }
        if (@row) {
          start_timer("generating output for one book");
          start_timer("top half");
          $bkref_id = $row[0];
          if ($lcc_class ne $last_class && $lcc_class ne "") {
            my $hdr = '';
            if (exists $loc_class{$lcc_class}) {
              $hdr = "$lcc_class - $loc_class{$lcc_class}$hdr_note\n";
            }
            else {
              $hdr = "Library of Congress class $lcc_class$hdr_note\n";
            }
            add_linked($hdr,"${toc_prefix}class$lcc_class",'h3');
          }
          if ($lcc_class ne "" && $lcc_subclass ne "" && ($lcc_class ne $last_class || $lcc_subclass ne $last_subclass)) {
            $last_subclass = $lcc_subclass;
            my $hdr = '';
            if (exists $loc_subclass{$lcc_class . $lcc_subclass}) {
              my $bbb = $lcc_class . $lcc_subclass;
              my $aaa = $loc_subclass{$bbb};
              $hdr = "$bbb - $aaa$hdr_note\n";
            }
            else {
              $hdr =  "Library of Congress subclass $lcc_class" . "$lcc_subclass$hdr_note\n";
            }
						add_linked($hdr,"${toc_prefix}class$lcc_class$lcc_subclass",'h4');
          }
          if (   $lcc_class ne "" && $lcc_subclass ne "" && $subsubclass ne "" 
              && ($lcc_class ne $last_class || $lcc_subclass ne $last_subclass || $subsubclass ne $last_subsubclass)) {
            for (my $i=0; $i<length($subsubclass); $i++) {
              if ($i>=length($last_subsubclass) || substr($subsubclass,0,$i+1) ne substr($last_subsubclass,0,$i+1)) {
                my $bbb = $lcc_class . $lcc_subclass . substr($subsubclass,0,$i+1);
                my $h = 5+$i;
                my $hdr = '';
                if (exists $subsubclass{$bbb}) {
                  my $aaa = $subsubclass{$bbb};
                  $hdr = "$aaa$hdr_note\n";
                }
                else {
                  $hdr = "subsubclass $subsubclass$hdr_note\n";
                }
								add_linked($hdr,"${toc_prefix}class$lcc_class$lcc_subclass$subsubclass","h$h",'p',('-' x ($i+1)).' ');
						  }
					  }
            $last_subsubclass = $subsubclass;
          }
          if ($lcc_class ne $last_class && $lcc_class ne "") {
            $last_class = $lcc_class;
          }
          add_body( "<a href=\"asbook.cgi?book=$bkref_id\">$title</a> ");
          end_timer("top half");
          start_timer("bottom half");
          if (0) { # putting in the aurefs was extremely inefficient, caused it to take 30 seconds on the Q category
					add_body(" / ");
          start_timer("aurefs");
          @auref_id_array = get_aurefs($bk_id,$dbh);
          end_timer("aurefs");
          $very_first_one = 1;
          foreach $auref_id(@auref_id_array) {
            my $au_id = au_ref_to_raw_id($auref_id,$dbh);
            my ($last,$first,$suffix) = get_name($au_id,$dbh);
            if (!$very_first_one) {add_body( ", ")}
            $very_first_one = 0;
            add_body( "<a href=\"asauthor.cgi?author=$auref_id\">" . printable_author($first,$last,$suffix,0) . "</a>");
          }
          add_body(  freedom_img_tag_with_link($homepath,$freedom,$url));
          if ($countrev) { add_body( count_reviews_html($dbh,$bkref_id)) }
				  }
          add_body( "<br>\n");
          end_timer();
          end_timer();
        }
        end_timer();
      } # end loop over books
    }
  }
}

print $toc . $body;

if ($bogus) {
        print "Sorry, error $bogus occurred.<p>\n ";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  if (ref $sth2) {$sth2->finish}
  $dbh->disconnect;
}

PrintFooterHTML($homepath);

#------------ profiling

our @timer;
our @describe_timer = '';
our $indentation = 0;
our $do_profiling = 0; # turn it on or off

sub start_timer {
  if (!$do_profiling) {return}
  my $d = shift;
  push @describe_timer,$d;
  push @timer,[gettimeofday];
  if (!open(F,">>/usr/local/www/theassayer/logs/assayer.profile")) { # not currently configured correctly, but ok because turned off
    return;
  }
  print F describe("> $d");
  close F;
  ++$indentation;
}

sub end_timer {
  if (!$do_profiling) {return}
  --$indentation;
  my $timer = pop @timer;
  my $describe_timer = pop @describe_timer;
  my $elapsed = tv_interval ( $timer );
  if (!open(F,">>/usr/local/www/theassayer/logs/assayer.profile")) { # not currently configured correctly, but ok because turned off
    return;
  }
  print F describe("< $describe_timer  $elapsed");
  close F;
}

sub describe {
  my $stuff = shift;
  my $result = '';
  for (my $i=1; $i<=$indentation; $i++) {
    $result = $result . ' ';
  }
  $result = $result . ' ' . $stuff . "\n";
  return $result;
}
