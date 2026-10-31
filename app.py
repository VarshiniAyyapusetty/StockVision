import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.market_data import load_stock_data, add_indicators, calculate_metrics, compare_stocks

st.set_page_config(page_title="StockVision | Market Analytics", page_icon="📈", layout="wide")
st.markdown("""
<style>
.stApp{background:#0b1118;color:#e8eef5}
[data-testid="stSidebar"]{background:#111c27}
.block-container{padding-top:1.5rem}
div[data-testid="stMetric"]{background:linear-gradient(135deg,#142332,#101923);border:1px solid #263b4d;padding:14px;border-radius:12px}
h1,h2,h3{color:#f2f6fa}
</style>""", unsafe_allow_html=True)

st.sidebar.markdown("# 📈 StockVision")
st.sidebar.caption("Stock Market Data Analytics & Insights")
ticker = st.sidebar.text_input("Stock ticker", "RELIANCE.NS").strip().upper()
period = st.sidebar.selectbox("Historical period", ["6mo","1y","2y","5y","10y","max"], index=2)
interval = st.sidebar.selectbox("Interval", ["1d","1wk","1mo"])
compare_input = st.sidebar.text_input("Compare tickers (comma-separated)", "TCS.NS, INFY.NS")
if st.sidebar.button("Refresh analysis", type="primary"):
    st.cache_data.clear()

@st.cache_data(ttl=900, show_spinner=False)
def get_data(symbol, period, interval):
    return load_stock_data(symbol, period, interval)

st.markdown("**HISTORICAL MARKET RESEARCH · DATA-DRIVEN INSIGHTS**")
st.title("StockVision")
st.subheader("Understand price action. Explore performance. Measure risk.")
st.caption("Educational analytics using historical data. Not investment advice.")

try:
    with st.spinner(f"Loading {ticker} historical data..."):
        raw = get_data(ticker, period, interval)
    if raw.empty:
        st.error("No data returned. Check the ticker symbol or try another period.")
        st.stop()
    df = add_indicators(raw)
    metrics = calculate_metrics(df)
except Exception as exc:
    st.error(f"Unable to load market data: {exc}")
    st.info("Check the ticker and internet connection. Yahoo Finance access may be temporarily unavailable.")
    st.stop()

st.markdown(f"## {ticker}")
st.caption(f"{len(df):,} observations · {df.index.min().date()} to {df.index.max().date()} · {interval}")
cols = st.columns(5)
cols[0].metric("Latest close", f"{metrics['latest_close']:,.2f}", f"{metrics['daily_change']:+.2f}%")
cols[1].metric("Period return", f"{metrics['period_return']:+.2f}%")
cols[2].metric("Period high", f"{metrics['period_high']:,.2f}")
cols[3].metric("Period low", f"{metrics['period_low']:,.2f}")
cols[4].metric("Annualized volatility", f"{metrics['annual_volatility']:.2f}%")

overview, technical, risk, comparison, explorer = st.tabs(
    ["Overview", "Technical Analysis", "Returns & Risk", "Stock Comparison", "Data Explorer"])

with overview:
    c1, c2 = st.columns([2,1])
    with c1:
        fig = go.Figure(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close,
            increasing_line_color="#35d49a", decreasing_line_color="#ff657a"))
        fig.update_layout(title="Historical price movement", template="plotly_dark", height=460,
            xaxis_rangeslider_visible=False, paper_bgcolor="#0b1118", plot_bgcolor="#0b1118")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(df, x=df.index, y="Volume", title="Trading volume")
        fig.update_layout(template="plotly_dark", height=460, paper_bgcolor="#0b1118", plot_bgcolor="#0b1118")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Price summary")
    st.dataframe(df[["Open","High","Low","Close","Volume"]].describe().T, use_container_width=True)

with technical:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index,y=df.Close,name="Close",line=dict(color="#e8eef5")))
    for col,color in [("SMA_20","#f5b942"),("SMA_50","#42c6d9"),("SMA_200","#bb8cff")]:
        fig.add_trace(go.Scatter(x=df.index,y=df[col],name=col.replace("_"," "),line=dict(color=color)))
    fig.update_layout(title="Moving averages",template="plotly_dark",height=420,paper_bgcolor="#0b1118",plot_bgcolor="#0b1118")
    st.plotly_chart(fig,use_container_width=True)
    a,b=st.columns(2)
    with a:
        f=px.line(df,x=df.index,y="RSI_14",title="Relative Strength Index (14)")
        f.add_hline(y=70,line_dash="dash",line_color="#ff657a")
        f.add_hline(y=30,line_dash="dash",line_color="#35d49a")
        f.update_layout(template="plotly_dark",paper_bgcolor="#0b1118",plot_bgcolor="#0b1118")
        st.plotly_chart(f,use_container_width=True)
    with b:
        f=go.Figure()
        f.add_trace(go.Scatter(x=df.index,y=df.MACD,name="MACD"))
        f.add_trace(go.Scatter(x=df.index,y=df.MACD_signal,name="Signal"))
        f.update_layout(title="MACD (12, 26, 9)",template="plotly_dark",paper_bgcolor="#0b1118",plot_bgcolor="#0b1118")
        st.plotly_chart(f,use_container_width=True)
    f=go.Figure()
    f.add_trace(go.Scatter(x=df.index,y=df.BB_upper,name="Upper band",line=dict(dash="dot")))
    f.add_trace(go.Scatter(x=df.index,y=df.BB_lower,name="Lower band",line=dict(dash="dot"),fill="tonexty"))
    f.add_trace(go.Scatter(x=df.index,y=df.Close,name="Close"))
    f.update_layout(title="Bollinger Bands (20, 2)",template="plotly_dark",height=350,paper_bgcolor="#0b1118",plot_bgcolor="#0b1118")
    st.plotly_chart(f,use_container_width=True)
    st.caption("Indicators describe historical price behavior; they are not guaranteed trading signals.")

with risk:
    returns=df.Daily_Return.dropna()
    f=px.histogram(returns,nbins=50,title="Daily return distribution (%)")
    f.update_layout(template="plotly_dark",paper_bgcolor="#0b1118",plot_bgcolor="#0b1118")
    st.plotly_chart(f,use_container_width=True)
    cumulative=(1+df.Daily_Return.fillna(0)/100).cumprod()
    f=px.line(x=df.index,y=(cumulative-1)*100,labels={"x":"Date","y":"Cumulative return (%)"},title="Cumulative price return")
    f.update_layout(template="plotly_dark",paper_bgcolor="#0b1118",plot_bgcolor="#0b1118")
    st.plotly_chart(f,use_container_width=True)
    x=st.columns(3)
    x[0].metric("Best daily return",f"{returns.max():+.2f}%")
    x[1].metric("Worst daily return",f"{returns.min():+.2f}%")
    x[2].metric("Maximum drawdown",f"{metrics['max_drawdown']:.2f}%")

with comparison:
    symbols=list(dict.fromkeys([ticker]+[s.strip().upper() for s in compare_input.split(",") if s.strip()]))[:6]
    comp=compare_stocks(symbols,period,interval)
    if comp.empty:
        st.warning("No comparison data available for these symbols.")
    else:
        f=px.line(comp,x=comp.index,y=comp.columns,title="Relative performance (first available close = 100)")
        f.update_layout(template="plotly_dark",height=440,yaxis_title="Indexed price",paper_bgcolor="#0b1118",plot_bgcolor="#0b1118")
        st.plotly_chart(f,use_container_width=True)
        st.caption("This compares price movement only; dividends and transaction costs are excluded.")

with explorer:
    st.dataframe(df.sort_index(ascending=False),use_container_width=True,height=440)
    st.download_button("Download processed data (CSV)",df.to_csv().encode("utf-8"),
        file_name=f"{ticker.replace('.','_')}_stockvision.csv",mime="text/csv")

st.divider()
st.markdown("**StockVision** · Python · Pandas · Plotly · Streamlit")
st.caption("Data retrieved from Yahoo Finance through yfinance. Availability and historical coverage may vary. For educational use only; not financial advice.")
