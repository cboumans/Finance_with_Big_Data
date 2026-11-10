"""Step 3: build daily and weekly cloudiness from the downloaded ISD files.

Method (paper, Sec. 4.2): sky cover per hour and location, averaged over daylight hours
(07:00-18:00 local), averaged across the ten hubs. Weekly measure uses the window from the
Thursday before the Friday inventory date through the Tuesday before the Wednesday
announcement (footnote 11). A week is "cloudy" if above the 75th percentile of the sample.

Sky cover per observation = max over config.SKY_LAYERS of oktas/8 (default GA1 only, which
matches the paper's Table 1 moments; see config.py). 9 = sky obscured -> 1.0; 10 = partial obscuration and 99 = missing -> NaN.
GA quality flags 2,3,6,7 (suspect/erroneous) are dropped.

Outputs (data/out): station_qc.csv, chosen_stations.csv, hourly_station.csv,
daily_cloudiness.csv, weekly_cloudiness.csv
Optional: data/eia_release_dates.csv (column `date`) overrides the default of every
Wednesday, to handle holiday-delayed announcements.
"""
import csv

import numpy as np
import pandas as pd

import config as C

BAD_QC = {"2", "3", "6", "7"}


def layer_cover(s):
    """Parse one GA field 'cc,q,height,q,type,q' -> cover in [0,1] or NaN."""
    parts = s.str.split(",", expand=True)
    cc = pd.to_numeric(parts[0], errors="coerce")
    qc = parts[1]
    cov = cc / 8
    cov = cov.where(cc <= 8, np.where(cc == 9, 1.0, np.nan))
    return cov.where(~qc.isin(BAD_QC))


def load_station_year(usaf, wban, year):
    p = C.ISD_DIR / f"{usaf}{wban}_{year}.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p, usecols=["DATE", "REPORT_TYPE", *C.SKY_LAYERS], dtype=str)
    d = d[d["REPORT_TYPE"].str.strip().isin(C.REPORT_TYPES)]
    layers = pd.concat([layer_cover(d[c].fillna("99,9,+99999,9,99,9")) for c in C.SKY_LAYERS], axis=1)
    d["cover"] = layers.max(axis=1, skipna=True)
    # GA1 missing => no sky information (layers 2/3 only exist alongside GA1)
    d.loc[layers.iloc[:, 0].isna(), "cover"] = np.nan
    t = pd.to_datetime(d["DATE"], utc=True).dt.tz_convert(C.TZ)
    # naive local wall-clock time (avoids ambiguous/nonexistent DST hour errors)
    return pd.DataFrame({"local": t.dt.tz_localize(None).values, "cover": d["cover"].values})


def station_hourly(usaf, wban):
    parts = [x for y in range(C.START_YEAR, C.END_YEAR + 1)
             if (x := load_station_year(usaf, wban, y)) is not None]
    if not parts:
        return None
    d = pd.concat(parts)
    d = d[(d.local.dt.hour >= C.DAY_START_HOUR) & (d.local.dt.hour < C.DAY_END_HOUR)]
    d = d[d.local.dt.year.between(C.START_YEAR, C.END_YEAR)]
    d["hour"] = d.local.dt.floor("h")
    h = d.groupby("hour")["cover"].mean()          # mean of valid obs within the hour
    return h


def expected_daylight_hours():
    days = pd.date_range(f"{C.START_YEAR}-01-01", f"{C.END_YEAR}-12-31")
    return len(days) * (C.DAY_END_HOUR - C.DAY_START_HOUR)


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)
    cands = pd.read_csv(C.OUT / "candidates.csv", dtype=str)
    cands["rank"] = cands["rank"].astype(int)
    qc_rows, hourly, chosen = [], {}, []
    for hub, g in cands.groupby("hub", sort=False):
        picked = False
        for _, r in g.sort_values("rank").iterrows():
            h = station_hourly(r.usaf, r.wban)
            n_ok = 0 if h is None else int(h.notna().sum())
            comp = n_ok / expected_daylight_hours()
            qc_rows.append(dict(hub=hub, rank=r["rank"], usaf=r.usaf, wban=r.wban, icao=r.icao,
                                km=r.km, hours_with_sky=n_ok, completeness=round(comp, 3)))
            if h is not None and comp >= C.MIN_SKY_COMPLETENESS and not picked:
                hourly[hub] = h
                chosen.append(dict(hub=hub, usaf=r.usaf, wban=r.wban, icao=r.icao, km=r.km,
                                   completeness=round(comp, 3)))
                picked = True
        if not picked:
            print(f"!! {hub}: no downloaded candidate reaches {C.MIN_SKY_COMPLETENESS:.0%} sky "
                  f"completeness (download more ranks with 02_download_isd.py N)")
    pd.DataFrame(qc_rows).to_csv(C.OUT / "station_qc.csv", index=False)
    pd.DataFrame(chosen).to_csv(C.OUT / "chosen_stations.csv", index=False)
    print(pd.DataFrame(qc_rows).to_string(index=False))

    H = pd.DataFrame(hourly)
    H.index.name = "hour"
    H.to_csv(C.OUT / "hourly_station.csv")

    # daily: per-station daylight mean (needs enough hours), then mean across hubs
    day = H.index.floor("D")
    cnt = H.notna().groupby(day).sum()
    per_station = H.groupby(day).mean().where(cnt >= C.MIN_HOURS_PER_DAY)
    daily = pd.DataFrame({"cloudiness": per_station.mean(axis=1),
                          "n_hubs": per_station.notna().sum(axis=1)})
    daily = daily.reindex(pd.date_range(f"{C.START_YEAR}-01-01", f"{C.END_YEAR}-12-31"))
    daily.index.name = "date"
    daily.to_csv(C.OUT / "daily_cloudiness.csv")

    # weekly: announcement dates default to every Wednesday
    p = C.DATA / "eia_release_dates.csv"
    if p.exists():
        ann = pd.to_datetime(pd.read_csv(p)["date"])
    else:
        ann = pd.date_range(f"{C.START_YEAR}-01-01", f"{C.END_YEAR}-12-31", freq="W-WED")
    rows = []
    for a in ann:
        # Thursday before the Friday measurement .. Tuesday before announcement (Wed)
        w = daily.loc[a - pd.Timedelta(days=6): a - pd.Timedelta(days=1), "cloudiness"]
        rows.append(dict(announcement=a.date(), cloudiness=w.mean(), n_days=int(w.notna().sum())))
    wk = pd.DataFrame(rows)
    thr = wk["cloudiness"].quantile(C.CLOUDY_QUANTILE)
    wk["cloudy"] = (wk["cloudiness"] > thr).astype(int)
    wk.to_csv(C.OUT / "weekly_cloudiness.csv", index=False)

    print(f"\nDaily: n={daily.cloudiness.notna().sum()} of {len(daily)}, "
          f"mean={daily.cloudiness.mean():.3f}, median={daily.cloudiness.median():.3f}, "
          f"sd={daily.cloudiness.std():.3f}   (paper 2014-18: mean .35, median .33, sd .16)")
    print(f"Weekly: n={len(wk)}, {C.CLOUDY_QUANTILE:.0%} threshold={thr:.3f}, cloudy weeks={wk.cloudy.sum()}")


if __name__ == "__main__":
    main()
