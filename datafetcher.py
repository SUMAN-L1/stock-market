import streamlit as st
import yfinance as yf
import pandas as pd
from io import BytesIO
import json
import requests

# Title of the app
st.title("Stock Market Analysis")

# Fetch stock symbols from a public API or file
@st.cache_data
def fetch_stock_symbols():
    # You can use a public API or a pre-defined list. Here we use a static list for demonstration.
    # This list can be updated or replaced with a dynamic source.
    symbols = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "GOOGL", "name": "Alphabet Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "AMZN", "name": "Amazon.com, Inc."},
        {"symbol": "TSLA", "name": "Tesla, Inc."},
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd"},
        {"symbol": "TCS.BO", "name": "Tata Consultancy Services Ltd"},
        # Add more symbols as needed
    ]
    return symbols

# Function to get suggestions
def get_suggestions(query, symbols):
    return [s for s in symbols if query.upper() in s["symbol"] or query.lower() in s["name"].lower()]

# Fetch stock symbols
stock_symbols = fetch_stock_symbols()

# Sidebar for user input
st.sidebar.header("User Input Parameters")

# Autocomplete input for stock symbols
query = st.sidebar.text_input("Stock Symbol (start typing to get suggestions)")

if query:
    suggestions = get_suggestions(query, stock_symbols)
    if suggestions:
        options = [s["symbol"] for s in suggestions]
        selected_symbol = st.sidebar.selectbox("Select Stock Symbol", options)
    else:
        st.sidebar.write("No suggestions found")
        selected_symbol = query
else:
    selected_symbol = "AAPL"  # Default symbol if no input

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

# Fetch stock data
@st.cache_data
def load_data(symbol, period, interval):
    return yf.download(symbol, period=period, interval=interval, progress=False)

data = load_data(selected_symbol, period, interval)

# Display stock data
st.subheader(f"Stock Data for {selected_symbol}")
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
        st.download_button(label="Download as CSV", data=file_data, file_name=f"{selected_symbol}_data.csv", mime="text/csv")
    elif file_format == "xlsx":
        st.download_button(label="Download as XLSX", data=file_data, file_name=f"{selected_symbol}_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif file_format == "slx":
        st.download_button(label="Download as SLX", data=file_data, file_name=f"{selected_symbol}_data.slx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
