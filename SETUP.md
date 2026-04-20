# ⚡ APEX SCALPER — Setup & Deployment Guide

## Local Setup (2 minutes)

```bash
# 1. Create folder
mkdir apex-scalper && cd apex-scalper

# 2. Copy app.py, requirements.txt, sample_data.csv here

# 3. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run
streamlit run app.py
```

App opens at: http://localhost:8501

---

## Deploy on Render (Free, 5 minutes)

1. Push your files to GitHub:
   - app.py
   - requirements.txt
   - render.yaml (optional)

2. Go to https://render.com → New → Web Service

3. Connect your GitHub repo

4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - **Instance Type**: Free

5. Click Deploy → Done! ✅

---

## Deploy on Streamlit Cloud (Easiest, Free)

1. Push to GitHub (public repo)
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select repo → branch → app.py
5. Click Deploy → Live in 2 minutes ✅

---

## CSV Format

Your CSV must have these exact columns:

```
datetime,open,high,low,close,volume
2024-01-01 00:00:00,42000.0,42500.0,41800.0,42300.0,1250.5
```

Use `sample_data.csv` as a template.

---

## Features

| Feature | Details |
|---------|---------|
| Live Data | Binance API, 6 pairs, 5 timeframes |
| Signal Engine | EMA9/21/50 + RSI + MACD + Bollinger + Stochastic |
| Trade Levels | Entry, TP1, TP2, SL based on ATR |
| Auto Refresh | Every 30 seconds |
| CSV Upload | Any OHLCV data |
| Backtest | Equity curve, win rate, drawdown |

---

## Disclaimer

This tool is for educational and informational purposes only.
Not financial advice. Always manage your risk.
