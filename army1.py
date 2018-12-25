import praw
import os
import string
import datetime

# Creating the reddit instance
reddit = praw.Reddit("botie2")

# Getting target subreddit
subreddit = reddit.subreddit('singapore')

# NS keywords and key phrases
ns_keyphrases = ['national service', 'air force']
ns_keywords = ['ns', 'nsf', 'army', 'navy', 'bmt', 'military', 'pes', 'enlist', 'enlisting', 'enlistment', 'ord', 'saf']
vocation_keywords = ['vocation', 'posting']

# Function: to determine whether post is about vocation/posting
def is_vocation_post(title):
    for word in vocation_keywords:
        if word in title:
            return True
    return False

# Function to determine whether post is related to NS
def is_related_to_ns(title):
    # checking for key phrases
    for phrase in ns_keyphrases:
        if phrase in title:
            return True
    # checking for keywords
    title = title.split(" ")
    for word in title:
        if word[-1] in string.punctuation:
            word = word[:-1] # remove any punctuation marks
        if word in ns_keywords:
            return True
    return False

#Function to append to url_file and title_file
def append_to_file(update, url_file, title_file):
    # don't do anything if file doesn't exist
    if not os.path.isfile(url_file) or not os.path.isfile(title_file):
        raise Exception("Append target file doesn't exist.")
    else:
        for post in update:
            with open(url_file, "a") as f:
                f.write("\n" + post.url)
            with open(title_file, "a") as g:
                g.write("\n" + post.title)

# Function to write to url_file and title_file
def write_to_file(update, url_file, title_file):
    if not os.path.isfile(url_file) or not os.path.isfile(title_file):
        raise Exception("Write target file doesn't exist.")
    else:
        with open(url_file, "w") as f:
            for post in update:
                f.write("\n" + post.url)
        with open(title_file, "w") as g:
            for post in update:
                g.write("\n" + post.title)

# Function to read from file, create list of the contents (either urls or titles)
def create_list_from_file(filename):
    lst = []
    if not os.path.isfile(filename):
        raise Exception("List source file doesn't exist.")
    else:
        with open(filename, 'r') as f:
            lst = f.read()
            lst = lst.split('\n') # split on newline
            lst = list(filter(None, lst)) # get rid of any empty values
            return lst

# Function to reply to normal posts
def normal_reply(post, discuss_url, discuss_title):
    url_lst = create_list_from_file(discuss_url)
    title_lst = create_list_from_file(discuss_title)
    if url_lst and title_lst:
        message = "IF you want to read more on NS, here are some relatively popular recent posts (rants, jokes, shitposts....): \n \n"
        # Add links to the message iteratively
        count = -1
        while count > -5:
            message += "[" + title_lst[count] + "](" + url_lst[count] + ") \n \n"
            count -= 1
        post.reply(message)
    else:
        raise Exception("Discuss file doesn't exist for producing normal reply.")

# Function to reply vocation posts
def vocation_reply(post, voc_url, voc_title, discuss_url, discuss_title):
    voc_url_lst = create_list_from_file(voc_url)
    voc_title_lst = create_list_from_file(voc_title)
    discuss_url_lst = create_list_from_file(discuss_url)
    discuss_title_lst = create_list_from_file(discuss_title)
    if not voc_url_lst or not voc_title_lst:
        raise Exception("Voc file doesn't exist for producing voc reply.")
    if not discuss_url_lst or not discuss_title_lst:
        raise Exception("Discuss file doesn't exist for producing voc reply.")
    # filters out discuss_posts that have already been mentioned in vocation_posts
    discuss_url_lst2 = []
    discuss_title_lst2 = []
    count = -1
    while len(discuss_url_lst2) < 4:
        if discuss_url_lst[count] not in voc_url_lst:
            discuss_url_lst2.append(discuss_url_lst[count])
            discuss_title_lst2.append(discuss_title_lst[count])
        count -= 1
    # Add links to the message iteratively
    message = "Here are some more recent threads on vocations/postings: \n \n"
    count = -1
    while count > -3:
        message += "[" + voc_title_lst[count] + "](" + voc_url_lst[count] + ") \n \n"
        count -= 1
    message += "More recent discussions on NS (rants, jokes, shitposts...): \n \n"
    count1 = 0
    while count1 < 4:
        message += "[" + discuss_title_lst2[count1] + "](" + discuss_url_lst2[count1] + ") \n \n"
        count1 += 1
    post.reply(message)

# List of posts to be added to the post files
vocation_posts_lst = []
monitored_posts_lst = []
mon_titles = create_list_from_file("monitored_titles.txt")
# filtering NS-related posts
for submission in subreddit.new(limit = POST_LIMIT):
    # remember to check if file is already being monitored
    title = submission.title
    if title in mon_titles:
        continue
    title = title.lower()
    if is_related_to_ns(title):
        if is_vocation_post(title):
            vocation_reply(submission, "vocation_url.txt", "vocation_titles.txt", "discuss_url.txt", "discuss_titles.txt")
            vocation_posts_lst.append(submission)
            monitored_posts_lst.append(submission)
            print(submission.title + " is vocation_post")
            continue
        normal_reply(submission, "discuss_url.txt", "discuss_titles.txt")
        monitored_posts_lst.append(submission)
        print(submission.title + " is normal_post")
# Updating files
append_to_file(vocation_posts_lst, "vocation_url.txt", "vocation_titles.txt")
append_to_file(monitored_posts_lst, "monitored_url.txt", "monitored_titles.txt")

# Look for popular discussion posts among those that are being monitored
mon_urls = create_list_from_file("monitored_url.txt")
new_mon_posts = []
discuss_posts = []
for site in mon_urls:
    submission = reddit.submission(url = site)
    if submission.score > SCORE_LIMIT or len(submission.comments) > COMMENT_LIMIT:
        discuss_posts.append(submission)
    else:
        new_mon_posts.append(submission)

# Updating files
write_to_file(new_mon_posts, "monitored_url.txt", "monitored_titles.txt")
append_to_file(discuss_posts, "discuss_url.txt", "discuss_titles.txt")
