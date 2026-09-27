"""Diagnostics and in-sample strategy calculations."""
import math
import numpy as np
import pandas as pd
import statsmodels.api as sm
from .fetch_preprocess_data import fetch_and_preprocess

WINDOWS = (10, 20, 60)
BUCKET_ORDER = ["Large Down", "Medium Down", "Small Down", "Small Up", "Medium Up", "Large Up"]

def signed_magnitude_buckets(v):
    out = pd.Series(index=v.index, dtype="object")
    for positive, labels in ((False, ["Small Down","Medium Down","Large Down"]),(True,["Small Up","Medium Up","Large Up"])):
        mask = v.ge(0) if positive else v.lt(0); ranks = v.loc[mask].abs().rank(method="first")
        if len(ranks): out.loc[mask] = pd.qcut(ranks, q=min(3,len(ranks)), labels=labels[:min(3,len(ranks))]).astype(str)
    return out

def add_diagnostics(s):
    s=s.copy(); s["rth_direction"]=np.where(s.rth_return>=0,"UP","DOWN"); s["overnight_direction"]=np.where(s.overnight_return>=0,"UP","DOWN")
    s["continuation"] = np.sign(s.rth_return)==np.sign(s.overnight_return); s["reversal"]=~s.continuation; s["rth_bucket"]=signed_magnitude_buckets(s.rth_return)
    for w in WINDOWS:
        m=max(3,w//2); s[f"corr_{w}"]=s.rth_return.rolling(w,min_periods=m).corr(s.overnight_return); s[f"continuation_{w}"]=s.continuation.astype(float).rolling(w,min_periods=m).mean(); s[f"reversal_{w}"]=s.reversal.astype(float).rolling(w,min_periods=m).mean()
    return s

def run_in_sample_ols(s):
    model=sm.OLS(s.overnight_return, sm.add_constant(s[["rth_return"]], has_constant="add")).fit(); out=s.copy(); out["fitted_overnight_return"]=model.predict(sm.add_constant(s[["rth_return"]],has_constant="add")); out["position"]=np.where(out.fitted_overnight_return>=0,1,-1); out["strategy_return"]=out.position*out.overnight_return; out["equity"]=(1+out.strategy_return).cumprod(); out["long_overnight_equity"]=(1+out.overnight_return).cumprod(); out["drawdown"]=out.equity/out.equity.cummax()-1; return out, model

def bucket_table(s):
    return pd.DataFrame([{ "bucket":b, "observations":int((s.rth_bucket==b).sum()), "mean_overnight":s.loc[s.rth_bucket==b,"overnight_return"].mean(), "continuation_pct":s.loc[s.rth_bucket==b,"continuation"].mean(), "reversal_pct":s.loc[s.rth_bucket==b,"reversal"].mean()} for b in BUCKET_ORDER])

def recent_summary(s,w):
    x=s if w is None else s.tail(w); return {"label":"All" if w is None else f"Last {w}","n":len(x),"correlation":x.rth_return.corr(x.overnight_return),"continuation":x.continuation.mean(),"reversal":x.reversal.mean()}

def run_analysis():
    s, model = run_in_sample_ols(add_diagnostics(fetch_and_preprocess())); return s, model, bucket_table(s), [recent_summary(s,w) for w in WINDOWS]+[recent_summary(s,None)]

if __name__ == "__main__":
    s, model, buckets, summaries = run_analysis(); print(summaries); print(model.summary()); print(buckets.to_string(index=False))
