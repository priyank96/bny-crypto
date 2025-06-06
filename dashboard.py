###################################
### Imports                     ###
###################################
import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import datetime
import random
import markdown
import requests
import openai
import tiktoken

import streamlit as st  # 🎈 data web app development
import streamlit.components.v1 as components
import hydralit_components as hc
from streamlit_chat import message
from streamlit_option_menu import option_menu
import streamlit_helpers
from plots import plots

from event_data import DashboardNewsData # In event_data/api.py

import asyncio
from EdgeGPT import Chatbot, ConversationStyle
import json

###################################
### Config Parameters           ###
###################################
development_mode = False
highlight_color = '#e3a72f' # BNYM yellow
shade_color = '#072632' # BNYM blue
button_color = '#ff5555' # BNYM red
padding = 0
theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
theme_alert = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-exclamation-triangle'}
button_time = 3
time_interval = '30Min'
inital_time = datetime.datetime(2022, 6, 6, 17, 0, 0, 0)
# fmdd_threshold = 0.03
price_fall_threshold = 50 # In percent
check_hours = 6
tabs = ['Overview', 'Social Media', 'News', 'Techical Indicators', 'CryptoGPT']
tab_icons = ['house-fill', 'twitter', 'newspaper', 'bar-chart-line-fill', 'chat-dots-fill']  # Icons from https://icons.getbootstrap.com/
if development_mode:
    tabs.append('About Us')
    tab_icons.append('people-fill')
load_tweets_count = 10
chatgpt_df_size = 10
openai_model_name = "gpt-3.5-turbo-0301"
###################################
### Dashboard Setup             ###
###################################
# Page config. Other configs are loaded from .streamlit/config.toml
st.set_page_config(page_title="CRISys - Cryptocurrency Risk Identification System Dashboard",
                   page_icon="images/crisys_logo.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

st.markdown(streamlit_helpers.hide_streamlit_style, unsafe_allow_html=True)
st.markdown(f"""
    <style>
    div.stButton > button:first-child {{
        background-color: {highlight_color};
        color:#ffffff;
    }}
    div.stButton > button:hover {{
        background-color: {button_color};
        border-color: {button_color};
        color:#000;
    }}
    div.stButton > button:focus {{
        background-color: {button_color};
        border-color: {button_color};
        color:#000;
    }}
    section[data-testid="stSidebar"] > div > div > div > div > div > div > div > div > div > div > div > div > div > div > button {{
        background-color: {highlight_color};
        color:#ffffff;
    }}
    </style>""", unsafe_allow_html=True)

st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }}
    div.block-container {{
        padding-top: {padding}rem;
        padding-bottom: {padding}rem;
    }}
    [data-testid=stImage] {{
        text-align: center;
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
    }}
    [data-testid="stSidebar"] {{
        background-color: {shade_color};
        color: #ffffff;
    }}
    section[data-testid="stSidebar"] > div > div > div > div > div > div > div > div > div > h1 {{
        color: #ffffff;
    }}
    section[data-testid="stSidebar"] > div > div > div > div > div > div > div > label > div > p {{
        color: #ffffff;
    }}
    # div[data-testid="stMarkdownContainer"] p {{
    #     font-size: 1.2em; /* Increase font size */
    # }}
       </style> """, unsafe_allow_html=True)

# st.metric CSS style modification
st.markdown("""
    <style>
    div[data-testid="metric-container"]{
    background-color: rgba(0, 0, 0, 0);
    border: 1px solid rgba(0, 0, 0, 0.2);
    padding: 5% 5% 5% 10%;
    border-radius: 5px;
    overflow-wrap: break-word;
    }

    /* breakline for metric text         */
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
    overflow-wrap: break-word;
    white-space: break-spaces;
    }
    </style>
    """
    , unsafe_allow_html=True)

if 'load_time' not in st.session_state:
    st.session_state['load_time'] = inital_time # Dummy value replace with datetime.datetime.now()
if 'ti_selected_values' not in st.session_state: # Default values
    st.session_state['ti_selected_values'] = ['volume', 'rsi', 'volatility', 'var_90']

###################################
### Sidebar                     ###
###################################
with st.sidebar:
    # st.image("images/bnym_logo.png", width=200, )
    file_path = "images/crisys_logo.png"
    try:
        st.image(file_path, width=200)
    except:
        link = 'https://drive.google.com/drive/u/0/folders/1SyUmoODcE-6KNw6Y9pIh32CVSccDcCdm'
        st.error(f"Please download the {file_path} from {link}")
        raise FileNotFoundError(f"Please download {file_path} from {link}")
    
    st.title("Dashboard Configuration")
    
    asset = st.selectbox("Cryptocurrency:", ["BTC - Bitcoin", "ETH - Etherium", "XRP - Ripple", "SOL - Solana"])

    period = st.select_slider("Period:", options=['3h', '6h', '12h', '24h', '2d', '4d', '7d', '14d'], value='24h')
    
    date = st.date_input("End Date:", st.session_state['load_time'], min_value=datetime.datetime(2022, 5, 19), max_value=datetime.datetime(2022, 7, 18))
    # end_time = st.time_input("Start Time:", streamlit_helpers.round_time(datetime.datetime.now()))
    end_time = st.time_input("End Time:", streamlit_helpers.round_time(st.session_state['load_time'], mins_delta=30), step=datetime.timedelta(minutes=30))
    # end_time = st.time_input("Start Time:")
    end_time = datetime.datetime.combine(date, end_time)
    st.session_state['load_time'] = end_time
    if end_time > datetime.datetime.now():
        st.error("Start Time cannot be in the future!")
    start_time = end_time - pd.to_timedelta(period)
    cols =  st.columns(2)
    
    if cols[0].button(f"◀ {button_time} hours"):
        # Refresh page with -6 hours delta
        # end_time = datetime.datetime.now() - pd.to_timedelta(period)
        st.session_state['load_time'] = st.session_state['load_time'] - pd.to_timedelta(f"{button_time}h")
        st.session_state['button_rerun'] = True
        if 'notifications' in st.session_state:
            del st.session_state['notifications']
        st.experimental_rerun()
    if cols[1].button(f"{button_time} hours ▶"):
        # Refresh page with -6 hours delta
        # end_time = datetime.datetime.now() - pd.to_timedelta(period)
        st.session_state['load_time'] = st.session_state['load_time'] + pd.to_timedelta(f"{button_time}h")
        st.session_state['button_rerun'] = True
        if 'notifications' in st.session_state:
            del st.session_state['notifications']
        st.experimental_rerun()

# Only take the crypto symbol
asset = asset[:3]

if 'h' in period:
    num_lookback_points = (int(period.split('h')[0]) * 2) + 1 # 24h * 2 + 1
elif 'd' in period:
    num_lookback_points = (int(period.split('d')[0]) * 24 * 2) + 1

###################################
### Load Data                   ###
###################################
# Load Dataframes
@st.cache_data
def get_price_data_df(file_path="new_values.csv"):
    try:
        return pd.read_csv(file_path) 
    except:
        link = 'https://drive.google.com/drive/u/0/folders/10_ddNCmYj-3mLQNsJjasLR5ZeaqdTnlb'
        st.error(f"Please download the {file_path} from {link}")
        raise FileNotFoundError(f"Please download {file_path} from {link}")

@st.cache_data
def get_logits_df(file_path = "with_news_predictions_val_95_12h.csv"):
    try:
        return pd.read_csv(file_path) 
    except:
        if file_path == 'with_news_predictions_val_95_12h.csv':
            link = 'https://drive.google.com/drive/u/0/folders/10wZur0a2ItSWzRI4PhVGr2i4LMN3bvz5'
        elif file_path == 'softmaxed_logits.csv':
            link = 'https://drive.google.com/drive/u/0/folders/1dpnfArCSXmh4Pbnq4BiSaenB63_PwQP_'
        st.error(f"Please download the {file_path} from {link}")
        raise FileNotFoundError(f"Please download {file_path} from {link}")

# @st.cache_data
def get_news_sentiment_df(asset, start_time, end_time):
    return DashboardNewsData.dashboard_news_aggregated_sentiment(asset, start_time, end_time)
 
# @st.cache_data
def get_article_df(asset, start_time, end_time):
    return DashboardNewsData.dashboard_news_articles_to_show(asset, start_time, end_time)

@st.cache_data
def get_twitter_dash_data(file_path = "twitter_dash_data.csv"):
    try: 
        twitter_dash_data = pd.read_csv(file_path) 
        twitter_dash_data['timestamp'] = pd.to_datetime(twitter_dash_data['timestamp'])
        return twitter_dash_data
    except:
        link = 'https://drive.google.com/drive/u/0/folders/1dpnfArCSXmh4Pbnq4BiSaenB63_PwQP_'
        st.error(f"Please download the {file_path} from {link}")
        raise FileNotFoundError(f"Please download {file_path} from {link}")
    
@st.cache_data
def get_tweet_df(file_path = 'tweets_with_consolidated_reach_subset.csv'):
    try:
        return pd.read_csv(file_path) 
    except:
        link = 'https://drive.google.com/drive/u/0/folders/1cqPxTpjMJ2sixoHqZZVo4bi3C3Ii6xZL'
        st.error(f"Please download the {file_path} from {link}")
        raise FileNotFoundError(f"Please download {file_path} from {link}")

@st.cache_data
def get_openai_api_key(file_path = 'openai_api_key.txt'):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except:
        link = 'https://drive.google.com/drive/u/0/folders/1yaSUB0mIycoLPF11ZXiWGsM47PxfdZCH'
        st.error(f"Please download the {file_path} from {link}")
        raise FileNotFoundError(f"Please download {file_path} from {link}")

# Load Data
with st.spinner('Loading Data...'):
    price_data_df = get_price_data_df()
    logits_df = get_logits_df('softmaxed_logits.csv')
    tweet_df = get_tweet_df()
    twitter_dash_data = get_twitter_dash_data()
    openai.api_key = get_openai_api_key()

price_data_df = price_data_df.query(f'timestamp <= "{str(end_time)}"').iloc[-num_lookback_points:]
logits_df = logits_df.query(f'timestamp <= "{str(end_time)}+00:00"').iloc[-num_lookback_points:]
tweet_df = tweet_df.query(f'"{str(start_time)}" <= timestamp <= "{str(end_time)}+00:00"')

###################################
### Dashboard Body              ###
###################################
# Notifcations
if 'notifications' not in st.session_state or ('notification_update_time' in st.session_state and st.session_state['notification_update_time'] != st.session_state['load_time']):
    # if [True for fmdd_value in price_data_df.iloc[-(check_hours*2+1):]['Forward MDD'] if fmdd_value > fmdd_threshold]:
    #     st.session_state['notifications'] = [f"Maximum Draw Down (MDD) was greater than {fmdd_threshold*100}% in the last {check_hours} hours"]
    latest_timestamp = logits_df.iloc[-(check_hours*2+1):]['timestamp'][logits_df.iloc[-(check_hours*2+1):]['prediction_logit'] > price_fall_threshold].max()
    threshold_check_list = [True for price_fall_value in logits_df.iloc[-(check_hours*2+1):]['prediction_logit'] if price_fall_value > price_fall_threshold]
    if True in threshold_check_list:
        st.session_state['notifications'] = [f"High likelihood of {asset} price to fall signifiantly!"]# by {datetime.datetime.strptime(latest_timestamp, '%Y-%m-%d %H:%M:%S+00:00')+datetime.timedelta(hours=6)}"]
        st.session_state['notification_update_time'] = st.session_state['load_time']
if 'notifications' in st.session_state:
    if st.session_state['notifications'] is not False:
        # hc.info_card(title="Alert Notification Body", content="TODO", theme_override=theme_alert)
        notification_list = '\n'.join(st.session_state['notifications'])
        cols = st.columns([11, 1])
        cols[0].error(f"""
            🚨 Alert 

            {notification_list}
            """)
        minimize_notification = cols[1].button("X")
        if minimize_notification:
            st.session_state['notifications'] = False
            st.session_state['button_rerun'] = True
            st.experimental_rerun()

selected_tab = option_menu(None, tabs, icons=tab_icons,
                            menu_icon="cast", default_index=0, orientation="horizontal",
                            styles={
                                    "container": {"padding": "5!important", "background-color": shade_color},
                                    "nav-link": {"color": '#ffffff',  'font-weight': 'bold'},
                                    "nav-link-selected": {"background-color": highlight_color}})
if 'selected_tab' not in st.session_state:
    st.session_state['selected_tab'] = selected_tab
if selected_tab != st.session_state['selected_tab']:
    if 'button_rerun' in st.session_state and st.session_state['button_rerun'] is True:
        selected_tab = st.session_state['selected_tab']
    else:
        st.session_state['selected_tab'] = selected_tab

st.session_state['button_rerun'] = False

selected_tab = st.session_state['selected_tab'] if 'selected_tab' in st.session_state else selected_tab

# with tab_overview:
if selected_tab == tabs[0]: # Overview Tab

    # Risk Probability Numbers
    price_fall_values = logits_df['prediction_logit'].values
    if price_fall_values[-2] == 0:
        price_fall_delta = 100
    else:
        price_fall_delta = round(price_fall_values[-1]-price_fall_values[-2],1)

    # Price Numbers
    price_values = [round(x,3) for x in price_data_df['close'].values]
    price_delta = round(100*(price_values[-1]-price_values[-2])/price_values[-2],1)
    # Volume Numbers
    volume_values = [round(x,0) for x in price_data_df['volume'].values]
    volume_delta = round(100*(volume_values[-1]-volume_values[-2])/(volume_values[-2]),1)

    cols = st.columns(3)

    

    # cols[0].metric(label="Maximum Draw Down", value=fmdd_values[-1], delta=f"{fmdd_delta}% in {time_interval}", delta_color="off" if fmdd_delta == 0 else "inverse", help=f'Risk of Price Fall in next 6 hours')
    cols[0].metric(label="Risk Event Probability", value=f'{price_fall_values[-1]}%', delta=f"{price_fall_delta}% in {time_interval}", delta_color="off" if price_fall_delta == 0 else "inverse", help=f'Confidence of price to fall by more than 3.8% in the next 6 hours')
    cols[1].metric(label=f"{asset} Price", value=f'${price_values[-1]}', delta=f"{price_delta}% in {time_interval}", delta_color="off" if price_delta == 0 else "normal", help=f'Last trade price value in USD at {end_time}')
    cols[2].metric(label=f"{asset} Volume", value=f'{volume_values[-1]}', delta=f"{volume_delta}% in {time_interval}", delta_color="off" if volume_delta == 0 else "normal", help=f'Units of cryptocurrency traded in last {time_interval}')
    
    cols = st.columns(2)
    # with cols[0].expander(f'Maximum Draw Down ({period})', expanded=True):
    #     st.plotly_chart(plots.line_plot_single(price_data_df, column_x = 'timestamp', column_y='Forward MDD', 
    #                                                 line_name="Maximum Draw Down", line_color=highlight_color, fill='tozeroy',
    #                                                 add_hline=True, hline_value=fmdd_threshold, hline_color='red', hline_annotation_text='High Risk Threshold'),
    #                         use_container_width=True)
    
    with cols[0].expander(f'**Risk Event Probability and Factors ({period})**', expanded=True):
        
        st.plotly_chart(plots.line_plot_double_shared_stacked_bars(df=logits_df, column_x='timestamp', 
                                                                   column_y1='prediction_logit', column_y2=['price_contribution', 'news_contribution', 'social_media_contribution'], 
                                                                   line_name1='Price Fall Probability', line_name2=['Price Contribution', 'News Contribution', 'Social Media Contribution'], 
                                                                   line_color1='black', line_color2=[highlight_color,'purple','blue'], title='',
                                                                   add_hline=True, hline_value=price_fall_threshold, hline_color='red', hline_annotation_text=f'High Risk Threshold',
                                                                   graph_height=400, legend_y=1.4)
                        ,use_container_width=True)

    with cols[1].expander(f'**Price and Volume ({period}) Shared**', expanded=True):
        st.plotly_chart(plots.line_plot_double_shared_bars(price_data_df, column_x = 'timestamp', column_y1='close', column_y2='volume', line_fill1=None, line_fill2='tozeroy',
                                                    line_name1="Price", line_name2='Volume', line_color2=highlight_color, line_color1='black',
                                                    graph_height=400, legend_y=1.4),
                            use_container_width=True)
    
    # if st.button("<- 30 Min"):
    #     end_time = end_time - pd.to_timedelta(-30, unit='m')
    #     st.experimental_rerun()

# with tab_social:
if selected_tab == tabs[1]: # Twitter Tab
    
    if development_mode is True:
        with st.expander(f"**Work in Progress! 🚧 Coming Soon:**", expanded=False):
            st.markdown("""
            * Twitter Sentiment Trend
            * Top Tweets (By high reach tweets that are significantly polarized)
            * Influencer Tweets
            * Named Entity Word Cloud
            * Hashtag Word Cloud
            """)

    main_cols = st.columns([2,1])

    plot_time = pd.to_datetime(end_time, utc=True)
    ind = twitter_dash_data.loc[twitter_dash_data['timestamp'] == plot_time].index[0]
    with main_cols[0].expander(f"**Engagement of Tweets**", expanded=True):
        st.plotly_chart(plots.line_plot_double_shared_bars(twitter_dash_data[ind-num_lookback_points:ind+1], column_x='timestamp', column_y1="reach", column_y2="tweet_count", line_fill1=None, line_fill2='tozeroy',
                                                    line_name1 = 'Tweet Engagement', line_name2 = 'Number of Tweet', line_color2=highlight_color, line_color1='black'), use_container_width=True)

    with main_cols[0].expander(f"**Twitter Sentiment Trend ({period})**", expanded=True):
        st.plotly_chart(plots.line_plot_double_shared(twitter_dash_data[ind-num_lookback_points:ind+1], column_x='timestamp', column_y1="sentiment", y2_value=0,
                                                    line_name1="User Sentiment", line_name2='Neutral', line_color1="black", line_color2='red', yaxis_title1='Sentiment'), use_container_width=True)
        
    
    with main_cols[0].expander(f"**Tweet Content Embedding Distance**", expanded=True):
        lookback_hours = "12h"
        # st.select_slider("Lookback Hours:", options=['3h', '6h', '12h', '24h'], value='6h')
        lookback_hours = int(lookback_hours.replace('h',''))
        st.plotly_chart(plots.scatter_plot(twitter_dash_data.iloc[:ind+1], column_x='embed_PCA_1', column_y='embed_PCA_2', opacity=0.5, color_primary=highlight_color, color_secondary='black', lookback_hours=lookback_hours,
                                           xaxis_title="Embedding Dimension 1", yaxis_title="Embedding Dimension 2"), use_container_width=True)
    with main_cols[0].expander(f"**#Hashtag Word Cloud**", expanded=True):
        st.plotly_chart(plots.hashtag_word_cloud(twitter_dash_data.loc[twitter_dash_data['timestamp'] == plot_time]["hashtags"].iloc[0]), use_container_width=True)

    
    with main_cols[1]:
        with st.expander(f"**Top Tweets**", expanded=True):
            # st.write(f"* 4 hour time delay between now and tweet render due to EST to UTC time difference")
            # order = st.selectbox('Sort By:', ['Latest', 'Highest Reach', 'Highest Per Follower Reach'], index=1)
            st.write()
            order_list = ['Latest', 'Highest Reach', 'Highest Per Follower Reach']
            if 'tweet_order' in st.session_state:
                order = st.selectbox(f'{len(tweet_df)} Tweets in {period}', order_list, index=order_list.index(st.session_state['tweet_order']))
            else:
                order = st.selectbox(f'{len(tweet_df)} Tweets in {period}', order_list, index=1)

            st.session_state['tweet_order'] = order
     
            if order == 'Latest':
                tweet_df.sort_index(inplace=True, ascending=False)
            elif order == 'Highest Reach':
                # Sort by 'NORMALIZED_ENGAGEMENT' column
                tweet_df.sort_values(by=['ENGAGEMENT'], inplace=True, ascending=False)
            elif order == 'Highest Per Follower Reach':
                tweet_df.sort_values(by=['NORMALIZED_ENGAGEMENT'], inplace=True, ascending=False)
                # if order == 'Top Positive':
                #     tweet_df = tweet_df[tweet_df['sentiment_logits'] == 'Positive']
                # elif order == 'Top Negative':
                #     tweet_df = tweet_df[tweet_df['sentiment_logits'] == 'Negative']
                # elif order == 'Top Neutral':
                #     tweet_df = tweet_df[tweet_df['sentiment_logits'] == 'Neutral']

            
            for i, row in tweet_df.iloc[:load_tweets_count].iterrows():
                
                t = streamlit_helpers.Tweet(row['url']).component(height=350)
                st.write('---')

            st.markdown(f"""
            <style>
            .more_button {{
                background-color: #ffffff;
                border: 1px solid black;
                color: rgb(0, 111, 214);
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                margin: auto;
                position: relative;
                cursor: pointer;
                border-radius: 9999px;
                font-family: inherit;
            }}
            </style>
            <div style="text-align: center;">
                <button class="more_button">{len(tweet_df)-load_tweets_count} more Tweets</button>
            </div>
            <br>
            """, unsafe_allow_html=True)

            cols = st.columns(2)
            if cols[0].button(f"◀ {load_tweets_count} Tweets"):
                # Refresh page with -6 hours delta
                # end_time = datetime.datetime.now() - pd.to_timedelta(period)
                st.session_state['load_time'] = st.session_state['load_time'] - pd.to_timedelta(f"{load_tweets_count}h")
                st.session_state['button_rerun'] = True
                if 'notifications' in st.session_state:
                    del st.session_state['notifications']
                st.experimental_rerun()
            if cols[1].button(f"{load_tweets_count} Tweets ▶"):
                # Refresh page with -6 hours delta
                # end_time = datetime.datetime.now() - pd.to_timedelta(period)
                st.session_state['load_time'] = st.session_state['load_time'] + pd.to_timedelta(f"{load_tweets_count}h")
                st.session_state['button_rerun'] = True
                if 'notifications' in st.session_state:
                    del st.session_state['notifications']
                st.experimental_rerun()



# with tab_news:
if selected_tab == tabs[2]: # News Tab

    news_sentiment_df = get_news_sentiment_df(asset, start_time, end_time)
    article_df = get_article_df(asset, start_time, end_time)
    logits_df = get_logits_df()

    if development_mode is True:
        with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
            st.markdown("""
            * Update News Sentiment Trend to add meaning
            * Show Press Releases
            * News Named Entity Word Cloud
            * Add price and FMDD to graph lines overlaid on news sentiment
            """)

    with st.expander(f"**News Entity Risk Trend ({period})**", expanded=True):
        # st.write(f"{asset}, {start_time}, {end_time}")
        if len(news_sentiment_df) == 0:
            st.write("No Articles In this Time Period")
        else:
            logits_df = logits_df.query(f'timestamp <= "{str(end_time)}+00:00"').iloc[-num_lookback_points:]
            st.plotly_chart(plots.line_plot_single(logits_df, column_x='timestamp', column_y="entity_max_fmdd",
                                                   line_name="News Entity Risk", line_color=highlight_color, fill='tozeroy', yaxis_title="Entity Risk Score",), 
                                                   use_container_width=True)
    with st.expander(f"**News Articles**", expanded=True):
        # article_df.set_index('timestamp', inplace=True)
        order_list = ['Latest', 'Latest Positive', 'Latest Negative', 'Latest Neutral']
        if 'news_order' in st.session_state:
            order = st.selectbox('Filter By:', order_list, index=order_list.index(st.session_state['news_order']))
        else:
            order = st.selectbox('Filter By:', order_list, index=0)

        st.session_state['news_order'] = order

        if order == 'Latest':
            article_df.sort_index(inplace=True, ascending=False)
        else:
            article_df.sort_index(inplace=True, ascending=False)
            if order == 'Latest Positive':
                article_df = article_df[article_df['sentiment_logits'] == 'Positive']
            elif order == 'Latest Negative':
                article_df = article_df[article_df['sentiment_logits'] == 'Negative']
            elif order == 'Latest Neutral':
                article_df = article_df[article_df['sentiment_logits'] == 'Neutral']

        if len(article_df) == 0:
            st.write("No News Articles In this Time Period")
        for i, row in article_df.iterrows():
            if row['sentiment_logits'] == 'Positive':
                theme = theme_good
            elif row['sentiment_logits'] == 'Negative':
                theme = theme_bad
            else:
                theme = theme_neutral

            # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
            hc.info_card(title=row['title'], content=f"{i.strftime('%b %d %Y, %H:%M')} - {row['subheadlines']}", theme_override=theme)

            # st.markdown(f"""
            #     <h6>{row['title']}</h6>
            #     <p>{i.strftime('%Y-%m-%d %H:%M')} - {row['subheadlines']}</p>
            #     Sentiment: {row['sentiment_logits']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Topic: {row['class_labels']}
            # """ + (i != article_df.index[len(article_df) - 1])*'<hr/>', unsafe_allow_html=True)

# with tab_ti:
if selected_tab == tabs[3]: # Technical Indicators Tab

    if development_mode is True:
        with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
            st.markdown("""
            * Add Important Tech Indicators Graphs (RSI, MACD, etc.)
            """)

    st.session_state['ti_selected_values'] = st.multiselect(
        label='Visualize Multiple Technical Indicators with Price and Volume',
        options=list(price_data_df.columns)[2:], # Ignoring timestamp and close
        default=st.session_state['ti_selected_values'],
    )

    for selected_value in st.session_state['ti_selected_values']:

        selected_value_name = selected_value.capitalize()
        if selected_value == 'rsi':
            selected_value_name = 'RSI'

            

        with st.expander(f'**{selected_value_name} history ({period})**', expanded=True):
            if selected_value == 'volume':
                st.plotly_chart(plots.line_plot_double_shared_bars(price_data_df, column_x = 'timestamp', column_y1='close', column_y2=selected_value, line_fill1=None, line_fill2='tozeroy',
                                                            line_name1="Price", line_name2=selected_value_name, line_color1=highlight_color, line_color2='black'),
                                    use_container_width=True)
            else:
                cols = st.columns(2)
                cols[0].plotly_chart(plots.line_plot_double_shared(price_data_df, column_x = 'timestamp', column_y1='close', column_y2=selected_value, line_fill1=None, line_fill2='tozeroy',
                                                            line_name1="Price", line_name2=selected_value, line_color1=highlight_color, line_color2='black'),
                                    use_container_width=True)
                cols[1].plotly_chart(plots.line_plot_double_shared_bars(price_data_df, column_x = 'timestamp', column_y1=selected_value, column_y2='volume', line_fill1=None, line_fill2='tozeroy',
                                                            line_name1=selected_value, line_name2='volume', line_color1='black', line_color2=highlight_color),
                                    use_container_width=True)


# with tab_chat:
if selected_tab == tabs[4]: # Chatbot Tab
    if development_mode is True:
        with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
            st.markdown("""
            * Chatbot
            * Summarize
            * Ask questions
            """)
    #Creating the chatbot interface

    # Storing the chat
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    def ask_chatgpt(user_query):

        # Understand Intent
        message_history = [{"role": "system", "content": f"""
                                You are CryptoGPT, a chatbot that analyzes, identifies, and advises on price fall risk of {asset} cryptocurrency. 
                                Consider today as {end_time}.
                                Data:
                                twitter_data latest = {tweet_df.sort_index(ascending=False).iloc[:chatgpt_df_size]['BODY']}
                                twitter_data highest reach = {tweet_df.sort_values(by=['ENGAGEMENT'], ascending=False).iloc[:chatgpt_df_size]['BODY']}
                                news_data latest = {get_article_df(asset, start_time, end_time).sort_index(ascending=False)}
                                price_fall_probability = {logits_df.set_index('timestamp')['prediction_logit']}
                                price_data = {price_data_df.set_index('timestamp')[['close','volume']]}
                                """}
                                ]
        for i in range(len(st.session_state['generated'])):
            message_history.append({"role": "user", "content": st.session_state['past'][i]})
            message_history.append({"role": "assistant", "content": st.session_state['generated'][i]})
        message_history.append({"role": "user", "content": f"{user_query}"})
        completion = openai.ChatCompletion.create(
            model = openai_model_name,
            temperature = 0.8,
            max_tokens = 4096-streamlit_helpers.num_tokens_from_messages(message_history, model=openai_model_name),
            messages = message_history
            )
        return completion.choices[0].message['content']
        

    if st.session_state['generated']:

        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="fun-emoji")
            message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral")

        user_query = st.text_input(label="Ask CryptoGPT a question: ", placeholder="", key=f"input{len(st.session_state['generated'])}", label_visibility="hidden")
    else:
        user_query = st.text_input(label="Ask CryptoGPT a question: ", placeholder="Summarize today's price and news", key="input")

    cols = st.columns([1,4,1])
    ask = cols[0].button("Ask ", key="ask")
    reset_chat = cols[-1].button("Start New Chat", key="reset_chat")

    if ask:
        if 'generated' in st.session_state and len(st.session_state['generated']) > 3:
            with st.spinner('🧹Starting Fresh...'):
                st.session_state['generated'] = []
                st.session_state['past'] = []

        with st.spinner('🤔 Thinking...'):
            lookback_interval = 6
            output = ask_chatgpt(user_query)
            output = '. '.join([line for line in output.split('. ') if 'sorry' not in line.lower()])
            if output[:9] == "However, ":
                output = output= output[9:]

        # time.sleep(30)
        print(f"output: {output}")
        # store the output
        st.session_state['past'].append(user_query)
        st.session_state['generated'].append(output)
        st.experimental_rerun()

    if reset_chat:
        with st.spinner('🧹Starting Fresh...'):
            st.session_state['generated'] = []
            st.session_state['past'] = []
            st.experimental_rerun()

# with tab4:
# if selected_tab == tabs[5]:

#     if development_mode is True:
#         with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
#             st.markdown("""
#             * Trends from other data processing
#             * API for other sources
#             * Open to ideas
#             """)

#     cols = st.columns(3)

#     with cols[0]:
#         if asset == "BTC":  # Show BTC Fear and Greed Index
#             with st.expander(f"**Fear & Greed Index**", expanded=True):
#                 st.image(
#                     f"https://alternative.me/images/fng/crypto-fear-and-greed-index-{str(date).replace('-0', '-')}.png",
#                     use_column_width=True)

         
if development_mode and selected_tab == tabs[5]: # About Us Tab

    if development_mode is True:
        with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
            st.markdown("""
            * Student Attribution
            """)

    st.write("Developed as part of the BNY Mellon sponsored capstone project at Carnegie Mellon University's MS in Artificial Intelligence and Innovation program in 2023.")

    cols = st.columns(2)
    with cols[0].expander(f"**CMU Student Team**", expanded=True):
        file_path = "images/BNYM_students.jpg"
        try:
            st.image(file_path, use_column_width=True)
        except:
            link = 'https://drive.google.com/drive/u/0/folders/1SyUmoODcE-6KNw6Y9pIh32CVSccDcCdm'
            st.error(f"Please download the {file_path} from {link}")
            raise FileNotFoundError(f"Please download {file_path} from {link}")

    with cols[1].expander(f"**Project Mentors and CMU Faculty**", expanded=True):
        file_path = "images/BNYM_mentors.jpg"
        try:
            st.image(file_path, use_column_width=True)
        except:
            link = 'https://drive.google.com/drive/u/0/folders/1SyUmoODcE-6KNw6Y9pIh32CVSccDcCdm'
            st.error(f"Please download the {file_path} from {link}")
            raise FileNotFoundError(f"Please download {file_path} from {link}")
        
