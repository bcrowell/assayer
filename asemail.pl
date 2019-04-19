
require "./asdbutil.pl";
#require "./asinstallation.pl";

sub send_email {
  my %args = (
    TO=>'',
    FROM=>$email_from,
    SUBJECT=>'The Assayer',
    BODY=>'',
    REASON=>'',
    @_,
	);
  my $to = $args{TO};
  my $from = $args{FROM};
  my $subject = $args{SUBJECT};
  my $body = $args{BODY};
  my $reason = $args{REASON};
  if (!($to && $body && reason)) {return 'must specify TO, BODY, and REASON'}
  my $footer = <<FOOTER;
This message was sent by The Assayer (http://theassayer.org) at your request,
for the following reason:
  $reason
It was generated automatically, and replying won't work. See this web page
  http://www.lightandmatter.com/area4author.html
for information on how to contact Ben Crowell, who runs The Assayer.
The return address on this message is \@lightandmatter.com rather than
\@theassayer.org for technical reasons (some mail service providers
bounce e-mail from theassayer.org because it doesn't have reverse DNS
enabled).
FOOTER
  open(MAIL, "|$sendmail_binary -t") or return "error opening pipe to $sendmail_binary";
  print MAIL <<__EMAIL__;
To: $to
From: $from
Subject: $subject

$body

-----------------------------------------------------------

$footer
__EMAIL__
  close MAIL;
  return '';
}

return 1;
