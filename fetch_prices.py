#!/usr/bin/env python3
"""tickers.txt の銘柄の最新価格(遅延)を yfinance で取得し prices.json に書き出す。
取得に失敗した銘柄は、前回の値をそのまま残す。"""
import json, os, sys, urllib.request, datetime as dt
from pathlib import Path
import yfinance as yf

ROOT = Path(__file__).parent
OUT = ROOT / "prices.json"

def codes():
    for line in (ROOT / "tickers.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            yield line

def latest(code):
    sym = code if "." in code else code + ".T"
    h = yf.Ticker(sym).history(period="7d", interval="1d", auto_adjust=False)
    h = h.dropna(subset=["Close"])
    if h.empty:
        return None
    row = h.iloc[-1]
    return {"date": h.index[-1].strftime("%Y%m%d"), "close": round(float(row["Close"]), 4)}

def push_supabase(prices):
    """SUPABASE_URL と SUPABASE_SERVICE_KEY が設定されているときだけ、最新価格を Supabase の latest_prices に書き込む"""
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        return
    rows = [{"code": c, "d": f"{v['date'][:4]}-{v['date'][4:6]}-{v['date'][6:8]}", "close": v["close"]}
            for c, v in prices.items() if isinstance(v, dict) and "date" in v and "close" in v]
    if not rows:
        return
    headers = {"apikey": key, "Content-Type": "application/json",
               "Prefer": "resolution=merge-duplicates,return=minimal"}
    if key.startswith("eyJ"):  # 旧形式(JWT)の鍵だけ Authorization にも付ける
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(url + "/rest/v1/latest_prices?on_conflict=code",
                                 data=json.dumps(rows).encode(), method="POST", headers=headers)
    try:
        urllib.request.urlopen(req, timeout=30).read()
        print(f"Supabase に {len(rows)} 銘柄を書き込みました")
    except Exception as e:
        print("Supabase への書き込みに失敗:", e, file=sys.stderr)

def main():
    old = {}
    if OUT.exists():
        try:
            old = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    new, ng = {}, []
    for c in codes():
        try:
            r = latest(c)
        except Exception as e:
            print(f"{c}: error {e}", file=sys.stderr)
            r = None
        if r:
            new[c] = r
            print(f"{c}: {r}")
        else:
            ng.append(c)
            if isinstance(old.get(c), dict):
                new[c] = old[c]
    jst = dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
    new["_updated"] = jst.strftime("%Y-%m-%d %H:%M:%S JST")
    OUT.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
    push_supabase(new)
    if ng:
        print("取得できなかった銘柄:", ", ".join(ng), file=sys.stderr)
    return 1 if len(ng) == len(list(codes())) else 0

if __name__ == "__main__":
    sys.exit(main())
