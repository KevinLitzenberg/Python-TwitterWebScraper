#Twitter Webscraper using BS to scrape statuses from provided users.

Built using python3.8 no backward compatabiliyt tested, but since we are using f'string < python3.6 is required.

1. Create a virtual environment.
    python3.8 -m venv venv
2. Activate that environment.
    source venv/bin/activate.
3. Install the pip packages.
    pip install -r requirements.txt
4. A psql db running on localhost:32768 


Postgres_db.py:
* Utilizes psycopsg2 package to manage the psql12 db.
* Class contains object methods for standard db management.
    - Instantiate db Object
        **host_ip, port_num, user_name, passwd, database**
    
###Notes on some methods:

* create_database: fakes the mysql IF EXISTS by checking if a row exists in the db.  If a single row exists we assume the db is already populated and append to that dbs table.

* insert_tweets: utilzes f' string to create the queries requires < python3.6.  Also calls santize_string and sanitize_link which both clean up the string prior to inserting them into the db.  
	 


tweet_status_scraper.py
* Uses pgpasslib which depends on db password to be stored in home dir.
* [pgpasslib](https://pgpasslib.readthedocs.io/en/latest/ "pgpasslib") Keeps password from repo.
