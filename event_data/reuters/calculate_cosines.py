import pickle

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

if __name__ == '__main__':
    df_train = pd.read_pickle('df_train.pkl')

    embeds = df_train['embeds'].to_numpy()
    embeds = np.vstack(embeds)
    print(embeds.shape)

    similarities = cosine_similarity(embeds)
    similarities = np.argsort(similarities)[::-1][0:101]
    print(similarities[0])
    print(similarities.shape)
    del embeds
    with open('df_train_similarities.pkl', 'wb') as f:
        pickle.dump(similarities, f)
    print("Done!")