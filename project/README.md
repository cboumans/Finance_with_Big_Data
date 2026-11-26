# Replication: "Eye in the sky: Private satellites and government macro data"

Mukherjee, Panayotov & Shon (JFE 2021), replicated by Group 4 with public data and one-minute USO prices from LSEG.

Start with **`Replication_Group4.ipynb`**: the paper's tests with USO minute prices (LSEG) and EIA, FRED and
NOAA data. It runs after the setup below, once `data/lseg/USO_1min.csv.gz` is in place (see Data). The
scripts in `pipeline/` build the cloud data it reads; the slides are in `slides/`.

## Folders

```
project/
├── Replication_Group4.ipynb   the replication (main notebook)
├── pipeline/                  scripts 01-04, config.py (all settings), viz.py
├── data/                      inputs and outputs (mostly git-ignored, see below)
│   ├── isd-history.csv        NOAA station list
│   ├── lseg/                  USO_1min.csv.gz: one-minute USO bars from LSEG (not in git)
│   └── out/                   derived tables, e.g. hourly_cover_long.csv.gz
└── slides/                    our deck
```

## Files

| File | What it does |
|---|---|
| `pipeline/config.py` | All settings: **`START_YEAR` / `END_YEAR`**, hub list, thresholds, paths |
| `pipeline/01_select_stations.py` | Finds candidate airport stations per hub covering the chosen years (uses `data/isd-history.csv`) |
| `pipeline/02_download_isd.py` | Downloads hourly ISD files from the public NOAA S3 bucket into `data/isd/` |
| `pipeline/03_cloudiness.py` | Builds hourly, daily and weekly cloudiness and the cloudy-week dummy into `data/out/` |
| `pipeline/04_build_long_sample.py` | Hourly sky cover per hub, 2007-2025, airport re-chosen each year, into `data/out/hourly_cover_long.csv.gz` |
| `pipeline/viz.py` | Helpers for NASA GIBS (MODIS) and Sentinel-2 images (used by the former demo notebook, not by the replication) |
| `data/isd-history.csv` | NOAA station list, from https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv |
| `data/lseg/USO_1min.csv.gz` | One-minute bars of USO (NYSE Arca), 2007 to November 2026, from LSEG Tick History; all returns of the replication |

## Data

`data/` is git-ignored (about 600 MB of raw ISD files), so everyone regenerates it locally. Two exceptions:

- **Committed:** the output of step 4 (`hourly_cover_long.csv.gz`, 1.3 MB, and `station_choice_long.csv`),
  because NOAA retired ISD in 2025.
- **Shared privately:** `data/lseg/USO_1min.csv.gz` (20 MB). It is licensed LSEG data and this repository
  is public, so get the file from the group and put it there.

The notebook downloads the EIA and FRED files itself (about 10 MB) on the first run.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

No logins or API keys are needed (NOAA ISD, NASA GIBS and Sentinel-2 on AWS are all public); only the USO file comes from LSEG.

## Run the pipeline (2014-2018, the paper's baseline period)

Run from this folder (`project/`):

```bash
python pipeline/01_select_stations.py
python pipeline/02_download_isd.py 1        # nearest station per hub, about 500 MB
python pipeline/03_cloudiness.py            # prints QC; some hubs will report "no candidate reaches 80%"
python pipeline/02_download_isd.py 3 houston midland wichita   # backups for those hubs
python pipeline/03_cloudiness.py            # final run; should print daily mean ~0.34, 261 weeks, 65 cloudy
```

For a **different period** (e.g. the paper's pre-period 2007-2011) change `START_YEAR` and
`END_YEAR` in `pipeline/config.py` and repeat. If step 3 reports hubs below the completeness threshold,
download more candidates for just those hubs: `python pipeline/02_download_isd.py 3 <hub name part> ...`.

Outputs in `data/out/`: `chosen_stations.csv`, `station_qc.csv`, `hourly_station.csv`,
`daily_cloudiness.csv`, `weekly_cloudiness.csv`.

## Notes

- Sky cover uses only the first ISD cloud layer (`GA1`, oktas/8). This reproduces the paper's
  Table 1 (daily mean 0.35, median 0.33, sd 0.16). Set `SKY_LAYERS` in `pipeline/config.py` to change it.
- Weekly cloudiness is the window's **least cloudy day** (paper, Sec. 4.2): a week is cloudy only if
  even its clearest day is above the 75th percentile. Until November 2026 `03_cloudiness.py` used the
  window mean, which labels 44 of the 261 weeks of 2014-2018 differently; `cloudiness_mean` keeps it.
- Weekly cloudiness assumes every announcement is a Wednesday. Put a `date` column in
  `data/eia_release_dates.csv` to override it with the real (holiday-shifted) EIA release dates.
- The notebook needs internet access on its first run (EIA, FRED and the NASA GIBS images of 1.3).
