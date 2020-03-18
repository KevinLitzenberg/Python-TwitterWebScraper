import requests
import logging
from bs4 import BeautifulSoup
from Postgres_db import postgresConnection
import pgpasslib

logging.basicConfig(level=logging.DEBUG)

# Prints the list of dictionary items.
def print_dict(dictonary):
    for i in dictonary:
        #logging.debug('i[id] {}'.format(i['id']))
        #logging.debug('i[text] {}'.format(i['text']))
        for k,v in i.items():
            print('{}:{}'.format(k,v))

# Prints all the html soup_obj   
def print_soup(soup_obj):
    print(soup_obj.prettify())

def tweet_base(soup_obj):
    timeline = html.select('#timeline li.stream-item')
    for tweet in timeline:
        tweet_id = tweet['data-item-id']
        tweet_text = tweet.select('p.tweet-text')[0].next
        tweet_link = tweet.select('a.twitter-timeline-link')[0].get_text()
        all_tweets.append({"id": tweet_id, "text": tweet_text, "link": tweet_link})

    return all_tweets


def print_tweet_base(soup_obj):
    timeline = html.select('#timeline li.stream-item')
    for tweet in timeline:
        tweet_text = tweet.select('p.tweet-text')[0].next
        print('tweet_text : {}'.format(tweet_text))

def write_to_file(soup_obj):
    f = open('html_output.txt', 'rb+')
    f.write(soup_obj)
    f.close()


def get_dbpasswd(host, port, user, db):
    password = pgpasslib.getpass(host, port, user, db)
    if not password:
        raise ValueError('Did not find a password in the .pgpass file')
    else:
        return password

if __name__== '__main__':
    
    # all tweets are global
    all_tweets = []
    url = 'https://twitter.com/TheOnion'
    data = requests.get(url)
    html = BeautifulSoup(data.text, 'html.parser')
   
    # pull all tweets and ids
    #logging.debug('Pretty print soup: {}'.format(print_soup(html))
    tweet_base(html)
    
    print_tweet_base(html)

    print_dict(all_tweets)
    #print(all_tweets)

    db_name = 'theonion'
    db_table = 'tweets'

    # Connect and create the postgres db connection object
    db_ps_wrd = get_dbpasswd('localhost', '32768', 'pgadmin', 'pgadmin')
    theOnion = postgresConnection('localhost', '32768', 'pgadmin', db_ps_wrd, 'pgadmin')
    theOnion.create_database(db_name)
    theOnion.close_dbconn()

    # Connect to new database and create the table
    db_ps_wrd = get_dbpasswd('localhost', '32768', 'pgadmin', db_name)
    theOnion = postgresConnection('localhost', '32768', 'pgadmin', db_ps_wrd, db_name)
    theOnion.create_table(db_table, db_name)
    theOnion.insert_tweets(all_tweets)

    theOnion.close_dbconn()

