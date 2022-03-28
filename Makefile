remove-db:
	if [ -d $(CURDIR)/db ]; then \
		sudo chown -R $(USER) $(CURDIR)/db; \
	fi
	rm -rf $(CURDIR)/db

build-docker-compose:
	echo y | docker system prune
	docker-compose up --build

run-docker-compose:
	docker-compose -f docker-compose.yml up