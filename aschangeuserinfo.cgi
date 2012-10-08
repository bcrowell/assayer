#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asinstallation.pl";
require "asuinfo.pl";

PrintHTTPHeader();

$title = "The Assayer: Change User Information";

use CGI;
use DBI;

$describe_changes = "";

$co = new CGI;


PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$do_what = 1;
if ($co->param('submit') eq "change") {
  $do_what = 2;
}


$login = $co->param('login');
$pwd = $co->param('pwd');
$newpwd1 = $co->param('newpwd1');
$newpwd2 = $co->param('newpwd2');

foreach $uinfo_key(@uinfo_order) {
  if ($uinfo_change_normal_way{$uinfo_key}) {
    $new_stuff{$uinfo_key} = $co->param($uinfo_key);
  }
}

$bogus = 0;
$connected = 0;
if ((length $login)<3) {$bogus=1;}
if ((length $pwd)<3) {$bogus=2;}
if ($newpwd1 && $newpwd2 
	&& (
		($newpwd1 ne $newpwd2) || ((length $newpwd1)<1)
	   ) 
	) {$bogus=4;}
if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) or $bogus=3;
}

if (! $bogus) {
    $connected = 1;
}

if (! $bogus) {
  	  print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$login) . " logged in.";

}

#################################################################
# Read info from database for the first time, and check for valid pwd
#################################################################
if (! $bogus) {
  $read_stuff = "";
  foreach $uinfo_key(@uinfo_order) {
      if ($read_stuff eq "") {
        $read_stuff = $read_stuff . $uinfo_key;
      }
      else {
        $read_stuff = $read_stuff . "," . $uinfo_key;
      }
  }
  $selectstmt = "SELECT " . $read_stuff . " FROM users WHERE login LIKE '$login' AND pwd LIKE '$pwd'";
  $sth = $dbh->prepare($selectstmt) or $bogus=5;
}
if (! $bogus) {
  $sth->execute() or $bogus=6;
}
if (! $bogus) {
  @stuff = $sth->fetchrow_array();
  if (! @stuff) {
    $bogus = "Invalid login name or password";
  }
}
if (! $bogus) {
  $k = 0;
  foreach $uinfo_key(@uinfo_order) {
    $user_hash{$uinfo_key} = $stuff[$k];
    ++$k;
  }
}
#################################################################
# Change pwd
#################################################################
if ((! $bogus) && $newpwd1 && $newpwd2) {
  $updatestmt = "UPDATE users SET pwd = '$newpwd1' WHERE login LIKE '$login' AND pwd LIKE '$pwd'";
  $sth = $dbh->prepare($updatestmt) or $bogus="Internal error (1)";
}
if ((! $bogus) && $newpwd1 && $newpwd2) {
  $sth->execute() or $bogus="Invalid login name or password (1)";

}
if ((! $bogus) && $newpwd1 && $newpwd2) {
	print "<h1>Password Changed</h1>\n";
	print "Your password has been changed.<p>";
	$pwd = $newpwd1;
}
#################################################################
# Change info
#################################################################
if (! $bogus && $do_what==2) {

  foreach $uinfo_key(keys %new_stuff) {
      $n = $new_stuff{$uinfo_key};
	  if ($n ne $user_hash{$uinfo_key} && $uinfo_change_normal_way{$uinfo_key}) {
	    if ($uinfo_html_ok{$uinfo_key}) {
	      $n = only_allowed_html($n);
	    }
	    else {
	      $n = remove_all_html($n);
	    }
	    $n = $dbh->quote($n);
	    $stmt = "UPDATE users SET $uinfo_key = $n WHERE login LIKE '$login' AND pwd LIKE '$pwd'";
	    $sth = $dbh->prepare($stmt) or $bogus="Internal error (5)";
	    $sth->execute() or $bogus="Error writing to database (6)";
	    $what = $uinfo_name{$uinfo_key};
	    print "Changed $what.<br>\n";
	  }
  }

}
#################################################################
# Read info from database for the second time
#################################################################
if (! $bogus) {
  $selectstmt = "SELECT " . $read_stuff . " FROM users WHERE login LIKE '$login' AND pwd LIKE '$pwd'";
  $sth = $dbh->prepare($selectstmt) or $bogus=5;
}
if (! $bogus) {
  $sth->execute() or $bogus=6;
}
if (! $bogus) {
  @stuff = $sth->fetchrow_array();
  if (! @stuff) {
    $bogus = "Invalid login name or password";
  }
}
if (! $bogus) {
  $k = 0;
  foreach $uinfo_key(@uinfo_order) {
    $user_hash{$uinfo_key} = $stuff[$k];
    ++$k;
  }
}

#################################################################
# Form
#################################################################
if (! $bogus) {
	print "<h2>Change user info:</h2>";
	print  $co->startform(-method=>'POST',-action=>"$cgi_full_path/aschangeuserinfo.cgi");
	print "<table>\n";
	foreach $uinfo_key(@uinfo_order) {
	    if ($uinfo_change_normal_way{$uinfo_key}) {
	      $what = $uinfo_name{$uinfo_key};
          if ($uinfo_private{$uinfo_key}) {$z="private";} else {$z="public";}
          if ($uinfo_optional{$uinfo_key}) {$z=$z . ",optional";}
          if ($uinfo_html_ok{$uinfo_key}) {$z=$z . ",html ok";}
          if ($uinfo_instructions{$uinfo_key} ne "") {$z=$z . "," . $uinfo_instructions{$uinfo_key};}
          
	      print "<tr><td bgcolor=\"#dddddd\" valign=\"top\"><b>$what</b> ($z)</td><td>";
	      if ($uinfo_long{$uinfo_key}==0) {
	        print $co->textfield(-name=>$uinfo_key,-value=>$user_hash{$uinfo_key},-size=>70,-maxlength=>70);
	      }
	      if ($uinfo_long{$uinfo_key}==1) {
	        print $co->textfield(-name=>$uinfo_key,-value=>$user_hash{$uinfo_key},-size=>70,-maxlength=>120);
	      }
	      if ($uinfo_long{$uinfo_key}==2) {
	        print $co->textarea(-name=>$uinfo_key,-value=>$user_hash{$uinfo_key},-rows=>8,-columns=>60);
	      }
	      print "</td></tr>";
	    }
	}

	print "</table>\n";
	print  	$co->hidden(-name=>'login',-default=>"$login",-override=>1);
	print  	$co->hidden(-name=>'pwd',-default=>"$pwd",-override=>1);
  	print	$co->submit(-name=>'submit',-value=>'change');
	print	$co->endform;
}

if ($bogus) {
	print "Sorry, error $bogus occurred.<p>\n ";
}
if ($connected) {
  if (ref $sth) {$sth->finish}
  $dbh->disconnect;
}


&PrintFooterHTML($homepath);
