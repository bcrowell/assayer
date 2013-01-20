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
	  print "User " . login_name_to_hyperlinked_login_name($cgi_full_path,$reader_login) . " logged in.";
	}
	else {
	  print "Not logged in.";
	}
	print "<p>\n";
  }
  
}




#---------------------------------------------------------------------------------------------

print '<table width="500"><tr><td>';
print &help_page_html;
print '</td></tr></table>';

#---------------------------------------------------------------------------------------------


PrintFooterHTML($homepath);

if ($connected) {
    $dbh->disconnect;
}

#---------------------------------------------------------------------------------------------

sub help_page_html {
return <<HELPPAGE;
	<h1>The Assayer: Help</h1>




	<ul>
		<li> <a href="#general">General</a></li>
		<ul>
			<li> What is it?
			<li> What's it good for?
			<li> Aren't you reinventing Amazon.com?
			<li> What's up with the name?
			<li> Who are you?
			<li> How do you pay your bills?
			<li> What do you mean by "free"?
			<li> Disclaimer
		</ul>
		<li> <a href="#privacy">Privacy</a></li>
		<ul>
			<li> General
			<li> What will you do with my e-mail address and other personal information?
			<li> Why do you need my e-mail address?
		</ul>
		<li> <a href="#contributing">Contributing</a></li>
		<ul>
			<li> What makes a good review?
			<li> Can I preview my review before submitting it?
			<li> Can I change a review once it's already in the database?
			<li> Can I delete my own review?
			<li> What is copyleft licensing?
			<li> How can I format my reviews?
			<li> How do the numerical scores work?
			<li> Adding a book without a review
		</ul>
		<li> <a href="#problems">Problems</a></li>
		<ul>
			<li> How do I report a bug?
			<li> I signed up as a member, but now it wants a password before I can log in.
			<li> I never got the e-mail telling me my password.
			<li>Oops! I made a typo in the book's title, the name of the author, or the URL.
		</ul>
		<li> <a href="#status">Status, To-Do List, and Bugs</a></li>
		<ul>
			<li> What's the status of the project?
			<li> To-do list
			<li> Bugs
		</ul>
		<li> <a href="#tech">Technical and Design Stuff</a></li>
		<ul>
			<li> Is the software open source?
			<li> How are you going to maintain a reliable, accurate catalog?
		</ul>
	</ul>
	
	
	
	<a name="general"><h2>General</h2>
	
	<h3>What is it?</h3>
	
	The Assayer is an online book reviewing facility that is free and nonprofit. All the reviews
	are free information, meaning that they are copyrighted by their authors, but are available
	for free reading and copying under a licensing agreement.<p>
	You can browse the database of reviews by clicking on a link in the bar above; browsing
	is free and anonymous. You need to be a member if you want to post your own reviews
	or participate in discussions of books.  
	<a href="http://www.theassayer.org/cgi-bin/asnewmember.cgi">Click here</a>
	to become a member. Membership is free, and the only personal information you need to give
	is your e-mail address (which will not be made available to other people unless you
	say it's OK).
	<h3>What's it good for?</h3>
	The Assayer's main reason for existing is to help people sort out the good stuff from
	the junk in the wild world of internet publishing. One of the traditional arguments against
	free books is that without a publisher to serve as a filter, you'd never know whether a
	book was any good. The Assayer aims to disprove that argument.<p>
	 Here are some other things The Assayer is good for:
	<ul>
		<li> Although there are several excellent catalogs of free books on the internet
			(<a href="http://digital.library.upenn.edu/books/">1</a>,
			<a href="http://www.ipl.org/">2</a>,
			<a href="http://www.gutenberg.org/">3</a>), The Assayer is different because it
			focuses on books that have been intentionally set free by their
			authors, as opposed to old public-domain books. Like those sites, however,
			The Assayer is dedicated to helping you find high-quality books, rather than
			simply serving as a massive list of links.
		<li> You can start a discussion of a particular book. Members can activate automatic
			e-mail notifications whenever a particular book is discussed. You can reply
			to other people's reviews or write your own.
		<li> If you're the author of a free book, you can use The Assayer make your book
			more visible to the world, and possibly attract reviews, which will give your
			book more credibility.
		<li> If you spend any amount of time browsing catalogs of free books on the web,
			you'll find many broken links, and also many cases of books that have been
			taken off the web by their publisher.
			Since The Assayer's catalog is open and user-modifiable, there are many eyeballs
			to catch and fix problems, so it's 
			generally very up to date. Feel free to update links
			or change the freedom setting of books whenever it's appropriate!
		<li> When a person sets information free, there's always the concern that someone
			else will take unfair advantage -- plagiarize it, modify it without explaining
			the modifications, sell it to people without letting them know it's available
			for free, or violate the licensing agreement. Visibility is the first line
			of defense against abuse. The Linux operating system, for example, is immunized
			against piracy by its high profile. Can you imagine anyone trying to sell
			Linux under their own brand name without disclosing what it was or that it
			was available for free? Good luck! By bringing together information about a lot of
			free books in one place, The Assayer makes free books more visible.
	</ul>
	
	<h3>Aren't you reinventing Amazon.com?</h3>
	Because Amazon.com has the best known public reviewing system, it's interesting to compare what
	The Assayer does with what Amazon does:<br>
	<ul>
		<li> Amazon only lets users review books that it can sell. The Assayer supports free books.
		<li> Amazon's database is copyrighted by Amazon, is proprietary, and will presumably cease to
			exist if Amazon goes out of business. An open system like The Assayer can be effectively
			immortal, and creative people can invent new ways to access, browse, and data-mine the
			database.
	</ul>
	 
	 <h3>What's up with the name?</h3>
	The name of the site is both a metaphor
	for book reviewing and a reference to The Assayer by Galileo, who was arguably the
	inventor of open-source computing. By the way, the accent is on the second syllable.
	 
	<a name="contact"><h3>How do I contact you? How do I report a bug?</h3>
	<a href="http://www.lightandmatter.com/area4author.html">Here</a>.
	 
	 <h3>How do you pay your bills?</h3>
	 The Assayer is nonprofit. The webhosting bills get paid either by me or
	 out of donations by members. Lion Kimbro donated $250 for a year's worth of
	 webhosting in 2001 -- thanks, Lion! I currently have a webhosting setup that
	 lets me run The Assayer essentially for free, piggypacked on top of another
	 site.
	 
	 <a name="free"><h3>What do you mean by "free"?</h3>
	 "Free" could mean that you just don't have to pay to read the book, or it could mean
	 "free" in the political sense: copyright law was originally designed to encourage authors
	 to write, at the cost of other people's freedom to copy, sell, or modify their writing.
	 The free software community traditionally refers to this as "free as in beer" versus
	 "free as in speech," or you could call it "gratis" and "libre," since French uses
	 different words for the two concepts. <a href="http://www.opensource.org/osd.html">Here</a>
	 is a good generic definition of what people mean by free as in speech as applied to
	 software (there is somewhat less agreement about books).<p>
	 The Assayer's database design defines the following levels of freedom:
	 <ul>
		0. Copyrighted, with a licensing agreement that prohibits selling or permanent use (an anti-book)<br>
		1. Copyrighted, with no licensing agreement (a traditional book) [also books on iUniverse]<br>
		2. Copyrighted, doesn't cost money to read, but otherwise not free<br>
		3. Public domain<br>
		4. Copylefted, but with restrictions on modification and/or sale<br>
		5. Copylefted: anyone can read, modify, and sell<br>
	 </ul>
	 Copylefted books (levels 4 and 5) are copyrighted, and have licensing agreements that you must
	 accept in order to have permission from the author to copy or download them. These licensing
	 agreements typically try to make the books as free as possible for readers, subject to the
	 economic realities of the print publishing world and the desire of the author not to have her
	 work used without attribution, modified without explanation, etc. The Assayer is now only accepting
   new books in the database if they have freedeom levels of 2 to 5.
   <p>
   These are two licenses commonly used for copylefting books:
   <ul>
     <li> <a href="http://creativecommons.org/license/">Creative Commons</a> (actually a bunch of different licenses)
	   <li> <a href="http://www.gnu.org/copyleft/fdl.html">GFDL</a>
   </ul>
   Historically, another important license
   was the <a href="http://opencontent.org/openpub/">Open Publication License 1.0 without options A or B</a>.
   Freedom level 5 would include the GFDL, the OPL without options A or B, and many of the CC licenses.
	 <a href="#contributing">Reviews</a> submitted to The Assayer must be copylefted under OPL or GFDL. For books,
   most people these days are using CC licenses, e.g., for my own books I use the Creative Commons
   Attribution Share-Alike license. The creator of the OPL has now thrown in his lot with CC.
	 <p>
	 Books that are theoretically free for reading on the internet nevertheless belong
	 in category 1 if they are supplied in a form that is intentionally made impractical
	 for reading. The most frequently encountered example is books on iUniverse, which are
	 available only as bitmapped page images and can't be printed by any practical method.
	 <p>
	 Yes, some of this does read like it has moral overtones, but you're free to ignore or disagree with
	 them. It's just a database, not the Ten Commandments. The ordering of the levels is meant to be
	 meaningful, but again this is debatable. Placing public domain in the middle rather than at the
	 highest level follows the conventional wisdom in the open-source software community that copylefted
	 information is freer than public-domain information. 
	 Books show up on the screen with a dandelion flower icon if their freedom level is 5, and
	 with a dandelion bud icon if they are from 2 to 4.
	 <p>
	 Note that conspicuously missing from this
	 set of definitions is any reference to whether the book is provided in a form that can be
	 easily modified, like the "source" part of open-source software.
	 The GFDL tries to do this, but the OPL and CC licenses don't. The problem with this is that whereas
	 there are standard and free software tools and formats for working with computer programs, there is
	 not necessarily any corresponding set of tools and formats for books, especially illustrated
	 books or books with complex layouts.
	 <a name="freedomdisclaimer"><h3>Disclaimer</h3>
	 The freedom data in this database is only meant to be a rough guide to people browsing it, 
	   not a full description of the legal status of the book. This information also may not 
	   be accurate, since many free book authors' web sites do not make the legal status of their 
	   books very clear. Authors: Please contact me if the information given for your book is incorrect.

	<a name="privacy"><h2>Privacy</h2>
	<h3>General</h3>
	In general, what you <i>do</i> on The Assayer is very public (see the
	<a href="http://www.theassayer.org/cgi-bin/asviewlog.cgi?n=20">public log</a>, for instance), but the only personal information
	you have to provide publicly is your login name, and even that can be fanciful. You can <i>choose</i>
	to link your login name publicly to personal information like your name, bio, e-mail address,
	and home page.

	<h3>What will you do with my e-mail address and other personal information?</h3>
	Not much! I'll use your e-mail to send you your password. The Assayer is a nonprofit
	organization. I will not send you unsolicited commercial e-mail ("spam"), and I
	will not give out your e-mail address to other people without your permission.
	
	<h3>Why do you need my e-mail address?</h3>
	Reason #1 is security.
	It hasn't happened yet, but every online forum of this kind eventually is afflicted
	with losers who 
	don't have anything better to do with their time than 
	to post irrelevant gross-out jokes and other juvenilia. Determined abusers
	of this kind may try posting a the same potty joke a hundred times in an hour if
	the software allows it. Requiring an e-mail address makes this kind of abuse less
	anonymous, and also makes it possible to institute more formal safeguards in the
	future, if necessary (e.g. a point system like <a href="http://slashdot.org">Slashdot</a>'s).
	(Without mandatory e-mail addresses, a point system doesn't work, because people can
	make up as many aliases as they like.)<p>
	Reason #2 is that there is a feature that lets you check a box to receive
	e-mail when anything is posted about a particular book. This allows people to have
	real online discussions rather than just posting reviews.
	
	 
	 <a name="contributing"><h2>Contributing</h2>
	 <h3>What makes a good review?</h3>
	 Actually, the most important part of the review isn't even the review itself,
	 it's your bio. Your bio is a brief personal sketch that tells readers what
	 your qualifications are for reviewing books. For example, my own bio
	 notes that I have a PhD in physics and I'm an amateur jazz musician,
	 so people will take my reviews of physics books more seriously than
	 my reviews of music books. To insert your bio into the database, go through
	 the process of logging in, and then click on the button under
	 <i>changing user information</i>.<p>
	  The perfect review is entertaining and informative. It doesn't assume
	  the reader already knows about the book or the subject of the book.
	  The reviewer backs up her opinions with facts, and makes specific
	  statements rather than general ones.<p>
	 Many of the books on The Assayer are technical in nature, and people
	 may be using them for reference rather than reading them from cover to
	 cover. It's ok to review a book that you haven't read from cover to
	 cover, but your review should note that fact. To take an extreme
	 example, the site has a listing of Nupedia: The Open Content Encyclopedia.
	 Nobody expects you to read the whole thing! The same would apply
	 to a dictionary or a technical manual documenting a large suite of
	 computer subroutines.<p>
	 Your review should also note any information that might cause you
	 to be biased for or against the book. Are
	 you the publisher? Are you financially involved? Did you get the book
	 as a freebie from the publisher? Is it a book by a close friend or
	 colleague?
	 
	 <h3>Can I preview my review before submitting it?</h3>
	 Yes. Click the Preview button.
	 <h3>Can I change a review once it's already in the database?</h3>
	 Yes. Browse the database to find your own review and
	  click the Revise button.
	  Note that your old versions are still in the database, and will
	  be publicly available to anyone who cares. This is to prevent abuse.
	  (I may delete old versions at my discretion, but it will not normally
	  happen right away.) Note that you can revise reviews, but not replies.
	  <h3>Can I delete my own review?</h3>
	  No, but you can revise it, and if you want to you can even revise it
	  and replace it with a message like "review withdrawn by the author."
	  However, the original version will still exist and be accessible to
	  anyone who cares.
	  <h3>What is copyleft licensing?</h3>
    See	  <a href="#free">above</a>
	  <h3>How can I format my reviews?</h3>
	  You can use the symbol &lt;p&gt; for paragraph breaks. Simply hitting return and
	  tab will not create a paragraph break. You can make italics &lt;i&gt;like this&lt;/i&gt;.<p>
	  If you know HTML, you can also use the following HTML tags: 
	  &lt;b&gt;, &lt;ul&gt;, &lt;ol&gt;, &lt;li&gt;, &lt;br&gt;, &lt;sup&gt;, &lt;sub&gt;, &lt;a&gt;,
	  &lt;tt&gt;.
	  <h3>How do the numerical scores work?</h3>
	  	You are rating the book against a comparison group, which by
	  	default is assumed to be the set of similar books that a typical public
	  	library has on its shelves.
	  	The scale is as follows:<br>
			<ul>
				<li> 0=substandard (would not be accepted in the comparison group)
				<li> 1=typical (not in the top 20% of the comparison group)
				<li> 2=better than 80%
				<li> 3=better than 90%
				<li> 4=better than 95%
				<li> 5=better than 98%
				<li> 6=better than 99%
				</ul>
	The idea is for nearly all books to be rated either 0 or 1, i.e. thumbs up
	or thumbs down, and the assumption is that most users will want to search
	only for books that rate at least 1 in both content and writing. <p>
	In certain cases, the reviewer will want to use a comparison group
	different from the default one. This is probably appropriate if the book is
	an amateur work, e.g. fan fiction, which should be compared with other fan fiction,
	or if it's a genre libraries don't normally have, like comic books.
	The review should state if a nonstandard comparison group was used.<p>
	Reviewers will eventually
	be allowed to give decimals, not just whole numbers, but this is not yet implemented. 

	<h3>Adding a book without a review</h3>
  The Assayer functions both as a catalog of free books and as a forum for reviews.
  Adding a book to the database without a review contributes to the catalog, and
	we also want to encourage people to do reviews, so
    you can save potential reviewers the trouble of entering all the bibliographic information by
    entering a free book into the database without a review. To do this, go through the
    process of writing a review of the book, but leave the actual review (and the title
    of the review) blank. The software will know what you're trying to do.  
	<p>
	If you'd like to encourage people to review your free book on The Assayer,
	you can use <a href="http://www.theassayer.org/reviewme.gif">this image</a>
	as a link. Here's some sample HTML:<br>
<pre>               &lt;a href="http://www.theassayer.org/cgi-bin/asbook.cgi?book=xxx" style="text-decoration:none" &gt;
                &lt;img src="http://yourwebsite.com/reviewme.gif" width="275" height="33"
                border="0" alt="Review this book on The Assayer"&gt;&lt;/a&gt;</pre><p>
	 You need to change xxx to the book identification number of your book, which you can find
	 by going to your book's page in The Assayer and looking at the URL. Of course
    you'll also want to activate e-mail notification for your own book.

	<a name="problems"><h2>Problems</h2>
	<h3>How do I report a bug?</h3>
	Click on <i>report bug</i> at the top of the screen.
	<h3>I signed up as a member, but now it wants a password before I can log in.</h3>
	Your password is being sent to you by e-mail.
	<h3>I forgot my username.</h3>
	You can use <i>browse by reviewer</i> to find yourself, or go to the <i>log in</i>
	page and click on the link to get an e-mail reminder sent to you.
	<h3>I forgot my password.</h3>
	Go to the <i>log in</i>
	page and click on the link to get an e-mail reminder sent to you.
	<h3>I never got the e-mail telling me my password.</h3>
	You probably made a typo in your e-mail address. Please just e-mail me (you can use
	the bug report form) and I'll fix the situation.
	<h3>Oops! I made a typo in the book's title, the name of the author, or the URL.</h3>
	You can either e-mail me about this (using the bug report form is fine), or
	fix it yourself. To fix it yourself, go to the book's page and click on the
	link for editing the information about that book. Please only do this if you
	know what you're doing: you've
	been using The Assayer for a while, you're familiar with it, and you've read the
	entire help page.
	
    
	<a name="tech"><h2>Technical and Design Stuff</h2>
	<h3>Is the software open source?</h3>
        <a href="https://github.com/bcrowell/assayer">Yes.</a>
	<h3>How are you going to maintain a reliable, accurate catalog?</h3>
	There are provisions in the database design for fixing cases where two people
	create two different book records for the same book using slightly different
	titles, or two different author records using different forms of the author's
	name. Normally you add a new book by a particular author starting from that
	author's screen, so you would not be entering the author's name again through
	the keyboard. <p>
	It's also important to realize that cataloging free books is fundamentally different
	from cataloging paper books. Free books move around on the web frequently, mutate
	into new forms, and may also be taken off the web by print publishers so that they
	are no longer free. The fluid nature of digital publishing makes it nearly
	impossible for a group of centrally organized librarians to keep a catalog of
	free books up to date. Seen from this angle, The Assayer's willingness to let
	users modify the catalog is a feature, not a bug.<p>
  It's also possible for the information in the database to get its logical structure
  messed up, e.g., a book could have no authors listed.
  There is a user-accessible page <a href="http://www.theassayer.org/cgi-bin/ascheckdb.cgi">here</a>
  that tries to find this kind of corrupted information in the database. I check this
  page myself from time to time, but if you notice something listed there, you can
  also contact me.
	
HELPPAGE
}
