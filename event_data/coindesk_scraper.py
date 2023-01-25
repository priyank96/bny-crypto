import requests
import pandas as pd
from tqdm import tqdm

url = 'https://api.queryly.com/json.aspx?queryly_key=d0ab87fd70264c0a&query=bitcoin&endindex=<index>&batchsize=100&showfaceted=true&extendeddatafields=subheadlines,subtype,type,section,sponsored_label,sponsored,pubDate&timezoneoffset=0'

if __name__ == '__main__':
    rows = []
    # the coindesk website lists 27493 articles
    for end_index in tqdm(range(0, 27493, 100)):
        response = requests.get(
            url.replace('<index>', str(end_index)))
        for article in response.json()["items"]:
            rows.append([
                article["title"],
                article["pubdateunix"],
                article["subheadlines"],
                article["sponsored"]
            ])
    df = pd.DataFrame(rows, columns=['title', 'pubdateunix', 'subheadlines', 'sponsored'])
    df['timestamp'] = pd.to_datetime(df['pubdateunix'], unit='s', utc=True)  # unix time is always UTC!
    del df['pubdateunix']
    print(df.info())
    df.to_csv('data/BTC_coindesk_articles.csv', index=False, sep='\t')
