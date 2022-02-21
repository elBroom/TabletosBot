reinstall:
    docker-compose down
    git checkout master
    docker-compose build
    python3 make_magrations.py
    docker-compose up -d

create_migrations:
    touch migrations/"$(date +"%s").sql"