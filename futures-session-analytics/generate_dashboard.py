"""Render the standalone interactive HTML dashboard from analysis output."""
import json
from pathlib import Path
from .main_analysis import run_analysis

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "dashboard_template.html"
OUTPUT = ROOT / "index.html"

def generate_dashboard(output=OUTPUT):
    sessions, _model, _buckets, _summaries = run_analysis()
    rows=[]
    for _, r in sessions.iterrows():
        rows.append({"time":str(r.overnight_date),"strategy_return":float(r.strategy_return),"overnight_return":float(r.overnight_return),"corr_10":None if r.corr_10!=r.corr_10 else float(r.corr_10),"corr_20":None if r.corr_20!=r.corr_20 else float(r.corr_20),"corr_60":None if r.corr_60!=r.corr_60 else float(r.corr_60)})
    html=TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", json.dumps(rows, allow_nan=False)); output.write_text(html,encoding="utf-8"); return output

if __name__ == "__main__": print(generate_dashboard())
