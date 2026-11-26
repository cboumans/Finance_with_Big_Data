`Final_Group4.ipynb` is the main notebook for the presentation. It replicates "Eye in the sky: Private satellites
and government macro data" (Mukherjee, Panayotov & Shon, JFE 2021) with public data and one-minute USO prices from
LSEG, and adds two parts of our own:

- **(a) Replication of the paper:** clouds blind satellites, so cloudy weeks show larger reactions to the EIA report.
- **(b) Can a normal person copy the satellite funds?** A free shadow index of Cushing from Sentinel 2 images.
- **(c) What to do instead:** a USO straddle bought before the report in cloudy weeks, with robustness checks.
- **(d) Limitations**, then the verdict.

It saves the slide figures (300 dpi PNGs) in `slides/figures/`; the deck is in `slides/`.

## Early stage notebooks (`early_stage_notebooks/`)

The final notebook was built by copying cells from these notebooks. They stay as the full record.

| Notebook | What it does | Used in the final notebook |
|---|---|---|
| `Replication_Group4.ipynb` | The paper's tests with USO minute prices (LSEG) and EIA, FRED and NOAA data | (a), almost unchanged |
| `Satellite_Group4.ipynb` | The Sentinel 2 shadow index of Cushing, baseline and improved; writes `data/out/shadow_index.csv` and `shadow_index_improved.csv` | (b) |
| `Satellite_experiments.ipynb` | Experiments behind the improved index, one change at a time, and the tank map checks C1–C4 | Appendix to (b), table b.6 |
| `Strategy_Group4.ipynb` | The cloud straddle and its robustness checks (release time, season) | (c) |
| `MERGE_PLAN.md` | Inventory of the branches and the plan for the final notebook | – |

Each notebook starts with a cell that switches to the `project/` folder, so the paths inside (`data/`,
`pipeline/`) work as before. They read the same data as the final notebook, except that `Strategy_Group4.ipynb`
reads the LSEG bars from `data/raw/USOP.csv.gz` (the same file as `data/lseg/USO_1min.csv.gz`).

## Run the final notebook

1. Set up the environment (see Setup below).
2. Put the licensed files in place (see the next section). Without them the notebook stops at the first cell that reads them.
3. Put the Sentinel 2 cache in `data/cache/` (about 2.6 GB, git-ignored: get it from the group). Without it, the
   notebook downloads the images again from the public Earth Search catalogue (AWS) and the tank outlines from
   OpenStreetMap, which takes a long time.
4. Put `data/raw/hurdat2.txt` in place (NHC best tracks, public, from https://www.nhc.noaa.gov/data/#hurdat). It is the
   only public file the notebook does not download itself.
5. Open `Final_Group4.ipynb` from `project/` and run all cells (or, with Jupyter installed, run
   `jupyter nbconvert --to notebook --execute --inplace Final_Group4.ipynb`).

With the cache in place it runs in about one minute and downloads nothing, except the EIA, FRED and NASA GIBS files on
the very first run. One robustness check of (a), with fixed airports, needs `data/out/daily_cloudiness.csv` from
`pipeline/03_cloudiness.py` (see Run the pipeline). Without it the chart shows 18 of 19 specifications.

## Licensed data (not in the repository)

The repository is public, so these files stay out of git. Get them from the group:

| File | Source | Read by |
|---|---|---|
| `data/lseg/USO_1min.csv.gz` (20 MB) | One-minute bars of USO (NYSE Arca), 2007 to November 2026, LSEG Tick History | Final notebook, Replication; Strategy reads the same file as `data/raw/USOP.csv.gz` |
| `data/raw/optionmetrics_uso_std_30d.csv` | Standardised 30-day USO options, OptionMetrics IvyDB (via WRDS), until December 2024 | Final notebook (c), Strategy |
| `data/raw/optionmetrics_uso_prices.csv` | USO prices and returns, OptionMetrics IvyDB (via WRDS) | Final notebook (c), Strategy |

## Folders

```
project/
├── Final_Group4.ipynb         the main notebook for the presentation
├── early_stage_notebooks/     the notebooks it was built from, and MERGE_PLAN.md
├── pipeline/                  scripts 01-04, config.py (all settings), viz.py
├── data/                      inputs and outputs (mostly git-ignored, see below)
│   ├── isd-history.csv        NOAA station list
│   ├── lseg/                  USO_1min.csv.gz: one-minute USO bars from LSEG (not in git)
│   ├── raw/                   public downloads, hurdat2.txt and the OptionMetrics files (not in git)
│   ├── cache/                 Sentinel 2 windows and OpenStreetMap tanks (not in git)
│   └── out/                   derived tables, e.g. hourly_cover_long.csv.gz
└── slides/                    our deck; figures/ holds the slide figures of the final notebook
```

## Files

| File | What it does |
|---|---|
| `pipeline/config.py` | All settings: **`START_YEAR` / `END_YEAR`**, hub list, thresholds, paths |
| `pipeline/01_select_stations.py` | Finds candidate airport stations per hub covering the chosen years (uses `data/isd-history.csv`) |
| `pipeline/02_download_isd.py` | Downloads hourly ISD files from the public NOAA S3 bucket into `data/isd/` |
| `pipeline/03_cloudiness.py` | Builds hourly, daily and weekly cloudiness and the cloudy-week dummy into `data/out/` |
| `pipeline/04_build_long_sample.py` | Hourly sky cover per hub, 2007-2025, airport re-chosen each year, into `data/out/hourly_cover_long.csv.gz` |
| `pipeline/viz.py` | Helpers for NASA GIBS (MODIS) and Sentinel-2 images (used by the former demo notebook and the satellite notebooks, not by the replication) |
| `data/isd-history.csv` | NOAA station list, from https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv |
| `data/lseg/USO_1min.csv.gz` | One-minute bars of USO (NYSE Arca), 2007 to November 2026, from LSEG Tick History; all returns of the replication |

## Data

`data/` is git-ignored (about 600 MB of raw ISD files), so everyone regenerates it locally. Two exceptions:

- **Committed:** the output of step 4 (`hourly_cover_long.csv.gz`, 1.3 MB, and `station_choice_long.csv`),
  because NOAA retired ISD in 2025.
- **Shared privately:** the licensed files listed above.

The notebooks download the EIA and FRED files themselves (about 10 MB) on the first run.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

No logins or API keys are needed (NOAA ISD, NASA GIBS and Sentinel-2 on AWS are all public); only the USO file comes
from LSEG and the option files from OptionMetrics.

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
- The notebooks need internet access on their first run (EIA, FRED and the NASA GIBS images of section 1.3, the cloud instrument).
