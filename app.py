from tweet_funcs import (
    cwd,
    check_handles,
    format_tweets,
    get_timeframe,
    get_tweets_multi,
    get_tweets_single,
    load_text,
    tweets_dict,
)


if __name__ == "__main__":

    single_multi = 0

    while single_multi not in (range(1, 4)):
        single_multi = int(
            input(
                "\nSelect an option:\n 1) Single Handle\n 2) Multiple Handles\n 3) Check Handles\n"
            )
        )
        if single_multi in (range(1, 4)):
            continue

    # Prompt user for Account Handle(s) then checks or scrapes them

    if single_multi == 1:
        handle = input(
            "Enter the handle of the account you wish to scrape from (Do not include the @):\n"
        )
        time_frame, time_list = get_timeframe()
        get_tweets_single(handle, time_frame, time_list)
        format_tweets(handle, tweets_dict)
    elif single_multi == 2:
        filename = input("\nEnter a name for the excel file (do NOT include .xlsx):\n")
        handle_list = load_text("Account Lists/handles.txt")
        time_frame, time_list = get_timeframe()
        get_tweets_multi(handle_list, time_frame, time_list)
        format_tweets(filename, tweets_dict)
    else:
        handle_list = load_text("Account Lists/handles.txt")
        check_handles(handle_list)
        scrape_check = input("\nDo you want to scrape from this list? (y or n): \n")
        if scrape_check == "y":
            filename = input(
                "\nEnter a name for the excel file (do NOT include .xlsx):\n"
            )
            time_frame, time_list = get_timeframe()
            get_tweets_multi(handle_list, time_frame, time_list)
            format_tweets(filename, tweets_dict)
        else:
            print(
                f"\nRoger. You can modify the list of handles by editing {cwd}/Account Lists/handles.txt"
            )
