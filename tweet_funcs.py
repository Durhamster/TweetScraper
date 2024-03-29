import pandas as pd
import sys

from datetime import datetime
from dotenv import load_dotenv
from os import getcwd, getenv, startfile
from rich import print
from rich.console import Console
from time import sleep, time
from tqdm import tqdm
from tweepy import API, Cursor, OAuthHandler, TweepyException

# Loads .env file
load_dotenv()

console = Console()
cwd = getcwd()
today = datetime.now()

# Gets API Credentials for Tweepy
auth = OAuthHandler(getenv("consumer_key"), getenv("consumer_secret"))
auth.set_access_token(getenv("access_key"), getenv("access_secret"))
auth_api = API(auth, wait_on_rate_limit=True)

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
    "Screen Name": [],
    "Handle": [],
    "URL": [],
    "Followers": [],
    "Verified": [],
}

"""Converts seconds at the end to show how long the scraping and formatting process took
----------
seconds : raw seconds from time() - start_time
"""


def convert_time(seconds):

    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


""" Converts URLs to strings if Excel limit is exceeded (65,530)"""


def check_url_count(df, file_name):
    if len(df.index) >= 65530:
        writer = pd.ExcelWriter(
            file_name,
            engine="xlsxwriter",
            engine_kwargs={"options": {"strings_to_urls": False}},
        )

        print(
            "\nThis file will exceed the URL limit in excel (65,530). Converting all URLs to strings...\n"
        )

    else:
        writer = pd.ExcelWriter(file_name, engine="xlsxwriter")

    return writer


""" Gets tweets based on a keyword search """


def keyword_search(keyword, rt):

    if rt == 1:
        results = "mixed"
    elif rt == 2:
        results = "popular"
    elif rt == 3:
        results = "recent"

    tweets = auth_api.search_tweets(
        keyword, result_type=results, lang="en", tweet_mode="extended", count=500
    )

    for tweet in tweets[:500]:
        tweets_dict["Date"].append(tweet.created_at)
        tweets_dict["Account Name"].append(tweet.user.name)
        tweets_dict["Handle"].append(tweet.user.screen_name)
        tweets_dict["URL"].append(
            f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
        )
        tweets_dict["Likes"].append(tweet.favorite_count)
        tweets_dict["Retweets"].append(tweet.retweet_count)
        tweets_dict["Text"].append(tweet.full_text)

    print(f"\nA total of {len(tweets)} tweets were scraped for '{keyword}'.\n")

    return tweets_dict


""" Gets tweets from single handle """


def get_tweets_single(handle):
    try:
        # Scrapes for each handle
        tweets = auth_api.user_timeline(
            screen_name=handle, count=500, include_rts=True, tweet_mode="extended"
        )

        for tweet in tweets[:500]:
            tweets_dict["Date"].append(tweet.created_at)
            tweets_dict["Account Name"].append(tweet.user.name)
            tweets_dict["Handle"].append(handle)
            tweets_dict["URL"].append(f"https://twitter.com/{handle}/status/{tweet.id}")
            tweets_dict["Likes"].append(tweet.favorite_count)
            tweets_dict["Retweets"].append(tweet.retweet_count)
            tweets_dict["Text"].append(tweet.full_text)
    except Exception:
        sys.exit("\nError. Account handle is suspended, private, or nonexistent.\n")


"""Gets tweets from a list of handles"""


def get_tweets_multi(handle_list):
    # Counts number of handles unable to scrape
    except_count = 0
    except_list = []
    with tqdm(total=len(handle_list), file=sys.stdout, colour="GREEN") as pbar:
        # Scrapes for each handle
        for handle in handle_list:
            try:
                tweets = auth_api.user_timeline(
                    screen_name=handle,
                    count=500,
                    include_rts=True,
                    tweet_mode="extended",
                )
                for tweet in tweets[:500]:
                    tweets_dict["Date"].append(tweet.created_at)
                    tweets_dict["Account Name"].append(tweet.user.name)
                    tweets_dict["Handle"].append(handle)
                    tweets_dict["URL"].append(
                        f"https://twitter.com/{handle}/status/{tweet.id}"
                    )
                    tweets_dict["Likes"].append(tweet.favorite_count)
                    tweets_dict["Retweets"].append(tweet.retweet_count)
                    tweets_dict["Text"].append(tweet.full_text)
                # Update progress bar
                pbar.update(1)

            except TweepyException:
                except_count += 1
                except_list.append(handle)
                pass

    if except_count >= 1:
        print(
            f"\nUnable to scrape from {except_count} accounts. "
            "The following are suspended, private, or incorrect:"
        )
        print(f"{except_list}\n")


"""Load a text file as a list"""


def load_text(file):
    try:
        with open(file) as in_file:
            loaded_txt = in_file.read().strip().split("\n")
            return loaded_txt
    except IOError as e:
        print(
            "{}\nError opening {}.".format(e, file),
            file=sys.stderr,
        )
        sys.exit(1)


""" Formats the scraped tweets into an excel file """


def format_tweets(handle, start_time, tweets_dict):
    file_name = f"Data/{handle} {today.month}-{today.day}.xlsx"
    # Formats Tweets into Excel
    df = pd.DataFrame(tweets_dict)
    # Removes timezone from Date to prevent excel issues
    df["Date"] = df["Date"].apply(lambda a: pd.to_datetime(a).date())

    writer = check_url_count(df, file_name)

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

    print(f"Data saved to [green]{cwd}\{file_name}[/green]\n")

    print("Job completed in", convert_time(round(time() - start_time, 2)), "⏰")

    open_sheet(cwd, file_name)


""" Checks list and returns list and number of handles that are unavailable """


def check_handles(handle_list):
    # Counts number of handles unable to scrape
    except_count = 0
    except_list = []
    with tqdm(total=len(handle_list), file=sys.stdout, colour="GREEN") as pbar:
        for handle in handle_list:
            try:
                auth_api.get_user(screen_name=handle)
                # Update progress bar
                pbar.update(1)
            except TweepyException:
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


""" Get the list of followers for a single account """


def get_follower_list(handle, start_time):
    file_name = f"Data/{handle} followers {today.month}-{today.day}.xlsx"
    # Gets follower count of the user
    user = auth_api.get_user(screen_name=handle)
    num_followers = user.followers_count
    print(f"Fetching names for {num_followers} followers...\n")
    # Keeps count for periodic saving
    count = 0

    count_stop_points = [
        int(num_followers / 10),
        int((num_followers / 10) * 2),
        int((num_followers / 10) * 3),
        int((num_followers / 10) * 4),
        int((num_followers / 10) * 5),
        int((num_followers / 10) * 6),
        int((num_followers / 10) * 7),
        int((num_followers / 10) * 8),
        int((num_followers / 10) * 9),
        num_followers,
    ]
    # Count number of suspended or banned accounts
    dead_count = 0
    # Adds # at the end of multiple sheets to prevent saving over
    sheet_count = 0
    # Progress bar
    with tqdm(total=num_followers, file=sys.stdout, colour="GREEN") as pbar:
        for i in range(1):
            for follower in Cursor(auth_api.get_followers, screen_name=handle).items(
                num_followers
            ):
                try:

                    accounts_dict["Screen Name"].append(follower.name)
                    accounts_dict["Handle"].append(follower.screen_name)
                    accounts_dict["URL"].append(
                        f"https://twitter.com/{follower.screen_name}"
                    )
                    accounts_dict["Followers"].append(follower.followers_count)
                    accounts_dict["Verified"].append(follower.verified)
                    count += 1

                    pbar.update(1)

                    if count in count_stop_points:
                        sheet_count += 1
                        print("\nStop point reached - saving CSV file...\n")
                        follow_df = pd.DataFrame(accounts_dict)
                        follow_df.to_csv(
                            f"Data/Checkpoints/{handle}_Follower_List{sheet_count}.csv"
                        )

                except TweepyException:
                    count += 1
                    dead_count += 1
                    pbar.update(1)

        print(f"\nNumber of suspended/banned/deleted accounts: {dead_count}\n")

    # Formats Results into Excel
    df = pd.DataFrame(accounts_dict)

    writer = check_url_count(df, file_name)

    df.to_excel(
        writer,
        sheet_name="Accounts",
        encoding="utf-8",
        index=False,
    )
    workbook = writer.book
    worksheet = writer.sheets["Accounts"]
    worksheet.freeze_panes(1, 0)
    worksheet.autofilter("A1:C1")
    top_row = workbook.add_format(
        {"bg_color": "black", "font_color": "white"}
    )  # sets the top row colors
    num_format = workbook.add_format({"num_format": "#,##0"})

    worksheet.set_column("A:A", 18)
    worksheet.set_column("B:B", 20)
    worksheet.set_column("C:C", 10, num_format)

    # Sets the top row/header font and color
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, top_row)

    writer.save()

    print("Job completed in", convert_time(round(time() - start_time, 2)), "⏰")

    print(f"Data saved to [green]{cwd}\{file_name}[/green]\n")

    open_sheet(cwd, file_name)

    return accounts_dict


""" Gets the follower count of a list of handles """


def get_follower_count(file_name, account_list, start_time):
    # Progress bar
    with tqdm(total=len(account_list), file=sys.stdout, colour="GREEN") as pbar:
        for i in range(1):
            # Scrapes followers for each handle
            for handle in account_list:
                try:
                    users = auth_api.get_user(screen_name=handle)
                    accounts_dict["Screen Name"].append(users.name)
                    accounts_dict["Handle"].append(handle)
                    accounts_dict["URL"].append(f"https://twitter.com/{handle}")
                    accounts_dict["Followers"].append(users.followers_count)
                    accounts_dict["Verified"].append(users.verified)

                    pbar.update(1)
                except TweepyException:
                    accounts_dict["Screen Name"].append(handle.name)
                    accounts_dict["Handle"].append(handle)
                    accounts_dict["URL"].append(f"https://twitter.com/{handle}")
                    accounts_dict["Followers"].append("N/A")
                    accounts_dict["Verified"].append("N/A")

                    pass

            # Formats Results into Excel
            df = pd.DataFrame(accounts_dict)

            writer = check_url_count(df, file_name)

            df.to_excel(
                writer,
                sheet_name="Accounts",
                encoding="utf-8",
                index=False,
            )
            workbook = writer.book
            worksheet = writer.sheets["Accounts"]
            worksheet.freeze_panes(1, 0)
            worksheet.autofilter("A1:C1")
            top_row = workbook.add_format(
                {"bg_color": "black", "font_color": "white"}
            )  # sets the top row colors
            num_format = workbook.add_format({"num_format": "#,##0"})

            worksheet.set_column("A:A", 18)
            worksheet.set_column("B:B", 20)
            worksheet.set_column("C:C", 10, num_format)

            # Sets the top row/header font and color
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, top_row)

            writer.save()

    print("Job completed in", convert_time(round(time() - start_time, 2)), "⏰")

    print(f"Data saved to [green]{cwd}\{file_name}[/green]\n")

    open_sheet(cwd, file_name)


""" Prompts user to open the file"""


def open_sheet(cwd, file_name):
    openSheet = " "
    while (openSheet != "y") and (openSheet != "n"):
        openSheet = console.input(
            "\nDo you want to open the excel file? [cyan](y or n)[/cyan]: \n"
        ).lower()

    if openSheet == "y":
        startfile(f"{cwd}/{file_name}")
        print("Opening file...\n")
        sleep(3)
    else:
        print("\n")
