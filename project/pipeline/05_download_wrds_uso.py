"""Step 5: one-minute bars of USO (United States Oil Fund) from WRDS TAQ, 2007 to today.

USO holds near-month WTI futures and trades on NYSE Arca from 09:30 to 16:00 New York time,
so it covers every return window of the paper (09:30-13:30). The bars are built on the WRDS
server, one trading day per query, so only about 390 rows per day travel over the network.

Needs a WRDS account with the TAQ millisecond subscription and `pip install wrds`.
The first run asks for the WRDS username and password in the terminal (Duo approval may follow)
and offers to store them in ~/.pgpass.

Resumable: one file per year in data/wrds/, finished years are skipped.
Usage: python pipeline/05_download_wrds_uso.py [first_year] [last_year] [ticker]
"""
import datetime as dt
import sys

import pandas as pd
import wrds

import config as C

FIRST = int(sys.argv[1]) if len(sys.argv) > 1 else 2007
LAST = int(sys.argv[2]) if len(sys.argv) > 2 else dt.date.today().year
TICKER = sys.argv[3] if len(sys.argv) > 3 else "USO"
OUT = C.DATA / "wrds"

# Regular trades only (tr_corr = '00'), regular session, aggregated to the minute on the server.
SQL = """
select date,
       extract(hour from time_m)::int * 60 + extract(minute from time_m)::int as minute,
       (array_agg(price order by time_m, tr_seqnum))[1]            as open,
       max(price)                                                  as high,
       min(price)                                                  as low,
       (array_agg(price order by time_m desc, tr_seqnum desc))[1]  as close,
       sum(size)                                                   as volume,
       count(*)                                                    as trades
from {lib}.{table}
where sym_root = '{ticker}' and (sym_suffix is null or sym_suffix = '')
  and tr_corr = '00' and price > 0
  and time_m >= '09:30:00' and time_m < '16:00:00'
group by 1, 2
order by 2
"""


def day_tables(db, year):
    """(library, [ctm_YYYYMMDD, ...]) for one year; WRDS keeps the daily tables per year."""
    for lib in (f"taqm_{year}", "taqmsec"):
        try:
            tabs = sorted(t for t in db.list_tables(library=lib) if t.startswith(f"ctm_{year}"))
        except Exception:
            tabs = []
        if tabs:
            return lib, tabs
    return None, []


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    db = wrds.Connection()
    for year in range(FIRST, LAST + 1):
        dest = OUT / f"{TICKER.lower()}_1min_{year}.csv.gz"
        if dest.exists() and year < dt.date.today().year:
            print(year, "cached")
            continue
        lib, tabs = day_tables(db, year)
        if not tabs:
            print(year, "!! no TAQ tables visible (is TAQ millisecond in the subscription?)")
            continue
        parts = []
        for i, table in enumerate(tabs, 1):
            parts.append(db.raw_sql(SQL.format(lib=lib, table=table, ticker=TICKER)))
            if i % 25 == 0 or i == len(tabs):
                print(f"{year}: {i}/{len(tabs)} days", flush=True)
        bars = pd.concat(parts, ignore_index=True)
        bars.to_csv(dest, index=False)
        print(year, "saved", len(bars), "bars")
    db.close()


if __name__ == "__main__":
    main()
