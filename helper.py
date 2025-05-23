from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

# Default stop words
DEFAULT_STOP_WORDS = """
the is are and or to in a an hai ke ka ki se aur par bhi nahi hi ok
""".split()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    percent_df = (df['user'].value_counts(normalize=True) * 100).round(2).reset_index()
    percent_df.columns = ['name', 'percent']
    return x, percent_df

def create_wordcloud(selected_user, df):
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read().split()
    except FileNotFoundError:
        stop_words = DEFAULT_STOP_WORDS

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        return " ".join(word for word in message.lower().split() if word not in stop_words)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white', colormap='viridis')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    try:
        with open('stop_hinglish.txt', 'r') as f:
            stop_words = f.read().split()
    except FileNotFoundError:
        stop_words = DEFAULT_STOP_WORDS

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        words.extend(word for word in message.lower().split() if word not in stop_words)

    return pd.DataFrame(Counter(words).most_common(20))

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend(c for c in message if emoji.is_emoji(c))

    return pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.groupby('only_date').count()['message'].reset_index()

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    time_order = [f"{str(i).zfill(2)}-{str((i+1)%24).zfill(2)}" for i in range(24)]
    user_heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)

    existing_periods = [col for col in time_order if col in user_heatmap.columns]
    user_heatmap = user_heatmap[existing_periods]
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return user_heatmap.reindex(day_order)