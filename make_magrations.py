import glob
import os
import sqlite3
import config

mdir = 'migrations'


def main():
    con = sqlite3.connect(config.DB_PATH.replace('sqlite:///', ''))
    cur = con.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS `migrations` (
      `filename` VARCHAR(32) NOT NULL
    );
    ''')
    con.commit()
    cur.execute('select `filename` from `migrations`')
    filenames = [f[0] for f in cur.fetchall()]

    os.chdir(mdir)
    for file in glob.glob("*.sql"):
        if file in filenames:
            continue
        print(f'make {file} ...')
        with open(file) as sql_file:
            sql_as_string = sql_file.read()
            cur.executescript(sql_as_string)
        cur.execute(f'INSERT INTO migrations (filename) VALUES ("{file}")')
        con.commit()
    print('migrations done')


if __name__ == '__main__':
    main()
