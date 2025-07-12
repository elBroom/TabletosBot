reinstall:
	docker-compose down
	git pull origin master --rebase
	docker-compose build
	python3 make_magrations.py
	docker-compose up -d

restart:
	git pull origin master --rebase
	docker-compose restart

start:
    source venv/bin/activate && python3 main.py &

create_migrations:
	touch migrations/$(shell date +"%s").sql