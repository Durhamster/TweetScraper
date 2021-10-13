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

    single_multi = 0

    while single_multi not in (range(1, 6)):
        single_multi = int(
            input(
                "\nSelect an option:\n"
                "1) Scrape a single account\n"
                "2) Scrape multiple accounts\n"
                "3) Follower Counts from a list of handles\n"
                "4) Follower List and follower count for single account\n"
                "5) Check Handles\n"
            )
        )
        if single_multi in (range(1, 6)):
            continue

    # Prompt user for Account Handle(s) then checks or scrapes them

    if single_multi == 1:
        handle = input(
            "\nEnter the handle of the account you wish to scrape from (Do not include the @):\n"
        )
        get_tweets_single(handle)
        format_tweets(handle, tweets_dict)

    elif single_multi == 2:
        filename = input("\nEnter a name for the excel file (do NOT include .xlsx):\n")
        handle_list = load_text("Account Lists/handles.txt")
        get_tweets_multi(handle_list)
        format_tweets(filename, tweets_dict)

    elif single_multi == 3:
        filename = input("\nEnter a name for the excel file (do NOT include .xlsx):\n")
        handle_list = load_text("Account Lists/handles.txt")
        get_follower_count(filename, handle_list)

    elif single_multi == 4:
        user_warning = input(
            "\nWARNING: For accounts with 5,0000+ followers this"
            " may take multiple hours. Do you want to continue? (y or n)\n"
        )
        if user_warning == "y":
            handle = input(
                "\nEnter the handle of the account you wish to scrape from (Do not include the @):\n"
            )
            filename = input(
                "\nEnter a name for the excel file (do NOT include .xlsx):\n"
            )
            get_follower_list(handle)
            handle_list = get_follower_count()
            get_follower_count(filename, handle_list)
        else:
            pass

    else:
        handle_list = load_text("Account Lists/handles.txt")
        check_handles(handle_list)
        scrape_check = input("\nDo you want to scrape from this list? (y or n): \n")
        if scrape_check == "y":
            filename = input(
                "\nEnter a name for the excel file (do NOT include .xlsx):\n"
            )
            get_tweets_multi(handle_list)
            format_tweets(filename, tweets_dict)
        else:
            print(
                f"\nRoger. You can modify the list of handles by editing {cwd}/Account Lists/handles.txt"
            )
