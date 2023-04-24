import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import datetime

import streamlit as st  # 🎈 data web app development
import hydralit_components as hc
from streamlit_chat import message
import streamlit_helpers
from plots import plots
import random

from event_data import DashboardNewsData # In event_data/api.py

import bing_chatbot
import asyncio
from EdgeGPT import Chatbot, ConversationStyle
import json

# Page config. Other configs are loaded from .streamlit/config.toml
st.set_page_config(page_title="CRISys - Cryptocurrency Risk Identification System Dashboard",
                   page_icon="images/crisys_logo.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

# st.balloons()
st.markdown(streamlit_helpers.hide_streamlit_style, unsafe_allow_html=True)
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #ff5555;
        color:#ffffff;
    }
    div.stButton > button:hover {
        background-color: #e3a72f;
        color:#ffffff;
        }
    </style>""", unsafe_allow_html=True)


padding = 0
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
       </style> """, unsafe_allow_html=True)

# HydraLit Info cards can apply customisation to almost all the properties of the card, including the progress bar
theme_good = {'bgcolor': '#EFF8F7','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-circle'}
theme_neutral = {'bgcolor': '#f9f9f9','title_color': 'orange','content_color': 'orange','icon_color': 'orange', 'icon': 'fa fa-question-circle'}
theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-times-circle'}
theme_alert = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red','icon_color': 'red', 'icon': 'fa fa-exclamation-triangle'}

if 'load_time' not in st.session_state:
    st.session_state['load_time'] = datetime.datetime(2022, 6, 30, 11, 0, 0, 0) # Dummy value replace with datetime.datetime.now()
if 'ti_selected_values' not in st.session_state: # Default values
    st.session_state['ti_selected_values'] = ['volume', 'rsi', 'volatility', 'var_90']

with st.sidebar:
    st.image("images/bnym_logo.png", width=200, )
    st.image("images/crisys_logo.png", width=200)
    st.title("Dashboard Configuration")
    
    asset = st.selectbox("Cryptocurrency:", ["BTC", "ETH", "XRP", "SOL"])
    # time_interval = st.selectbox("Time Intervals:", ["30Min", "1h", "6h", "1d"])
    time_interval = '30Min'
    # lookback_period = st.selectbox("Lookback Period:", ["6h", "12h", "24h"], index=2)
    lookback_period = st.select_slider("Lookback Period:", options=["6h", "12h", "24h","3d", "7d"], value="24h")
    
    date = st.date_input("End Date:", st.session_state['load_time'])
    # end_time = st.time_input("Start Time:", streamlit_helpers.round_time(datetime.datetime.now()))
    end_time = st.time_input("End Time:", streamlit_helpers.round_time(st.session_state['load_time'], mins_delta=30), step=datetime.timedelta(minutes=30))
    # end_time = st.time_input("Start Time:")
    end_time = datetime.datetime.combine(date, end_time)
    st.session_state['load_time'] = end_time
    if end_time > datetime.datetime.now():
        st.error("Start Time cannot be in the future!")
    start_time = end_time - pd.to_timedelta(lookback_period)
    col1, col2 =  st.columns(2)
    if col1.button("◀ 6 hours"):
        # Refresh page with -6 hours delta
        # end_time = datetime.datetime.now() - pd.to_timedelta(lookback_period)
        st.session_state['load_time'] = st.session_state['load_time'] - pd.to_timedelta("6h")
        st.experimental_rerun()
    if col2.button("6 hours ▶"):
        # Refresh page with -6 hours delta
        # end_time = datetime.datetime.now() - pd.to_timedelta(lookback_period)
        st.session_state['load_time'] = st.session_state['load_time'] + pd.to_timedelta("6h")
        st.experimental_rerun()

if 'notifications' not in st.session_state:
    st.session_state['notifications'] = True
if 'notifications' in st.session_state and  st.session_state['notifications'] is not None:
    # hc.info_card(title="Alert Notification Body", content="TODO", theme_override=theme_alert)
    st.error("🚨 Alert Notification Body")

    dismiss_notification = st.button("Dismiss Alerts")
    if dismiss_notification:
        st.session_state['notifications'] = None
        st.experimental_rerun()


# Main Body
highlight_color = '#e3a72f'
# st.markdown(f"""
# <style>
#     div.block-container{{
#         padding-top: 0;
#     }}
#     .highlight{{
#         color: #e3a72f;
#     }}
# </style>
# <h4>Dashboard for <span class='highlight'>{asset}</span> 
# in <span class='highlight'>{time_interval}</span> 
# intervals and <span class='highlight'>{lookback_period}</span> lookback period
# at <span class='highlight'>{end_time.strftime("%Y-%m-%d %H:%M")}</span></h4>
# """, unsafe_allow_html=True)
# st.title(f"Dashboard for {asset} in {time_interval} intervals and {lookback_period} lookback period")
# st.markdown('----')

if 'h' in lookback_period:
    num_lookback_points = (int(lookback_period.split('h')[0]) * 2) + 1 # 24h * 2 + 1
elif 'd' in lookback_period:
    num_lookback_points = (int(lookback_period.split('d')[0]) * 24 * 2) + 1
price_data_df = pd.read_csv("new_values.csv")
price_data_df = price_data_df.query(f'timestamp <= "{str(end_time)}"').iloc[-num_lookback_points:]
news_sentiment_df = DashboardNewsData.dashboard_news_aggregated_sentiment(asset, start_time, end_time)
article_df = DashboardNewsData.dashboard_news_articles_to_show(asset, start_time, end_time)

tab_overview, tab_social, tab_news, tab_ti, tab_chat, tab4 = st.tabs(["📜 Overview", "🐦 Twitter", "📰 News", "📊 Technical Indictors", "💬 CrisysGPT Chat", "🤔 More?"])

with tab_overview:
    
    # FMDD Numbers
    fmdd_values = [round(x,3) for x in price_data_df['Forward MDD'].values]
    if fmdd_values[-2] == 0:
        fmdd_delta = 100
    else:
        fmdd_delta = round(100*(fmdd_values[-1]-fmdd_values[-2])/fmdd_values[-2],1)
    # Price Numbers
    price_values = [round(x,3) for x in price_data_df['close'].values]
    price_delta = round(100*(price_values[-1]-price_values[-2])/price_values[-2],1)
    # Volume Numbers
    volume_values = [round(x,0) for x in price_data_df['volume'].values]
    volume_delta = round(100*(volume_values[-1]-volume_values[-2])/(volume_values[-2]),1)

    col1, col2, col3 = st.columns(3)

    col1.metric(label="Maximum Draw Down", value=fmdd_values[-1], delta=f"{fmdd_delta}% in {time_interval}", delta_color="off" if fmdd_delta == 0 else "inverse", help=f'Risk of Price Fall in next 6 hours')
    col2.metric(label=f"{asset} Price", value=f'${price_values[-1]}', delta=f"{price_delta}% in {time_interval}", delta_color="off" if price_delta == 0 else "normal", help=f'Last trade price value in USD at {end_time}')
    col3.metric(label=f"{asset} Volume", value=f'{volume_values[-1]}', delta=f"{volume_delta}% in {time_interval}", delta_color="off" if volume_delta == 0 else "normal", help=f'Units of cryptocurrency traded in last {time_interval}')
    
    with st.expander(f'Maximum Draw Down ({lookback_period})', expanded=True):
        st.plotly_chart(plots.line_plot_single(price_data_df, column_x = 'timestamp', column_y='Forward MDD', 
                                                    line_name="Maximum Draw Down", line_color=highlight_color, fill='tozeroy',
                                                    add_hline=True, hline_value=0.03, hline_color='red', hline_annotation_text='High Risk Threshold'),
                            use_container_width=True)

    with st.expander(f'Price and Volume ({lookback_period}) Shared', expanded=True):
        st.plotly_chart(plots.line_plot_double_shared_bars(price_data_df, column_x = 'timestamp', column_y1='close', column_y2='volume', line_fill1=None, line_fill2='tozeroy',
                                                    line_name1="Price", line_name2='Volume', line_color1=highlight_color, line_color2='grey'),
                            use_container_width=True)
    
    # if st.button("<- 30 Min"):
    #     end_time = end_time - pd.to_timedelta(-30, unit='m')
    #     st.experimental_rerun()

with tab_social:
    with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
        st.markdown("""
        * Twitter Sentiment Trend
        * Trending Topics
        * Mentions
        * Top Tweets
        * Wordcloud
        """)
    with st.expander(f"Mentions #crypto #btc (Placeholder Data)", expanded=True):
        st.plotly_chart(plots.mentions_line_plot(title='Mentions', n=10), use_container_width=True)

with tab_news:

    with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
        st.markdown("""
        * Show Press Releases
        * News Named Entity Word Cloud
        * Add price and FMDD to graph lines overlaid on news sentiment
        """)

    with st.expander(f"News Sentiment Trend ({lookback_period})", expanded=True):
        # st.write(f"{asset}, {start_time}, {end_time}")
        if len(news_sentiment_df) == 0:
            st.write("No Articles In this Time Period")
        else:
            st.plotly_chart(plots.line_plot_single(news_sentiment_df, column_y='sentiment', line_name='News Sentiment Trend'),
                            use_container_width=True)

    with st.expander(f"News Articles", expanded=True):
        # article_df.set_index('timestamp', inplace=True)
        order = st.selectbox('Sort By', ['Latest', 'Top Positive', 'Top Negative', 'Top Neutral'], index=0)
        if order == 'Latest':
            article_df.sort_index(inplace=True, ascending=False)
        else:
            article_df.sort_index(inplace=True, ascending=False)
            if order == 'Top Positive':
                article_df = article_df[article_df['sentiment_logits'] == 'Positive']
            elif order == 'Top Negative':
                article_df = article_df[article_df['sentiment_logits'] == 'Negative']
            elif order == 'Top Neutral':
                article_df = article_df[article_df['sentiment_logits'] == 'Neutral']
        
        if len(article_df) == 0:
            st.write("No Articles In this Time Period")
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

with tab_ti:
    with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
        st.markdown("""
        * Add Important Technical Indictors Graphs (RSI, MACD, etc.)
        """)

    
    
    # col_list = list(price_data_df.columns)
    # col_list.pop(0)


    st.session_state['ti_selected_values'] = st.multiselect(
        label='Visualize Technical Indicators',
        options=list(price_data_df.columns)[2:], # Ignoring timestamp and close
        default=st.session_state['ti_selected_values'],
    )

    for selected_value in st.session_state['ti_selected_values']:

        selected_value_name = selected_value.capitalize()
        if selected_value == 'rsi':
            selected_value_name = 'RSI'

            

        with st.expander(f'{selected_value_name} history ({lookback_period}) Shared', expanded=True):
            if selected_value == 'volume':
                st.plotly_chart(plots.line_plot_double_shared_bars(price_data_df, column_x = 'timestamp', column_y1='close', column_y2=selected_value, line_fill1=None, line_fill2='tozeroy',
                                                            line_name1="Price", line_name2=selected_value_name, line_color1=highlight_color, line_color2='grey'),
                                    use_container_width=True)
            else:
                cols = st.columns(2)
                cols[0].plotly_chart(plots.line_plot_double_shared(price_data_df, column_x = 'timestamp', column_y1='close', column_y2=selected_value, line_fill1=None, line_fill2='tozeroy',
                                                            line_name1="Price", line_name2=selected_value, line_color1=highlight_color, line_color2='grey'),
                                    use_container_width=True)
                cols[1].plotly_chart(plots.line_plot_double_shared_bars(price_data_df, column_x = 'timestamp', column_y1=selected_value, column_y2='volume', line_fill1=None, line_fill2='tozeroy',
                                                            line_name1=selected_value, line_name2='volume', line_color1='grey', line_color2=highlight_color),
                                    use_container_width=True)


with tab_chat:
    with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
        st.markdown("""
        * Chatbot
        * Summarize
        * Ask questions
        """)
    #Creating the chatbot interface
    st.write("Ask CRISysGPT a question!")

    # Storing the chat
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    with hc.HyLoader('Loading',hc.Loaders.standard_loaders,index=0):
        async def ask_bing(input_prompt):
            # return "Amazingly Insightful ChatGPT Response"
            bot = Chatbot(cookies=bing_chatbot.BING_COOKIES_FILE)
            # input_prompt = input("User: ")
            wait_count = 0
            while True:
                reply_dict = await bot.ask(prompt=input_prompt, conversation_style=ConversationStyle.precise, wss_link="wss://sydney.bing.com/sydney/ChatHub")
                # print(f"User: {reply_dict['item']['messages'][0]['text']}")
                reply = reply_dict['item']['messages'][1]['text']
                if 'Searching the web for' not in reply:
                    await bot.close()
                    return reply
    # def generate_response(input_prompt):
    #     return bing_chatbot.ask_bing(input_prompt)
        # return "Amazingly Insightful ChatGPT Response"
        # completions = openai.Completion.create(
        #     engine = "text-davinci-003",
        #     prompt = prompt,
        #     max_tokens = 1024,
        #     n = 1,
        #     stop = None,
        #     temperature=0.5,
        # )
        # message = completions.choices[0].text
        # return message 

    if st.session_state['generated']:
    
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="fun-emoji")
            message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral")

    input_text = st.text_input("Ask: ","What were the most impactful news and tweets today?", key="input")
    ask = st.button("Ask", key="ask")

    if ask:
        input_prompt = f"""
                        I want you to summarize what happened today and advice what will happen to {asset}.
                        Do not use the internet to answer this question and do not use any information beyond {end_time}.
                        Do not mention that you cannot provide financial advice. 
                        Be brief and to the point.
                        {asset} price from past to now in 30 minute increaments: {list(price_data_df['close'].values[-10:])}
                        Top News: {article_df['title'].values[-10:]}
                        Top Tweets: {None}
                        Please advice on: {input_text}.
                        Consider 'today' as {end_time} and everything else relative.
                        """
        print(f"{len(input_prompt)} char input: {input_prompt}")
        
        output = asyncio.run(ask_bing(input_prompt))
        output = '. '.join([line for line in output.split('. ') if 'sorry' not in line.lower()])
        
        # time.sleep(30)
        print(f"output: {output}")
        # store the output 
        st.session_state.past.append(input_text)
        st.session_state.generated.append(output)
        st.experimental_rerun()

    

with tab4:

    with st.expander(f"Work in Progress! 🚧 Coming Soon:", expanded=False):
        st.markdown("""
        * Trends from other data processing
        * API for other sources
        * Open to ideas
        """)

    col1, col2, col3 = st.columns(3)

    with col1:
        if asset == "BTC":  # Show BTC Fear and Greed Index
            with st.expander(f"Fear & Greed Index", expanded=True):
                st.image(
                    f"https://alternative.me/images/fng/crypto-fear-and-greed-index-{str(date).replace('-0', '-')}.png",
                    use_column_width=True)
                
    
