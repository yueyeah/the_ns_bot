import os
# Can't import from army1.py. Will cause the bot to crash, dk why.

# Function to read from file, create list of the contents (either urls or titles)
def create_list_from_file(filename):
    lst = []
    if not os.path.isfile(filename):
        raise Exception("List source file doesn't exist.")
    else:
        with open(filename, 'r') as f:
            lst = f.read()
            lst = lst.split('\n') #split on newline
            lst = list(filter(None, lst)) # get rid of any empty values
            return lst

# Function to update the file. Note that this time the update type is string, not submission,
# so it only needs to takes in one file as argument.
def write_to_file(update, filename):
    if not os.path.isfile(filename):
        raise Exception("Write target file doesn't exist.")
    else:
        with open(filename, "w") as f:
            for entry in update:
                f.write("\n" + entry)

# Function to prevent files from getting too big.
# This assumes that the url_file and title_file are both of the same size and are in sync. 
def control_size(url_file, title_file):
    url_lst = create_list_from_file(url_file)
    title_lst = create_list_from_file(title_file)
    print(title_lst)
    print(len(title_lst))
    if len(url_lst) > 15:
        url_lst = url_lst[-10:]
        title_lst = title_lst[-10:]
        write_to_file(url_lst, url_file)
        write_to_file(title_lst, title_file)
        print(url_file + " is handled.")
    else:
        return 

control_size("monitored_url.txt", "monitored_titles.txt")
control_size("discuss_url.txt", "discuss_titles.txt")
control_size("vocation_url.txt", "vocation_titles.txt")
