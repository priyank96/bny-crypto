import pickle

import numpy as np
import tqdm
from sklearn.metrics.pairwise import cosine_similarity

if __name__ == ' __main__':
    df_train = None
    with open('df_train.pkl', 'rb') as f:
        df_train = pickle.load(f)

    embeds = df_train['embeds'].to_numpy()
    embeds = np.vstack(embeds)
    print(embeds.shape)

    similarities = []
    for i in tqdm.tqdm(range(len(embeds))):
        similarities.append(
            np.argsort(cosine_similarity(embeds[i].reshape((1, -1)), embeds).reshape(-1))[::-1][1:101]
        )
    similarities = np.array(similarities)
    with open('df_train_similarities.pkl', 'wb') as f:
        pickle.dump(similarities, f)
