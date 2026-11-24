"""Step 1: candidate ISD stations per hub that cover START_YEAR..END_YEAR.

Writes data/out/candidates.csv (hub, rank, usaf, wban, name, icao, km, begin, end).
"""
import csv
import math
import sys

import config as C


def km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(a))


def load_stations():
    need_begin, need_end = f"{C.START_YEAR}0101", f"{C.END_YEAR}1231"
    out = []
    with open(C.ISD_HISTORY, newline="") as f:
        for r in csv.DictReader(f):
            if r["CTRY"] != "US" or r["BEGIN"] > need_begin or r["END"] < need_end:
                continue
            if C.REQUIRE_ICAO and not r["ICAO"].strip():
                continue
            try:
                r["lat"], r["lon"] = float(r["LAT"]), float(r["LON"])
            except ValueError:
                continue
            if r["lat"] == 0 and r["lon"] == 0:
                continue
            out.append(r)
    return out


def main():
    stations = load_stations()
    C.OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for hub, (state, lat, lon) in C.HUBS.items():
        cands = sorted(((km(lat, lon, s["lat"], s["lon"]), s) for s in stations
                        if s["STATE"] == state), key=lambda t: t[0])
        cands = [(d, s) for d, s in cands if d <= C.MAX_KM][:C.N_CANDIDATES]
        if not cands:
            print(f"!! {hub}: no candidate within {C.MAX_KM} km", file=sys.stderr)
        for rank, (d, s) in enumerate(cands, 1):
            rows.append(dict(hub=hub, rank=rank, usaf=s["USAF"], wban=s["WBAN"],
                             name=s["STATION NAME"], icao=s["ICAO"], km=round(d, 1),
                             begin=s["BEGIN"], end=s["END"]))
            print(f'{hub:24} #{rank} {s["USAF"]}-{s["WBAN"]} {s["STATION NAME"]:38} '
                  f'{s["ICAO"]:5} {d:5.1f} km  {s["BEGIN"]}-{s["END"]}')
    with open(C.OUT / "candidates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
