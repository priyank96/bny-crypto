import pandas as pd


logits_df = pd.read_csv('with_news_predictions_val_95_12h.csv')
## normalizing data
logits_df['prediction_logit'] = logits_df['prediction_logit'].apply(lambda x: round(x*100,1))
logits_df["price_contribution"] = logits_df["price_contribution"]
logits_df["news_contribution"] = (logits_df["news_contribution"] - min(logits_df["news_contribution"]))
logits_df["social_media_contribution"] = logits_df["social_media_contribution"]- min(logits_df["social_media_contribution"])
logits_df["total"] = (logits_df["price_contribution"]+logits_df["news_contribution"]+logits_df["social_media_contribution"])
logits_df["price_contribution"] = (logits_df["price_contribution"]/logits_df["total"])*logits_df["prediction_logit"]
logits_df["news_contribution"] = ((logits_df["news_contribution"])/logits_df["total"])*logits_df["prediction_logit"]
logits_df["social_media_contribution"] = (logits_df["social_media_contribution"]/logits_df["total"])*logits_df["prediction_logit"]


logits_df.to_csv('with_news_predictions_val_95_12h.csv')