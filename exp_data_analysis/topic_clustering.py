import pickle

import numpy as np
import pandas as pd
import torch
import tqdm
from transformers import AutoModel, AutoTokenizer
from torch.utils.data import Dataset, DataLoader
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.cluster import KMeans

device = 'cuda'


class TestDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]).to(device) for key, val in self.encodings.items()}
        return item

    def __len__(self):
        return len(self.encodings.input_ids)


def get_tfidf_top_features(documents, n_top=10):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(documents)
    importance = np.argsort(np.asarray(tfidf.sum(axis=0)).ravel())[::-1]
    tfidf_feature_names = np.array(tfidf_vectorizer.get_feature_names())
    return tfidf_feature_names[importance[:n_top]]


if __name__ == '__main__':
    df = pd.read_csv('../event_data/data/BTC_coindesk_articles.csv', header=0, sep='\t')
    print(df.info())

    tokenizer = AutoTokenizer.from_pretrained("ElKulako/cryptobert")
    model = AutoModel.from_pretrained("ElKulako/cryptobert").to(device)

    tokens = tokenizer.batch_encode_plus(df['title'].tolist(), return_tensors='pt', padding=True, truncation=True)
    dataset = DataLoader(TestDataset(tokens), batch_size=32, shuffle=False)

    embeddings = []
    with torch.no_grad():
        model.eval()
        for inputs in tqdm.tqdm(dataset):
            outputs = model(**inputs)
            embeddings.extend(outputs.last_hidden_state[:, 0, :].to('cpu'))
    pickle.dump(embeddings, open('embeddings.pkl', 'wb'))
    embeddings = pickle.load(open('embeddings.pkl', 'rb'))
    embeddings = torch.stack(embeddings)
    clustering = KMeans(n_clusters=8, init='k-means++').fit(embeddings)
    # -1 for noise
    for i in range(0, len(set(clustering.labels_)) - 1):
        temp = df[clustering.labels_ == i]
        print(f"{i}\n{get_tfidf_top_features(temp['title'].tolist())}")
