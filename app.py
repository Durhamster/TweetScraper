from os import getcwd, getenv, makedirs, path, startfile
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
from time import sleep
from tweepy import API, OAuthHandler, TweepError
import pandas as pd
from tqdm import tqdm

# Loads .env file
load_dotenv()

cwd = getcwd()
today = datetime.now()

# Gets API Credentials for Tweepy
auth = OAuthHandler(getenv("consumer_key"), getenv("consumer_secret"))
auth.set_access_token(getenv("access_key"), getenv("access_secret"))
auth_api = API(auth)

# Dictionary to store tweets scraped
tweets_dict = {
    "Date": [],
    "Account Name": [],
    "Handle": [],
    "URL": [],
    "Likes": [],
    "Retweets": [],
    "Text": [],
}

# Dictionary to store accounts follower count
accounts_dict = {
    "Handle": [],
    "URL": [],
    "Followers": [],
}

""" Gets tweets from single handle """


def get_tweets_single(handle, time_frame, time_list):
    try:
        # Scrapes for each handle
        tweets = auth_api.user_timeline(
            screen_name=handle, count=500, include_rts=True, tweet_mode="extended"
        )

        for tweet in tweets[:500]:
            if tweet.created_at >= time_list[int(time_frame)]:
                tweets_dict["Date"].append(tweet.created_at)
                tweets_dict["Account Name"].append(tweet.user.name)
                tweets_dict["Handle"].append(handle)
                tweets_dict["URL"].append(
                    f"https://twitter.com/{handle}/status/{tweet.id}"
                )
                tweets_dict["Likes"].append(tweet.favorite_count)
                tweets_dict["Retweets"].append(tweet.retweet_count)
                tweets_dict["Text"].append(tweet.full_text)
            else:
                pass
    except Exception:
        sys.exit("\nError. Account handle is suspended, private, or nonexistent.\n")


""" Gets tweets from a list of handles """


def get_tweets_multi(handle_list, time_frame, time_list):
    # Counts number of handles scraped
    count = 0
    # Counts number of handles unable to scrape
    except_count = 0
    except_list = []
    with tqdm(total=len(handle_list), file=sys.stdout) as pbar:
        # Scrapes for each handle
        for handle in handle_list:
            try:
                tweets = auth_api.user_timeline(
                    screen_name=handle,
                    count=500,
                    include_rts=True,
                    tweet_mode="extended",
                )
                count += 1
                for tweet in tweets[:500]:
                    if tweet.created_at >= time_list[int(time_frame)]:
                        tweets_dict["Date"].append(tweet.created_at)
                        tweets_dict["Account Name"].append(tweet.user.name)
                        tweets_dict["Handle"].append(handle)
                        tweets_dict["URL"].append(
                            f"https://twitter.com/{handle}/status/{tweet.id}"
                        )
                        tweets_dict["Likes"].append(tweet.favorite_count)
                        tweets_dict["Retweets"].append(tweet.retweet_count)
                        tweets_dict["Text"].append(tweet.full_text)
                    else:
                        pass
                # Update progress bar
                pbar.update(1)

                # Pauses periodically to avoid hitting tweepy's rate limit
                if count == 50:
                    sleep(60)
                    count -= 50
            except TweepError:
                except_count += 1
                except_list.append(handle)
                pass

    if except_count >= 1:
        print(
            f"\nUnable to scrape from {except_count} accounts. "
            "The following are suspended, private, or incorrect:"
        )
        print(f"{except_list}\n")


""" Load a text file as a list."""


def load(file):
    try:
        with open(file) as in_file:
            loaded_txt = in_file.read().strip().split("\n")
            loaded_txt = [x.lower() for x in loaded_txt]
            return loaded_txt
    except IOError as e:
        print(
            "{}\nError opening {}.".format(e, file),
            file=sys.stderr,
        )
        sys.exit(1)


""" Formats the scraped tweets into an excel file """


def format_tweets(handle, tweets_dict):

    # Creates scraped data folder if it does not exist
    if not path.exists("Data/"):
        makedirs("Data/")

    file_name = f"Data/{handle} {today.month}-{today.day}.xlsx"
    # Formats Tweets into Excel
    df = pd.DataFrame(tweets_dict)
    writer = pd.ExcelWriter(file_name, engine="xlsxwriter")
    df.to_excel(
        writer,
        sheet_name=handle,
        encoding="utf-8",
        index=False,
    )
    workbook = writer.book
    worksheet = writer.sheets[handle]
    worksheet.freeze_panes(1, 0)
    worksheet.autofilter("A1:G1")
    top_row = workbook.add_format(
        {"bg_color": "black", "font_color": "white"}
    )  # sets the top row colors
    worksheet.set_column("A:A", 18)
    worksheet.set_column("B:B", 20)
    worksheet.set_column("C:C", 20)
    worksheet.set_column("D:D", 10)
    worksheet.set_column("E:E", 10)
    worksheet.set_column("F:F", 10)
    worksheet.set_column("G:G", 75)

    # Sets the top row/header font and color
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, top_row)

    writer.save()

    print(f"Data saved to {cwd}\{file_name}\n")

    # Asks user if they want to open the file
    opensheet = input("Press y to open the file:\n").lower()

    if opensheet == "y":
        startfile(f"{cwd}/{file_name}")
    else:
        pass


""" Gets the timeframe for the tweets to be scraped """


def get_timeframe():
    # Filters out tweets not from the past 24 hours or past weekend
    today, yesterday, twodays, threedays, oneweek, twoweeks, onemonth, all500 = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=3),
        datetime.now() - timedelta(days=4),
        datetime.now() - timedelta(days=7),
        datetime.now() - timedelta(days=14),
        datetime.now() - timedelta(days=30),
        datetime.now() - timedelta(days=365),
    ]
    time_frame = " "
    time_list = [
        today,
        yesterday,
        twodays,
        threedays,
        oneweek,
        twoweeks,
        onemonth,
        all500,
    ]

    # Prompt user for time frame to scrape from
    while time_frame not in (range(1, 8)):
        time_frame = int(
            input(
                "\nEnter a Time Frame:\n 1) The Past 24 Hours\n 2) 48 Hours\n 3) 72 Hours\n 4) Week\n 5) Two Weeks\n 6) One Month\n 7) Last 500 Tweets\n \n"
            )
        )
        if time_frame in (range(1, 8)):
            continue

    return time_frame, time_list


def check_handles(handle_list):
    # Counts number of handles scraped
    count = 0
    # Counts number of handles unable to scrape
    except_count = 0
    except_list = []
    with tqdm(total=len(handle_list), file=sys.stdout) as pbar:
        for handle in handle_list:
            count += 1
            try:
                auth_api.get_user(handle)
                # Update progress bar
                pbar.update(1)
            except TweepError:
                except_count += 1
                except_list.append(handle)
                pass

    if except_count >= 1:
        print(
            f"\nUnable to connect with {except_count} handles. "
            "The following are suspended, private, or incorrect:"
        )
        print(f"{except_list}\n")
    else:
        print(
            "\nNone of the handles on the list are suspended, private, or incorrect.\n"
        )


# USER INPUT SECTION
single_multi = 0

while single_multi not in (range(1, 4)):
    single_multi = int(
        input(
            "\nSelect an option:\n 1) Single Handle\n 2) Multiple Handles\n 3) Check Handles\n"
        )
    )
    if single_multi in (range(1, 4)):
        continue

# Get Account Handle(s) from user

if single_multi == 1:
    handle = input(
        "Enter the handle of the account you wish to scrape from (Do not include the @):\n"
    )
    time_frame, time_list = get_timeframe()
    get_tweets_single(handle, time_frame, time_list)
    format_tweets(handle, tweets_dict)
elif single_multi == 2:
    filename = input("\nEnter a name for the excel file (do NOT include .xlsx):\n")
    handle_list = load("Account Lists/handles.txt")
    time_frame, time_list = get_timeframe()
    get_tweets_multi(handle_list, time_frame, time_list)
    format_tweets(filename, tweets_dict)
else:
    handle_list = load("Account Lists/handles.txt")
    check_handles(handle_list)
