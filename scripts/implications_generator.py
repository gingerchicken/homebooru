import requests
import tqdm
import json
from bs4 import BeautifulSoup
import base64

with open("implications.json", "r") as f:
    implications = json.load(f)

def md5(s):
    """Used for debugging purposes"""

    import hashlib
    return hashlib.md5(s.encode()).hexdigest()

def list_md5(l):
    """Used for debugging purposes"""

    return md5(json.dumps(l))

def get_banned_words():
    """Returns a list of banned words"""

    # Credit https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words

    WORD_LIST = "https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/refs/heads/master/en"

    banned_words = requests.get(WORD_LIST).text # Get the list of banned words
    banned_words = banned_words.strip() # Strip whitespace on both sides
    banned_words = banned_words.split("\n") # Split by newline

    # Remove all words with spaces in them
    banned_words = [word for word in banned_words if ' ' not in word]

    # Convert to set to remove duplicates
    banned_words = set(banned_words)

    # Convert back to list
    banned_words = list(banned_words)

    # Sort the list
    banned_words.sort()

    print(f"Loaded {len(banned_words)} banned words (MD5: {list_md5(banned_words)})")
    return banned_words

# Get the list of tags
def get_tags(implications):
    tags = [tag for (parent, child) in implications for tag in [parent, child]] # Get all tags from implications
    
    tags = set(tags) # Convert to set to remove duplicates
    tags = list(tags) # Convert to list

    tags.sort() # Sort the list (for consistency)

    print(f"Loaded {len(tags)} tags (MD5: {list_md5(tags)})")
    return tags

def get_banned_tags(tags, words):
    banned_tags = []

    for word in tqdm.tqdm(words, desc="Checking for banned tags", unit="word"):
        for tag in tags:
            is_banned = False

            # First check if the word is in the tag
            if word not in tag:
                continue
            
            # Now check if the word is in the tag
            for tag_word in tag.split('_'):
                # Strip the word
                tag_word = tag_word.strip()

                # Make it alphanumeric
                tag_word = ''.join(e for e in tag_word if e.isalnum())

                # If the word is not a word in the tag, then continue
                if word != tag_word:
                    continue

                is_banned = True
                break

            if is_banned:
                banned_tags.append(tag)
    
    banned_tags = list(set(banned_tags))
    banned_tags.sort()

    print(f"Found {len(banned_tags)} banned tags (MD5: {list_md5(banned_tags)})")
    
    return banned_tags

def get_implied_banned_tags(banned_tags, implications):
    # If a banned tag is a child, then the parent is also banned (and vice versa)
    implied_banned_tags = []

    for i in tqdm.tqdm(implications, desc="Checking for implied banned tags", unit="implication"):
        (parent, child) = i

        # If the parent is banned, then the child is also banned (and vice versa)
        
        # This isn't a perfect solution since "doing something rude" whilst wearing a "hat" would mark "hat" as banned
        # But it's better than nothing and makes sure that there are no implications that contain banned tags

        if parent in banned_tags:
            implied_banned_tags.append(child) # "Rude" implies "Hat"
        elif child in banned_tags:
            implied_banned_tags.append(parent) # "Hat" implies "Rude"

    
    before = len(banned_tags)
    banned_tags += implied_banned_tags
    banned_tags = list(set(banned_tags))
    banned_tags.sort()

    added = len(banned_tags) - before

    print(f"Found {added} implied banned tags (MD5: {list_md5(banned_tags)})")

    return banned_tags, added

def filter_implications(implications, banned_tags):
    filtered_implications = [] # A clean list of implications

    for (parent, child) in tqdm.tqdm(implications, desc="Filtering implications", unit="implication"):
        if parent in banned_tags or child in banned_tags:
            continue

        filtered_implications.append((parent, child)) # Add the implication to the filtered implications
    
    print(f"Filtered {len(implications) - len(filtered_implications)} implications resulting in a remaining {len(filtered_implications)} (MD5: {list_md5(filtered_implications)})")

    return filtered_implications

def clean(implications, additional_banned_words=[]):
    # Get the list of tags
    words = get_banned_words() # Get the list of banned words
    # Add additional banned words
    words += additional_banned_words

    # Get the list of tags
    tags = get_tags(implications)

    # Get the list of banned tags (tags that contain banned words)
    banned_tags = get_banned_tags(
        tags=tags,
        words=words
    )

    # Get the implied banned tags
    added = 1

    while added > 0:
        banned_tags, added = get_implied_banned_tags(banned_tags=banned_tags, implications=implications)

    # Filter the implications (remove implications that contain banned tags)
    filtered_implications = filter_implications(
        implications=implications,
        banned_tags=banned_tags
    )

    return filtered_implications # Return the filtered implications

# I don't want to associate with this website so I'm not going to include the URL directly
URL = base64.b64decode("aHR0cHM6Ly9nZWxib29ydS5jb20vaW5kZXgucGhwP3BhZ2U9dGFncyZzPWltcGxpY2F0aW9ucw==").decode("utf-8")

def get_paginator_pages():
    # Get the page
    page = requests.get(URL)

    # Get the soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Select #id=paginator
    paginator = soup.select("#paginator")

    # Get the a tags
    paginator[0].find_all('a')

    # Return the hrefs
    return [a['href'] for a in paginator[0].find_all('a')]

def convert_to_pid(url : str):
    pid = url.split("pid=")[1]

    # Select only numbers until there is a non-number
    cleaned_pid = ''
    while len(pid) > 0 and pid[0].isdigit():
        cleaned_pid += pid[0]
        pid = pid[1:]
    
    return int(cleaned_pid)

def get_page(pid : int):
    # Get the page
    current_url = URL + f"&pid={pid}"

    page = requests.get(current_url)

    # Get the soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get class mainBodyPadding
    main_body_padding = soup.select(".mainBodyPadding")

    # Get the next table
    table = main_body_padding[0].find_all('table')[1]

    # Get the td tags
    td_tags = table.find_all('td')

    implications = []

    for td_tag in td_tags:
        # Select the <b> tags
        b_tags = td_tag.find_all('b')

        if len(b_tags) == 0:
            continue

        # Get the text
        splitter = b_tags[0].text

        # Get the main text
        main_text = td_tag.text

        # Split the text
        split_text = main_text.split(splitter)

        # Get the two parts
        [a, b] = split_text
        
        # Remove whitespace
        a = a.strip()
        b = b.strip()

        implications.append((a, b))
    
    return implications

def download_implications():
    pages = get_paginator_pages()

    page_step = convert_to_pid(pages[0])
    page_end = convert_to_pid(pages[-1])

    total_pages = page_end // page_step

    print(f"Total pages: {total_pages}")

    implications = []
    for i in tqdm.tqdm(range(page_step, page_end + page_step, page_step), total=total_pages, desc="Enumerating all implications", unit="page"):
        implications += get_page(i)


    # Sort the implications by the parent
    implications.sort(key=lambda x: x[0])

    return implications

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate implications by scraping a website")
    parser.add_argument("--clean", action="store_true", help="Clean the implications by removing NSFW implications", default=True)
    parser.add_argument("--output", type=str, help="Output the implications to a file", default="implications.json")

    # Parse the arguments
    args = parser.parse_args()

    # Download the implications
    implications = download_implications()

    # Clean the implications
    if args.clean:
        implications = clean(implications, additional_banned_words=[
            "breasts", "breast", "suck", "sucking" # Add some additional banned words since the list is not perfect
        ])
    
    # Convert to fixtures
    fixtures = []

    pk = 1
    for impl in implications:
        (parent, child) = impl

        fixtures.append({
            "model": "booru.implication",
            "pk": pk,
            "fields": {
                "parent": parent,
                "child": child
            }
        })

        pk += 1
    
    # Save the fixtures to a file
    with open(args.output, "w") as f:
        json.dump(fixtures, f, indent=4)