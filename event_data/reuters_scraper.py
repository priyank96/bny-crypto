import pprint

import pandas as pd
import requests
from tqdm import tqdm

url = "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query=%7B%22keyword%22%3A%22bitcoin%22%2C%22offset%22%3A<index>%2C%22orderby%22%3A%22display_date%3Adesc%22%2C%22size%22%3A20%2C%22website%22%3A%22reuters%22%7D&d=130&_website=reuters"

if __name__ == '__main__':
    rows = []
    for end_index in tqdm(range(20, 2321, 20)):
        response = requests.get(
            url.replace('<index>', str(end_index)))
        if response.json()["result"] is not None:
            for article in response.json()["result"]["articles"]:
                rows.append([
                    article["title"],
                    article["published_time"],
                    article["description"],

                ])
    df = pd.DataFrame(rows, columns=['title', 'published_time', 'subheadlines'])
    df['timestamp'] = pd.to_datetime(df['published_time'], utc=True)
    del df['published_time']
    print(df.info())
    df.to_csv('data/BTC_reuters_articles.csv', index=False, sep='\t')