import json
import time
import urllib
from datetime import datetime, timedelta

import pandas as pd
import requests
from tqdm import tqdm

url = "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?"
size = 100


def get_end_date(start_date):
    return start_date + timedelta(days=92)  # any less than 92 and it's 400


def get_news():
    start_date = pd.to_datetime("2021-03-01T00:00:00.000Z")
    end_date = get_end_date(start_date)

    def get_rows(response_json):
        response_rows = []
        if response_json["result"] is None:
            print('empty response')
            return response_rows
        if response_json["result"] is not None:
            if len(response.json()["result"]["articles"]) == 0:
                print('empty response')
                return response_rows

            for article in response_json["result"]["articles"]:
                response_rows.append([
                    article["title"],
                    article["published_time"],
                    article["description"],
                    article.get('kicker', {}).get('names', [])

                ])
        return response_rows

    def get_data(offset):
        params = {
            "query": json.dumps({"end_date": datetime.strftime(end_date, '%Y-%m-%dT%H:%M:%S.%fZ'),
                                 "keyword": "*",
                                 "offset": offset,
                                 "orderby": "display_date:asc",
                                 # "sections": "/world",
                                 "size": 100,
                                 "start_date": datetime.strftime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ'),
                                 "website": "reuters"}),
            "d": 132,
            "_website": "reuters",

        }
        return requests.get(url + urllib.parse.urlencode(params))

    all_rows = []
    while start_date <= pd.to_datetime("2022-09-19T04:57:25.047Z"):
        response = get_data(0)
        total_articles = int(response.json()["result"]["pagination"]["total_size"])

        for end_index in tqdm(range(0, total_articles, size)):
            try:
                rows_for_date_slice = get_rows(get_data(end_index).json())
            except:
                print("Exception! Going to Sleep")
                # reset the search starting from the last fetched articles,
                # subtract 92 days because outside it gets added back outside
                start_date = pd.to_datetime(all_rows[-1][1]) - timedelta(days=92) # publish time of last fetched row
                time.sleep(60)
                break

            all_rows.extend(rows_for_date_slice)

        start_date += timedelta(days=92)
        end_date = get_end_date(start_date)

    return all_rows


if __name__ == '__main__':
    rows = get_news()
    df = pd.DataFrame(rows, columns=['title', 'published_time', 'subheadlines', 'categories'])
    df['timestamp'] = pd.to_datetime(df['published_time'], utc=True)
    del df['published_time']
    print(df.info())
    df.to_csv('data/BTC_reuters_articles.csv', index=False, sep='\t')
