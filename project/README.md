# Replication: "Eye in the sky: Private satellites and government macro data"

Mukherjee, Panayotov & Shon (JFE 2021). This folder builds the paper's **cloud-cover instrument**
(daily and weekly cloudiness over ten US oil storage hubs, from NOAA ISD weather stations) and
shows what it looks like from space. EIA inventories, OVX and oil futures prices are still to do.

Start with **`Project_Group4.ipynb`**, a walkthrough of everything below. It reads files that the
scripts create, so run the pipeline first.

## Files

| File | What it does |
|---|---|
| `config.py` | All settings: **`START_YEAR` / `END_YEAR`**, hub list, thresholds, paths |
| `01_select_stations.py` | Finds candidate airport stations per hub covering the chosen years (uses `isd-history.csv`) |
| `02_download_isd.py` | Downloads hourly ISD files from the public NOAA S3 bucket into `data/isd/` |
| `03_cloudiness.py` | Builds hourly, daily and weekly cloudiness and the cloudy-week dummy into `data/out/` |
| `viz.py` | Helpers for NASA GIBS (MODIS) and Sentinel-2 images (used by the notebook) |
| `isd-history.csv` | NOAA station list, from https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv |
| `Project_Group4.ipynb` | Demo notebook |
| `04_build_long_sample.py` | Hourly sky cover per hub, 2007-2025, airport re-chosen each year, into `data/out/hourly_cover_long.csv.gz` |
| `05_download_wrds_uso.py` | One-minute USO bars from WRDS TAQ for intraday returns (needs a WRDS login; not used yet) |
| `Replication_Group4.ipynb` | Replication of the paper with public data (EIA, FRED) and the cloud data of step 4 |
| `Eyyyye in the Sky Replication with Public Data (Group 4).pptx` | Our slides |

`data/` is git-ignored (about 600 MB of raw ISD files), so everyone regenerates it locally. The exception is
the output of step 4 (`hourly_cover_long.csv.gz`, 1.3 MB, and `station_choice_long.csv`), which is committed
because NOAA retired ISD in 2025: with it, `Replication_Group4.ipynb` runs right after `pip install -r
requirements.txt` (it downloads the EIA and FRED files itself, about 10 MB, on the first run).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

No logins or API keys are needed (NOAA ISD, NASA GIBS and Sentinel-2 on AWS are all public).

## Run the pipeline (2014-2018, the paper's baseline period)

Run from this folder (`project/`):

```bash
python 01_select_stations.py
python 02_download_isd.py 1        # nearest station per hub, about 500 MB
python 03_cloudiness.py            # prints QC; some hubs will report "no candidate reaches 80%"
python 02_download_isd.py 3 houston midland wichita   # backups for those hubs
python 03_cloudiness.py            # final run; should print daily mean ~0.34, 261 weeks, 65 cloudy
```

For a **different period** (e.g. the paper's pre-period 2007-2011) change `START_YEAR` and
`END_YEAR` in `config.py` and repeat. If step 3 reports hubs below the completeness threshold,
download more candidates for just those hubs: `python 02_download_isd.py 3 <hub name part> ...`.

Outputs in `data/out/`: `chosen_stations.csv`, `station_qc.csv`, `hourly_station.csv`,
`daily_cloudiness.csv`, `weekly_cloudiness.csv`.

## Notes

- Sky cover uses only the first ISD cloud layer (`GA1`, oktas/8). This reproduces the paper's
  Table 1 (daily mean 0.35, median 0.33, sd 0.16). Set `SKY_LAYERS` in `config.py` to change it.
- Weekly cloudiness is the window's **least cloudy day** (paper, Sec. 4.2): a week is cloudy only if
  even its clearest day is above the 75th percentile. Until November 2026 `03_cloudiness.py` used the
  window mean, which labels 44 of the 261 weeks of 2014-2018 differently; `cloudiness_mean` keeps it.
- Weekly cloudiness assumes every announcement is a Wednesday. Put a `date` column in
  `data/eia_release_dates.csv` to override it with the real (holiday-shifted) EIA release dates.
- The notebook needs internet access for the satellite images (GIBS and Sentinel-2).
