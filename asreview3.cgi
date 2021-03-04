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
require "./asinstallation.pl";
require "./asnotifyutil.pl";
require "./asgetmethod.pl";
require "./asfreedom.pl";

PrintHTTPHeader();



use CGI;
use DBI;

$co = new CGI;

$inserted_review = 0;
$inserted_author = 0;
$inserted_book = 0;

%query_hash = decode_query_hash();
$debug = exists($query_hash{"debug"});

$do_what = $co->param('submit');
my $preview_button = 'I want to preview my review and edit it further.';
my $submit_button = 'I am not the author, and have no personal, professional, or business relationship with the author. I am submitting my review.';
my $no_review_button = 'I want to add the book to the database without a review.';

# The following are optional. By experiment, I've found that these get
# set to null strings if there's no such parameter.
$raw_subject = $co->param('subject');
$raw_review = $co->param('review');
$subject = remove_all_html($raw_subject);
$review = only_allowed_html($raw_review);



# We don't need or use the following if it's a preexisting book:
# n = number of authors
$n = $co->param('n');
for ($k=0; $k<$n; $k++) {
  $m = $k+1;
  $last[$k] = $co->param("last$m");
  $first[$k] = $co->param("first$m");
  $suffix[$k] = $co->param("suffix$m");
  $auref[$k]  = $co->param("auref$m");
}


$title = $co->param('title');
$title =~ s/<//; #strip html
$title =~ s/^The (.*)/$1, The/;

$freedom = $co->param('freedom');
$url = $co->param('url');
$lccclass = $co->param('lccclass');
$lccsubclass = $co->param('lccsubclass');
$bkref = $co->param('bkref');


$content = $co->param('content');
$writing = $co->param('writing');

$parent_review = $co->param('parent_review');
if ((length $parent_review)==0 || (((length $parent_review)!=0) && ($parent_review<0))) {$parent_review = 0;}

if ($parent_review) {
  $what_it_is = "comment";
}
else {
  $what_it_is = "review";
}
        


# The purpose of $revising is to stop them from changing stuff they're not
# allowed to change when revising, e.g. the license.
$revising = $co->param('revising');
if ((length $revising)==0) {$revising=0;}



if ((length $do_what)==0 || (((length $do_what)>0)&&($do_what eq "Reply"))) {
  $do_what = 1;
}
else {
  $license = $co->param('license');
  $printable_license = printable_form_of_license_code($license,1);
  if ($do_what eq $preview_button || $do_what eq "Revise") {
    $do_what = 2;
  }
  else {
    $do_what = 3;
  }
}

if ($do_what<3) {
  $pagetitle = "The Assayer: Add a Review: Step 3";
}
else {
  $pagetitle = "The Assayer: Add a Review: Step 4";
}


PrintHeaderHTML($homepath,$pagetitle);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);
print "<h1>$pagetitle</h1>\n";

if ($debug) {print "---debugging mode---<p>\n";}

$bogus = 0;

        $connected = 0;
        if (! $bogus) {
            $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
        }
        if ($debug) {print "--2- $bogus<p>";}
        
        if (! $bogus) {
            $connected = 1;
        }

if ($freedom<2 && $url ne "") {
  $url = "";
  print "Sorry, but you cannot give a web address for a book that is not available for free reading."
          . " The web address will not be listed.<p>";
}

# Don't let them add books inappropriately.
my $allow_non_free = 0; # also in asreview2
if ($bkref eq "") {
    if ($freedom>=2 && !($url=~m@https?://.+\..+@)) {
        $bogus = "Since the book is available for free reading, please give a web address.<p>";
    }
    if ($freedom<=1 && $review eq "" && $do_what==3) {
        $bogus = "If a book isn't available for free reading, then it can't be added to the database without a review.<p>\n";
    }
    if ($freedom<=1 && !$allow_non_free) {
  			$bogus = "Only free books may be added to the database.<p>\n";
    }
}

if ($review ne '') {
  if ($review eq uc($review)) {
    $bogus = "Reviews may not be written in ALL CAPS.";
  }
  if ($subject eq uc($subject)) {
    $bogus = "The subject line may not be written in ALL CAPS.";
  }
}

#############################################################################
# show information about the book
#############################################################################
if (!$bogus) {
        

        if ((length $bkref)>0) { # reviewing a preexisting book
          print "$title (book #" . $bkref. ")<br>";
        }
        else {
          print "Title: $title<br>";
          if ($debug) {print "n=$n<p>\n";}
          for ($k=0; $k<$n; $k++) {
            $o = ordinal($k+1,1);
            print "$o author: " . printable_author($first[$k],$last[$k],$suffix[$k],0);
            if ($auref[$k] ne "") {print " (author id #" . $auref[$k] . ")";}
            print  "<br>\n";
          }
          if ($url ne "") {print "Web address: $url<br>\n";}
          if ($lccclass ne "") {print "LoC class: $lccclass<br>\n";}
          if ($lccsubclass ne "") {print "LoC subclass: $lccsubclass<br>\n";}
          print "Legal: " . $describe_freedom{$freedom} . "<p>\n";
        }
}

#############################################################################
# show review
#############################################################################
if (!$bogus && $do_what>1 && ($review ne "")) {
                if ($parent_review) {
                  print "Parent review id # $parent_review <p>\n";
                }
                print displayable_review($subject,seems_loggedIn($co),
                $content,$writing,$review,$license,$parent_review,$homepath,0,$titlebgcolor,"",0,$dbh);

}

if ($do_what<3) {
        #############################################################################
        # writing review
        #############################################################################

        $score_labels{'0'} = "Substandard";
        $score_labels{'1'} = "Average";
        $score_labels{'2'} = "Better than 80\%";
        $score_labels{'3'} = "Better than 90\%";
        $score_labels{'4'} = "Better than 95\%";
        $score_labels{'5'} = "Better than 98\%";
        $score_labels{'6'} = "Better than 99\%";
        
        $license_labels{'110'} = printable_form_of_license_code(110,0);
        $license_labels{'211'} = printable_form_of_license_code(211,0);
#        $license_labels{'310'} = printable_form_of_license_code(310,0);
#        $license_labels{'410'} = printable_form_of_license_code(410,0);

        #If changing this, need to change 110 & 211 in code below. Is this redundancy necessary?
        
        

        

        if (! seems_loggedIn($co)) {$bogus = "Not logged in.  If you think you are logged in, try hitting the reload button in your browser.";}
        
        
        if (!$bogus) {
        
                print "Please note the following rules, which operate on an honor system: (1) The author or publisher of the book "
                        . "may list the book in the database without a review, but may not write an actual review. If the "
                        . "author wishes to reply to a review, he/she must state in the reply that he/she is the author. "
                        . "(2) If you have even a possible conflict of interest, you should disclose it in your review. "
                        . " This includes, but is not limited to, a case where you have a personal, professional, or business "
                        . " relationship with the author or publisher.";
        
            if (!$debug) {
              print $co->start_form( -method=>'POST',-action=>"$cgi_full_path/asreview3.cgi");
            }
            else {
              print $co->start_form( -method=>'POST',-action=>"$cgi_full_path/asreview3.cgi?debug=true");
            }
                        
                        
        print "\n<p> ";
        
        if (!$parent_review) {
            if ((length $content)==0) {$content = 1;}
            if ((length $writing)==0) {$writing = 1;}
                print "Content score: " 
                . $co->popup_menu(
                  -name=>"content",
                  -values=>['0','1','2','3','4','5','6'],
                  -default=>$content,
                  -labels=>\%score_labels
                ) . "<br>\n";
        
                print "Writing score: " 
                . $co->popup_menu(
                  -name=>"writing",
                  -values=>['0','1','2','3','4','5','6'],
                  -default=>$writing,
                  -labels=>\%score_labels
                ) . "<p>\n";
        }
        
        print "<b>Legal information:</b> You retain the copyright to your $what_it_is. However, by submitting \n";
        print "your $what_it_is to The Assayer's database, you agree to copyleft it according to one of the \n";
        print "licenses from the pull-down menu.<br>\n";
        
        print "In the $what_it_is, you can make paragraph breaks using the symbol &lt;p&gt;, \n";
        print "and you can italicize &lt;i&gt;like this&lt;/i&gt;.<p>\n";
        
        print '<a href="'.help_link($homepath,"reviews").'"  target="window">Help</a><p>';
        
        
        print "Title of your $what_it_is:<br> " . $co->textfield(-name=>'subject',-value=>$raw_subject,-value=>'',-size=>70,-maxlength=>70) ."<p>\n";
        print "Text:<br> " . $co->textarea(-name=>'review',-value=>$raw_review,-value=>'',-rows=>10,-columns=>70) ."<p>\n";
        
        if (!$revising) {
                print "Copyleft licensing is required for all " . $what_it_is . "s. Choose license: " 
                . $co->popup_menu(
                  -name=>"license",
                  -values=>['110','211'],
                  -default=>'110',
                  -labels=>\%license_labels
                ) . "<br>\n";
                print "See the help page for information about these licenses.<br/>";
        }
        
        #print $co->checkbox_group(-name=>'preview',-values=>['Preview only'],-defaults=>[]) . "<br>";
                                                
        print $co->submit(-name=>'submit',-value=>$preview_button)."<br>\n";
        print $co->submit(-name=>'submit',-value=>$submit_button)."<br>\n";
        if ((length $bkref)==0) {
          print $co->submit(-name=>'submit',-value=>$no_review_button)."<br>\n";
        }
        
        if ($n ne "") {
          for ($k=0; $k<$n; $k++) {
            $m = $k+1;
            print $co->hidden(-name=>"last$m",-default=>$last[$k],-override=>1) . "\n";
            print $co->hidden(-name=>"first$m",-default=>$first[$k],-override=>1) . "\n";
            print $co->hidden(-name=>"suffix$m",-default=>$suffix[$k],-override=>1) . "\n";
            if ($auref[$k] ne "") {print $co->hidden(-name=>"auref$m",-default=>$auref[$k],-override=>1) . "\n";}
          }
        }
        print $co->hidden(-name=>'n',-default=>$n,-override=>1);
        print          $co->hidden(-name=>'title',-default=>"$title",-override=>1);
        print          $co->hidden(-name=>'bkref',-default=>"$bkref",-override=>1);
        print          $co->hidden(-name=>'parent_review',-default=>"$parent_review",-override=>1);
        print          $co->hidden(-name=>'license',-default=>"$license",-override=>1);
        print          $co->hidden(-name=>'revising',-default=>"$revising",-override=>1);
        print          $co->hidden(-name=>'freedom',-default=>"$freedom",-override=>1);
        if ($url ne "") {print          $co->hidden(-name=>'url',-default=>"$url",-override=>1);}
        if ($lccclass ne "") {print          $co->hidden(-name=>'lccclass',-default=>"$lccclass",-override=>1);}
        if ($lccsubclass ne "") {print          $co->hidden(-name=>'lccsubclass',-default=>"$lccsubclass",-override=>1);}

        print        $co->end_form;
        }
        if ($bogus) {
          print "Error: $bogus<p>\n";
          print "If you need to log in, click <a href=\"aslogin.cgi\" target=\"window\">here</a> ";
          print "to bring up a log-in screen in ";
          print "a separate window. After you log in, close that window and reload this one.<p>\n";
        }
} # end if $do_what<3
else {
        #############################################################################
        # inserting in database
        #############################################################################
        
        
        
        #if ((length $raw_subject)<2) {$bogus="You must supply a subject line.";}
        #if ((length $raw_review)<10) {$bogus="You must supply a review.";}
        
        
        if ((length $printable_license)==0) {
          $bogus = "Error -- unknown license $license.";
        }
        
        
        
        
        
        if ($do_what<3) {
          print "<h1>Previewing Review</h1>\n";
          print "Previewing only.<p>\n";
        }
        else {
          print "<h1>Adding Review</h1>\n";
        
        }
        if ($debug) {print "--1- $bogus<p>";}
        
        
        
        if (! ($login=loggedIn($co,$dbh,\$err))) {$bogus = "Not logged in.";}
        
        if ($debug) {print "--3- $bogus<p>";}
        
        if (!$bogus) {
        
        
                        
                #########################################################
                ###### Get this person's user ID
                #########################################################
                if (! $bogus) {
                  $selectstmt = "SELECT id FROM users WHERE login LIKE " . $dbh->quote($login);
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
                #########################################################
                ###### Add author records if they don't already exist.
                #########################################################
                if ($n ne "" && !$preview) {
                  for ($k=0; $k<$n; $k++) {
                          if ($auref[$k] eq "") {
                                  if (! $bogus) {
                                      $ql = $dbh->quote($last[$k]);
                                      $qf = $dbh->quote($first[$k]);
                                      $qs = $dbh->quote($suffix[$k]);
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
                                  }
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
                                      $auref[$k] = $row[0];
                                      $inserted_author = 1;
                      make_log_entry($dbh,$user_id,"newauthor",$bkref,0,$auref[$k],0,0,0,"");
                                    }
                                  }
                          } # end if new author
                  }# end for k
                }
                #########################################################
                ###### Add book record if it doesn't already exist.
                #########################################################
                if ((length $bkref)==0 && !$preview) {
                  if ($n eq "") {
                    $bogus = "Internal error (5).";
                  }
                  if (! $bogus) {
                          $qt = $dbh->quote($title);
                          $fields_to_set = "title,created_by_user_id,date_created";
                          $field_values = "$qt,\'$user_id\',NOW()";
                          for ($k=0; $k<$n; $k++) {
                            $m = $k+1;
                            $fields_to_set = $fields_to_set . ",auref_id$m";
                            $field_values = $field_values . ",\'" . $auref[$k] . "\'";
                          }
                          
                          $lccclass = uc($lccclass);
                          $lccsubclass = uc($lccsubclass);
                          if ((length $lccclass)!=1) {$lccclass="";}
                          if ((length $lccsubclass)!=1) {$lccsubclass="";}
                          $fields_to_set = $fields_to_set . ",freedom"; $field_values = $field_values . ",\'$freedom\'";
                          if ($url ne "") {$fields_to_set = $fields_to_set . ",url"; $field_values = $field_values . ",\'$url\'";}
                          if ($lccclass ne "") {$fields_to_set = $fields_to_set . ",lcc_class"; $field_values = $field_values . ",\'$lccclass\'";}
                          if ($lccsubclass ne "") {$fields_to_set = $fields_to_set . ",lcc_subclass"; $field_values = $field_values . ",\'$lccsubclass\'";}
                  }
                  if (! $bogus) {
                          $insertstmt = "INSERT INTO bk_tbl ($fields_to_set) VALUES ($field_values)";
                          #print "--- $n $insertstmt<p>\n";
                          $sth = $dbh->prepare($insertstmt) or $bogus="Internal error (6).";
                  }
                  if (!$bogus) {
                    if (! $debug) {
                      $sth->execute() or $bogus="Error writing to database (6).";
                    }
                    else {
                      print "SQL: $insertstmt<p>\n";
                    }
                  }
                  if (! $bogus) {
                          $insertstmt = "INSERT INTO bkref_tbl (
                            bk_id,
                            created_by_user_id,
                            date_created
                          )
                          VALUES (
                            LAST_INSERT_ID(),
                            \'$user_id\',
                            NOW()
                          )";
                          $sth = $dbh->prepare($insertstmt) or $bogus="Internal error (7).";
                  }
                  if (! $bogus) {
                    if (! $debug) {
                      $sth->execute() or $bogus="Error writing to database (7).";
                    }
                    else {
                      print "SQL: $insertstmt<p>\n";
                    }
                  }
                  if (! $bogus) {
                    $selectstmt = "SELECT bkref_id FROM bkref_tbl WHERE bkref_id LIKE LAST_INSERT_ID()";
                    $sth = $dbh->prepare($selectstmt) or $bogus="Internal error (8).";
                  }
                  if (! $bogus) {
                    $sth->execute() or $bogus="Error updating database (9).";
                  }
                  if (! $bogus) {
                    @row = $sth->fetchrow_array();
                    if (! @row) {
                      $bogus = "Error reading database (10).";
                    }
                    else {
                      $bkref = $row[0];
                      #print "bkref= $bkref<br>\n";
                      $inserted_book = 1;
                    }
                  }
                }
                #########################################################
                ###### Add review record.
                #########################################################
                if ($do_what eq $no_review_button) {$review = ''}
                if ((length $bkref)!=0 && !$preview && ($review ne "")) {
                  if (! $bogus) {
                      if ((length $parent_review)==0) {
                        $parent_review = 0;
                      }
                      $sc = $content * 10;
                      $sw = $writing * 10;
                      $rq = $dbh->quote($review);
                      $sq = $dbh->quote($subject);
                          $insertstmt = "INSERT INTO review_tbl (
                            bkref_id,
                            parent_review_id,
                            user_id,
                            subject,
                            review,
                            license,
                            score_content,
                            score_writing,
                            date
                          )
                          VALUES (
                            \'$bkref\',
                            \'$parent_review\',
                            \'$user_id\',
                            $sq,
                            $rq,
                            \'$license\',
                            \'$sc\',
                            \'$sw\',
                            NOW())";
                          $sth = $dbh->prepare($insertstmt) or $bogus="Internal error (11).";
                  }
                  if (! $bogus) {
                    if (!$debug) {
                      $sth->execute() or $bogus="Error writing to database (11).";
                    }
                    else {
                      print "SQL: $insertstmt<p>\n";
                    }
                  }
                  if (! $bogus && !$debug) {
                    send_notifications($dbh,$bkref);
                    print "Thank you for your review! Your review has been added successfully to the database.<p>";
                    $inserted_review = 1;
                  }
                  #print "--- $bogus --- $insertstmt <p>\n";
                }
        }
        
        #print "---<p>";

if (!$bogus) {
  print "<a href=\"$cgi_full_path/asbook.cgi?book=$bkref\">$title</a><p>\n";
}
        
        if ($bogus) {
          print "Error: $bogus<p>\n";
          print "If you need to log in, click <a href=\"aslogin.cgi\" target=\"window\">here</a> ";
          print "to bring up a log-in screen in ";
          print "a separate window. After you log in, close that window and reload this one.<p>\n";
        }
        
        


}
&PrintFooterHTML($homepath);

if (!$bogus && $connected && !$debug) {
  if ($inserted_book) {
    make_log_entry($dbh,$user_id,"newbook",$bkref,0,$auref[$k],0,0,0,"");
  }
  if ($inserted_review) {
    my $sth = $dbh->prepare("SELECT review_id FROM review_tbl WHERE user_id='$user_id' AND bkref_id='$bkref' ORDER BY review_id DESC");
    $sth->execute();
    if (@row = $sth->fetchrow_array()) {
      make_log_entry($dbh,$user_id,"review",$bkref,0,$auref[$k],0,$row[0],0,"");
    }
  }
}

if ($connected) {
  $dbh->disconnect;
}

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
