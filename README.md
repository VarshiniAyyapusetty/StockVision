# StockVision – Stock Market Data Analytics & Insights

An interactive educational dashboard for exploring historical stock prices, technical indicators, returns, volatility and relative performance.

## Features
- Historical OHLCV data through Yahoo Finance
- Interactive candlestick and volume charts
- 20, 50, 100 and 200-period moving averages
- RSI, MACD and Bollinger Bands
- Daily returns, cumulative price return and maximum drawdown
- Normalized comparison of up to six tickers
- Downloadable processed CSV
- Streamlit dashboard with dark financial-terminal styling

## Stack
Python, Streamlit, Pandas, NumPy, Plotly and yfinance.

## Structure
```text
StockVision/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   └── market_data.py
├── data/
└── notebooks/
```

## Run locally
Python 3.10+ is recommended.
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Example symbols
Indian equities: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `SBIN.NS`.
US equities: `AAPL`, `MSFT`, `NVDA`, `AMZN`.

## Methodology
- Uses `yfinance` with `auto_adjust=True`; prices reflect the provider's adjusted-price behavior.
- Daily returns are percentage changes in adjusted closing prices.
- Moving averages are rolling means of closing prices.
- RSI uses 14-period exponentially smoothed average gains and losses.
- MACD uses 12- and 26-period EMAs; the signal line is a 9-period EMA.
- Bollinger Bands use a 20-period moving average plus/minus two rolling standard deviations.
- Annualized volatility is the standard deviation of daily returns multiplied by square root of 252.
- Maximum drawdown is the largest peak-to-trough decline in the selected closing-price series.
- Comparison rebases each ticker to 100 at its first available observation. It excludes dividends and transaction costs.

## Data source and limitations
Data is retrieved at runtime from Yahoo Finance using the third-party `yfinance` library. `yfinance` is not an official Yahoo Finance product or a guaranteed data feed. Data availability, adjustments, ticker coverage, rate limits and historical depth may vary. Internet access is required.

## Disclaimer
For educational and informational use only. Technical indicators are descriptive and are not guaranteed trading signals. Nothing in this project is investment, trading, tax or financial advice.

## Deploy
Push the repository to GitHub, then create a Streamlit Community Cloud app using branch `main` and main file `app.py`. Dependencies are installed from `requirements.txt`.
