import streamlit as st
import yfinance as yf
import pandas as pd
from io import BytesIO

# Title of the app
st.title("Stock Market Analysis")

# Sidebar for user input
st.sidebar.header("User Input Parameters")

# Function to get user input
def get_user_input():
    # Select stock
    stock_symbol = st.sidebar.text_input("Stock Symbol", "AAPL")

    # Select period
    period = st.sidebar.selectbox(
        "Period",
        ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
    )

    # Select interval
    interval = st.sidebar.selectbox(
        "Interval",
        ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
    )

    return stock_symbol, period, interval

# Get user input
stock_symbol, period, interval = get_user_input()

# Fetch stock data
@st.cache_data
def load_data(symbol, period, interval):
    return yf.download(symbol, period=period, interval=interval, progress=False)

data = load_data(stock_symbol, period, interval)

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
