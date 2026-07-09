
import streamlit as st
import yfinance as yf
import pandas as pd
import anthropic

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC-API-KEY"])

def get_ai_insights(summary_text):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {"role": "user", "content": f"Here is a portfolio performance summary:\n{summary_text}\n\nGive a 3-4 sentence plain-English take for the investor. Mention whether they're beating the market and any notable risks (e.g. concentration in one stock)."}]

st.title("Portfolio Analyzer")
st.write("Track your stock portfolio and benchmark against the S&P 500")

tickers_input = st.text_input("Enter tickers separated by commas (e.g. AAPL,MSFT,GOOGL)")
shares_input = st.text_input("Enter number of shares for each ticker (same order)")
prices_input = st.text_input("Enter purchase price for each ticker (same order)")

if st.button("Analyze Portfolio"):
    try:
        tickers = [t.strip().upper() for t in tickers_input.split(",")]
        shares_list = [float(s.strip()) for s in shares_input.split(",")]
        prices_list = [float(p.strip()) for p in prices_input.split(",")]

        portfolio_df = pd.DataFrame({
            "ticker": tickers,
            "shares": shares_list,
            "purchase_price": prices_list
        })

        current_prices = []
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            price = stock.history(period="1d")["Close"].iloc[-1]
            current_prices.append(round(price, 2))

        portfolio_df["current_price"] = current_prices
        portfolio_df["current_value"] = portfolio_df["shares"] * portfolio_df["current_price"]
        portfolio_df["cost_basis"] = portfolio_df["shares"] * portfolio_df["purchase_price"]
        portfolio_df["gain_loss"] = portfolio_df["current_value"] - portfolio_df["cost_basis"]
        portfolio_df["return_pct"] = ((portfolio_df["gain_loss"]) / portfolio_df["cost_basis"] * 100).round(2)

        total_value = portfolio_df["current_value"].sum()
        total_cost = portfolio_df["cost_basis"].sum()
        total_return = ((total_value - total_cost) / total_cost * 100).round(2)

        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="1y")
        spy_return = ((spy_hist["Close"].iloc[-1] - spy_hist["Close"].iloc[0]) / spy_hist["Close"].iloc[0] * 100).round(2)

        st.subheader("Portfolio Results")
        st.dataframe(portfolio_df[["ticker", "shares", "current_price", "gain_loss", "return_pct"]])

        st.subheader("Summary")
        st.write(f"Total Invested: ${total_cost:,.2f}")
        st.write(f"Current Value: ${total_value:,.2f}")
        st.write(f"Total Return: {total_return}%")
        st.write(f"S&P 500 Return: {spy_return}%")

        if total_return > spy_return:
            st.success("Your portfolio BEAT the market!")
        else:
            st.warning("Your portfolio UNDERPERFORMED the market")

        st.subheader("Gain/Loss by Stock")
        st.bar_chart(portfolio_df.set_index("ticker")["gain_loss"])
        st.subheader("AI Insights")
                if st.button("Get AI Insights"):
                    with st.spinner("Analyzing your portfolio..."):
                        summary_text = f"""
                        Total Invested: ${total_cost:,.2f}
                        Current Value: ${total_value:,.2f}
                        Total Return: {total_return}%
                        S&P 500 Return: {spy_return}%
                        Holdings: {portfolio_df[['ticker', 'return_pct']].to_string(index=False)}
                        """
                        insights = get_ai_insights(summary_text)
                        st.write(insights)

    except Exception as e:
        st.error(f"Error: {e}")
