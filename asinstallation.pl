#$homepath = "http://64.33.110.96";
#$cgi_full_path = "http://64.33.110.96/cgi-bin";
$homepath = "http://www.theassayer.org";
$cgi_full_path = "http://www.theassayer.org/cgi-bin";
$dsn = "DBI:mysql:assayer:localhost:3306";
$db_user = "theassayer";
$titlebgcolor = "#cccccc";
$max_authors = 5;
$default_screen_width = 500;
$login_period = 365;
$email_from = 'no-reply@'.'lightandmatter.com'; 
  # Don't use theassayer.org because no reverse DNS, so many people bounce it.
  # Break address apart so spam robots won't recognize it as an e-mail address.
$sendmail_binary = '/usr/sbin/sendmail';
  # ... on debian, doesn't work unless you give the full path

return 1;
