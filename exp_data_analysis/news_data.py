from event_data import read_news_events


# read the news articles
def preprocess_data():
    df = read_news_events('BTC_BERTopic', '1990-01-01T00:00:00Z', '2024-01-01T00:00:00Z')

    print(df.info())
    # [[1, 19, 5]]
    print(df.iloc[0]['probs'])
    df['class_labels'] = df['probs'].apply(lambda x: [int(val) for val in x[2:-2].split(',')])
    del df['probs']
    print(df.iloc[0]['class_labels'][0])
    return df


if __name__ == '__main__':
    df = preprocess_data()
    # now we need to add sentiment to the news articles
