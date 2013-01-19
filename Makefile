archive:
	git archive --format=tar --prefix=assayer/ HEAD | gzip >assayer.tar.gz

post:
	cp assayer.tar.gz /var/www-assayer

clean:
	rm -f *~
	rm -f assayer.tar.gz
