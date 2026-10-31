import numpy as np
import pandas as pd
import yfinance as yf

def load_stock_data(ticker, period="2y", interval="1d"):
    symbol=ticker.strip().upper()
    if not symbol:
        raise ValueError("Enter a ticker symbol.")
    data=yf.download(symbol,period=period,interval=interval,auto_adjust=True,progress=False,threads=False)
    if data is None or data.empty:
        return pd.DataFrame()
    if isinstance(data.columns,pd.MultiIndex):
        data.columns=data.columns.get_level_values(0)
    required=["Open","High","Low","Close","Volume"]
    missing=[c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing downloaded columns: "+", ".join(missing))
    data=data[required].copy()
    data=data[~data.index.duplicated(keep="last")].sort_index()
    for col in required:
        data[col]=pd.to_numeric(data[col],errors="coerce")
    data=data.dropna(subset=["Open","High","Low","Close"])
    data["Volume"]=data["Volume"].fillna(0)
    return data

def add_indicators(data):
    df=data.copy()
    close=df["Close"]
    df["Daily_Return"]=close.pct_change()*100
    for window in (20,50,100,200):
        df[f"SMA_{window}"]=close.rolling(window).mean()
    delta=close.diff()
    gain=delta.clip(lower=0)
    loss=-delta.clip(upper=0)
    avg_gain=gain.ewm(alpha=1/14,min_periods=14,adjust=False).mean()
    avg_loss=loss.ewm(alpha=1/14,min_periods=14,adjust=False).mean()
    rs=avg_gain/avg_loss.replace(0,np.nan)
    df["RSI_14"]=100-(100/(1+rs))
    ema12=close.ewm(span=12,adjust=False).mean()
    ema26=close.ewm(span=26,adjust=False).mean()
    df["MACD"]=ema12-ema26
    df["MACD_signal"]=df["MACD"].ewm(span=9,adjust=False).mean()
    sma=close.rolling(20).mean()
    std=close.rolling(20).std()
    df["BB_upper"]=sma+2*std
    df["BB_lower"]=sma-2*std
    return df

def calculate_metrics(df):
    close=df["Close"].dropna()
    returns=df["Daily_Return"].dropna()
    if close.empty:
        raise ValueError("No valid closing prices.")
    first,last=float(close.iloc[0]),float(close.iloc[-1])
    vol=float(returns.std()*np.sqrt(252)) if len(returns)>1 else 0.0
    drawdown=(close/close.cummax()-1)*100
    return {
        "latest_close":last,
        "daily_change":float(returns.iloc[-1]) if len(returns) else 0.0,
        "period_return":((last/first)-1)*100 if first else 0.0,
        "period_high":float(df.High.max()),
        "period_low":float(df.Low.min()),
        "annual_volatility":vol,
        "max_drawdown":float(drawdown.min()) if len(drawdown) else 0.0
    }

def compare_stocks(symbols,period="2y",interval="1d"):
    series={}
    for symbol in symbols:
        try:
            data=load_stock_data(symbol,period,interval)
            close=data["Close"].dropna()
            if len(close):
                series[symbol]=close/close.iloc[0]*100
        except Exception:
            continue
    return pd.concat(series,axis=1).sort_index() if series else pd.DataFrame()
