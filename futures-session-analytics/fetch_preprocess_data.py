"""Download hourly futures data and construct paired RTH/overnight sessions."""
from pathlib import Path
import os
import pandas as pd
import yfinance as yf

SYMBOL, PERIOD, INTERVAL, TIMEZONE = "ES=F", "730d", "1h", "America/New_York"
RTH_START, RTH_END = 9 * 60 + 30, 16 * 60 + 59
MIN_RTH_BARS, MIN_OVERNIGHT_BARS = 3, 5
ROOT = Path(__file__).resolve().parent
RAW_CSV, SESSION_CSV = ROOT / "es_hourly_raw.csv", ROOT / "es_session_returns.csv"

def _rth(ts): return RTH_START <= ts.hour * 60 + ts.minute <= RTH_END
def _overnight(ts): return ts.hour >= 18 or ts.hour <= 8
def _overnight_day(ts): return (ts + pd.Timedelta(days=1)).date() if ts.hour >= 18 else ts.date()

def download_data(output=RAW_CSV):
    df = yf.download(SYMBOL, period=PERIOD, interval=INTERVAL, auto_adjust=False, progress=False, prepost=True)
    if df.empty: raise RuntimeError("Yahoo returned no data.")
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    missing = [c for c in ("Open", "High", "Low", "Close") if c not in df.columns]
    if missing: raise RuntimeError(f"Missing required columns: {missing}")
    if df.index.tz is None: df.index = df.index.tz_localize("UTC")
    df.index = df.index.tz_convert(TIMEZONE).sort_values()
    df.to_csv(output); return df

def build_sessions(df):
    work = df.copy(); work["is_rth"] = [_rth(ts) for ts in work.index]; work["is_overnight"] = [_overnight(ts) for ts in work.index]
    r = work.loc[work.is_rth].copy(); r["session_day"] = [ts.date() for ts in r.index]
    rrows = []
    for day, g in r.groupby("session_day", sort=True):
        if len(g) >= MIN_RTH_BARS: rrows.append({"rth_date": day, "rth_open": float(g.Open.iloc[0]), "rth_close": float(g.Close.iloc[-1]), "rth_return": float(g.Close.iloc[-1] / g.Open.iloc[0] - 1), "rth_bars": len(g), "rth_start": g.index[0], "rth_end": g.index[-1]})
    o = work.loc[work.is_overnight].copy(); o["session_day"] = [_overnight_day(ts) for ts in o.index]
    orows = []
    for day, g in o.groupby("session_day", sort=True):
        if len(g) >= MIN_OVERNIGHT_BARS: orows.append({"overnight_date": day, "overnight_open": float(g.Open.iloc[0]), "overnight_close": float(g.Close.iloc[-1]), "overnight_return": float(g.Close.iloc[-1] / g.Open.iloc[0] - 1), "overnight_bars": len(g), "overnight_start": g.index[0], "overnight_end": g.index[-1]})
    rth, on = pd.DataFrame(rrows).sort_values("rth_end"), pd.DataFrame(orows).sort_values("overnight_start")
    paired = pd.merge_asof(on, rth, left_on="overnight_start", right_on="rth_end", direction="backward", tolerance=pd.Timedelta(days=4)).dropna(subset=["rth_return"])
    paired = paired.loc[paired.overnight_start > paired.rth_end].sort_values("overnight_end").drop_duplicates("rth_end").reset_index(drop=True)
    if len(paired) < 10: raise RuntimeError(f"Only {len(paired)} valid pairs were constructed.")
    paired.to_csv(SESSION_CSV, index=False); return paired

def fetch_and_preprocess():
    # Reuse a previously written session file for reproducible/offline rendering.
    cache_path = SESSION_CSV if SESSION_CSV.exists() else ROOT.parent / "es_session_returns.csv"
    if os.getenv("FSA_USE_CACHED") == "1" and cache_path.exists():
        cached = pd.read_csv(cache_path, parse_dates=["rth_start", "rth_end", "overnight_start", "overnight_end"])
        for col in ("rth_date", "overnight_date"):
            cached[col] = pd.to_datetime(cached[col]).dt.date
        return cached
    return build_sessions(download_data())
