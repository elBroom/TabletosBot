reinstall:
	docker-compose down
	git pull origin master --rebase
	docker-compose build
	python3 make_magrations.py
	docker-compose up -d

reload:
	docker-compose down
	git pull origin master --rebase
	docker-compose up -d

create_migrations:
	touch migrations/"$(date +"%s").sql"