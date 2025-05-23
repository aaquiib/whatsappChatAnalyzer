import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set page configuration for wide layout and modern theme
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide", page_icon="📱")

# Custom CSS for modern UI
st.markdown("""
    <style>
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #25D366;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #20b558;
    }
    .card {
        background-color: #2C2C2C;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #FFFFFF;
    }
    .stSelectbox {
        background-color: #2C2C2C;
        border-radius: 8px;
    }
    .stFileUploader {
        background-color: #2C2C2C;
        border-radius: 8px;
    }
    .stForm {
        background-color: #2C2C2C;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False

# Sidebar configuration
with st.sidebar:
    st.title("📱 WhatsApp Chat Analyzer")
    st.markdown("Analyze your WhatsApp chat data with a modern and interactive interface.")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload WhatsApp Chat (.txt)", type=["txt"])
    
    if uploaded_file:
        with st.spinner("Processing chat file..."):
            bytes_data = uploaded_file.getvalue()
            data = bytes_data.decode("utf-8")
            df = preprocessor.preprocess(data)
            if df is None:
                st.error("Failed to process the file. Please ensure it follows the WhatsApp chat format.")
                st.stop()
            st.session_state.df = df

        # User selection
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")
        
        with st.form(key="analysis_form"):
            st.session_state.selected_user = st.selectbox("Select User/Group", user_list, help="Choose a user or 'Overall' for group analysis")
            submit_button = st.form_submit_button("Analyze Chat")
            if submit_button:
                st.session_state.show_analysis = True

# Main content
if uploaded_file and st.session_state.show_analysis and st.session_state.df is not None:
    df = st.session_state.df
    selected_user = st.session_state.selected_user
    st.title("Chat Analysis Dashboard")
    
    # Top Statistics
    num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
    st.markdown("### 📊 Top Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='card'><h3>Total Messages</h3><h2>{}</h2></div>".format(num_messages), unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>Total Words</h3><h2>{}</h2></div>".format(words), unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><h3>Media Shared</h3><h2>{}</h2></div>".format(num_media_messages), unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='card'><h3>Links Shared</h3><h2>{}</h2></div>".format(num_links), unsafe_allow_html=True)

    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Timelines", "📈 Activity", "☁️ Word Cloud", "😊 Emojis"])

    with tab1:
        st.markdown("### Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(timeline['time'], timeline['message'], color='#25D366', linewidth=2)
        ax.fill_between(timeline['time'], timeline['message'], alpha=0.1, color='#25D366')
        ax.set_facecolor('#2C2C2C')
        fig.patch.set_facecolor('#1E1E1E')
        ax.tick_params(axis='x', rotation=45, colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)

        st.markdown("### Daily Timeline")
        # Month and Year selection
        col1, col2 = st.columns(2)
        with col1:
            available_years = sorted(df['year'].unique())
            selected_year = st.selectbox("Select Year", available_years, key="year_select")
        with col2:
            available_months = sorted(df[df['year'] == selected_year]['month'].unique())
            selected_month = st.selectbox("Select Month", available_months, key="month_select")
        
        # Filter daily timeline for selected month and year
        daily_timeline = helper.daily_timeline(selected_user, df)
        daily_timeline['only_date'] = pd.to_datetime(daily_timeline['only_date'])
        filtered_timeline = daily_timeline[
            (daily_timeline['only_date'].dt.year == selected_year) &
            (daily_timeline['only_date'].dt.month_name() == selected_month)
        ]
        
        if not filtered_timeline.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(filtered_timeline['only_date'], filtered_timeline['message'], color='#25D366', linewidth=2)
            ax.set_facecolor('#2C2C2C')
            fig.patch.set_facecolor('#1E1E1E')
            ax.tick_params(axis='x', rotation=45, colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.set_title(f"Daily Activity for {selected_month} {selected_year}", color='white')
            st.pyplot(fig)
        else:
            st.warning(f"No data available for {selected_month} {selected_year}.")

    with tab2:
        st.markdown("### Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Most Active Days")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.bar(busy_day.index, busy_day.values, color='#25D366')
            ax.set_facecolor('#2C2C2C')
            fig.patch.set_facecolor('#1E1E1E')
            ax.tick_params(axis='x', rotation=45, colors='white')
            ax.tick_params(axis='y', colors='white')
            st.pyplot(fig)

        with col2:
            st.markdown("#### Most Active Months")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.bar(busy_month.index, busy_month.values, color='#FF5733')
            ax.set_facecolor('#2C2C2C')
            fig.patch.set_facecolor('#1E1E1E')
            ax.tick_params(axis='x', rotation=45, colors='white')
            ax.tick_params(axis='y', colors='white')
            st.pyplot(fig)

        st.markdown("### Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(user_heatmap, cmap='YlGnBu', annot=True, fmt='.0f', ax=ax)
        ax.set_facecolor('#2C2C2C')
        fig.patch.set_facecolor('#1E1E1E')
        ax.tick_params(colors='white')
        st.pyplot(fig)

    with tab3:
        st.markdown("### Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis('off')
        fig.patch.set_facecolor('#1E1E1E')
        st.pyplot(fig)

        st.markdown("### Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(most_common_df[0], most_common_df[1], color='#25D366')
        ax.set_facecolor('#2C2C2C')
        fig.patch.set_facecolor('#1E1E1E')
        ax.tick_params(colors='white')
        st.pyplot(fig)

    with tab4:
        st.markdown("### Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df.style.set_properties(**{'background-color': '#2C2C2C', 'color': 'white'}))
        with col2:
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f%%", colors=sns.color_palette("Set2"))
            ax.set_facecolor('#2C2C2C')
            fig.patch.set_facecolor('#1E1E1E')
            st.pyplot(fig)

    # Most Busy Users (Group Level)
    if selected_user == 'Overall':
        st.markdown("### Most Active Users")
        x, new_df = helper.most_busy_users(df)
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.bar(x.index, x.values, color='#FF5733')
            ax.set_facecolor('#2C2C2C')
            fig.patch.set_facecolor('#1E1E1E')
            ax.tick_params(axis='x', rotation=45, colors='white')
            ax.tick_params(axis='y', colors='white')
            st.pyplot(fig)
        with col2:
            st.dataframe(new_df.style.set_properties(**{'background-color': '#2C2C2C', 'color': 'white'}))
else:
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>Welcome to WhatsApp Chat Analyzer</h1>
            <p>Upload a WhatsApp chat export (.txt file) to get started.</p>
        </div>
    """, unsafe_allow_html=True)