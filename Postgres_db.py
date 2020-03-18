import psycopg2
from psycopg2 import connect, extensions, sql
import logging
import re

logging.basicConfig(level=logging.DEBUG)
  
class postgresConnection:
    # Compile the characters to strip from strings going into the db table.
    strip_chars = re.compile("'")

    def __init__(self, host_ip, port_num, user_name, passwd, database):
        #print('Creating the db {}'.format(db_name))
        # Create the db file
        self.conn = psycopg2.connect(host=host_ip, port=port_num, user=user_name, password=passwd, dbname=database)
        # set the ISOLATION_LEVEL_AUTOCOMMIT
        autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
        # set the isolation level for the connection's cursors
        # will raise ActiveSqlTransaction exception otherwise 
        self.conn.set_isolation_level( autocommit )

        # Create the cursor object
        self.cur = self.conn.cursor()


    def create_database(self, db_name):
        # Check for the existance of the db
        sql_query = "SELECT count(*) FROM pg_catalog.pg_database WHERE datname = '%s';"%(db_name)
        #print(sql_query.format(sql.Identifier(db_name[2])))
        logging.debug('Check for existance of db before creating.\n'.format(sql_query))

        # execute the query to check for existance.
        self.cur.execute(sql_query)

        exists = self.cur.fetchone()
        logging.debug('exists: {}'.format(exists[0]))
        if exists[0] == 0:
           self.cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
           logging.debug('Creating the database {}.'.format(db_name))
        else:
           logging.debug('{} already exists.'.format(db_name))

    def connect_database(self, db_name):
        self.cur.execute(sql.SQL("CONNECT DATABASE '{}'").format(sql.Identifier(db_name)))
        #logging.debug('self.cur.status: {}'.format(self.cur.status))


    def create_table(self, table_name, db_name):
        #sql_execute_string = 'CREATE TABLE '+table_name+' ( tweet_id bigint, tweet_text varchar(512));'
        self.cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS {} ( tweet_id bigint, tweet_text varchar(512), tweet_link varchar(256))").format(sql.Identifier(table_name)))
        logging.debug('Creating the table {} in {}.'.format(table_name, db_name))

    def insert_tweets(self, scraped_tweets):
        for i in scraped_tweets:
            #sql_string = ("INSERT INTO tweets (tweet_id, tweet_text) VALUES(%s, %s)",( i['id'], i['text']))

            # Check for entry based on id
            if self.check_tweet(i['id']) == False:
                # Sanitize the text.
                i['text'] = self.sanitize_string(i['text'])
                # Sanitize the link
                i['link'] = self.sanitize_link(i['link'])
                # Inseet the data.
                logging.debug('Returned sanitized string : {}'.format(i['text']))
                sql_query = (f"INSERT INTO tweets (tweet_id, tweet_text, tweet_link) VALUES('{i['id']}', '{i['text']}', '{i['link']}')")
                logging.debug('check_tweet: Adding to db {}'.format(sql_query))
                #safe_sql_query = (sql.SQL('{}').format(sql.Identifier(sql_query)))
                #safe_sql_query = (safe_sql_query.as_string(self.conn))
                self.cur.execute(sql_query)
                #self.cur.execute(sql_string)
                ##self.conn.commit()
            else:
                sql_query = (f"INSERT INTO tweets (tweet_id, tweet_text, tweet_link) VALUES('{i['id']}', '{i['text']}', '{i['link']}')")
                logging.debug('check_tweet: Already in db {}'.format(sql_query))     

    def check_tweet(self, tweet_id):
        sql_query = sql.SQL("SELECT tweet_id FROM tweets WHERE tweet_id='%s'"%(tweet_id))
        #logging.debug('check_tweet: {}'.format(sql_query))
        self.cur.execute(sql_query)
        return self.cur.fetchone() is not None

    def sanitize_string(self, tweet_string):
        #strip_chars = re.compile("'")
        logging.debug('tweet_string: {}'.format(tweet_string))
        formatted_string = self.strip_chars.sub("`", tweet_string)
        # remove trailing white space.
        if formatted_string.endswith(" "):
           formatted_string = formatted_string[:-1]
        # Add a period if one is not there.
        if formatted_string[-1] not in ['!', ',', '.', '\n', '?']:
            formatted_string += '.'
        logging.debug('sanitized_string: {}'.format(formatted_string))
        return formatted_string

    def sanitize_link(self, tweet_link):
        if tweet_link.endswith(" "):
            tweet_link = tweet_link[:-1]
        return tweet_link    

    def close_dbconn(self):
        self.cur.close()
        self.conn.close()
