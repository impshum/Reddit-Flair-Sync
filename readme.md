## Reddit Flair Sync

Syncs user flairs from one to many subreddits. Searches for user flairs over a given day range, stores them in an SQLite database and finally updates flairs.

### Instructions

-   Install requirements `pip install -r requirements.txt`
-   Create Reddit (script) app at https://www.reddit.com/prefs/apps/ and get keys
-   Edit conf.ini with your details
-   Run it `python run.py`

### Settings Info

**[REDDIT]**

`user` - Reddit username  
`pass` - Reddit password  
`client_id` - Reddit Client ID  
`client_secret` - Reddit Client Secret  

**[SETTINGS]**

`main_target_subreddit` - Subreddit to collect flairs from  
`flair_subreddits` = Subreddits to apply flairs e.g. one,two,three  
`min_days` = minimum days to search for user flairs (0 = today)  
`max_days` = maximum days to search for user flairs (7 = 1 week)

### More Info

Get all the user flairs from the last month.

    min_days = 0
    max_days = 30

Get all the user flairs from the last 24hrs.

    min_days = 0
    max_days = 1
