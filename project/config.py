"""Shared settings for the oil-hub cloud-cover pipeline (Mukherjee, Panayotov & Shon, JFE 2021).

Change START_YEAR / END_YEAR to pick the sample. The paper uses
baseline 2014-2018 and pre-period 2007-2011.
"""
from pathlib import Path

START_YEAR = 2014
END_YEAR = 2018

ROOT = Path(__file__).resolve().parent
ISD_HISTORY = ROOT / "isd-history.csv"
DATA = ROOT / "data"
ISD_DIR = DATA / "isd"            # raw per-station-year files
OUT = DATA / "out"                # derived tables
ISD_URL = "https://noaa-global-hourly-pds.s3.amazonaws.com/{year}/{usaf}{wban}.csv"

# Ten storage hubs listed in footnote 9 of the paper (approximate coordinates).
# All ten are in the US Central time zone.
HUBS = {
    "Cushing, OK":            ("OK", 35.985, -96.767),
    "Patoka, IL":             ("IL", 38.754, -89.098),
    "Clovelly, LA":           ("LA", 29.430, -90.250),
    "Saint James, LA":        ("LA", 30.020, -90.820),
    "Houston, TX":            ("TX", 29.760, -95.370),
    "Beaumont-Nederland, TX": ("TX", 30.000, -94.050),
    "Corpus Christi, TX":     ("TX", 27.800, -97.400),
    "Midland, TX":            ("TX", 31.997, -102.078),
    "Wink, TX":               ("TX", 31.750, -103.150),
    "Wichita Falls, TX":      ("TX", 33.910, -98.490),
}
TZ = "America/Chicago"

# Station selection
MAX_KM = 60                 # candidate must be within this distance of the hub
N_CANDIDATES = 3            # how many nearest candidates per hub to consider
REQUIRE_ICAO = True         # airports only ("airports have higher quality data")

# Cloudiness construction
DAY_START_HOUR = 7          # local hours [7, 18) = 07:00-18:00
DAY_END_HOUR = 18
MIN_SKY_COMPLETENESS = 0.80 # share of daylight hours with a usable sky reading, per station
MIN_HOURS_PER_DAY = 6       # daily cloudiness needs at least this many usable daylight hours
CLOUDY_QUANTILE = 0.75      # week is "cloudy" if above this quantile of the sample
REPORT_TYPES = {"FM-12", "FM-15", "FM-16"}  # SYNOP, METAR, SPECI (drops daily summaries)

# Which ISD cloud-layer fields define sky cover. ("GA1",) reproduces the paper's Table 1 daily
# cloudiness (mean .35 / median .33 / sd .16); ("GA1","GA2","GA3") takes the max over layers
# and gives a cloudier series (mean ~.45).
SKY_LAYERS = ("GA1",)
