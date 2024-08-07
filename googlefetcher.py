import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from datetime import datetime

# Title of the app
st.title("Advanced Stock Market Analysis with Google Finance")

# Sidebar for user input
st.sidebar.header("User Input Parameters")

# Function to get user input
def get_user_input():
    # Select exchange
    exchange = st.sidebar.selectbox("Select Exchange", ["NSE", "BSE", "NASDAQ", "NYSE"])

    # Select stock symbol
    stock_symbol = st.sidebar.text_input("Stock Symbol (e.g., RELIANCE for Reliance Industries)")

    # Date range inputs
    min_date = datetime(1980, 1, 1)
    max_date = datetime(2024, 12, 31)
    
    start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", value=datetime.today(), min_value=min_date, max_value=max_date)

    # Ensure end_date is not before start_date
    if end_date < start_date:
        st.sidebar.error("End date cannot be before start date.")
        end_date = start_date

    # Format dates for display
    formatted_start_date = start_date.strftime("%d/%m/%Y")
    formatted_end_date = end_date.strftime("%d/%m/%Y")

    # Display formatted dates
    st.sidebar.write(f"Fetching data from: {formatted_start_date} to {formatted_end_date}")

    return exchange, stock_symbol, start_date, end_date

# Get user input
exchange, stock_symbol, start_date, end_date = get_user_input()

# Function to fetch stock data from Google Finance
@st.cache_data
def fetch_data_from_google(exchange, symbol, start_date, end_date):
    base_url = "https://www.google.com/finance/quote/"
    
    if exchange == "NSE":
        symbol = f"{symbol}:NSE"
    elif exchange == "BSE":
        symbol = f"{symbol}:BOM"
    elif exchange == "NASDAQ":
        symbol = f"{symbol}:NASDAQ"
    elif exchange == "NYSE":
        symbol = f"{symbol}:NYSE"
    
    url = f"{base_url}{symbol}"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error("Failed to fetch data from Google Finance")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the script tag containing JSON data
    script = soup.find('script', {'id': 'K3kOpe'})
    
    if not script:
        st.error("Failed to parse Google Finance data")
        return pd.DataFrame()
    
    import json
    json_data = json.loads(script.string)
    
    # Extract the relevant stock data from the JSON object
    historical_data = json_data['historicalPrices']
    
    if not historical_data:
        st.warning("No historical data available")
        return pd.DataFrame()
    
    # Convert the data into a DataFrame
    df = pd.DataFrame(historical_data)
    
    # Filter data within the selected date range
    df['date'] = pd.to_datetime(df['date'], unit='s').dt.date
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    return df

# Fetch stock data
data = fetch_data_from_google(exchange, stock_symbol, start_date, end_date)

# Check if data is empty
if not data.empty:
    # Display stock data
    st.subheader(f"Stock Data for {stock_symbol}")
    st.write(data)

    # Plot stock data
    st.subheader("Stock Closing Price")
    st.line_chart(data.set_index('date')['close'])

    # Display descriptive statistics
    st.subheader("Descriptive Statistics")
    st.write(data.describe())

    # Function to convert DataFrame to different formats
    def convert_df(df, file_format):
        if file_format == "csv":
            return df.to_csv(index=False).encode('utf-8')
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
else:
    st.warning("No data available for the selected period.")
