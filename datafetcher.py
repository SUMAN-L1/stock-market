import streamlit as st
import yfinance as yf
import pandas as pd
from io import BytesIO
from datetime import datetime

# Title of the app
st.title("Stock Market Analysis")

# Sidebar for user input
st.sidebar.header("User Input Parameters")

# Function to get user input
def get_user_input():
    # Select exchange
    exchange = st.sidebar.selectbox("Select Exchange", ["NSE", "BSE"])

    # Select stock symbol
    stock_symbol = st.sidebar.text_input("Stock Symbol (e.g., RELIANCE for Reliance Industries)")

    # Append exchange suffix to stock symbol
    if exchange == "NSE":
        stock_symbol += ".NS"
    elif exchange == "BSE":
        stock_symbol += ".BO"

    # Date range inputs
    start_date = st.sidebar.date_input("Start Date", value=datetime(2010, 1, 1))  # Allowing older start dates
    end_date = st.sidebar.date_input("End Date", value=datetime.today())

    # Format dates for display
    formatted_start_date = start_date.strftime("%d/%m/%Y")
    formatted_end_date = end_date.strftime("%d/%m/%Y")

    # Display formatted dates
    st.sidebar.write(f"Fetching data from: {formatted_start_date} to {formatted_end_date}")

    # Select interval
    interval = st.sidebar.selectbox(
        "Interval",
        ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
    )

    return stock_symbol, start_date, end_date, interval

# Get user input
stock_symbol, start_date, end_date, interval = get_user_input()

# Fetch stock data
@st.cache_data
def load_data(symbol, start_date, end_date, interval):
    return yf.download(symbol, start=start_date, end=end_date, interval=interval, progress=False)

data = load_data(stock_symbol, start_date, end_date, interval)

# Display stock data
st.subheader(f"Stock Data for {stock_symbol}")
st.write(data)

# Plot stock data
st.subheader("Stock Closing Price")
st.line_chart(data['Close'])

# Display descriptive statistics
st.subheader("Descriptive Statistics")
st.write(data.describe())

# Function to convert DataFrame to different formats
def convert_df(df, file_format):
    if file_format == "csv":
        return df.to_csv().encode('utf-8')
    elif file_format == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        return output.getvalue()
    elif file_format == "slx":
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='Sheet1')
        return output.getvalue()
    else:
        raise ValueError("Unsupported file format")

# Download data
st.subheader("Download Historical Data")
file_format = st.selectbox("Select File Format", ("csv", "xlsx", "slx"))

if st.button("Download"):
    file_data = convert_df(data, file_format)
    if file_format == "csv":
        st.download_button(label="Download as CSV", data=file_data, file_name=f"{stock_symbol}_data.csv", mime="text/csv")
    elif file_format == "xlsx":
        st.download_button(label="Download as XLSX", data=file_data, file_name=f"{stock_symbol}_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif file_format == "slx":
        st.download_button(label="Download as SLX", data=file_data, file_name=f"{stock_symbol}_data.slx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
