import pandas as pd
import sys

from datetime import datetime
from dotenv import load_dotenv
from os import getcwd, getenv, startfile
from time import sleep
from tqdm import tqdm
from tweepy import API, Cursor, OAuthHandler, TweepyException

# Loads .env file
load_dotenv()

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


def format_tweets(handle, tweets_dict):
    filename = f"Data/{handle} {today.month}-{today.day}.xlsx"
    # Formats Tweets into Excel
    df = pd.DataFrame(tweets_dict)
    # Removes timezone from Date to prevent excel issues
    df["Date"] = df["Date"].apply(lambda a: pd.to_datetime(a).date())
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")
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

    print(f"Data saved to {cwd}\{filename}\n")

    open_sheet(cwd, filename)


""" Checks list and returns list and number of handles that are unavailable """


def check_handles(handle_list):
    # Counts number of handles unable to scrape
    except_count = 0
    except_list = []
    with tqdm(total=len(handle_list), file=sys.stdout) as pbar:
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


def get_follower_list(handle):
    filename = f"Data/{handle} followers {today.month}-{today.day}.xlsx"
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
    with tqdm(total=num_followers, file=sys.stdout) as pbar:
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
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")
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

    print(f"Data saved to {cwd}\{filename}\n")

    open_sheet(cwd, filename)

    return accounts_dict


""" Gets the follower count of a list of handles """


def get_follower_count(filename, account_list):
    # Progress bar
    with tqdm(total=len(account_list), file=sys.stdout) as pbar:
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
            writer = pd.ExcelWriter(filename, engine="xlsxwriter")
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

    print(f"Data saved to {cwd}\{filename}\n")

    open_sheet(cwd, filename)


""" Prompts user to open the file"""


def open_sheet(cwd, filename):
    opensheet = input("Do you want to open the excel file? (y or n): \n").lower()

    if opensheet == "y":
        startfile(f"{cwd}/{filename}")
        print("Opening file...\n")
        sleep(3)
    else:
        pass
