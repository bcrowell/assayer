require "./asdbutil.pl";

sub help_link {
  my $homepath = shift;
  my $anchor = '';
  if (@_) {$anchor = '#'.shift}
  return "$homepath/cgi-bin/ashelp.cgi$anchor";
}

sub user_id_to_hyperlinked_login_name($$$)
{
  my ($dbh,$cgi_full_path,$id) = @_;
  $login = get_login_of_other_user($id,$dbh);
  return login_name_to_hyperlinked_login_name($cgi_full_path,$login);
}

sub login_name_to_hyperlinked_login_name($$)
{
  my $cgi_full_path = shift;
  my $login = shift;
  $raw_login = $login;
  $login =~ tr/ /+/;
  $readable = $raw_login;
  #----if ($real_name) {$readable = "$real_name ($raw_login)"} # don't have real_name
  return "<a href=\"" . $cgi_full_path . "/asuser.cgi?login=" . $login . "\">" . $readable . "</a>";
}

sub user_id_to_hyperlinked_full_name
{
  my $dbh = shift;
  my $id = shift;
  my $cgi_full_path = shift;
  $r = user_id_to_full_name_and_login($dbh,$id);
  $real_name = $r->{'full'};
  $raw_login = $r->{'login'};
  $login = $raw_login;
  $login =~ tr/ /+/;
  return "<a href=\"" . $cgi_full_path . "/asuser.cgi?login=" . $login . "\">" . $real_name . "</a>";
}

sub user_id_to_full_name_and_login
{
  my $dbh = shift;
  my $id = shift;
  my $login = get_login_of_other_user($id,$dbh);
  $real_name = get_user_info($dbh,$id,'real_name');
  if ($real_name) {
    return {'full'=>ucfirst($real_name),'login'=>$login};
  }
  else {
    return {'full'=>$login,'login'=>$login};
  }
}

sub ucfirst_each {
  my $x = shift;
  $x =~ s/(\w+)/ucfirst($1)/ge;
  return $x;
}


sub explain_icons($)
{
	my ($homepath) = @_;
	return "<b>Key:</b> "
		 . freedom_img_tag($homepath,2) . ": can be read for free; "
		. freedom_img_tag($homepath,5) . ": is copylefted under a license similar to Wikipedia's, allowing modification and commercial reuse<p>\n";

}

sub freedom_img_tag_with_link($$$)
{
	my ($homepath,$freedom,$link) = @_;
	if ($link ne "") {
	  return "<a href=\"$link\">" . freedom_img_tag($homepath,$freedom) . "</a>";
	}
	else {
	  return freedom_img_tag($homepath,$freedom);
	}
}

sub freedom_img_tag($$)
{
	my ($homepath,$freedom) = @_;
	if ($freedom>=5) {
	    return "<img src=\"$homepath/flower.gif\" width=\"33\" height=\"12\" alt=\"libre\" border=\"0\">";
	}
	else {
	  if ($freedom>=2) {
	    return "<img src=\"$homepath/bud.gif\" width=\"17\" height=\"12\" alt=\"gratis\" border=\"0\">";
	  }
	}
	return "";
}


sub printable_author($$$$)
{
	my ($first,$last,$suffix,$show_last_first) = @_;
	if ($show_last_first) {
			if ((length $suffix)>0) {
		      return "$last, $first, $suffix";
		    }
		    else {
		      return "$last, $first";
		    }
	}
	else {
			if ((length $suffix)>0) {
		      return "$first $last $suffix";
		    }
		    else {
		      return "$first $last";
		    }
	}

}

sub remove_all_html()
{
	my ($raw) = @_;
	
	my $result = $raw;
	$result =~ s/</&lt\;/g;
	$result =~ s/>/&gt\;/g;
	
	return $result;
	
}

sub only_allowed_html()
{
	my ($raw) = @_;
	
	my $result = $raw;
	$result =~ s@<(i|b|p|sup|sub|ul|ol|li|br|tt)>@---begin\1---@gi;
	$result =~ s@</(i|b|p|sup|sub|ul|ol|li|br|tt)>@---end\1---@gi;
	
#	$result =~ s@<a(\s+)href(\s+)="[^"\n]+"(\s*)>([^<]+)</a>@<a href="\3">\5</a>@gi;
	$result =~ s@<a\shref="([^"\n]+)">([^<]+)</a>@---link1--- href="\1"---link2---\2---link3---@gi;
		
	$result =~ s/</&lt\;/g;
	$result =~ s/>/&gt\;/g;
	
	$result =~ s@---begin(i|b|p|sup|sub|ul|ol|li|br|tt)---@<\1>@g;
	$result =~ s@---end(i|b|p|sup|sub|ul|ol|li|br|tt)---@</\1>@g;
	$result =~ s@---link1---@<a@g;
	$result =~ s@---link2---@>@g;
	$result =~ s@---link3---@</a>@g;

	return $result;
}



sub PrintHTTPHeader()
{
	#print "Content-type:text/html\n\n";
	print "Pragma: no-cache\nCache-control: private\nContent-Type: text/html\n\n";


}

sub displayable_review($$$$$$$$$$$$$)
{
	my ($subject,$reviewer_login,$score_content,$score_writing,$review,
				$license,$is_reply,$homepath,$depth,$titlebgcolor,$date,$review_id,$dbh)
		= @_;
		      $sc = $score_content;
		      $sw = $score_writing;
		      $pr_lic = printable_form_of_license_code($license,1);
	my $s;
	$reviewer_id = user_login_to_id($reviewer_login,$dbh);
	my $review_id_text;
	if ($date ne "") {
	  $date = " on " . $date;
	}
	$review_id_text = "";
	if ($review_id) {
	  $review_id_text = ", review #$review_id";
	}
	if ($is_reply) {
	  $s = "";
	  $what = "comment";
	}
	else {
	  $s = describe_score($sc,"content",$homepath) . describe_score($sw,"writing",$homepath);
	  $what = "review";
	}
	my $email_text = "";
	my $e = get_user_info($dbh,$reviewer_id,"fake_email");
	if ($e ne "") {
	  $email_text = " (" . $e . ")";
	}
	my $homepage_text = "";
	my $h = get_user_info($dbh,$reviewer_id,"homepage");
	if ($h ne "") {
	  $homepage_text = "<br><a href=\"$h\">$h</a>";
	}
	my $sig_text = "";
	my $siggy = get_user_info($dbh,$reviewer_id,"sig");
	if ($siggy ne "") {
	  $sig_text = "<p>$siggy";
	}
  if ($subject eq uc($subject)) {$subject = lc($subject)}
  if ($review eq uc($review)) {$review = lc($review)}
  my $reviewer_realname = get_user_info($dbh,$reviewer_id,'real_name');
  my $reviewer_bio = get_user_info($dbh,$reviewer_id,'bio');

  # Count reviews by this reviewer.
	my $selectstmt = "SELECT bkref_id FROM review_tbl WHERE user_id LIKE '$reviewer_id'";
	my $sth = $dbh->prepare($selectstmt) or $bogus="Internal error reading database to count reviews (1)";
	if (! $bogus) {
	  $sth->execute() or $bogus="Internal error reading database to count reviews (1)";
	}
  my $count_reviews_by_this_reviewer = 0;
	if (! $bogus) {
	  while (my @row = $sth->fetchrow_array()) {
      ++$count_reviews_by_this_reviewer;
    }
	}

  my $warning = '';
  if (0) { # deactivated because of user complaint
    if ($reviewer_realname eq '' || $reviewer_bio eq '' || $count_reviews_by_this_reviewer==1) {
      $warning = "Warning: This review may not be trustworthy, for the following reasons: ";
      my $k = 0;
      if ($reviewer_realname eq '') {++$k; $warning = $warning . "($k)" . 'The reviewer has not disclosed his/her real name. '}
      if ($reviewer_bio eq '') {++$k; $warning = $warning . "($k)" . 'The reviewer has not supplied a bio. '}
      if ($count_reviews_by_this_reviewer==1) {++$k; $warning = $warning . "($k)" . 'The reviewer has not written any other reviews. '}
      $warning = $warning . ' This warning was generated by a machine, so use your own judgment in evaluating the trustworthiness of the review. '
                          . 'In all probability the reviewer is honest, but The Assayer sometimes receives reviews that are really just thinly veiled '
                          . 'promotional blurbs written by the author of the book. You should be especially suspicious of reviews of non-free books that '
                          . 'are overwhelmingly positive.';
      $warning = "<ul>$warning</ul>";
    }
  }
  $reviewer_id = user_login_to_id($reviewer_login,$dbh);
	return 
		("<ul>" x $depth) 
			. "<table><tr><td bgcolor=\"$titlebgcolor\"><b>$subject</b><br>by "
			. user_id_to_hyperlinked_full_name($dbh,$reviewer_id,$cgi_full_path)
			. $email_text
			. $date
			. $review_id_text
			. $homepage_text
			. "</td></tr>\n"
		      . "<tr><td></table>"
		      . $s
		      . "$review<p>\n"
          . "$warning<p>\n"
		      . $sig_text
		      . "<p><ul><i> The above $what is copyrighted by its author, and is "
		      . "copylefted under the following license:<br>$pr_lic</i></ul>"
		      . ("</ul>" x $depth) ;
}

sub describe_score()
{
	my ($s,$what,$homepath) = @_;
	my $int_score;
	$int_score = 0;
	if ($s>0.5) {$int_score = 1;}
	if ($s>1.5) {$int_score = 2;}
	if ($s>2.5) {$int_score = 3;}
	if ($s>3.5) {$int_score = 4;}
	if ($s>4.5) {$int_score = 5;}
	if ($s>5.5) {$int_score = 6;}
	if ($int_score <= 0) {
	  $describe =  "substandard";
	}
	else {
	  if ($s <= 1.5) {
	    $describe = "typical";
	  }
	  else {
	    $x = 100. - 20. * exp( - ($s - 2.)*log(2.));
	    $x = int ($x + 0.50001);
	    $describe = "better than " . $x . "\%";
	  }
	}
	return "<table><tr>"
		. "<td><img src=\"$homepath/spiral"
		. $int_score . ".gif\" width=\"25\" height=\"18\"</td>"
		. "<td><b>$what</b><br>$describe</td> "
		. "</tr></table>\n";
}

sub PrintHeaderHTML($$)
{
	my ($homepath,$title) = @_;
	print HeaderHTML($homepath,$title);
}

sub HeaderHTML($$)
{
	my ($homepath,$title) = @_;

    return <<__HTML__;
<HTML><BODY><HEAD>
<TITLE>$title</TITLE>
<LINK rel="stylesheet" href="$homepath/assayer.css" type="text/css">
<META HTTP-EQUIV="Pragma" CONTENT="no-cache">
</HEAD>
<BODY bgcolor="white">
__HTML__
} 


sub PrintBannerHTML($)
{
	my ($homepath) = @_;
	print BannerHTML($homepath);
}

sub BannerHTML($)
{
	my ($homepath) = @_;
    return <<__HTML__;

 	<a href="http://theassayer.org"><img border="0" src="$homepath/logob.png" width="499" height="84"
	 alt="The Assayer - book reviews and discussion for the free-information renaissance"></a><br>

__HTML__
}

sub PrintFooterHTML($)
{
	my ($homepath) = @_;
	print FooterHTML($homepath);
}

sub FooterHTML($)
{
	my ($homepath) = @_;
    return <<__HTML__;

	<table width="500"><tr><td>
	<div align="center"><img src="$homepath/footerimage.gif" width="493" height="38"></div>
	</td></tr></table>

	<table width="500"><tr><td><font color="gray">
		The contents of this web page, except the parts contributed by
		members of The Assayer, are copyright (c) 2000 by Benjamin Crowell, and
		are copyleft licensed under the Open Publication License 1.0, without options
		A or B.
		</td></tr></table>
    </body></HTML>

__HTML__
} # End of PrintFooterHTML

sub toolbar_HTML($)
{
	my ($homepath) = @_;
    return <<__HTML__;
		<table width="500"><tr><td>
        <div align="right"><table><tr><td bgcolor="#dddddd">
        		<a href="$homepath">home</a>
        		 &nbsp;&nbsp; <a href="$cgi_full_path/ashelp.cgi">help</a>
        		 &nbsp;&nbsp; <a href="$cgi_full_path/aslinks.cgi">links</a>
        		 &nbsp;&nbsp; <a href="$cgi_full_path/aslogin.cgi">log in</a>
        		 &nbsp;&nbsp; <a href="$cgi_full_path/aslogout.cgi">log out</a>
        		 &nbsp;&nbsp; <a href="$cgi_full_path/asreview0.cgi">add or review a book</a>
        		 &nbsp;&nbsp; <a href="http://www.lightandmatter.com/area4author.html">contact</a>
        </td></tr></table></div>
        <div align="right"><table><tr><td bgcolor="#dddddd">
        		<b>Browse by</b>
        		 &nbsp;&nbsp;  <a href="$cgi_full_path/asbrowsesubject.cgi">subject</a>
        		 &nbsp;&nbsp;  <a href="$cgi_full_path/asbrowseauthor.cgi">author</a>
        		 &nbsp;&nbsp;  <a href="$cgi_full_path/asbrowsetitle.cgi">title</a>
        		 &nbsp;&nbsp;  <a href="$cgi_full_path/asbrowsereviewer.cgi">reviewer</a>
        </td></tr></table></div>
        </td></tr></table>
__HTML__
}



return 1;
