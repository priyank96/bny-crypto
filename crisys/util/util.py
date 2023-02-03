"""
Common utils
"""
import json
import pandas as pd


def jsonify(df):
    return json.dumps(df.to_json(orient='columns', date_format='iso'))


def json_to_df(message):
    return pd.read_json(json.loads(message), orient='columns')
