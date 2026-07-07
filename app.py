import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Portfolio Analyzer")
st.write("Track your stock portfolio and benchmark against the S&P 500")

st.subheader("Enter Your Portfolio")

tickers_input: = st.text_input("Enter tickers seperated by commas (e.g. AAPL, MSFT, NVDA)")

if tickers_input:
  tickers = [t.strip().upper() for t in tickers_input.split(",")]

  shares_list = []
  prices_list = []

  for ticker in tickers:
      col1, col2 = st.columns(2)
      with col1:
          shares = st.number_input(f"Shares of {ticker}", min_value=0, value=10)
      with col2:
          price = st.number_input(f"Purchase price of {ticker} ($)", min_value=0.0, value=100.0)
      shares_list.append(shares)
      prices_list.append(price)
  if st.button("Analyze Portfolio"):
      st.write("Analyzing...")
