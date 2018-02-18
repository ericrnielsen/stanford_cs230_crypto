import praw
import pandas as pd
from datetime import datetime
from datetime import date
import time

START_DATE = '2017-01-01'
END_DATE = 'today'
SUBREDDITS = [  "bitcoin", "ethereum", "litecoin", 
                "btc", "bitcoinmarkets", 
                "cryptocurrency", "cryptomarkets", "altcoin", "cryptocurrencies", "blockchain"]

RAW_FILEPATH = "raw/"
ALL_SUB_RAW_FILE = "all_sub_raw.csv"

############################################################################
# Convert strings to unix dates
############################################################################
def get_unix_dates(start_date, end_date):

    # Create date objects from start and end dates
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date == 'today':
        today = '%s-%s-%s' % (date.today().year, date.today().month, date.today().day)
        end_date_obj = datetime.strptime(today, '%Y-%m-%d').date()
    else:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Convert to unix dates and return
    return time.mktime(start_date_obj.timetuple()), time.mktime(end_date_obj.timetuple())

############################################################################
# Scrape single subreddit and save to csv file
############################################################################
def scrape_subreddit(sub_name, start, end):

    # Just for printing
    print "Starting r.%s" % sub_name.upper()

    # Will be list of dictionaries with post info
    data = []

    # Get all posts for subreddit within desired timeframe
    subreddit = reddit.subreddit(sub_name)
    posts = subreddit.submissions(start, end)

    # Loop through all posts
    i, j = 0, 0
    for post in posts:
        i += 1

        # Get post date, title, score, and num comments; append to master data list
        temp_dict = {}
        temp_dict["date"] = datetime.fromtimestamp(post.created).strftime('%m/%d/%Y')
        temp_dict["title"] = post.title.encode("utf8")
        temp_dict["score"] = post.score
        temp_dict["num_comments"] = post.num_comments
        data.append(temp_dict)

        # Just for printing
        if i == 1 or datetime.fromtimestamp(post.created).date() < current_date.date():
            current_date = datetime.fromtimestamp(post.created)
            print "[%s] Added: %d  Total: %d" % (current_date.strftime('%m/%d/%Y'), (i-j), i)
            j = i

    # Just for printing
    print "Retrieved %d posts from r.%s" % (i, sub_name.upper())

    # Store the list of data in a Pandas dataframe, save to csv
    sub_df = pd.DataFrame(data)
    sub_df.to_csv(RAW_FILEPATH + ALL_SUB_RAW_FILE)

    # Return df
    return sub_df

############################################################################
# Combine all posts into single csv file
############################################################################
def combine_subreddits(frames):

    # If needing to read in all raw data from files
    if not frames:
        frames = []
        for sub_name in SUBREDDITS:
            sub_df = pd.read_csv(RAW_FILEPATH + sub_name + "_sub_raw.csv")
            print "[%s] %d" % (sub_name, sub_df.shape[0])
            sub_df['subreddit'] = sub_name
            frames.append(sub_df)

    # Combine into single df
    subs_df = pd.concat(frames, ignore_index=True)

    # Sort values in df by descending date
    subs_df['date'] = pd.to_datetime(subs_df['date'])   # Convert date column to datetime objs
    subs_df = subs_df.sort_values(['date'], ascending=[False])           # Sort by descending date
    subs_df['date'] = subs_df['date'].dt.strftime('%m/%d/%Y')   # Convert dates back to strings
    subs_df.reset_index(drop=True)                      # Re-index

    # Save all posts to a single raw file
    print "Total posts: %s" % subs_df.shape[0]
    subs_df = subs_df.reindex(columns=["date", "subreddit", "score", "num_comments", "title"])
    subs_df.to_csv(RAW_FILEPATH + "all" + "_sub_raw.csv")

############################################################################
# Main
############################################################################
def main():

    #################################
    # NORMAL
    #################################
    if (False):

        # Get start and stop unix dates (required by praw)
        start_unix, end_unix = get_unix_dates(START_DATE, END_DATE)

        # Initialize reddit instance
        reddit = praw.Reddit('bot1')

        # Loop through all subreddits
        frames = []
        for sub_name in SUBREDDITS:  
            sub_df = scrape_subreddit(sub_name, start_unix, end_unix)
            frames.append(sub_df)

        # Combine into single raw datafile
        combine_subreddits(frames)

    #################################
    # JUST TO COMBINE DATA
    #################################
    if (True):
        combine_subreddits(None)

if __name__ == '__main__':
	main()