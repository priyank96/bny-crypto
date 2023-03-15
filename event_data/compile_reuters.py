import pandas as pd

if __name__ == '__main__':
    files = ['reuters_business_articles.csv', 'reuters_legal_articles.csv', 'reuters_markets_articles.csv',
             'reuters_technology_articles.csv', 'reuters_world_articles.csv']
    df = pd.read_csv('data/' + files[0], header=0, sep='\t')
    for i in range(1, len(files)):
        temp = pd.read_csv('data/' + files[i], header=0, sep='\t')
        df = pd.concat([df, temp])
    print(df.info())
    df = df.drop_duplicates()
    print(df.info())
    df.to_csv('data/reuters_all_articles.csv', sep='\t', index=False)
