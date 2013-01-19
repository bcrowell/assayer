
@uinfo_order = (
	id	,
	login ,
	pwd_hash	 ,
	email ,
	special_sauce ,
	real_name ,
	fake_email ,
	homepage ,
	sig	 ,
	bio	
);

%uinfo_name = (
	id				=> "user number",
	login			=> "login name",
	pwd_hash				=> "password",
	email			=> "real e-mail",
	special_sauce	=> "special sauce",
	real_name		=> "real name",
	fake_email		=> "fake e-mail",
	homepage		=> "home page",
	sig				=> "sig",
	bio				=> "bio"
);

%uinfo_private = (
	id				=> "0",
	login			=> "0",
	pwd_hash				=> "1",
	email			=> "1",
	special_sauce	=> "1",
	real_name		=> "0",
	fake_email		=> "0",
	homepage		=> "0",
	sig				=> "0",
	bio				=> "0"
);

%uinfo_optional = (
	id				=> "0",
	login			=> "0",
	pwd_hash				=> "0",
	email			=> "0",
	special_sauce	=> "0",
	real_name		=> "0",
	fake_email		=> "1",
	homepage		=> "1",
	sig				=> "1",
	bio				=> "1"
);

%uinfo_change_normal_way = (
	id				=> "0",
	login			=> "0",
	pwd_hash				=> "0",
	email			=> "1",
	special_sauce	=> "0",
	real_name		=> "1",
	fake_email		=> "1",
	homepage		=> "1",
	sig				=> "1",
	bio				=> "1"
);

%uinfo_long = (
	id				=> "0",
	login			=> "0",
	pwd_hash				=> "0",
	email			=> "0",
	special_sauce	=> "0",
	real_name		=> "0",
	fake_email		=> "0",
	homepage		=> "0",
	sig				=> "1",
	bio				=> "2"
);

%uinfo_html_ok = (
	id				=> "0",
	login			=> "0",
	pwd_hash				=> "0",
	email			=> "0",
	special_sauce	=> "0",
	real_name		=> "0",
	fake_email		=> "0",
	homepage		=> "0",
	sig				=> "1",
	bio				=> "1"
);

%uinfo_instructions = (
	id				=> "",
	login			=> "",
	pwd_hash				=> "",
	email			=> "",
	special_sauce	=> "",
	real_name		=> "",
	fake_email		=> "can be spam-proofed",
	homepage		=> "including http://",
	sig				=> "",
	bio				=> ""
);

return 1;
