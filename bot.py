"""
Reddit '/u/sub_toppings_bot' v2.0
A bot that steals top submissions and comments from subreddits, and posts
them to /r/thegreatsub

@author: Toofifty
"""

import praw, time, re
from datetime import datetime

# Interval between executions of the loop (seconds)
INTERVAL = 300

# Regex pattern matching for variable replacements in
# the template strings.
# Words inside the braces will be replaced by their
# variable evaluations.
pt = re.compile(ur'{([^}]*)}')

def grab_next(reddit, complete):
    # Check every incoming comment with PRAW's
    # get_comment generator.
    for comment in reddit.get_comments("all"):
        # Extract the subreddit name from the link of
        # the comment, since there is no way (that I
        # know of) to grab it directly.
        subr = comment.permalink.split("/r/")[1]
        subr = subr.split("/comments/")[0]
        print "Comment found for: %s." % subr,

        # Return the subreddit if it is not on the
        # complete list.
        # Returning None will reset the generator and
        # will check the same comment repeatedly.
        if subr not in complete:
            print "\tFinding top post for %s..." % subr
            return reddit.get_subreddit(subr)

        # Next comment will be checked.
        print "Subreddit already complete."

def post_top_subm(subm, subr, gsub, template):
    title = "%s - /r/%s" % (subm.title, subr)

    # Reddit doesn't accept posts with titles over 300
    # characters long.
    # So we truncate the submission title by the length
    # of the filler characters and the subreddit name.
    if len(title) > 300:
        title = "%s... - /r/%s" % (subm.title[0:290 - len(subr.title)], subr)

    print "> %s" % title

    # All further interactions with Reddit are inside this block,
    # so it's best to catch Reddit/praw exceptions out here.
    try:
        # Handles text posts vs link posts.
        if hasattr(subm, "text"):
            gsubm = gsub.submit(title, text=subm.text)
        else:
            gsubm = gsub.submit(title, url=subm.url)

        if subm.over_18:
            gsubm.mark_as_nsfw()

        # Populate the information comment and post it
        # to the gsubm (greatsub submission).
        gsubm.add_comment(pop_comment(subm, subr, template))

    except praw.errors.APIException as e:
        print "Couldn't post submission to /r/thegreatsub, error:"
        print e

def pop_comment(subm, subr, comment):
    date = datetime.fromtimestamp(subm.created).strftime("%a %d-%m-%y")

    # Only initialise the top comment variable if
    # there are comments on the submission.
    # I'm not too sure how a top post doesn't get
    # any comments, though...
    if len(subm.comments) > 0:
        topc = subm.comments[0]

    # Look for all matches in the template text.
    # 'm' will be set to the string inside the braces.
    for m in re.findall(pt, comment):
        # Replaces {m} with the evaluation of m,
        # i.e. the variable that m is.
        # Also is able to run code within braces,
        # which is handy. :)
        comment = comment.replace("{%s}" % m, str(eval(m)))

    return comment

def load_txt(file_name):
    # Helper method to load from plaintext.
    with open(file_name + ".txt", 'r') as f:
        return f.read().strip()


def main():
    print "\nIdentifying with Reddit...",

    # Loading from plain text like a bawss
    creds = load_txt("creds").split("\n")

    # Identify with Reddit, and log in using the
    # credentials loaded from plaintext.
    # Exceptions here may as well just raise their
    # error and stop the program.
    reddit = praw.Reddit("Sub Toppings Stealer v2.0 by /u/Toofifty")
    reddit.login(creds[0], creds[1])
    gsub = reddit.get_subreddit("thegreatsub")
    print "Success."

    # Load complete subreddits and split into a list
    complete = load_txt("complete").split("\n")

    # Load templates
    temp_top = load_txt("temp_top")
    temp_no_top = load_txt("temp_no_top")

    while True:
        subr = grab_next(reddit, complete)

        # Will only grab one submission, but since get_top_from_all
        # is a generator we can't access it like a regular array.
        # Not sure if there is a better way to do this.
        for subm in subr.get_top_from_all(limit=1):
            # Use a special template if no comments are found on the
            # submission. Prevents raising an exception from not
            # being able to find the first comment.
            template = temp_top if len(subm.comments) > 0 else temp_no_top
            post_top_subm(subm, subr, gsub, template)

        # Append subreddit's name to the complete list, and commit
        # it to the file ASAP, just in case something goes wrong.
        # Also need to make sure to do this last so if there is
        # a crash anywhere before here we don't add an 'unifinished'
        # subreddit to the list.
        complete.append(str(subr))
        with open("complete.txt", 'w') as f:
            f.write("\n".join(complete))
        # Zzz...
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
