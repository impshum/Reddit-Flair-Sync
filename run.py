from psaw import PushshiftAPI
import praw
from datetime import datetime, time, timedelta
import sqlite3
from sqlite3 import Error
import configparser


def db_connect():
    try:
        conn = sqlite3.connect('data.db')
        create_table = """CREATE TABLE IF NOT EXISTS users (
                                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        author TEXT NOT NULL,
                                        flair TEXT NOT NULL,
                                        complete INTEGER DEFAULT 0
                                        );"""
        conn.execute(create_table)
        return conn
    except Error as e:
        print(e)
    return None


def insert_row(conn, author, flair):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE author = ? LIMIT 1", (author,))
    if not cur.fetchone():
        conn.execute("INSERT INTO users (author, flair) VALUES (?, ?);", (author, flair))
        return True


def get_epochs(days):
    midnight = datetime.combine(
        datetime.today(), time.min) - timedelta(days=days)
    yesterday_midnight = midnight - timedelta(days=1)
    x = midnight.strftime('%d')
    y = yesterday_midnight.strftime('%d/%m/%Y')
    midnight = int(midnight.timestamp())
    yesterday_midnight = int(yesterday_midnight.timestamp())
    return x, y, midnight, yesterday_midnight


def apply_flairs(conn, reddit, reddit_flair_subreddits):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE complete = 0")
    rows = cur.fetchall()
    for i, row in enumerate(rows):
        author = row[1]
        flair = row[2]
        for sub in reddit_flair_subreddits:
            reddit.subreddit(sub).flair.set(author, flair)
        print(f'{author} - {flair}')
        conn.execute("UPDATE users SET complete = 1 WHERE author = ?;", (author,))
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('conf.ini')
    reddit_user = config['REDDIT']['user']
    reddit_pass = config['REDDIT']['pass']
    reddit_client_id = config['REDDIT']['client_id']
    reddit_client_secret = config['REDDIT']['client_secret']
    reddit_main_target_subreddit = config['SETTINGS']['main_target_subreddit']
    reddit_flair_subreddits = config['SETTINGS']['flair_subreddits'].split(',')
    reddit_min_days = int(config['SETTINGS']['min_days'])
    reddit_max_days = int(config['SETTINGS']['max_days'])
    test_mode = config['SETTINGS'].getboolean('test_mode')

    reddit = praw.Reddit(
        username=reddit_user,
        password=reddit_pass,
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent='Reddit Flair Sync (by u/impshum)'
    )

    conn = db_connect()
    api = PushshiftAPI()

    new_users = 0

    for i in range(reddit_min_days, reddit_max_days):
        day_users = 0
        x, y, midnight, yesterday_midnight = get_epochs(i)
        posts = list(api.search_submissions(after=yesterday_midnight,
                                            before=midnight,
                                            subreddit=reddit_main_target_subreddit,
                                            filter=['author', 'author_flair_text']))
        for post in posts:
            author = post.author
            author_flair_text = post.author_flair_text
            if author_flair_text:
                if insert_row(conn, author, author_flair_text):
                    day_users += 1
                    new_users += 1
        if day_users:
            conn.commit()

        print(f'{x}-{y} --- {day_users} new users')

    print(f'total new users found: {new_users}')

    apply_flairs(conn, reddit, reddit_flair_subreddits)

if __name__ == '__main__':
    main()
