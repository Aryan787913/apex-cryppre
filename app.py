import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="APEX SCALPER — Pro Trading Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Premium Dark CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:        #050811;
    --bg2:       #090f1e;
    --card:      #0d1526;
    --border:    #1a2a4a;
    --accent:    #0af;
    --accent2:   #0ff;
    --green:     #00e676;
    --red:       #ff1744;
    --yellow:    #ffd600;
    --muted:     #4a6080;
    --text:      #c8d8f0;
    --text-dim:  #6888aa;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

/* ── Top Header Bar ── */
.apex-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 1.5rem; margin-bottom: 1.5rem;
    background: linear-gradient(90deg, #0d1526 0%, #050f2a 100%);
    border: 1px solid var(--border); border-radius: 12px;
    box-shadow: 0 0 30px rgba(0,170,255,0.08);
}
.apex-logo { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800;
    background: linear-gradient(90deg, #0af, #0ff); -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; letter-spacing: 2px; }
.apex-sub { font-size: 0.7rem; color: var(--text-dim); letter-spacing: 3px;
    text-transform: uppercase; margin-top: 2px; }
.live-dot { display: inline-block; width: 8px; height: 8px; background: var(--green);
    border-radius: 50%; margin-right: 6px;
    box-shadow: 0 0 8px var(--green);
    animation: pulse-dot 1.5s infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.3)} }
.live-badge { font-size: 0.75rem; color: var(--green); font-family: 'Space Mono', monospace; }
.clock { font-family: 'Space Mono', monospace; font-size: 0.85rem; color: var(--accent); }

/* ── Signal Card (BIG) ── */
.signal-card {
    padding: 1.8rem; border-radius: 14px;
    background: var(--card);
    border: 1px solid var(--border);
    position: relative; overflow: hidden;
    box-shadow: 0 4px 30px rgba(0,0,0,0.4);
}
.signal-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.signal-buy::before   { background: linear-gradient(90deg, #00e676, #00c853); }
.signal-sell::before  { background: linear-gradient(90deg, #ff1744, #d50000); }
.signal-hold::before  { background: linear-gradient(90deg, #ffd600, #ff8f00); }

.signal-label { font-size: 3rem; font-weight: 800; letter-spacing: 4px; margin: 0; }
.signal-buy  .signal-label { color: var(--green); text-shadow: 0 0 20px rgba(0,230,118,0.4); }
.signal-sell .signal-label { color: var(--red);   text-shadow: 0 0 20px rgba(255,23,68,0.4); }
.signal-hold .signal-label { color: var(--yellow);text-shadow: 0 0 20px rgba(255,214,0,0.4); }

.conf-badge {
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; margin-top: 8px;
}
.conf-high   { background: rgba(0,230,118,0.15); color: var(--green); border: 1px solid rgba(0,230,118,0.3); }
.conf-medium { background: rgba(255,214,0,0.15);  color: var(--yellow); border: 1px solid rgba(255,214,0,0.3); }
.conf-low    { background: rgba(255,23,68,0.15);  color: var(--red);    border: 1px solid rgba(255,23,68,0.3); }

/* ── Metric Card ── */
.metric-card {
    padding: 1.2rem 1.4rem; border-radius: 12px;
    background: var(--card); border: 1px solid var(--border);
    text-align: center; height: 100%;
}
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.6rem;
    font-weight: 700; margin: 4px 0; }
.metric-label { font-size: 0.65rem; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 2px; }
.metric-green { color: var(--green); }
.metric-red   { color: var(--red); }
.metric-blue  { color: var(--accent); }
.metric-white { color: #fff; }

/* ── Level Card (TP/SL/Entry) ── */
.level-card {
    padding: 1rem 1.2rem; border-radius: 10px;
    background: var(--card); border: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 8px;
}
.level-tag { font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 2px; color: var(--text-dim); }
.level-val { font-family: 'Space Mono', monospace; font-size: 1.1rem; font-weight: 700; }

/* ── Reason Box ── */
.reason-box {
    padding: 1rem 1.4rem; border-radius: 10px;
    background: rgba(0,170,255,0.05);
    border: 1px solid rgba(0,170,255,0.2);
    font-size: 0.85rem; color: var(--text); line-height: 1.6;
    margin-top: 8px;
}
.reason-icon { color: var(--accent); margin-right: 6px; }

/* ── Section Title ── */
.section-title {
    font-size: 0.65rem; text-transform: uppercase; letter-spacing: 3px;
    color: var(--text-dim); margin-bottom: 10px;
    padding-bottom: 6px; border-bottom: 1px solid var(--border);
}

/* ── Table ── */
.dataframe { background: var(--card) !important; color: var(--text) !important; }

/* ── Scrolling ticker ── */
.ticker-bar {
    background: var(--bg2); border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 6px 0; margin-bottom: 1.5rem;
    overflow: hidden; white-space: nowrap;
}
.ticker-inner { display: inline-flex; gap: 3rem;
    animation: scroll-ticker 30s linear infinite; }
@keyframes scroll-ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.ticker-item { font-family: 'Space Mono', monospace; font-size: 0.75rem; }

/* ── Upload area ── */
.uploadedFile { background: var(--card) !important; border: 1px dashed var(--border) !important; }

/* Override Streamlit inputs */
.stSelectbox > div > div, .stSlider { background: var(--card) !important; }
.stButton > button {
    background: linear-gradient(135deg, #0af, #006688) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 1px !important; padding: 0.5rem 1.5rem !important;
    box-shadow: 0 4px 15px rgba(0,170,255,0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,170,255,0.5) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important; border-radius: 10px !important;
    padding: 4px !important; gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-dim) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important; border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important; color: var(--accent) !important;
    border: 1px solid var(--border) !important;
}

/* Plotly transparent */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ─── Constants ─────────────────────────────────────────────────────────────────
BINANCE_BASE = "https://api.binance.com/api/v3"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
INTERVALS = {"1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "1h": "1h"}


# ─── Data Fetching ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_klines(symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
    try:
        url = f"{BINANCE_BASE}/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","quote_vol","trades","taker_buy_base",
            "taker_buy_quote","ignore"
        ])
        for col in ["open","high","low","close","volume"]:
            df[col] = df[col].astype(float)
        df["datetime"] = pd.to_datetime(df["open_time"], unit="ms")
        return df[["datetime","open","high","low","close","volume"]].reset_index(drop=True)
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=10)
def fetch_ticker(symbol: str) -> dict:
    try:
        r = requests.get(f"{BINANCE_BASE}/ticker/24hr", params={"symbol": symbol}, timeout=5)
        return r.json()
    except:
        return {}


# ─── Indicators ────────────────────────────────────────────────────────────────
def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["close"]

    # EMAs
    df["ema9"]  = c.ewm(span=9,  adjust=False).mean()
    df["ema21"] = c.ewm(span=21, adjust=False).mean()
    df["ema50"] = c.ewm(span=50, adjust=False).mean()

    # RSI
    delta = c.diff()
    gain  = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - 100 / (1 + rs)

    # MACD
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["macd"]        = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # Bollinger Bands
    sma20          = c.rolling(20).mean()
    std20          = c.rolling(20).std()
    df["bb_upper"] = sma20 + 2 * std20
    df["bb_lower"] = sma20 - 2 * std20
    df["bb_mid"]   = sma20

    # ATR
    hl  = df["high"] - df["low"]
    hpc = (df["high"] - c.shift()).abs()
    lpc = (df["low"]  - c.shift()).abs()
    tr  = pd.concat([hl, hpc, lpc], axis=1).max(axis=1)
    df["atr"] = tr.ewm(span=14, adjust=False).mean()

    # Stochastic
    low14  = df["low"].rolling(14).min()
    high14 = df["high"].rolling(14).max()
    df["stoch_k"] = 100 * (c - low14) / (high14 - low14).replace(0, np.nan)
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    # Volume MA
    df["vol_ma"] = df["volume"].rolling(20).mean()

    # Candle patterns (simple)
    df["body"]    = (df["close"] - df["open"]).abs()
    df["upper_w"] = df["high"] - df[["open","close"]].max(axis=1)
    df["lower_w"] = df[["open","close"]].min(axis=1) - df["low"]

    return df


def generate_signal(df: pd.DataFrame) -> dict:
    """Generate scalping signal from latest candle data."""
    if df.empty or len(df) < 55:
        return {"signal": "HOLD", "confidence": "Low", "reason": "Insufficient data",
                "entry": 0, "tp1": 0, "tp2": 0, "sl": 0, "rr": 0, "score": 0}

    row  = df.iloc[-1]
    prev = df.iloc[-2]

    price   = row["close"]
    atr     = row["atr"] if row["atr"] > 0 else price * 0.001
    score   = 0
    reasons = []

    # ── Trend (EMAs) ──
    if row["ema9"] > row["ema21"] > row["ema50"]:
        score += 2
        reasons.append("EMA stack bullish (9>21>50)")
    elif row["ema9"] < row["ema21"] < row["ema50"]:
        score -= 2
        reasons.append("EMA stack bearish (9<21<50)")
    elif row["ema9"] > row["ema21"]:
        score += 1
        reasons.append("Short EMA above mid EMA")
    elif row["ema9"] < row["ema21"]:
        score -= 1
        reasons.append("Short EMA below mid EMA")

    # EMA cross
    if prev["ema9"] <= prev["ema21"] and row["ema9"] > row["ema21"]:
        score += 2
        reasons.append("⚡ Bullish EMA9/21 crossover (fresh)")
    elif prev["ema9"] >= prev["ema21"] and row["ema9"] < row["ema21"]:
        score -= 2
        reasons.append("⚡ Bearish EMA9/21 crossover (fresh)")

    # ── RSI ──
    rsi = row["rsi"]
    if 45 < rsi < 65:
        score += 1
        reasons.append(f"RSI at {rsi:.0f} (bullish momentum zone)")
    elif rsi < 30:
        score += 2
        reasons.append(f"RSI oversold at {rsi:.0f} (reversal likely)")
    elif rsi > 70:
        score -= 2
        reasons.append(f"RSI overbought at {rsi:.0f} (exhaustion risk)")
    elif 35 < rsi < 45:
        score -= 1
        reasons.append(f"RSI at {rsi:.0f} (bearish pressure)")

    # ── MACD ──
    if row["macd_hist"] > 0 and prev["macd_hist"] < 0:
        score += 2
        reasons.append("MACD histogram turned positive (momentum shift ↑)")
    elif row["macd_hist"] < 0 and prev["macd_hist"] > 0:
        score -= 2
        reasons.append("MACD histogram turned negative (momentum shift ↓)")
    elif row["macd"] > row["macd_signal"]:
        score += 1
        reasons.append(f"MACD above signal line (+{row['macd_hist']:.2f})")
    elif row["macd"] < row["macd_signal"]:
        score -= 1
        reasons.append(f"MACD below signal line ({row['macd_hist']:.2f})")

    # ── Bollinger Bands ──
    if price < row["bb_lower"] * 1.002:
        score += 2
        reasons.append("Price at/below lower Bollinger Band (oversold bounce)")
    elif price > row["bb_upper"] * 0.998:
        score -= 2
        reasons.append("Price at/above upper Bollinger Band (overbought)")
    elif price > row["bb_mid"]:
        score += 0.5
        reasons.append(f"Price above BB midline ({row['bb_mid']:.2f})")

    # ── Volume confirmation ──
    if row["volume"] > row["vol_ma"] * 1.5:
        if score > 0:
            score += 1
            reasons.append(f"Volume surge {row['volume']/row['vol_ma']:.1f}x avg (confirms move)")
        else:
            reasons.append(f"High volume ({row['volume']/row['vol_ma']:.1f}x avg)")

    # ── Stochastic ──
    sk, sd = row["stoch_k"], row["stoch_d"]
    if sk < 20 and sd < 20:
        score += 1
        reasons.append(f"Stoch oversold (K:{sk:.0f}, D:{sd:.0f})")
    elif sk > 80 and sd > 80:
        score -= 1
        reasons.append(f"Stoch overbought (K:{sk:.0f}, D:{sd:.0f})")

    # ── Determine signal ──
    if   score >= 5:  signal, conf = "BUY",  "High"
    elif score >= 3:  signal, conf = "BUY",  "Medium"
    elif score >= 1:  signal, conf = "BUY",  "Low"
    elif score <= -5: signal, conf = "SELL", "High"
    elif score <= -3: signal, conf = "SELL", "Medium"
    elif score <= -1: signal, conf = "SELL", "Low"
    else:             signal, conf = "HOLD", "Medium"

    # ── TP / SL levels ──
    multiplier = {"High": 2.5, "Medium": 2.0, "Low": 1.5}[conf]
    if signal == "BUY":
        entry = price
        sl    = price - atr * 1.5
        tp1   = price + atr * multiplier
        tp2   = price + atr * multiplier * 1.8
    elif signal == "SELL":
        entry = price
        sl    = price + atr * 1.5
        tp1   = price - atr * multiplier
        tp2   = price - atr * multiplier * 1.8
    else:
        entry = price
        sl    = price - atr
        tp1   = price + atr
        tp2   = price + atr * 1.5

    rr = abs(tp1 - entry) / max(abs(sl - entry), 0.0001)

    return {
        "signal":     signal,
        "confidence": conf,
        "score":      score,
        "reason":     " · ".join(reasons[:5]) if reasons else "Mixed signals",
        "entry":      entry,
        "tp1":        tp1,
        "tp2":        tp2,
        "sl":         sl,
        "rr":         rr,
        "rsi":        rsi,
        "atr":        atr,
    }


# ─── Backtest ───────────────────────────────────────────────────────────────────
def run_backtest(df: pd.DataFrame) -> dict:
    df = compute_indicators(df)
    trades, equity = [], [1.0]
    pos = None
    for i in range(55, len(df)):
        sub = df.iloc[:i+1]
        sig = generate_signal(sub)

        if sig["signal"] == "BUY" and pos is None:
            pos = {"entry": sub.iloc[-1]["close"], "type": "BUY", "idx": i}

        elif sig["signal"] == "SELL" and pos is not None and pos["type"] == "BUY":
            exit_p = sub.iloc[-1]["close"]
            ret    = (exit_p - pos["entry"]) / pos["entry"]
            equity.append(equity[-1] * (1 + ret))
            trades.append({"entry": pos["entry"], "exit": exit_p, "return": ret, "win": ret > 0})
            pos = None

    if not trades:
        return {"total": 0, "wins": 0, "win_rate": 0,
                "profit_pct": 0, "max_dd": 0, "equity": [1.0]}

    total    = len(trades)
    wins     = sum(1 for t in trades if t["win"])
    win_rate = wins / total * 100
    profit   = (equity[-1] - 1) * 100

    # Max drawdown
    eq   = np.array(equity)
    peak = np.maximum.accumulate(eq)
    dd   = (peak - eq) / peak
    max_dd = float(dd.max() * 100)

    return {
        "total":      total,
        "wins":       wins,
        "win_rate":   win_rate,
        "profit_pct": profit,
        "max_dd":     max_dd,
        "equity":     equity,
        "trades":     trades,
    }


# ─── Chart ──────────────────────────────────────────────────────────────────────
def build_chart(df: pd.DataFrame, sig: dict, symbol: str) -> go.Figure:
    tail = df.tail(80)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.58, 0.22, 0.20],
        vertical_spacing=0.04
    )

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=tail["datetime"], open=tail["open"], high=tail["high"],
        low=tail["low"], close=tail["close"], name="Price",
        increasing_fillcolor="#00e676", increasing_line_color="#00e676",
        decreasing_fillcolor="#ff1744", decreasing_line_color="#ff1744",
    ), row=1, col=1)

    # EMAs
    for ema, color, width in [("ema9","#0af",1.5),("ema21","#ff9800",1.2),("ema50","#e040fb",1)]:
        if ema in tail:
            fig.add_trace(go.Scatter(
                x=tail["datetime"], y=tail[ema], name=ema.upper(),
                line=dict(color=color, width=width), opacity=0.9
            ), row=1, col=1)

    # BB
    for bb, clr, fill in [("bb_upper","rgba(0,170,255,0.3)",None),
                           ("bb_lower","rgba(0,170,255,0.3)","tonexty")]:
        if bb in tail:
            fig.add_trace(go.Scatter(
                x=tail["datetime"], y=tail[bb], name=bb,
                line=dict(color=clr, width=1, dash="dot"),
                fill=fill, fillcolor="rgba(0,170,255,0.04)",
                showlegend=False
            ), row=1, col=1)

    # Signal lines
    price = sig["entry"]
    for lvl, clr, dash, name in [
        (sig["tp1"], "#00e676", "dash", f"TP1 {sig['tp1']:.2f}"),
        (sig["tp2"], "#69f0ae", "dot",  f"TP2 {sig['tp2']:.2f}"),
        (sig["sl"],  "#ff1744", "dash", f"SL  {sig['sl']:.2f}"),
    ]:
        fig.add_hline(y=lvl, line_color=clr, line_dash=dash,
                      line_width=1.2, opacity=0.8, row=1, col=1,
                      annotation_text=name, annotation_font_color=clr,
                      annotation_font_size=10)

    # Volume
    colors = ["#00e676" if c >= o else "#ff1744"
              for c, o in zip(tail["close"], tail["open"])]
    fig.add_trace(go.Bar(
        x=tail["datetime"], y=tail["volume"], name="Volume",
        marker_color=colors, opacity=0.7, showlegend=False
    ), row=2, col=1)
    if "vol_ma" in tail:
        fig.add_trace(go.Scatter(
            x=tail["datetime"], y=tail["vol_ma"], name="Vol MA",
            line=dict(color="#ffd600", width=1.5), showlegend=False
        ), row=2, col=1)

    # RSI
    if "rsi" in tail:
        fig.add_trace(go.Scatter(
            x=tail["datetime"], y=tail["rsi"], name="RSI",
            line=dict(color="#e040fb", width=1.5), showlegend=False
        ), row=3, col=1)
        for lvl, clr in [(70,"#ff1744"),(50,"#4a6080"),(30,"#00e676")]:
            fig.add_hline(y=lvl, line_color=clr, line_dash="dot",
                          line_width=1, opacity=0.5, row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#090f1e",
        font=dict(family="Space Mono", color="#c8d8f0", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="left", x=0, bgcolor="rgba(0,0,0,0)",
                    font=dict(size=10)),
        margin=dict(l=10, r=10, t=10, b=10),
        height=560,
    )
    for i in range(1, 4):
        fig.update_xaxes(
            gridcolor="#1a2a4a", zeroline=False,
            showspikes=True, spikecolor="#0af", spikethickness=1,
            row=i, col=1
        )
        fig.update_yaxes(
            gridcolor="#1a2a4a", zeroline=False,
            showspikes=True, spikecolor="#0af", spikethickness=1,
            row=i, col=1
        )

    return fig


def equity_chart(equity_curve: list) -> go.Figure:
    x = list(range(len(equity_curve)))
    y = [(v - 1) * 100 for v in equity_curve]
    colors = ["#00e676" if v >= 0 else "#ff1744" for v in y]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines",
        line=dict(color="#0af", width=2),
        fill="tozeroy", fillcolor="rgba(0,170,255,0.08)",
        name="Equity %"
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#090f1e",
        font=dict(family="Space Mono", color="#c8d8f0", size=11),
        height=220, margin=dict(l=10, r=10, t=10, b=10),
        yaxis_ticksuffix="%",
        xaxis=dict(gridcolor="#1a2a4a"),
        yaxis=dict(gridcolor="#1a2a4a"),
    )
    return fig


# ─── Helpers ────────────────────────────────────────────────────────────────────
def fmt_price(p: float, sym: str) -> str:
    return f"${p:,.2f}" if "BTC" in sym else f"${p:,.4f}"

def signal_class(s: str) -> str:
    return {"BUY": "signal-buy", "SELL": "signal-sell"}.get(s, "signal-hold")

def conf_class(c: str) -> str:
    return {"High": "conf-high", "Medium": "conf-medium", "Low": "conf-low"}.get(c, "conf-low")

def color_metric(v: float, invert: bool = False) -> str:
    pos = v > 0
    if invert: pos = not pos
    return "metric-green" if pos else "metric-red"


# ─── State ──────────────────────────────────────────────────────────────────────
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True


# ─── HEADER ─────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
<div class="apex-header">
  <div>
    <div class="apex-logo">⚡ APEX SCALPER</div>
    <div class="apex-sub">Leverage · Scalping · Futures · Pro Dashboard</div>
  </div>
  <div style="display:flex;align-items:center;gap:1.5rem">
    <div><span class="live-dot"></span><span class="live-badge">LIVE</span></div>
    <div class="clock" id="clock">{now_str} IST</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Controls Row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
with c1:
    symbol = st.selectbox("Pair", SYMBOLS, index=0, label_visibility="collapsed")
with c2:
    interval = st.selectbox("Timeframe", list(INTERVALS.keys()), index=2, label_visibility="collapsed")
with c3:
    auto = st.toggle("Auto-refresh (30s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto
with c4:
    refresh_btn = st.button("🔄  Refresh Now")

# ─── TABS ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["⚡  Live Scalping Signal", "📂  CSV Analysis", "📊  Backtest Results"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE SIGNALS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    now_ts = time.time()
    should_refresh = (
        refresh_btn or
        (st.session_state.auto_refresh and now_ts - st.session_state.last_refresh > 30)
    )

    with st.spinner("⚡ Fetching tick data & computing signals..."):
        df = fetch_klines(symbol, INTERVALS[interval], limit=200)

    if df.empty:
        st.error("⚠️ Could not fetch data from Binance. Check your connection.")
        st.stop()

    df = compute_indicators(df)
    sig = generate_signal(df)
    ticker = fetch_ticker(symbol)
    st.session_state.last_refresh = now_ts

    # ── Ticker strip ──────────────────────────────────────────────────────────
    price_chg   = float(ticker.get("priceChangePercent", 0))
    last_price  = float(ticker.get("lastPrice", df.iloc[-1]["close"]))
    chg_color   = "#00e676" if price_chg >= 0 else "#ff1744"
    chg_arrow   = "▲" if price_chg >= 0 else "▼"
    vol_24h     = float(ticker.get("volume", 0))
    high_24h    = float(ticker.get("highPrice", 0))
    low_24h     = float(ticker.get("lowPrice", 0))

    ticker_items = " &nbsp;·&nbsp; ".join([
        f'<span class="ticker-item" style="color:#c8d8f0">{symbol}</span>'
        f'<span class="ticker-item" style="color:#fff;font-weight:700"> ${last_price:,.2f}</span>'
        f'<span class="ticker-item" style="color:{chg_color}"> {chg_arrow}{abs(price_chg):.2f}%</span>',
        f'<span class="ticker-item" style="color:#4a6080">24H HIGH</span>'
        f'<span class="ticker-item" style="color:#c8d8f0"> ${high_24h:,.2f}</span>',
        f'<span class="ticker-item" style="color:#4a6080">24H LOW</span>'
        f'<span class="ticker-item" style="color:#c8d8f0"> ${low_24h:,.2f}</span>',
        f'<span class="ticker-item" style="color:#4a6080">VOL</span>'
        f'<span class="ticker-item" style="color:#c8d8f0"> {vol_24h:,.0f}</span>',
        f'<span class="ticker-item" style="color:#4a6080">ATR</span>'
        f'<span class="ticker-item" style="color:#0af"> ${sig["atr"]:.2f}</span>',
    ] * 3)

    st.markdown(f"""
    <div class="ticker-bar">
      <div class="ticker-inner">{ticker_items}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Main Layout ────────────────────────────────────────────────────────────
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        sc = signal_class(sig["signal"])
        cc = conf_class(sig["confidence"])

        # Big signal card
        st.markdown(f"""
        <div class="signal-card {sc}">
          <div class="section-title">SIGNAL</div>
          <div class="signal-label">{sig['signal']}</div>
          <span class="conf-badge {cc}">{sig['confidence']} Confidence</span>
          <div style="margin-top:1rem">
            <div class="reason-box">
              <span class="reason-icon">🧠</span>{sig['reason']}
            </div>
          </div>
          <div style="margin-top:1rem;font-family:'Space Mono',monospace;font-size:0.7rem;color:#4a6080">
            Score: {sig['score']:+d} &nbsp;|&nbsp; RSI: {sig['rsi']:.1f} &nbsp;|&nbsp; ATR: ${sig['atr']:.2f}
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Entry / TP / SL
        st.markdown('<div class="section-title">TRADE LEVELS</div>', unsafe_allow_html=True)

        def lvl_card(tag, val, color):
            st.markdown(f"""
            <div class="level-card">
              <span class="level-tag">{tag}</span>
              <span class="level-val" style="color:{color}">{fmt_price(val, symbol)}</span>
            </div>
            """, unsafe_allow_html=True)

        lvl_card("ENTRY",  sig["entry"], "#fff")
        lvl_card("TP1 🎯", sig["tp1"],   "#00e676")
        lvl_card("TP2 🚀", sig["tp2"],   "#69f0ae")
        lvl_card("SL  🛑", sig["sl"],    "#ff1744")

        rr_col = "#00e676" if sig["rr"] >= 1.5 else "#ffd600"
        st.markdown(f"""
        <div class="metric-card" style="margin-top:8px">
          <div class="metric-label">Risk:Reward</div>
          <div class="metric-value" style="color:{rr_col}">1 : {sig['rr']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">PRICE ACTION + INDICATORS</div>', unsafe_allow_html=True)
        fig = build_chart(df, sig, symbol)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Bottom metrics row ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:1rem">MARKET METRICS</div>', unsafe_allow_html=True)
    row = df.iloc[-1]
    m1, m2, m3, m4, m5, m6 = st.columns(6)

    metrics = [
        ("PRICE",       f"${last_price:,.2f}",     "metric-white"),
        ("24H CHANGE",  f"{price_chg:+.2f}%",      color_metric(price_chg)),
        ("RSI",         f"{row['rsi']:.1f}",        "metric-blue"),
        ("MACD HIST",   f"{row['macd_hist']:.4f}",  color_metric(row['macd_hist'])),
        ("BB WIDTH",    f"{((row['bb_upper']-row['bb_lower'])/row['bb_mid']*100):.2f}%", "metric-blue"),
        ("STOCH K",     f"{row['stoch_k']:.0f}",    "metric-blue"),
    ]
    for col, (lbl, val, clr) in zip([m1,m2,m3,m4,m5,m6], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{lbl}</div>
              <div class="metric-value {clr}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Recent signal history ─────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:1.5rem">RECENT SIGNAL HISTORY (LAST 20 CANDLES)</div>', unsafe_allow_html=True)
    history_rows = []
    for i in range(max(55, len(df)-20), len(df)):
        sub = df.iloc[:i+1]
        s   = generate_signal(sub)
        r   = sub.iloc[-1]
        history_rows.append({
            "Time":       r["datetime"].strftime("%H:%M"),
            "Signal":     s["signal"],
            "Confidence": s["confidence"],
            "Price":      f"${r['close']:,.2f}",
            "RSI":        f"{s['rsi']:.1f}",
            "Score":      f"{s['score']:+d}",
        })
    hist_df = pd.DataFrame(history_rows[::-1])

    def highlight_signal(val):
        if val == "BUY":  return "color: #00e676; font-weight: bold"
        if val == "SELL": return "color: #ff1744; font-weight: bold"
        return "color: #ffd600"

    st.dataframe(
        hist_df.style.applymap(highlight_signal, subset=["Signal"]),
        use_container_width=True, hide_index=True, height=260
    )

    # Auto-refresh
    if st.session_state.auto_refresh:
        time.sleep(0.1)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CSV UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div style="margin-bottom:1rem;padding:1rem 1.4rem;border-radius:10px;
        background:rgba(0,170,255,0.05);border:1px solid rgba(0,170,255,0.2);font-size:0.85rem">
      📋 Upload a CSV with columns: <b>datetime, open, high, low, close, volume</b><br>
      <span style="color:#4a6080">Datetime format: YYYY-MM-DD HH:MM:SS or Unix timestamp</span>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    if uploaded:
        try:
            csv_df = pd.read_csv(uploaded)
            csv_df.columns = csv_df.columns.str.strip().str.lower()
            if "datetime" in csv_df.columns:
                csv_df["datetime"] = pd.to_datetime(csv_df["datetime"])
            elif "timestamp" in csv_df.columns:
                csv_df["datetime"] = pd.to_datetime(csv_df["timestamp"], unit="ms")
            for col in ["open","high","low","close","volume"]:
                csv_df[col] = csv_df[col].astype(float)
            csv_df = csv_df[["datetime","open","high","low","close","volume"]].dropna()

            st.success(f"✅ Loaded {len(csv_df)} rows · {csv_df['datetime'].min()} → {csv_df['datetime'].max()}")

            csv_df = compute_indicators(csv_df)
            csv_sig = generate_signal(csv_df)

            cl, cr = st.columns([1, 2.4], gap="large")
            with cl:
                sc = signal_class(csv_sig["signal"])
                cc = conf_class(csv_sig["confidence"])
                st.markdown(f"""
                <div class="signal-card {sc}">
                  <div class="section-title">LATEST SIGNAL</div>
                  <div class="signal-label">{csv_sig['signal']}</div>
                  <span class="conf-badge {cc}">{csv_sig['confidence']} Confidence</span>
                  <div style="margin-top:1rem">
                    <div class="reason-box"><span class="reason-icon">🧠</span>{csv_sig['reason']}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                for tag, val, color in [
                    ("ENTRY",  csv_sig["entry"], "#fff"),
                    ("TP1 🎯", csv_sig["tp1"],   "#00e676"),
                    ("TP2 🚀", csv_sig["tp2"],   "#69f0ae"),
                    ("SL  🛑", csv_sig["sl"],    "#ff1744"),
                ]:
                    st.markdown(f"""
                    <div class="level-card">
                      <span class="level-tag">{tag}</span>
                      <span class="level-val" style="color:{color}">${val:,.4f}</span>
                    </div>
                    """, unsafe_allow_html=True)

            with cr:
                fig2 = build_chart(csv_df, csv_sig, "CSV")
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        except Exception as e:
            st.error(f"⚠️ Error reading CSV: {e}\n\nMake sure columns are: datetime, open, high, low, close, volume")
    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem;color:#4a6080;border:2px dashed #1a2a4a;border-radius:12px">
          <div style="font-size:3rem">📂</div>
          <div style="font-size:1rem;margin-top:1rem">Drop your CSV file here</div>
          <div style="font-size:0.75rem;margin-top:0.5rem">datetime, open, high, low, close, volume</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — BACKTEST
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    bc1, bc2 = st.columns([3, 1])
    with bc2:
        bt_symbol   = st.selectbox("Symbol",    SYMBOLS,                    key="bt_sym")
        bt_interval = st.selectbox("Timeframe", list(INTERVALS.keys()),     key="bt_int", index=2)
        bt_limit    = st.slider("Candles",      100, 500, 300, 50,          key="bt_lim")
        run_bt      = st.button("▶  Run Backtest")

    with bc1:
        if run_bt:
            with st.spinner("🔄 Backtesting... simulating trades..."):
                bt_df = fetch_klines(bt_symbol, INTERVALS[bt_interval], limit=bt_limit)
                if bt_df.empty:
                    st.error("Could not fetch data.")
                else:
                    bt = run_backtest(bt_df)

                    if bt["total"] == 0:
                        st.warning("No completed trades in this period. Try a longer timeframe.")
                    else:
                        # Metrics
                        m1, m2, m3, m4 = st.columns(4)
                        bt_metrics = [
                            ("TOTAL TRADES",  str(bt["total"]),              "metric-white"),
                            ("WIN RATE",      f"{bt['win_rate']:.1f}%",      color_metric(bt['win_rate'] - 50)),
                            ("PROFIT",        f"{bt['profit_pct']:+.2f}%",   color_metric(bt['profit_pct'])),
                            ("MAX DRAWDOWN",  f"{bt['max_dd']:.2f}%",        "metric-red"),
                        ]
                        for col, (lbl, val, clr) in zip([m1,m2,m3,m4], bt_metrics):
                            with col:
                                st.markdown(f"""
                                <div class="metric-card">
                                  <div class="metric-label">{lbl}</div>
                                  <div class="metric-value {clr}">{val}</div>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown('<div class="section-title">EQUITY CURVE</div>', unsafe_allow_html=True)
                        st.plotly_chart(equity_chart(bt["equity"]),
                                        use_container_width=True, config={"displayModeBar": False})

                        # Trade log
                        st.markdown('<div class="section-title">TRADE LOG</div>', unsafe_allow_html=True)
                        trades_df = pd.DataFrame(bt["trades"])
                        trades_df["entry"]  = trades_df["entry"].map(lambda x: f"${x:,.2f}")
                        trades_df["exit"]   = trades_df["exit"].map(lambda x: f"${x:,.2f}")
                        trades_df["return"] = trades_df["return"].map(lambda x: f"{x*100:+.2f}%")
                        trades_df["win"]    = trades_df["win"].map(lambda x: "✅ WIN" if x else "❌ LOSS")
                        trades_df.columns   = ["Entry Price", "Exit Price", "Return %", "Result"]

                        st.dataframe(
                            trades_df.style.applymap(
                                lambda v: "color:#00e676" if "WIN" in str(v) else ("color:#ff1744" if "LOSS" in str(v) else ""),
                                subset=["Result"]
                            ),
                            use_container_width=True, hide_index=True, height=320
                        )

                        st.markdown("""
                        <div style="margin-top:1rem;padding:0.8rem 1.2rem;border-radius:8px;
                            background:rgba(255,214,0,0.05);border:1px solid rgba(255,214,0,0.2);
                            font-size:0.75rem;color:#888">
                          ⚠️ Past performance does not guarantee future results. This backtest is for 
                          educational purposes only. Always use proper risk management in live trading.
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:5rem;color:#4a6080;
                border:2px dashed #1a2a4a;border-radius:12px">
              <div style="font-size:3rem">📊</div>
              <div style="font-size:1rem;margin-top:1rem">Configure settings and click Run Backtest</div>
              <div style="font-size:0.75rem;margin-top:0.5rem">
                Simulates BUY/SELL trades based on signal logic
              </div>
            </div>
            """, unsafe_allow_html=True)
