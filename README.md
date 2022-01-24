# TweetScraper

![Python Version](https://img.shields.io/pypi/pyversions/pandas?style=for-the-badge)
![License](https://img.shields.io/github/license/Durhamster/TweetScraper?style=for-the-badge)

A script using the Twitter API to do the following:

1. Scrape a single account
2. Scrape a list of accounts
3. Get the follower count for a list of accounts
4. Check a list of handles to see if any are suspended, private, or incorrect.

All tweets and follower counts are saved to a formatted excel (.xlsx) file.

> Please note that this only scrapes up to the 500 recent tweets. This can be changed in the script itself.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required libraries.

```bash
pip install -r requirements.txt
```

## Obtaining a Twitter Developer Key

> If you do not have a Twitter handle you must first sign up for one.

1. Apply for [API access](https://developer.twitter.com/en/apply-for-access.html)
2. Create your application.
3. Get your authentication details.
4. In the folder containing this README file (_the main folder for this project_)
   - Open the .env file and enter the client id and secret like the following and save the file.

```bash
consumer_key = "YourConsumerKeyHere"
consumer_secret = "YourSecretKeyHere"
access_key = "YourAccessKeyHere"
access_secret = "YourAccessSecretHere"
```

More detailed instructions on how to obtain an api key can be found [here.](https://towardsdatascience.com/how-to-access-twitters-api-using-tweepy-5a13a206683b)

## Scraping Lists of Twitter Handles

> When scraping multiple handles, this script will pause periodically to prevent the user from exceeding the rate limit.

To change the list of handles to be scraped, open the handles.txt file under the Account Lists directory. Do NOT include the '@' sign. Make sure to list one handle per line.

For example:

```bash
Twitter
Jack
BBCNews
Apple
Windows
msexcel
Android
Reddit
Discord
github
```
