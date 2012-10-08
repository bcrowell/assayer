sub decode_query_hash()
{

	my $my_query_string = $ENV{'QUERY_STRING'};
		
	my @query_key_pairs = split(/&/, $my_query_string);
	
	if (! @query_key_pairs) {return 0;}
	
	# There's supposed be something called %in that cgi-lib makes for me,
	# but it doesn't seem to work, so I reinvent the wheel:
	my %query_hash = ();
	foreach $par (@query_key_pairs) {
	  my @par_parts = split(/=/, $par);
	  $query_hash{$par_parts[0]} = $par_parts[1];
	}
	
	return %query_hash;

}


return 1;
