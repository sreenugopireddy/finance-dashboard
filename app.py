import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# -------------------------
# UI: Title and Sidebar
# -------------------------
st.set_page_config(page_title="📈 Financial Dashboard", layout="wide")
st.title("📈 Real-Time Financial Dashboard")
st.subheader("Live Stock Prices, Technical Indicators, and Volatility Analysis")

st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.info("Select the ticker, interval, and duration to visualize real-time data with technical indicators like RSI and MACD.")
ticker = st.sidebar.text_input("Ticker Symbol", "AAPL")
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d"], index=2)
duration = st.sidebar.selectbox("Duration", ["1d", "5d", "1mo", "3mo"], index=1)

# -------------------------
# Data Fetching
# -------------------------
data = yf.download(ticker, period=duration, interval=interval)

if data.empty:
    st.warning("⚠️ No data available for the selected configuration. Try changing the interval or duration.")
else:
    st.success(f"✅ Data fetched successfully: {data.shape[0]} rows.")

    # -------------------------
    # Technical Indicators
    # -------------------------
    data['RSI'] = data['Close'].rolling(window=14).apply(lambda x: 100 - (100 / (1 + (x.diff().clip(lower=0).sum() / abs(x.diff().clip(upper=0).sum()))) if abs(x.diff().clip(upper=0).sum()) != 0 else 0))
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # -------------------------
    # Layout Columns
    # -------------------------
    col1, col2 = st.columns(2)

    # Price Chart with EMAs
    with col1:
        st.markdown("### 📈 Price Chart with EMAs")
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
        fig_price.add_trace(go.Scatter(x=data.index, y=data['EMA12'], mode='lines', name='EMA12'))
        fig_price.add_trace(go.Scatter(x=data.index, y=data['EMA26'], mode='lines', name='EMA26'))
        fig_price.update_layout(height=400)
        st.plotly_chart(fig_price, use_container_width=True)

    # RSI Chart
    with col2:
        st.markdown("### 📊 RSI Indicator")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='orange')))
        fig_rsi.add_hline(y=70, line_dash='dash', line_color='red')
        fig_rsi.add_hline(y=30, line_dash='dash', line_color='green')
        fig_rsi.update_layout(height=400, yaxis_title='RSI')
        st.plotly_chart(fig_rsi, use_container_width=True)

    # MACD Chart
    st.markdown("### 📊 MACD Indicator")
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
    fig_macd.add_trace(go.Scatter(x=data.index, y=data['Signal'], mode='lines', name='Signal Line', line=dict(color='red')))
    fig_macd.add_trace(go.Bar(x=data.index, y=(data['MACD'] - data['Signal']), name='Histogram', marker_color='gray'))
    fig_macd.update_layout(height=400)
    st.plotly_chart(fig_macd, use_container_width=True)

    # Display Data Table
    with st.expander("📄 View Raw Data"):
        st.dataframe(data.tail(50))

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.markdown("Built with ❤️ by [Your Name](https://github.com/yourgithub) for portfolio showcase.")
