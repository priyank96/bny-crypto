import pprint
import pickle

import pandas as pd
from event_data import read_news_events

group_to_article = {}
article_to_group = {}
max_group_id = 0


def to_string(df):
    articles = []
    for i in range(len(df)):
        if not pd.isna(df.iloc[i]['title']) and not pd.isna(df.iloc[i]['subheadlines']):
            articles.append(df.iloc[i]['title'] + ' ' + df.iloc[i]['subheadlines'])
        elif pd.isna(df.iloc[i]['title']):
            articles.append(df.iloc[i]['subheadlines'])
        else:
            articles.append(df.iloc[i]['title'])
    return articles


def update(choice, rows):
    global max_group_id
    # they are similar
    if choice == 'q':
        # Both articles are already in groups
        if rows[0] in article_to_group and rows[1] in article_to_group:
            # Both are from same group, do nothing
            if article_to_group[rows[0]] == article_to_group[rows[1]]:
                return
            else:
                # add all articles from 2nd group to 1st article's group
                group_to_article[article_to_group[rows[0]]].extend(group_to_article[article_to_group[rows[1]]])
                # delete 2nd group
                del group_to_article[article_to_group[rows[1]]]

                # update 2nd group articles group id mapping
                articles_to_update = []
                for article, group in article_to_group.items():
                    if group == article_to_group[rows[1]]:
                        articles_to_update.append(article)
                for article in articles_to_update:
                    article_to_group[article] = article_to_group[rows[0]]

        # one of the articles already has a group
        elif rows[0] in article_to_group or rows[1] in article_to_group:
            # 1st article has a group, add 2nd to it
            if rows[0] in article_to_group:
                group_to_article[article_to_group[rows[0]]].append(rows[1])
                article_to_group[rows[1]] = article_to_group[rows[0]]
            # 2nd article has a group, add 1st to it
            else:
                group_to_article[article_to_group[rows[1]]].append(rows[0])
                article_to_group[rows[0]] = article_to_group[rows[1]]

        # Both articles are new, create a group and add both to it
        else:
            max_group_id += 1
            group_to_article[max_group_id] = [rows[0]]
            article_to_group[rows[0]] = max_group_id
            group_to_article[max_group_id].append(rows[1])
            article_to_group[rows[1]] = max_group_id

    # they are not similar
    elif choice == 'w':
        # Both articles are already in groups, do nothing
        if rows[0] in article_to_group and rows[1] in article_to_group:
            return
        # Create a group for whichever article is not already in a group
        else:
            if rows[0] not in article_to_group:
                max_group_id += 1
                group_to_article[max_group_id] = [rows[0]]
                article_to_group[rows[0]] = max_group_id
            if rows[1] not in article_to_group:
                max_group_id += 1
                group_to_article[max_group_id] = [rows[1]]
                article_to_group[rows[1]] = max_group_id
    elif choice == 'e':
        return

    else:
        # Save these after testing!!
        pprint.pprint(article_to_group)
        pprint.pprint(group_to_article)
        with open('group_to_article.pickle', 'wb') as handle:
            pickle.dump(group_to_article, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open('article_to_group.pickle', 'wb') as handle:
            pickle.dump(article_to_group, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return


if __name__ == '__main__':
    df = read_news_events('BTC', '1900-01-01', '2100-01-01')

    while True:
        rows = to_string(df.sample(n=2))
        for row in rows:
            print(row + '\n')
        choice = input('Are they similar? (q=yes, w=no, e=skip, m=exit)\n')
        update(choice, rows)
        if choice not in ['q', 'w', 'e']:
            break
    # Test
    # update('q', ['1', '2'])
    # update('q', ['1', '3'])
    # update('q', ['2', '3'])
    # update('m', None)
    # update('q', ['4', '5'])
    # update('m', None)
