archive:
	git archive --format=tar --prefix=project/ HEAD | gzip >assayer.tar.gz
