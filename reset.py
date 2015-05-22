"""
Reddit '/u/sub_toppings_bot' v2.0
Subreddit reset button. Clears the entire subreddit
of submissions (posted by the bot).
Super dangerous.

@author: Toofifty
"""

import time, praw

def main():
    print "\nIdentifying with Reddit...",

    # Loading from plain text like a bawss
    with open("creds.txt", 'r') as f:
        creds = f.read().strip().split("\n")

    # Identify with Reddit, and log in using the
    # credentials loaded from plaintext.
    reddit = praw.Reddit("Sub Toppings Stealer v2.0 by /u/Toofifty")
    reddit.login(creds[0], creds[1])
    gsub = reddit.get_subreddit("thegreatsub")
    print "Success."

    # Only need to use get_hot - it doesn't matter
    # which order we get all the submissions in.
    for subm in gsub.get_hot():
        print "Deleting %s..." % subm.title,
        if str(subm.author) == creds[0]:
            subm.delete()
            print "Done."
        # Don't really need to sleep, but it helps
        # keep things under control.
        time.sleep(2)
    print "Finished clearing submissions."

if __name__ == "__main__":
    main()
