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
$title = "The Assayer: Log Out";

use CGI;
use DBI;


$co = new CGI;

    $cookies = [
      $co->cookie(
        -name=>'assayerlogin',
        -value=>"",
        -expires=>'-1d',
        -path=>cookie_path(),
      ),
      # We used to use the path "/cgi-bin/" -- make sure to
      # eradicate these old cookies:
      $co->cookie(
        -name=>'assayerlogin',
        -value=>"",
        -expires=>'-1d',
        -path=>"/cgi-bin/",
      ),
	  ];
  
	print $co->header(-cookie=>$cookies);



PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

&PrintFooterHTML($homepath);
