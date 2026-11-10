"""Step 2: download ISD hourly files for candidate stations, START_YEAR..END_YEAR.

Resumable (skips files that exist). Usage: 02_download_isd.py [max_rank] [hub-substring ...]
max_rank limits how many ranked candidates per hub are fetched (default 1; rerun with 2, 3
for hubs whose first choice fails QC in step 3).
"""
import csv
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import config as C


def fetch(job):
    usaf, wban, year = job
    dest = C.ISD_DIR / f"{usaf}{wban}_{year}.csv"
    if dest.exists():
        return job, "cached"
    url = C.ISD_URL.format(year=year, usaf=usaf, wban=wban)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            dest.with_suffix(".tmp").write_bytes(data)
            dest.with_suffix(".tmp").rename(dest)
            return job, f"ok {len(data)/1e6:.1f}MB"
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return job, "404"
            time.sleep(2 * (attempt + 1))
        except Exception:
            time.sleep(2 * (attempt + 1))
    return job, "FAILED"


def main():
    max_rank = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    C.ISD_DIR.mkdir(parents=True, exist_ok=True)
    only = [h.lower() for h in sys.argv[2:]]
    with open(C.OUT / "candidates.csv", newline="") as f:
        cands = [r for r in csv.DictReader(f) if int(r["rank"]) <= max_rank
                 and (not only or any(h in r["hub"].lower() for h in only))]
    jobs = sorted({(r["usaf"], r["wban"], y) for r in cands
                   for y in range(C.START_YEAR, C.END_YEAR + 1)})
    print(f"{len(jobs)} station-years")
    with ThreadPoolExecutor(4) as ex:
        for (usaf, wban, y), status in ex.map(fetch, jobs):
            print(f"{usaf}-{wban} {y}: {status}", flush=True)


if __name__ == "__main__":
    main()
