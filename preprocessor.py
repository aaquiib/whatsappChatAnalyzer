import pandas as pd
import re
import streamlit as st

def preprocess(data):
    # Define regex pattern for WhatsApp chat format
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:am|pm)?\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create initial DataFrame
    df = pd.DataFrame({
        'user_message': messages,
        'message_date': dates
    })

    # Clean date strings
    df['message_date'] = df['message_date'].str.replace('\u202f', '', regex=True)  # Remove non-breaking space
    df['message_date'] = df['message_date'].str.strip().str.rstrip('-').str.strip()

    # Convert to datetime with error handling
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M%p')
    except ValueError:
        # Fallback for 24-hour format or other variations
        df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce')
        if df['message_date'].isna().any():
            st.error("Some dates could not be parsed. Please ensure the chat file follows the expected format.")
            return None

    # Rename column
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # User name present
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract date components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create period column for hourly activity
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    df['period'] = period

    return df