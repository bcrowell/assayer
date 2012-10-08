#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "cgi-lib.pl";


require "ashtmlutil.pl";
require "asdbutil.pl";
require "asgetmethod.pl";
require "asinstallation.pl";
require "asuinfo.pl";
require "aslog.pl";

use CGI;
use DBI;


$co = new CGI;

$title = 'The Assayer';

PrintHTTPHeader();
PrintHeaderHTML($homepath,$title);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

$bogus = 0;
$connected = 0;

if (! $bogus) {
    $dbh = DBI->connect($dsn,$db_user,db_password(),{PrintError=>0,RaiseError=>0}) 
    		or $bogus="Error connecting to database.";
}
if (! $bogus) {
    $connected = 1;
}
if (! $bogus) {
   
  if (1) {
	if ($reader_login = seems_loggedIn($co)) {
	  #print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$reader_login) . " logged in.";
	  print "User " . user_id_to_hyperlinked_full_name($dbh,
                             user_login_to_id($reader_login,$dbh),$cgi_full_path) . " logged in.";
	}
	else {
	  # print "Not logged in."; # This would get printed, erroneously, whenever the user hit the site for the first time during a browsing session. Dunno why.
	}
	print "<p>\n";
  }
  
}


#---------------------------------------------------------------------------------------------

print '<table width="800">';
$results = get_latest_from_log($dbh,'review');
if ((! $results->{'bogus'}) && $results->{'title'} && !($results->{'user_link'}=~m/login\=0/)) {
  print "<tr><td>The latest user-submitted review:</td><td>".$results->{'book_link'}.", reviewed by ".$results->{'user_link'}."</td></tr>\n";
}
else {
  #print "<p>error=$bogus</p>\n";
}
$results = get_latest_from_log($dbh,'newbook');
if ((! $results->{'bogus'}) && $results->{'title'}) {
  $bk_id = $results->{'bk_id'};
	@auref_id_array = get_aurefs($bk_id,$dbh);
  @authors = ();
	foreach $auref_id(@auref_id_array) {
    $au_id = au_ref_to_raw_id($auref_id,$dbh);
		if ($au_id < 0) {$err=$au_id;} else {$err=0;}
	  ($last,$first,$suffix) = get_name($au_id,$dbh);
    push @authors,printable_author($first,$last,$suffix,0);
	}
  $byline = join(',',@authors);
  print "<tr><td>The latest book to be entered in the database:</td><td>".$results->{'book_link'}.", by $byline</td></tr>\n";
}
$results = get_random_book($dbh,2);
if ((! $results->{'bogus'}) && $results->{'title'}) {
  print "<tr><td>A random free book:</td><td>".$results->{'book_link'}."</td></tr>\n";
}
print '</table>';


#---------------------------------------------------------------------------------------------

print &homepage_html;

#---------------------------------------------------------------------------------------------


PrintFooterHTML($homepath);

if ($connected) {
    if (ref $sth) {$sth->finish}
    $dbh->disconnect;
}

#-------------------------------------------------------------------------------------------------------------------
sub get_random_book {
  my $dbh = shift;
  my $min_free = shift;

	  $selectstmt = "SELECT title,bk_id,freedom FROM bk_tbl WHERE title LIKE "
	  	. $dbh->quote($search . "%") . " AND freedom >= '$min_free' ORDER BY title";


  # Find the greatest bk_id:
	$selectstmt = "SELECT bk_id FROM bk_tbl ORDER BY bk_id DESC";
  $sth = $dbh->prepare($selectstmt) or $bogus=1;
  if (! $bogus) {
    $sth->execute() or $bogus=2;
  }
  @row = $sth->fetchrow_array();
  $greatest_bk_id = @row[0];

  if (!$bogus) {
    $count = 0;
    do {
      $bk_id = int (rand($greatest_bk_id+1)); # random number between 0 and greatest_bk_id
	    $selectstmt = "SELECT title,freedom FROM bk_tbl WHERE bk_id LIKE $bk_id";
      $sth = $dbh->prepare($selectstmt) or $bogus=3;
      if (!$bogus) {$sth->execute() or $bogus=4}
      if (!$bogus) {
        @row = $sth->fetchrow_array();
        ($title,$freedom) = @row;
      }
      $count++;
      if ($count>1000) {$bogus=5}
    } while (!$bogus && $freedom<$min_free);
  }

  if (!$bogus) {
	  my $selectstmt = "SELECT bkref_id FROM bkref_tbl WHERE bk_id LIKE '$bk_id'";
    $sth = $dbh->prepare($selectstmt) or $bogus=6;
    if (! $bogus) {
      $sth->execute() or $bogus=7;
    }
    @row = $sth->fetchrow_array() or $bogus=8;
  }
  if (!$bogus) {
    $bkref_id = @row[0];
    $title = get_title($bk_id,$dbh);
    %results = (
	  	'bk_id'=>$bk_id,
		  'bkref_id'=>$bkref_id,
      'title'=>$title,
	    'book_link'=>'<a href="'.$cgi_full_path.'/asbook.cgi?book='.$bkref_id.'">'.$title."</a>",

    );
    return \%results;
  }
  else {
    return {'bogus'=>$bogus};
  }

}

sub get_latest_from_log {
  my $dbh = shift;
  my $what = shift; # = newbook or review
  my %results = ();
  $bogus = '';
  $selectstmt = "SELECT log_key,user_id,what,bkref_id,bk_id,auref_id,au_id,review_id,user_id_affected,description,clock"
                 ." FROM log_tbl WHERE what LIKE '$what' ORDER BY log_key DESC";
  $sth = $dbh->prepare($selectstmt) or $bogus=4;
  if (! $bogus) {
    $sth->execute() or $bogus=5;
  }
  if (! $bogus) {
    $count = 0;
    $n=10;
    while ((@row = $sth->fetchrow_array()) && $count<$n) {
      ++$count;
      ($results{'log_key'},$results{'user_id'},$results{'what'},$results{'bkref_id'},$results{'bk_id'},
       $results{'auref_id'},$results{'au_id'},$results{'review_id'},$results{'user_id_affected'},
       $results{'description'},$results{'when'}) 
          = @row;
      if ($results{'user_id'}) {
  	    $results{'login'} = get_login_of_other_user($results{'user_id'},$dbh);
        $results{'user_link'}=user_id_to_hyperlinked_full_name($dbh,$results{'user_id'},$cgi_full_path);
		  }
			if ($results{'bk_id'}) {
        $results{'title'}=get_title($results{'bk_id'},$dbh);
	      $results{'book_link'}='<a href="'.$cgi_full_path.'/asbook.cgi?book='.$results{'bkref_id'}.'">'
                                            .$results{'title'}."</a>";

      }
      $no_good = 0;
      if ($what eq 'review') {
        $no_good = 1; # guilty until proven innocent
        $selectstmt2 = "SELECT count(*) FROM review_tbl WHERE bkref_id = '$results{bkref_id}'";
        $sth2 = $dbh->prepare($selectstmt2) or $bogus=6;
        if (! $bogus) {
          $sth2->execute() or $bogus=$DBI::errstr;
        }
        if (! $bogus) {
          @row = $sth->fetchrow_array();
          $nrev = $row[0];
          $no_good=0 if $nrev>=1;
        }
      }
      last unless $no_good;
    }
  }
  $results{'bogus'} = $bogus;
	return \%results;
}
#-------------------------------------------------------------------------------------------------------------------

sub homepage_html {
return <<HOMEPAGE;
<p/>	<table width="1000"><tr><td valign="top" width="390">
	<h2>Welcome</h2>
    The Assayer is the web's largest catalog of books whose authors have made them available for free. Users can also submit reviews.
    The site has been around since 2000, and is a particularly good place to find free books about math, science, and computers.
    If you're looking for old books that have fallen into the public domain, you're more likely to find what you want at
    <a href="http://www.gutenberg.org/">Project Gutenberg</a>.
  <p>
	You can browse the catalog by clicking on a link in the bar above.
	You need to become a member if you want to post your own reviews,
	add books to the database,
	or participate in discussions of books.  
	<a href="http://www.theassayer.org/cgi-bin/asnewmember.cgi">Click here</a>
	to become a member. Membership is free, and the only personal information you need to give
	is your e-mail address. (We won't spam you, and other visitors will only be able to see
  your address if you say it's OK.)
	<p>Members can also reply to each other's reviews, creating a discussion of
	a book, and can choose to receive e-mail notifications when new discussion has occurred
	about a particular book.<p>
	Click on the <i>Help</i> link above for more detailed information on the purpose of The Assayer and
	how to use it.
</td><td>
<h2>Brown Signs California Bill for Free Textbooks</h2>
<p>
California Governor Jerry Brown has
 <a href="http://latimesblogs.latimes.com/california-politics/2012/09/free-digital-textbooks-to-be-made-available-after-gov-jerry-brown-signs-bills.html">signed</a>
<a href="http://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201120120SB1052">SB 1052</a> and
<a href="http://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201120120SB1053">1053</a>, 
authored by state senator Darrell Steinberg, to create free textbooks for 50 core
lower-division college
courses.</p>
<p> SB 1052 creates a California Open Education Resources Council, made up of faculty from the
UC, Cal State, and community college systems. The council is supposed to pick 50 core courses.
They are then to establish a "competitive request-for-proposal process
in which faculty members, publishers, and other interested parties would apply for funds
to produce, in 2013, 50 high-quality, affordable, digital open source textbooks and related
materials, meeting specified requirements." The bill doesn't become operative unless the legislature funds it --
a questionable prospect in California's current political situation. The books could be either newly produced
(which seems unlikely, given the 1-year time frame stated) or existing ones that the state would buy or have
free access to. Unlike former Gov. Schwarzenegger's failed K-12 free textbook program, this one specifically
defines what it means by "open source," rather than using the term as a feel-good phrase; books have to be
under a CC-BY (or CC-BY-SA?) license, in XML format. They're supposed to be modularized and conform to state and W3C
accessibility guidelines. Faculty would not be required to use the free books.
</p>
                       <p align="right"><i>September 28, 2012</i></p>
<h2>Apple Taking the Proprietary Road with eBooks?</h2>
<p>
Today Apple announced easy-to-use software for creating electronic textbooks.
Picking through the typically overblown Apple hype, there are some disturbing signs that Apple may be heading down the same road that Amazon has
taken by trying to make books proprietary and only availale from a single distributor.
Previously, Apple had hitched its wagon to the open Epub standard as the format for its electronic books, whereas Amazon
uses their own format. <a href="http://techcrunch.com/2012/01/19/apple-textbook-event/">Apparently</a> they are now using a format that is similar to, but not the same as
Epub 3: "Books are not technically in the EPUB format, but they borrow from it (likely EPUB 3). Certain interactive
elements of the books require the files to be done in the slightly different iBooks format, Apple says."
No word on interoperability. Embrace and extend, anyone? They have also announced that some titles, including E.O. Wilson's
Life on Earth, will only be available electronically from them. This is the same ugly lock-in tactic that Amazon has
already been trying to pull. The licensing agreement for Apple's authoring software also 
<a href="http://www.engadget.com/2012/01/19/apples-ibooks-author-hands-on/#continued">states</a> that any book you create
with it must be distributed exclusively through Apple. It appears that B&amp;N may be the only remaining ebook publisher that is committed to
open formats and nonexclusive distribution.
</p>
                       <p align="right"><i>January 19, 2012</i></p>
<h2>California State Senator Pushes for Free Textbooks</h2>
<p>
Although former Governor Schwarzenegger's free digital textbook initiative for K-12 education was a failure,
state senator Darrell Steinberg has a 
<a href="http://sd06.senate.ca.gov/news/2011-12-13-steinberg-proposal-slashes-textbook-costs-california-college-students">new idea</a> for the state-subsidized
publication of college textbooks. (Details are given in the PDF files linked to from the bottom of the page.) Newspaper editorials
seem positive.<a href="http://www.sacbee.com/2011/12/14/4121224/darrell-steinberg-pushes-open.html">[1]</a>,
<a href="http://www.mercurynews.com/opinion/ci_19533735">[2]</a>.
</p>
                       <p align="right"><i>January 4, 2012</i></p>
<h2>B&amp;N Stands up to Amazon on Lock-In</h2>
<p>
Amazon has been trying to negotiate exclusive deals with publishers to sell e-books;
obviously their dream is to achieve lock-in, so that their customers become their captives.
Barnes and Noble is <a href="http://www.pcmag.com/article2/0,2817,2394365,00.asp#fbid=jCpZfrx0MmI">responding</a>
by refusing to sell paper books by publishers, such as DC Comics, who won't let them
sell the electronic version.
</p>
                       <p align="right"><i>October 9, 2011</i></p>
<h2>Illegal Fees for Disappearing Books</h2>
<p>
Publishers such as Pearson have been <a href="http://www.sfgate.com/cgi-bin/article.cgi?f=%2Fc%2Fa%2F2011%2F08%2F11%2FMN1L1KLC3H.DTL">illegally charging</a>
California community college students for required access to online books, which the students can no longer access once the semester is over.
A task force, packed with industry representatives, met behind closed doors and recommended changing the law.
</p>
                       <p align="right"><i>September 10, 2011</i></p>
<h2>Michael Hart, 1947-2011</h2>
<p>
Project Gutenberg founder and electronic book pioneer Michael Hart has died of a heart attack.
He started his life's work by typing the U.S. Declaration of Independence into a computer in 1971
and making it available for free downloading.
</p>
                       <p align="right"><i>September 6, 2011</i></p>
<h2>NSF UTMOST Project</h2>
<p>
NSF has funded a grant, with Jason Grout at Drake as PI, for a project called <a href="http://artsci.drake.edu/grout/doku.php/grants">UTMOST</a>:
Undergraduate Teaching in Mathematics with Open Software and Textbooks. The idea is to take
preexisting free math textbooks and convert them into worksheets for the open-source math
program Sage. Students can then use a computer aided algebra system to try calculations
on the same screen from which they're reading the book itself.
</p>
                       <p align="right"><i>June 7, 2011</i></p>

<h2>Results of Textbook Initiative Announced</h2>
<p> 
The <a href="http://www.clrn.org/fdti/">results</a> of California Governor Schwarzenegger's
<a href="http://news.bbc.co.uk/2/hi/americas/8090450.stm">Free Digital Textbook Initiative</a>
were announced today at a <a href="http://cetpa-k12.org/pub/htdocs/symposiuminfo.html">symposium</a>
near Los Angeles, which I attended. Participants included open-source types from <a href="http://www.curriki.org/">Curriki</a>,
<a href="http://about.ck12.org/">CK-12</a>, and <a href="http://cnx.org/">Connexions</a>, as well as
teachers, politicians, IT folks, hardware vendors, and textbook publishers.
Sixteen free high school math and science textbooks were submitted, and were evaluated as
to whether they met state content standards. Almost all the books were Creative Commons-licensed works produced
by individuals and nonprofits, with the exception of a consumable biology workbook from Pearson.
</p>
<p>
The genesis of Schwarzenegger's initiative was the current state budget crisis, so it was entertaining
to see the various interests jockeying for a bigger slice of a shrinking pie. Dell and Apple would like
to see funds for textbooks freed up so that they can be used to buy computers on which students can
access the free books, and they had demos with actual grade school kids (highly intent on their Apple laptops)
and high school kids (chewing gum and socializing in front of their Dell netbooks).
</p>
<p>The traditional publishers
didn't seem to be able to decide how to present themselves. Pearson's rep referred to its workbook as "free and
open-source" (it's not open-source). Houghton Mifflin Harcourt's rep, when questioned about DRM, said that her
company was committed to DRM, and envisioned its DRM'd materials being mixed and matched with open-source ones.
Both said that they wanted to be service providers (think Red Hat), rather than just content providers (a la
Microsoft) -- but, hey, they produce really great content, too. Apple and Dell's reps argued for open formats
such as XML.
</p>
<p>
Nobody seemed sure about the implications of the settlement in the <a href="http://www.decentschools.org/">Williams case</a>,             
which requires equal access to books for all students. Will poor students be locked out because they don't have computers?
Schwarzenegger's proposed solution is to  <a href="http://www.mercurynews.com/opinion/ci_12536333?nclick_check=1">print out books as needed</a>, but
Murugan Pal from CK-12 pointed out that current state law allows a school to use textbook funds to pay 
\$80 for a book from a commercial publisher, but forbids it to pay \$10 to print out a copy of a free book at Kinko's.
</p>
<p>
As a community college professor, I was surprised by the level of top-down control that seems to be taken for granted
in the K-12 system. There was a lot of concern about whether a digital textbook that had been blessed by the state
would then change overnight, falling from its state of grace. CLRN, which is running the evaluation process, says
that they want authors to freeze their books for two years after the evaluation. This seems to run counter to
the Governor's criticism of traditional textbooks as "antiquated."
Pal from CK-12 pointed out that although CK-12 is a wiki, it's not open for editing by all, like Wikipedia. But
teacher Lainie Rowell recounted the charming story of the Lousiana students who found out that there was
no Wikipedia article about the Pitot House, and proceeded to <a href="http://en.wikipedia.org/wiki/Pitot_house">write one</a> as
a class.
</p>
<p>
A big change since I went to high school in California is that many high schools are offering online classes, and
over-scheduled, affluent students seem to love being able to fit them in between soccer and SAT prep classes.
Orange Country Superintendent of Schools William Habermehl proposed that since budget cuts will force schools to put
42 students in an Algebra 1 class, they could have 30 kids (the ones who need more help) in the classroom, and
the other 12 taking the class online. Somehow this sounds to me like making the teacher teach two classes for the
price of one, and as a parent I'm a little worried about what it would be like if one of my daughters was in the
group of 12 deemed not to need any help.
</p>
                       <p align="right"><i>August 11, 2009</i></p>
<h2>New York Times on Electronic Textbooks</h2>
<p>
The New York Times has a good <a href="http://www.nytimes.com/2009/08/09/education/09textbook.html?hp">article</a>
on electronic textbooks, including the California initiative.
                           <p align="right"><i>August 8, 2009</i></p>
</p>
<h2>California Initiative for Free Textbooks</h2>
<p>
Motivated by the California state budget crisis, Governor Schwarzenegger has announced a <a href="http://clrn.org/FDTI/index.cfm">Free Digital Textbook Initiative</a>,
which is producing a list of free, online high school math and science textbooks that are aligned with state content standards.
The list will be announced June 16, and the intention is to have the books used in classrooms in fall 2009.
 The idea seems to be to look for preexisting free books put out by individuals. 
<a href="http://arstechnica.com/open-source/news/2009/05/california-launches-open-source-digital-textbook-initiative.ars">This</a> article has some
useful background, but it mistakenly suggests that the arduous state adoption process will be an obstacle to the FDTI; statewide adoption
only applies to K-8, but FDTI is doing high-school books.
There was a previous, unsuccessful
effort called <a href="http://www.opensourcetext.org/">COSTP</a>, which tried to produce a history textbook using
<a href="http://wikibooks.org/">Wikibooks</a>. <a href="http://news.bbc.co.uk/2/hi/americas/8090450.stm">Here</a>
is a BBC article about the present effort, and <a href="http://www.mercurynews.com/opinion/ci_12536333">here</a> is a newspaper opinion piece
by the Governor. <a href="http://www.gov.ca.gov/speech/12462/">This</a> is a transcript of a speech by the Governor, with some interesting Q&A
at the end.
Twenty books were submitted (<a href="http://www.gov.ca.gov/press-release/12542/">press release</a>,
<a href="http://bbridges51.edublogs.org/2009/06/16/free-digital-textbook-initiative-complete-submission-list/">links</a>).
The four books from traditional publisher Pearson are consumable workbooks, not actual textbooks.

</p>
                           <p align="right"><i>June 16, 2009</i></p>
<h2>Flat World Knowledge</h2>
<p>
<a href="http://www.flatworldknowledge.com/minisite/about.html">Flat World Knowledge</a> is a new startup company
that is distributing CC-BY-NC-licensed textbooks via free digital downloads and print on demand.
Professors can produce customized versions of the texts by, e.g., cutting chapters they don't intend to cover,
and can edit "down to the sentence level." They're currently at the testing stage, and plan a full commercial launch
in 2009. There doesn't seem to be any information on their site about what books they've got lined up. The restriction
to the CC-BY-NC license seems unfortunate to me, since it locks out a whole body of books that are licensed under CC-BY, or
under licenses like the GFDL (used, e.g., by Wikipedia) that are compatible with CC-BY.
</p>
                          <p align="right"><i>April 25, 2008</i></p>
<h2>Open Text Book</h2>
<p>
<a href="http://blog.opentextbook.org/about/">Open Text Book</a> is a new web site that catalogs textbooks that are free-as-in-speech.
</p>
                          <p align="right"><i>October 4, 2007</i></p>
<h2>Manybooks</h2>
<p>
<a href="http://manybooks.net/">Manybooks</a> is a web site for free books, as well as shorter works. 
They seem to have started by converting the books on the Project Gutenberg DVD into a variety of
convenient formats. In addition, they have a pretty good catalog of science fiction novels and short
stories whose authors have made them free online.
</p>
                          <p align="right"><i>September 15, 2007</i></p>
<h2>Scribd</h2>
<p>
<a href="http://scribd.com">Scribd</a> is a new service that aims to do for the print medium
what youtube did for video. It could be a useful no-cost, no-hassle way for authors of free
books to distribute them online, without having to  maintain their own web sites. Books are
automatically translated into a variety of formats, and by default users are shown a flash interface
that lets them flip through the book page by page. My own experience with Mac/Linux/Firefox was
that the flash interface didn't work very well, but YMMV, and I'm sure the glitches will get worked out
over time.
</p>
                          <p align="right"><i>August 11, 2007</i></p>
<h2>Ink Textbooks</h2>
<p><a href="http://www.inktextbooks.com">Ink Textbooks</a> is a new textbook publisher that plans
to sell books inexpensively in print, and also make the same books available for free online in
digital form. They require an exclusive license from the author, so their system isn't compatible
with Creative Commons or GFDL-licensed books.
</p>
                          <p align="right"><i>July 28, 2007</i></p>
<h2>Free Curricula Center</h2>
<p>The <a href="http://www.freecurricula.org/">Free Curricula Center</a> is a new project that is going to
try to get people to cooperate on writing free textbooks.</p>
                          <p align="right"><i>Mar. 23, 2006</i></p>

<h2>An Infrastructure for Free Books</h2>
<p><a href="http://www.lightandmatter.com/article/infrastructure.html">Here</a> is an article I wrote about what's going on these days in the world
of free books. From the article:
<i>With the cost of college textbooks up 62% over the last decade,
 pressure is building for an alternative model of publishing: the free book. Five years ago, an
 author had to be very persistent --- maybe even a little crazy --- to try the new approach. But
 now a whole new infrastructure is springing up to make it easier.</i></p>
                          <p align="right"><i>Dec. 15, 2005</i></p>
<h2>1000 Free Books</h2>
<p>The Assayer's catalog has now passed the milestone of 1000 free books.</p>
                          <p align="right"><i>Dec. 12, 2005</i></p>
<h2>A Proposal For Governnment-Financed Textbooks</h2>
<p>The Center for Economic and Policy Research has published <a href="http://www.cepr.net/publications/textbook_2005_09.pdf">a
proposal</a> for the government to finance the production of textbooks, on the condition that they
would then be placed into the public domain. Personally, it raises my libertarian hackles, but
it's true that one of my favorite physics textbooks, PSSC Physics, was created as a government-financed project.
</p>
													<p align="right"><i>June 22, 2005</i></p>
<h2>CALPIRG Cheaper Textbooks Campaign</h2>
<p>Lindsay Hopkins (lindsay dot hopkins at gmail dot com)
 contacted me today about the
CALPIRG Cheaper Textbooks Campaign, of which she's the
statewide coordinator. <a href="http://calpirg.org/">CALPIRG</a>, the
California Public Interest Research Group, is an organization of
students in the University of California System. Their Cheaper
Textbooks Campaign is interested in putting together a how-to
manual on writing your own free textbook.</p>
													<p align="right"><i>Apr. 21, 2005</i></p>
<h2>Free Textbook Project</h2>
<p>I've been contacted by Joshua Gay about a new endeavor called
the <a href="http://www.freetextbookproject.org">Free Textbook
Project</a>, which looks very promising.</p>
													<p align="right"><i>Apr. 8, 2005</i></p>
<h2>Real Names Now Required</h2>
<p>
I've been seeing an increasing number of "reviews" that are
actually the author's promotional blurb. These are usually painfully
obvious, and I delete them immediately. However, I've decided to start
requiring new users to supply their real names when they set up an
account. Of course, there's nothing to stop them from faking this
information. When you read a review, think critically about whether
the reviewer appears trustworthy. It's usually a sign of trouble if
the reviewer has only ever written a single review on The Assayer, and
the review reads like promotional material.
</p>
													<p align="right"><i>Dec. 16, 2004</i></p>
<h2>3000th Member</h2>
<p>The Assayer's membership passed the 3k mark with member <a href="http://www.theassayer.org/cgi-bin/asuser.cgi?login=jameslee">jameslee</a>. Thanks, everybody, for all of your continuing contributions to The Assayer!
</p
													<p align="right"><i>Aug. 10, 2004</i></p>

<h2>No New Non-Free Books</h2>
<p>When I first created The Assayer, I decided as an afterthought to allow people to review non-free books
here. I didn't want to come off as a fire-breathing zealout, and I thought an exclusionary policy toward
non-free books might cause a lot of arguments about what qualified as free. Since then, the site's
catalog of free books has grown greatly, and gradually more and more of them are getting reviewed by
TA members. It's become clear to me, however, that accepting reviews of non-free books is not producing
anything worthwhile (Amazon.com is the venue for that), and is taking up a lot of my time and
resources. In particular, there have been a lot of cases where the authors of a non-free book posted
thinly veiled promotional material in the guise of a review. I've also noticed that at least one
person has cross-posted reviews here and on Amazon.com, despite the prominent warnings on this
site not to do that because Amazon owns the copyrights on reviews submitted to them. That creates
a potential for legal problems that I don't need. Therefore I've decided to stop accepting new
reviews of non-free books. Reviews of non-free books that are already in the database will be retained,
except in cases where they appear to violate Amazon's copyright. (Note added Oct. 2005: It appears that
Amazon.com no longer claims copyright on reviews, but only a royalty-free license to use them.)
</p>
													<p align="right"><i>Feb. 15, 2004</i></p>

<h2>New Subject Categories</h2>
<p>The number of books in Library of Congress category QA, math and computer science,
is getting huge, so I've introduced smaller subcategories, which you'll see when
you browse by subject. I've done my best to place as many math and computer books
as possible in appropriate subcategories, but some of them get pretty esoteric, so
feel free to help out if you have the necessary expertise; to place a book in
a subcategory, just click on its "edit information about this book" link, and it
will show you the legal choices.</p>
													<p align="right"><i>Jan. 11, 2004</i></p>

<h2>Warning Messages Eliminated</h2>
<p>I didn't receive any more comments about the warning messages (see below). I've decided
to eliminate them.</p>
													<p align="right"><i>Nov. 8, 2003</i></p>

<h2>Comments on Warning Messages?</h2>
<p>I recently added a feature to The Assayer that some might consider a bug :-)
When you're viewing a review, you get an error message if the reviewer hasn't supplied a
real name, hasn't supplied a bio, or has only every written one review. One user of the
Assayer has e-mailed me to say he hates the warnings. Does anyone else have comments?
The warnings are meant to handle a situation that is unfortunately pretty common: the
author of a book submits a review of his own book. Am I overreacting? Let me know!
Click on the <i>contact</i> link above for info on how to e-mail me, and please let
me know if it's OK to quote you and use your name in this space. Based on the one
user's feedback, I've already made the warnings less prominent.
</p>


<h2>Two Licenses Eliminated</h2>
<p>I've decided that it was a bad idea to create two of my own <a href="#homebrew">homebrewed licenses</a>
for reviews, and I will no longer be accepting new reviews under these licenses. I think the proliferation
of licenses is a bad thing, and I'm also not a lawyer, so I don't know if these licenses have legal
defects.</p>
<p>The default license for reviews is still the 
<a href="http://opencontent.org">OPL without options A and B</a>. This may seem strange, since its creator,
Dave Wiley, recommends using a <a href="http://creativecommons.org">Creative Commons</a> license
for new works instead of the OPL. However, it seems to me that the OPL is more appropriate for
book reviews, because it requires modified versions to be given out with a description of the modifications,
which is important in order to keep people from changing a reviewer's words to misrepresent the reviewer's
opinions.</p>
													<p align="right"><i>Aug. 29, 2003</i></p>


<h2>OpenContent Shuts Down</h2>
Dave Wiley, a pioneer in the application of copyleft licenses to non-software
publications, is now recommending that people use <a href="http://creativecommons.org">Creative
Commons</a> licenses instead of the Open Publication licenses (OPL).
The <a href="http://opencontent.org">OpenContent.org</a> site
will remain up, and still has the text of the Open Publication licenses.

<h2>Open E-<b style="color:black;background-color:#A0FFFF">Book</b> Format Proposed</h2>
        Here are some links discussing a recent proposal for an open format for e-books:
													<a href="http://12.108.175.91/ebookweb/discuss/msgReader$2165">[1]</a>,
													<a href="http://www.oreillynet.com/pub/wlg/3227">[2]</a>,
													<a href="http://www.blackmask.com/archive/0030522.html">[3]</a>,
													<a href="http://slashdot.org/article.pl?sid=03/06/05/0244203">[4]</a>.
													<p align="right"><i>Jun. 5, 2003</i></p>

													<h2>GFDL not free?</h2>
													There's been some <a href="http://slashdot.org/article.pl?sid=03/04/20/1357236">discussion</a>
about whether the GFDL license actually fails to qualify as a true free-information
license.
<p align="right"><i>Apr. 24, 2003</i></p>

<h2>Internet <b style="color:black;background-color:#A0FFFF">Book</b> List</h2>

<a href="http://www.iblist.com">Internet <b style="color:black;background-color:#A0FFFF">Book</b> List</a> is a new site for user-submitted
<b style="color:black;background-color:#A0FFFF">book</b> reviews. It's been <a href="http://slashdot.org/article.pl?sid=03/03/07/1343205">
													discussed</a> on Slashdot.
													<p align="right"><i>Mar. 7, 2003</i></p>


<h2>Books as Sewage?</h2>
Arnold Kling has an
<a href="http://www.techcentralstation.com/1051/techwrapper.jsp?PID=1051-250&CID=1051-011303A">
article</a> with a skeptical take on the idea of free-information publishing.
It's been <a href="http://slashdot.org/article.pl?sid=03/01/15/154254">discussed</a>
													on Slashdot.
													<p align="right"><i>Jan. 15, 2003</i></p>
													

													<h2>An Article About Free Books</h2>

													<a href="http://www.lightandmatter.com/article/sneaky.html">Here's an article</a> I wrote
about what's new in the world of free books. It was recently
													<a href="http://slashdot.org/article.pl?sid=02/10/21/1941237&mode=nested&tid=96">discussed</a>
													 on Slashdot.<p align="right"><i>Oct. 21, 2002</i></p>



	<h2>1000th Member Joins The Assayer</h2>
	The Assayer's membership moved into four-digit territory. Go team!
       <p align="right"><i>May 3, 2002</i></p>

	<h2>Green Tea Press</h2>
	It used to be that if you made a list of publishers who understood
	free information, there was only one: O'Reilly. That's changed a little,
	e.g., Addison-Wesley has print-published <a href="http://www.pragmaticprogrammer.com/ruby/downloads/book.html">Programming Ruby</a>, which is also free
	in digital form. But even so, any addition to this short list is newsworthy.
	<a href="http://greenteapress.com/">Green Tea Press</a> is a new print
	publishing house started up by Lisa Cutler and Allen Downey, one of the
	authors of <a href="http://greenteapress.com/thinkpython.html">How to Think
	Like a Computer Scientist</a>, a wonderful book which also happens to be
	free in digital form. It's good to see an initiative like this coming from
	an author, and it will be interesting to see if the digitization of
	the publishing industry leads to a more author-centered approach. Best
	wishes go out to Lisa and Allen in their new endeavor!
       <p align="right"><i>Feb. 11, 2002</i></p>
	<h2>New Licenses For Reviews</h2><a name="homebrew">
	Based on requests from users, I've added two more options for
	the licenses of reviews: a
        BSD-style license called the <a href="http://www.theassayer.org/freeword
.txt">Free
        Word</a> license, and another called the
        <a href="http://www.theassayer.org/soapbox.txt">Soapbox license</a>, 
	which
        is intended for use with writing that expresses opinions, in order
        to ensure that it can't be modified so as to misrepresent the
        opinions of the original author. Both of these are homebrewed
	licenses. The Free Word is really nothing but the BSD license, with
	a couple of minor changes to adapt it to writing that isn't software.
	The Soapbox license is my attempt to address reviewers' concerns,
	without going as far as a verbatim-copying-only license,
	which I think would be inappropriate for a free-information site
	like The Assayer.
	<p align="right"><i>Feb. 1, 2002</i></p>
	<h2>TA's Most Prolific New Member</h2>
	The Assayer has a prolific new reviewer! Check out
	the eclectic work of <a href="http://www.theassayer.org/cgi-bin/asuser.cgi?login=voiceofthewhirlwind">voiceofthewhirlwind</a>, with reviews on
	topics from history to crime fiction to technology. 
	<p align="right"><i>Jan. 18, 2002</i></p>
	<h2>More Choices of Licenses?</h2>
	A TA user e-mailed me recently to suggest adding a third license
	to the menu you choose from when submitting a review. His
	concern was that both the GFDL and the OPL allow modification,
	which might allow people to make it sound as though you said things
	you didn't. Although both licenses require changes to be documented,
	the concern is a valid one, since TA deals with opinion, not
	software documentation, which is what GFDL in particular is tuned
	up for. Would it be a good thing to have a third choice, basically
	saying that the review can be copied but not modified? If you have
	comments, please e-mail them to me at crowell02 at
	lightandmatter.NOSPAM.com, and I'll post them on TA.	
	<p align="right"><i>B. Crowell, Jan. 18, 2002</i></p>
	User Lucas Walter says "I was going to suggest the same thing, maybe add OPL _with_ option A
(minor alterations permitted, but no semantic changes)."
	<p align="right"><i>Jan. 18, 2002</i></p>
	Another possibility, for those who prefer it, is a BSD-style license
	of some kind. IMHO this is <i>more</i> free than GPL-style licenses
	such as the GFDL and OPL-without-options, although "freer" isn't
	necessarily the same as better :-) 
	<p align="right"><i>B. Crowell, Jan. 18, 2002</i></p>

	<h2>The Assayer Featured in Indian Newspaper</h2>
	The Assayer was prominently featured in a recent
	<a href="http://www.hinduonnet.com/thehindu/2001/07/19/stories/08190001.htm">article</a> in the Indian newspaper <i>The Hindu</i>. A big thank you
	goes out to reporter J. Murali! 
	<p align="right"><i>July 19, 2001.</i></p>

		

	</td></tr></table>
	
HOMEPAGE
}
