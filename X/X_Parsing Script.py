from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import re
import sys, os


def extract_usernames(text):
    pattern = r'@\w+'
    usernames = re.findall(pattern, text)
    return usernames

with open(r'X\symposium.json', encoding='utf-8') as f:
    data = json.load(f)

# Prepare CSV filename
csv_filename = 'X\Parsed_tweets.csv'
usernames = list(data.keys())
# print(len(usernames))

list_of_usernames = []
for name in usernames:
    for tweet_html in data[name]: 
        soup = BeautifulSoup(tweet_html, 'html.parser')
        # print(soup.prettify())
        x = extract_usernames(soup.get_text())
        for y in x:
            if y[1:] not in list_of_usernames:
                list_of_usernames.append(y[1:])
print(f'List of usernames: {list_of_usernames} \n')

keywords = ['(asians OR “asian OR people" OR "asian OR american” OR “asian OR americans”)', 
            '(arab OR arabs OR “middle OR eastern” OR “arab OR americans”)']

# Prepare CSV file and write headers
with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Poster', 'Date', 'Tweet', 'No of Likes', 'No of Retweets', 'No of Replies', 'No of Views'])

    for key in keywords:
        try: 
             # Initialize tweet_info with default values
            for tweet_html in data[key]: 
                all_username = []
                all_time = []
                all_likes = []
                all_comments = []
                all_retweets = []
                
                soup = BeautifulSoup(tweet_html, 'html.parser')

                # Find all usernames
                usernames = soup.find_all('a', attrs = {'aria-hidden': 'true'})
                
                for username in usernames:
                    href_value = username.get('href', None)
                    if href_value and href_value not in all_username:
                        all_username.append(href_value[1:])
                    else:
                        print('No name found')
                print(f'{key}: {all_username} \n')

                # Extract all tweet texts
                tweets = soup.find_all(attrs={"data-testid": "tweetText"})
                tweet_texts = [tweet.get_text(strip=True) for tweet in tweets]
                print(f'{key}: {tweet_texts} \n')
                # print(len(tweet_texts))
                # 15, 14

                # Select the time value
                time_element = soup.find_all('time')
                if time_element:
                    # print(f'{key}: {len(time_element)}')

                    datetime_value = time_element['datetime']
                    dt = datetime.fromisoformat(datetime_value.replace("Z", "+00:00")) 
                    readable_time = dt.strftime("%B %d, %Y %I:%M %p")
                    all_time.append(readable_time)
                else:
                    readable_time = ''

                # Find all <div> elements with aria-label for likes, comments, and retweets
                div_elements = soup.find_all('div', attrs={"aria-label": True})
                likes = retweets = replies = 0
                views = 'N/A' 
                count = 0

                for div_element in div_elements:
                    aria_label_value = div_element['aria-label']
                    # print(aria_label_value)
                    if 'likes' in aria_label_value or ('bookmarks' in aria_label_value or 'views' in aria_label_value):
                        # print(aria_label_value)
                        values = aria_label_value.split(', ')
                        try:
                            replies = values[0].split(' ')[0]
                        except IndexError:
                            replies = 'N/A'
                        try:
                            retweets = values[1].split(' ')[0]
                        except IndexError:
                            retweets = 'N/A'
                        try:
                            likes = values[2].split(' ')[0]
                        except IndexError:
                            likes = 'N/A'
                        for v in values:
                            if 'views' in v:
                                views = v.split(' ')[0]
                        break

                # Write to CSV
                for t in tweet_texts:
                    writer.writerow([name, readable_time, t.strip(), likes, retweets, replies, views])
        except Exception as e:
            print(f"Error processing tweet for keyword: {name}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            continue

