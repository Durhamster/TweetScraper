from os import makedirs, path
from tweet_funcs import (
    cwd,
    check_handles,
    format_tweets,
    get_follower_count,
    get_follower_list,
    get_tweets_multi,
    get_tweets_single,
    load_text,
    tweets_dict,
)


if __name__ == "__main__":

    # Creates scraped data folder if it does not exist
    if not path.exists("Data"):
        makedirs("Data")

    single_multi = 0

    while single_multi not in (range(1, 6)):
        single_multi = int(
            input(
                "\nSelect an option:\n"
                "1) Scrape a single account\n"
                "2) Scrape multiple accounts\n"
                "3) Follower counts from a list of handles\n"
                "4) Follower list and follower count for a single account\n"
                "5) Check handles\n"
            )
        )
        if single_multi in (range(1, 6)):
            continue

    # Prompt user for Account Handle(s) then checks or scrapes them

    if single_multi == 1:
        handle = input(
            "\nEnter the handle of the account you wish to scrape from (do NOT include the @):\n"
        )
        get_tweets_single(handle)
        format_tweets(handle, tweets_dict)

    elif single_multi == 2:
        file_name = input("\nEnter a name for the excel file (do NOT include .xlsx):\n")
        handle_list = load_text("Account Lists/handles.txt")
        get_tweets_multi(handle_list)
        format_tweets(file_name, tweets_dict)

    elif single_multi == 3:
        file_name = input("\nEnter a name for the excel file (do NOT include .xlsx):\n")
        handle_list = load_text("Account Lists/handles.txt")
        get_follower_count(file_name, handle_list)

    elif single_multi == 4:
        user_warning = input(
            "\nWARNING: For accounts with 5,0000+ followers this"
            " may take multiple hours. During this there will be checkpoints created each time the number "
            "of accounts scraped reaches 10 percent of the list of followers. These can be found as CSV files under "
            "the data directory, in a directory called 'Checkpoints'. "
            " Do you want to continue? (y or n)\n"
        ).lower()
        if user_warning == "y":
            if not path.exists("Data/Checkpoints"):
                makedirs("Data/Checkpoints")
            handle = input(
                "\nEnter the handle of the account you wish to scrape from (Do not include the @):\n"
            )
            get_follower_list(handle)
        else:
            pass

    else:
        handle_list = load_text("Account Lists/handles.txt")
        check_handles(handle_list)
        scrape_check = input(
            "\nDo you want to scrape from this list? (y or n):\n"
        ).lower()
        if scrape_check == "y":
            file_name = input(
                "\nEnter a name for the excel file (do NOT include .xlsx):\n"
            )
            get_tweets_multi(handle_list)
            format_tweets(file_name, tweets_dict)
        else:
            print(
                f"\nRoger. You can modify the list of handles by editing {cwd}/Account Lists/handles.txt"
            )
