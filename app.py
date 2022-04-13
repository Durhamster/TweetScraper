from os import makedirs, path
from rich import print
from rich.console import Console
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


console = Console()

if __name__ == "__main__":

    # Creates scraped data folder if it does not exist
    if not path.exists("Data"):
        makedirs("Data")

    single_multi = 0

    while single_multi not in (range(1, 6)):
        try:
            single_multi = int(
                console.input(
                    "\n[cyan]Select an option[/cyan]:\n"
                    "1) Scrape a single account\n"
                    "2) Scrape multiple accounts\n"
                    "3) Follower counts from a list of handles\n"
                    "4) Follower list and follower count for a single account\n"
                    "5) Check handles\n"
                )
            )
        except ValueError:
            print("\n[red]Please enter a number.[/red]")

        if single_multi in (range(1, 6)):
            continue

    # Prompt user for Account Handle(s) then checks or scrapes them

    if single_multi == 1:
        handle = console.input(
            "\nEnter the handle of the account you wish to scrape from [red](do NOT include the @)[/red]:\n"
        )
        get_tweets_single(handle)
        format_tweets(handle, tweets_dict)

    elif single_multi == 2:
        file_name = console.input(
            "\nEnter a name for the excel file [red](do NOT include .xlsx)[/red]:\n"
        )
        handle_list = load_text("Account Lists/handles.txt")
        get_tweets_multi(handle_list)
        format_tweets(file_name, tweets_dict)

    elif single_multi == 3:
        file_name = console.input(
            "\nEnter a name for the excel file [red](do NOT include .xlsx)[/red]:\n"
        )
        handle_list = load_text("Account Lists/handles.txt")
        get_follower_count(file_name, handle_list)

    elif single_multi == 4:
        user_warning = " "
        while (user_warning != "y") and (user_warning != "n"):
            user_warning = console.input(
                "\n[red]WARNING[/red]: For accounts with 5,0000+ followers this"
                " may take multiple hours. During this there will be checkpoints created each time the number "
                "of accounts scraped reaches 10 percent of the list of followers. These can be found as CSV files under "
                "the data directory, in a directory called 'Checkpoints'. "
                " Do you want to continue? [cyan](y or n)[/cyan]:\n"
            ).lower()
        if user_warning == "y":
            if not path.exists("Data/Checkpoints"):
                makedirs("Data/Checkpoints")
            handle = console.input(
                "\nEnter the handle of the account you wish to scrape from [red](do not include the @)[/red]:\n"
            )
            get_follower_list(handle)
        else:
            pass

    else:
        handle_list = load_text("Account Lists/handles.txt")
        check_handles(handle_list)
        scrape_check = " "
        while (scrape_check != "y") and (scrape_check != "n"):
            scrape_check = console.input(
                "\nDo you want to scrape from this list? [cyan](y or n)[/cyan]:\n"
            ).lower()
        if scrape_check == "y":
            file_name = console.input(
                "\nEnter a name for the excel file [red](do NOT include .xlsx)[/red]:\n"
            )
            get_tweets_multi(handle_list)
            format_tweets(file_name, tweets_dict)
        else:
            print(
                f"\nRoger. You can modify the list of handles by editing [cyan]{cwd}/Account Lists/handles.txt[/cyan]"
            )
