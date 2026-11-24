"""Step 4: hourly sky cover for the ten hubs over a long sample (default 2007 to the end of ISD).

Unlike steps 2-3 this also reads a clear sky from GF1 when GA1 is absent (needed before 2013), and it streams each NOAA ISD station-year, keeps only the hourly sky cover and
throws the raw file away, so the whole 2007-2025 sample needs about 30 MB instead of several GB.
The station is chosen per hub and year: the nearest airport whose daylight sky readings are at
least MIN_SKY_COMPLETENESS complete in that year (same rule as 03_cloudiness.py, applied yearly
because few stations report without gaps for two decades).

Outputs (data/out):
  hourly_cover_long.csv.gz   local hour x hub, mean first-layer sky cover (all 24 hours)
  station_choice_long.csv    hub, year, station used, distance, completeness

Usage: python pipeline/04_build_long_sample.py [first_year] [last_year]
"""
import csv
import importlib
import io
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

import config as C

sel = importlib.import_module("01_select_stations")      # reuse the distance function
cloud = importlib.import_module("03_cloudiness")         # reuse the GA1 parser

FIRST = int(sys.argv[1]) if len(sys.argv) > 1 else 2007
LAST = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
MAX_RANK = 5                                             # nearest candidates tried per hub-year
CACHE = C.DATA / "cache_hourly"                          # one small file per station-year


def candidates(hub, year):
    """Airport stations within MAX_KM of the hub that were active in `year`, nearest first."""
    state, lat, lon = C.HUBS[hub]
    out = []
    with open(C.ISD_HISTORY, newline="") as f:
        for r in csv.DictReader(f):
            if r["CTRY"] != "US" or r["STATE"] != state or not r["ICAO"].strip():
                continue
            if r["BEGIN"] > f"{year}0131" or r["END"] < f"{year}0601":
                continue
            try:
                d = sel.km(lat, lon, float(r["LAT"]), float(r["LON"]))
            except ValueError:
                continue
            if d <= C.MAX_KM:
                out.append((round(d, 1), r["USAF"], r["WBAN"], r["ICAO"]))
    return sorted(out)[:MAX_RANK]


def station_year(usaf, wban, year):
    """Hourly mean sky cover (local time, all hours) for one station-year; cached. None if absent."""
    p = CACHE / f"{usaf}{wban}_{year}.csv.gz"
    if p.exists():
        s = pd.read_csv(p, index_col=0, parse_dates=True)["cover"]
        return s if len(s) else None
    url = C.ISD_URL.format(year=year, usaf=usaf, wban=wban)
    raw = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                raw = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
            time.sleep(3 * (attempt + 1))
        except Exception:
            time.sleep(3 * (attempt + 1))
    if raw is None:
        pd.Series(dtype=float, name="cover").to_csv(p)
        return None
    d = pd.read_csv(io.BytesIO(raw), usecols=lambda c: c in {"DATE", "REPORT_TYPE", "GA1", "GF1"}, dtype=str)
    for col in ("GA1", "GF1"):
        if col not in d:
            d[col] = np.nan
    d = d[d["REPORT_TYPE"].str.strip().isin(C.REPORT_TYPES)]
    cover = cloud.layer_cover(d["GA1"].fillna("99,9,+99999,9,99,9"))
    # Before about 2013 a clear sky (METAR "CLR") has no GA1 layer at all; it only shows up as
    # total coverage GF1 = 00. Without this line clear hours are lost and old years look cloudy.
    cover = cover.where(~(d["GA1"].isna() & d["GF1"].fillna("").str.startswith("00")), 0.0)
    local = pd.to_datetime(d["DATE"], utc=True).dt.tz_convert(C.TZ).dt.tz_localize(None)
    s = pd.Series(cover.values, index=local.dt.floor("h").values, name="cover").groupby(level=0).mean().dropna()
    s.index.name = "hour"
    s.to_csv(p)
    return s if len(s) else None


def completeness(s, year):
    """Share of daylight hours (07:00-18:00 local) of the year with a usable sky reading."""
    if s is None:
        return 0.0
    days = pd.date_range(f"{year}-01-01", f"{year}-12-31")
    if year == LAST:                                     # the last year may be incomplete at the source
        days = days[days <= s.index.max().normalize()]
    h = s.index.hour
    return float(((h >= C.DAY_START_HOUR) & (h < C.DAY_END_HOUR)).sum() / (len(days) * (C.DAY_END_HOUR - C.DAY_START_HOUR)))


def pick(job):
    """Nearest candidate that passes the completeness rule; otherwise the most complete one."""
    hub, year = job
    best = None
    for rank, (km_, usaf, wban, icao) in enumerate(candidates(hub, year), 1):
        s = station_year(usaf, wban, year)
        comp = completeness(s, year)
        row = dict(hub=hub, year=year, rank=rank, usaf=usaf, wban=wban, icao=icao, km=km_,
                   completeness=round(comp, 3))
        if comp >= C.MIN_SKY_COMPLETENESS:
            return row, s
        if s is not None and (best is None or comp > best[0]["completeness"]):
            best = (row, s)
    return best if best else (dict(hub=hub, year=year, rank=0, completeness=0.0), None)


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    C.OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(hub, y) for hub in C.HUBS for y in range(FIRST, LAST + 1)]
    rows, series = [], {hub: [] for hub in C.HUBS}
    with ThreadPoolExecutor(4) as ex:
        for (hub, y), (row, s) in zip(jobs, ex.map(pick, jobs)):
            rows.append(row)
            if s is not None:
                series[hub].append(s[s.index.year == y])
            print(f"{hub:24} {y}: {row.get('icao', '-'):5} rank {row['rank']} "
                  f"completeness {row['completeness']:.2f}", flush=True)
    H = pd.DataFrame({hub: pd.concat(v) for hub, v in series.items() if v}).sort_index()
    H.index.name = "hour"
    H.round(4).to_csv(C.OUT / "hourly_cover_long.csv.gz")
    pd.DataFrame(rows).to_csv(C.OUT / "station_choice_long.csv", index=False)
    print(f"\n{H.shape[0]} hours x {H.shape[1]} hubs, {H.index.min()} to {H.index.max()}")


if __name__ == "__main__":
    main()
