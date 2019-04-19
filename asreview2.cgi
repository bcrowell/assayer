#!/usr/bin/perl

#####################################################################
# This software is copyright (c) 2000 Benjamin Crowell, and is open-
# sourced under the GPL license, http://www.gnu.org/copyleft/gpl.html.
#####################################################################

#$| = 1; # Set output to flush directly (for troubleshooting)
require "./cgi-lib.pl";


require "./ashtmlutil.pl";
require "./asdbutil.pl";
require "./asfreedom.pl";
require "./asinstallation.pl";
PrintHTTPHeader();

$pagetitle = "The Assayer: Add a Review: Step 2";

use CGI;
use DBI;


$co = new CGI;

# n = number of authors
$n = $co->param('n');
if ($n eq "") {$n=1;}

for ($k=0; $k<$n; $k++) {
  $m = $k+1;
  $last[$k] = $co->param("last$m");
  $first[$k] = $co->param("first$m");
  $suffix[$k] = $co->param("suffix$m");
  $auref[$k]  = $co->param("auref$m");
}

PrintHeaderHTML($homepath,$pagetitle);
PrintBannerHTML($homepath);
print toolbar_HTML($homepath);

print "<h1>Add a Review: Step 2</h1>\n";

$bogus = 0;
if (! seems_loggedIn($co)) {$bogus = "Not logged in.  If you think you are logged in, try hitting the reload button in your browser.";}

if (!$bogus) {

for ($k=0; $k<$n; $k++) {
  $o = ordinal($k+1,1);
  print "$o author: " . printable_author($first[$k],$last[$k],$suffix[$k],0);
  if ($auref[$k] ne "") {print " (author id #" . $auref[$k] . ")";}
  print  "<br>\n";
}

    print  $co->start_form( -method=>'POST',-action=>"$cgi_full_path/asreview3.cgi");
		
		

print "<b>Title</b> (required):<br> " . $co->textfield(-name=>'title',-value=>'',-size=>"100") 
					. " Example: War of the Worlds, The<br>";
print "\nIf the first word is not the one under which the ";
print "title should be alphabetized, put it at the end after a comma.<p> ";

print "<b>Library of congress subject class</b> (required):<br>" . $co->textfield(-name=>'lccclass',-value=>'',-size=>"2")
	. "<br>(first letter of the Library of Congress classification; see definitions below; P for novels in English)<p>";
					
print "<b>Library of congress subject subclass</b> (optional):<br>" . $co->textfield(-name=>'lccsubclass',-value=>'',-size=>"2")
	. "<br>(second letter of the Library of Congress classification; see definitions below; Z for novels in English)<p>";
					
print "<b>Web address for reading</b>:<br>" . $co->textfield(-name=>'url',-value=>'http://',-size=>"100")
	. "<br>(A web site at which the <i>entire</i> book can be read or downloaded <i>for free</i>. Be sure to include http://. Books can't be listed on this site if they are not available on the web for free.<p>";

my $allow_non_free = 0; # also in asreview3
my $values;
if ($allow_non_free) {
  $values = ['1','2','3','4','5'];
}					
else {
  $values = ['2','3','4','5'];
}
print "<b>Legal</b>:<br>" . $co->popup_menu(
		  -name=>'freedom',
		  -values=>$values,
		  -default=>'2',
		  -labels=>\%describe_freedom
		) . "<p>\n";

					
print	$co->submit(-name=>'Go On To Step 3');

for ($k=0; $k<$n; $k++) {
  $m = $k+1;
  print $co->hidden(-name=>"last$m",-default=>$last[$k],-override=>1) . "\n";
  print $co->hidden(-name=>"first$m",-default=>$first[$k],-override=>1) . "\n";
  print $co->hidden(-name=>"suffix$m",-default=>$suffix[$k],-override=>1) . "\n";
  if ($auref[$k] ne "") {print $co->hidden(-name=>"auref$m",-default=>$auref[$k],-override=>1) . "\n";}
}
print $co->hidden(-name=>'n',-default=>$n,-override=>1);

print  	$co->hidden(-name=>'bkref',-default=>"$bkref",-override=>1);
print  	$co->hidden(-name=>'parent_review',-default=>"",-override=>1);
		
print	$co->end_form;
}
if ($bogus) {
  print "Error: $bogus<p>\n";
  print "If you need to log in, click <a href=\"aslogin.cgi\" target=\"window\">here</a> ";
  print "to bring up a log-in screen in ";
  print "a separate window. After you log in, close that window and reload this one.<p>\n";
}

print  <<__html__;

<h2>Library of Congress Classes</h2>
Sometimes you may need to look at the subclasses to figure out in which class a book belongs.<p>
<b>A</b> - General Works<br>
<b>B</b> - Philosophy, Psychology, Religion<br>
<b>C</b> - Auxiliary Sciences of History<br>
<b>D</b> - History: General and Old World<br>
<b>E</b> - American history: precolumbian and U.S.<br>
<b>F</b> - American history: U.S. local, colonial, Latin American<br>
<b>G</b> - Geography, Anthropology, Recreation<br>
<b>H</b> - Social Sciences. Business<br>
<b>J</b> - Political Science<br>
<b>K</b> - Law<br>
<b>L</b> - Education<br>
<b>M</b> - Music<br>
<b>N</b> - Fine Arts<br>
<b>P</b> - Language and Literature<br>
<b>Q</b> - Science. Math. Computing<br>
<b>R</b> - Medicine<br>
<b>S</b> - Agriculture<br>
<b>T</b> - Technology<br>
<b>U</b> - Military Science<br>
<b>V</b> - Naval Science<br>
<b>Z</b> - Library Science<br>

<h2>Library of Congress Subclasses</h2>
Books on general subjects may not have a subclass. Categories E and F do not
have subclasses. For more detailed information,
see <a href="http://lcweb.loc.gov/catdir/cpso/lcco/lcco.html">this site</a>.

<h3>A - General Works</h3>
AC - Collections. Series. Collected works<br>
AE - Encyclopedias<br>
AG - Dictionaries and other general reference works<br>
AI - Indexes<br>
AM - Museums. Collectors and collecting<br>
AN - Newspapers<br>
AP - Periodicals<br>
AS - Academies and learned societies<br>
AY - Yearbooks. Almanacs. Directories<br>
AZ - History of scholarship and learning. The humanities<br>
<h3>B - Philosophy, Psychology, Religion</h3>
BC - Logic<br>
BD - Speculative philosophy<br>
BF - Psychology<br>
BH - Aesthetics<br>
BJ - Ethics. Etiquette<br>
BL - Religions. Mythology. Rationalism<br>
BM - Judaism<br>
BP - Islam. Bahaism. Theosophy, etc.<br>
BQ - Buddhism<br>
BR - Christianity<br>
BS - The Bible<br>
BT - Doctrinal Theology<br>
BV - Practical Theology<br>
BX - Christian Denominations<br>
<h3>C - Auxiliary Sciences of History</h3>
CB - History of Civilization<br>
CC - Archaeology<br>
CD - Diplomatics. Archives. Seals<br>
CE - Technical Chronology. Calendar<br>
CJ - Numismatics<br>
CN - Inscriptions. Epigraphy<br>
CR - Heraldry<br>
CS - Genealogy<br>
CT - Biography<br>
<h3>D - History: General and Old World</h3>
DA - Great Britain. Central Europe<br>
DB - Austria<br>
DC - France<br>
DD - Germany<br>
DE - The Mediterranean Region. The Greco-Roman World<br>
DF - Greece<br>
DG - Italy<br>
DH - Belgium. Luxembourg<br>
DJ - Holland. Eastern Europe<br>
DK - Russia. Poland. Former Soviet republics<br>
DL - Northern Europe. Scandinavia<br>
DP - Spain<br>
DQ - Switzerland<br>
DR - Balkan Peninsula<br>
DS - Asia<br>
DT - Africa<br>
DU - Oceania<br>
DX - Gypsies<br>
<h3>E - American history: precolumbian and U.S.</h3>
<h3>F - American history: U.S. local, colonial, Latin American</h3>
<h3>G - Geography, Anthropology, Recreation</h3>
GA - Mathematical geography. Cartography<br>
GB - Physical geography<br>
GC - Oceanography<br>
GE - Environmental Sciences<br>
GF - Human ecology. Anthropogeography<br>
GN - Anthropology<br>
GR - Folklore<br>
GT - Manners and customs<br>
GV - Recreation. Leisure<br>
<h3>H - Social Sciences. Business</h3>
HA - Statistics<br>
HB - Economic theory. Demography<br>
HC - Economic history and conditions (1)<br>
HD - Economic history and conditions (2)<br>
HE - Transportation and communications<br>
HF - Commerce<br>
HG - Finance<br>
HJ - Public finance<br>
HM - Sociology (general)<br>
HN - Social history and conditions. Social problems. Social reform<br>
HQ - The family. Marriage. Woman<br>
HS - Societies: secret, benevolent, etc.<br>
HT - Communities. Classes. Races<br>
HV - Social pathology. Social and public welfare. Criminology<br>
HX - Socialism. Communism. Anarchism<br>
<h3>J - Political Science</h3>
JA - Political science (General)<br>
JC - Political theory<br>
JF - Political institutions and public administration<br>
JK - Political institutions and public administration: U.S.<br>
JL - Political institutions and public administration: Canada and Latin America<br>
JN - Political institutions and public administration: Europe<br>
JQ - Political institutions and public administration: Asia, Africa, Australia<br>
JV - Colonies and migration<br>
JZ - International relations<br>
<h3>K - Law</h3>
KD - Law of the United Kingdom and Ireland<br>
KE - Law of Canada<br>
KF - Law of the United States<br>
KG - Law of Latin America, northern hemisphere<br>
KH - Law of South America<br>
KJ - Law of Europe (countries G-Z)<br>
KL - Law of Eurasia. Ancient orient and near east<br>
KM - Law of southwest Asia<br>
KN - Law of the far east (general and countries A-J)<br>
KP - Law of the far east (countries K-Z)<br>
KQ - Law of Africa (general and countries A-C)<br>
KR - Law of Africa (countries D-Gi)<br>
KS - Law of Africa (countries Gu-Na)<br>
KT - Law of Africa (countries Ni-Z)<br>
KU - Law of Australia and New Zealand<br>
KV - Law of Oceania (general and countries A-Ne)<br>
KW - Law of Oceania (countries Ni-Z) and Antarctica<br>
KZ - Law of nations<br>
<h3>L - Education</h3>
LA - History of education<br>
LB - Theory and practice of education<br>
LC - Special aspects of education<br>
LD - Individual institutions (U.S.)<br>
LE - Individual institutions (America, except the U.S.)<br>
LF - Individual institutions (Europe)<br>
LG - Individual institutions (Asia, Africa, Pacific)<br>
LH - College and school magazines and papers<br>
LJ - Student fraternities and societies, United States<br>
LT - Textbooks<br>
<h3>M - Music</h3>
ML - Literature on music<br>
MT - Musical instruction and study<br>
<h3>N - Fine Arts</h3>
NA - Architecture<br>
NB - Sculpture<br>
NC - Drawing. Design. Illustration<br>
ND - Painting<br>
NE - Print media<br>
NK - Decorative arts<br>
NX - Arts in general<br>
<h3>P - Language and Literature</h3>
PA - Classical philology<br>
PB - Philology: Modern languages. Celtic languages<br>
PC - Philology: Romanic<br>
PD - Philology: Germanic<br>
PE - Philology: English<br>
PF - Philology: West Germanic<br>
PG - Philology: Slavic. Baltic. Albanian<br>
PH - Philology: Uralic. Basque<br>
PJ - Oriental philology and literature<br>
PK - Indo-Iranian philology and literature<br>
PL - Languages and literatures of Eastern Asia, Africa, Oceania<br>
PM - Hyperborean, Indian, and Artificial languages<br>
PN - Literature (General)<br>
PQ - Literature in romance languages<br>
PR - Literature of England<br>
PS - American literature<br>
PT - Literature in German, Dutch, Flemish, Afrikaans, and Scandinavian languages<br>
PZ - Fiction in English and juvenile belles lettres<br>
<h3>Q - Science. Math. Computing</h3>
QA - Mathematics. Computer science<br>
QB - Astronomy<br>
QC - Physics<br>
QD - Chemistry<br>
QE - Geology<br>
QH - Natural history<br>
QK - Botany<br>
QL - Zoology<br>
QM - Human anatomy<br>
QP - Physiology<br>
QR - Microbiology<br>
<h3>R - Medicine</h3>
RA - Public aspects of medicine<br>
RB - Pathology<br>
RC - Internal medicine<br>
RD - Surgery<br>
RE - Ophthalmology<br>
RF - Otorhinolaryngology<br>
RG - Gynecology and obstetrics<br>
RJ - Pediatrics<br>
RK - Dentistry<br>
RL - Dermatology<br>
RM - Therapeutics. Pharmacology<br>
RS - Pharmacy and materia medica<br>
RT - Nursing<br>
RV - Botanic, Thomsonian, and eclectic medicine<br>
RX - Homeopathy<br>
RZ - Other systems of medicine<br>
<h3>S - Agriculture</h3>
SB - Plant culture<br>
SD - Forestry<br>
SF - Animal culture<br>
SH - Aquaculture. Fisheries. Angling<br>
SK - Hunting sports<br>
<h3>T - Technology</h3>
TA - Engineering (General). Civil engineering (General)<br>
TC - Hydraulic engineering<br>
TD - Environmental technology. Sanitary engineering<br>
TE - Highway engineering. Roads and pavements<br>
TF - Railroad engineering and operation<br>
TG - Bridge engineering<br>
TH - Building construction<br>
TJ - Mechanical engineering and machinery<br>
TK - Electrical engineering. Electronics. Nuclear engineering<br>
TL - Motor vehicles. Aeronautics. Astronautics<br>
TN - Mining engineering. Metallurgy<br>
TP - Chemical technology<br>
TR - Photography<br>
TS - Manufactures<br>
TT - Handicrafts. Arts and crafts<br>
TX - Home economics<br>
<h3>U - Military Science</h3>
UA - Armies: Organization, distribution, military situation<br>
UB - Military administration<br>
UC - Maintenance and transportation<br>
UD - Infantry<br>
UE - Cavalry. Armor<br>
UF - Artillery<br>
UG - Military engineering<br>
UH - Other services<br>
<h3>V - Naval Science</h3>
VA - Navies: Organization, distribution, naval situation<br>
VB - Naval administration<br>
VC - Naval maintenance<br>
VD - Naval seamen<br>
VE - Marines<br>
VF - Naval ordnance<br>
VG - Minor services of navies<br>
VK - Navigation. Merchant marine<br>
VM - Naval architecture. Shipbuilding. Marine engineering<br>
<h3>Z - Library Science</h3>
ZA - Information resources (General)<br>
__html__

&PrintFooterHTML($homepath);

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

