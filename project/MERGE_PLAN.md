# Merge plan: one final notebook for 3 December

Status on 26 November 2026, after `git fetch`. Nothing was edited for this plan; all numbers come from the notebooks as
they are on the branches, run from `project/` on this machine.

## 1. Branches

| Branch | Last commit | Author | Notebooks that differ from `origin/main` |
|---|---|---|---|
| `origin/main` | `2989615`, 26 Nov | cboumans (Claas) | – (has `Replication_Group4.ipynb`, the USO version) |
| `origin/Giuliano` | `c345291`, 26 Nov | 6IULIAN0 (Giuliano) | `Satellite_Group4.ipynb` (26 Nov), `Satellite_experiments.ipynb` (26 Nov), `Strategy_Group4.ipynb` (26 Nov); 7 commits ahead of main, 0 behind |
| `origin/claas-lab5` | `bed1b3a`, 3 Nov | cboumans | none: fully contained in main (0 ahead, 14 behind) |
| `origin/hackathon-refactor` | `577a412`, 2 Nov | Theodor Nissen-Meyer | none: fully in main (0 ahead, 23 behind) |
| `origin/hackathon-robustness-checks` | `74516fb`, 2 Nov | Theodor Nissen-Meyer | none: fully in main (0 ahead, 19 behind) |
| `origin/theodor-lab3` | `7dff5b4`, 1 Oct | Theodor | none: fully in main (0 ahead, 44 behind) |

Only `Giuliano` has notebooks that are not on main. The other four branches can be ignored for the merge.

## 2. The four notebooks

| Notebook | Sections | Figures | Data it reads | Runtime |
|---|---|---|---|---|
| `Replication_Group4.ipynb` (main) | 0 Setup · Task 1 Data (sources; release dates, surprises, returns; cloud instrument; Table 1) · Task 2 Main result (Tables 2–3; Figure 5) · Task 3 Mechanism (Table 5 OVX; Table 6 first clear day) · Task 4 Robustness · Task 5 Out of sample 2019–Aug 2025 · Conclusion · References | 6: cloudy/clear filmstrip (VIIRS) · gap by return window · Figure 5 overlay ("60 minutes instead of 15") · OVX caveat · robustness forest · rolling 5-year gap | `data/lseg/USO_1min.csv.gz` · `data/raw/eia_WCESTUS1w.xls`, `eia_wpsr_archive.html`, `fred_OVXCLS.csv`, `hurdat2.txt`, `gibs/*.jpg` · `data/out/hourly_cover_long.csv.gz` · optional `data/out/daily_cloudiness.csv` | 10 s |
| `Satellite_Group4.ipynb` (Giuliano) | Recognizing the tank (image, brightness mask, blob test, OSM map, circles, built filter) · Recognizing the shade (shadow geometry, `shadow_counts`, dark threshold, dark-roof filter, baseline index, EIA Cushing test, HAC regression) · Improved index (1b + 8 + 9, heights 15/18/12 m, comparison, chart, comments) | 7: Sentinel-2 window · bright-pixel mask · blob circles · OSM circles · largest tank with shadow arrow · baseline index vs Cushing stocks · baseline vs improved (2 panels) | `data/cache/` (S2 windows, item list, `osm_tanks.json`) · `data/raw/eia_cushing_w.xls` · writes `data/out/shadow_index.csv`, `shadow_index_improved.csv` | ≈ 38 s (from cache) |
| `Satellite_experiments.ipynb` (Giuliano) | 1–5 cache, tank map, index, test, baseline reproduction · 6 Experiments 1–10 · 7 Results table · 8 Baseline vs combined chart · 9 Conclusions · 10 Tank map checks C1–C4 | 1: baseline vs combined index vs Cushing stocks | `data/cache/` (S2 windows, SCL masks, item list, OSM 14 km and 20 km) · `data/raw/eia_cushing_w.xls` | 87 s (from cache) |
| `Strategy_Group4.ipynb` (Giuliano) | 0 Setup · 1 Data (copied from main) · 2 Rules · 3 Mechanism check · 4 Straddle · 5 Robustness · 6 Where the profit comes from · 7 Verdict · 8 Release time · 9 Season | 2: mean absolute 10:30–11:00 move, cloudy vs clear · cumulative straddle profit, 3 periods | `data/raw/USOP.csv.gz` (same bytes as `data/lseg/USO_1min.csv.gz`) · `optionmetrics_uso_std_30d.csv`, `optionmetrics_uso_prices.csv` · `eia_WCESTUS1w.xls`, `eia_wpsr_archive.html` · `data/out/hourly_cover_long.csv.gz` | 5 s |

Licensed inputs (LSEG minute bars, OptionMetrics) stay out of git; everything else is public or rebuilt by `pipeline/`.

## 3. Overlaps and conflicts

| # | Topic | Where | What differs | Proposal |
|---|---|---|---|---|
| 1 | Release dates, surprises, cloudy weeks | Replication §1.2–1.3; Strategy §1 (copied unchanged) | Same code, done twice | Keep once, in part (a) |
| 2 | USO minute bars | Replication reads `data/lseg/USO_1min.csv.gz`; Strategy reads `data/raw/USOP.csv.gz` | Same file under two paths | Read main's path only |
| 3 | Sample periods | Replication: 2007–11, 2014–18, 2019–25 (cloud data end Aug 2025) · Strategy mechanism: same · straddle: 2019–24 (OptionMetrics ends Dec 2024), 2007–11 starts May 2007 (first options) · satellite: winters 2017–24 | Last period has two ends; the satellite index covers different years | Keep both ends, but label every table "2019–25" or "2019–24" explicitly; give the satellite sample its own line |
| 4 | Cloudy-week threshold | Replication: 75th percentile of weeks with a 10:30–11:00 return · straddle: 75th percentile of the trade sample | Thresholds 0.239 vs 0.235 in 2007–11 → 3 of 242 weeks labelled differently; 2014–18 and 2019–24 identical (1 of 311 differs if the replication uses 2019–25) | **Resolved (26 Nov):** the straddle now uses the replication's labels (its sample and threshold per period; 2019–24 takes the 2019–25 labels). No trade is lost; 2014–18 is unchanged; 2007–11 goes from −0.05 (p = 0.72) to −0.02 (p = 0.90), 2019–24 from +0.18 (p = 0.32) to +0.17 (p = 0.36) |
| 5 | Release time | Replication: every report at 10:30 · Strategy §8: 145 of 990 releases (2007–25) are not on a Wednesday, true times unknown | The replication's main window may miss holiday-week reports | Keep Strategy §8 as the check; mention in limitations of (a) too |
| 6 | "Daily return" | Replication Table 6: open-to-open from minute bars · straddle: OptionMetrics close-to-close `return` | Two definitions of a day's return | Say which one each table uses |
| 7 | What "the mechanism" is | Replication: cloudy weeks react **more steeply to the surprise** (slope gap −0.16, p = 0.25 at 10:30–11:00; −0.42, p = 0.02 at 9:30–11:30) · Strategy: cloudy weeks do **not** move more in size (gap −0.02, p = 0.82) | Not contradictory, but easy to misread: the paper is about direction, the straddle only about size | Keep the two strictly apart (see the note below the table) |
| 8 | Seasonality | Replication Table 5 (OVX): gap vanishes within the same month · Strategy §9: straddle gap survives month dummies (+0.48, p = 0.02) | Same idea, opposite outcome | Show both; good material for the limitations |
| 9 | Out of sample | Replication: slope gap gone after 2018 (+0.06, p = 0.56) · straddle 2019–24: +0.17, p = 0.36 | Consistent: nothing significant after 2018 | Use one "after 2018" message |
| 10 | Satellite index | Satellite_Group4 baseline (−0.40, z −4.6) and improved (−0.66, z −6.1); experiments notebook repeats both | Two versions, done twice | Final notebook: improved index, baseline in one comparison row, labelled "chosen after seeing results" |
| 11 | Inference | Replication and Strategy: bootstrap of weeks, 5,000 draws, seed 20598 · satellite: OLS with HAC (3 lags) | Different methods across parts | Fine, but state it in each part |
| 12 | Name clashes | `stocks` = US crude ex-SPR (Replication) vs Cushing stocks (satellite) · "cloud" = NOAA sky cover vs image cloud flag (ratio ≥ 0.7) | Same names, different things | Rename in the merge: `cushing_stocks`, `image_cloud_flag` |
| 13 | Fixed-airport robustness | Replication Task 4 reads `data/out/daily_cloudiness.csv` if it exists | Missing here, so the robustness chart shows 18 specifications, while main's comments say 19 | **Deferred (26 Nov):** `03_cloudiness.py` needs the NOAA ISD files (steps 01 and 02, about 400–650 MB download), not run yet. Until then, say in the notebook that the fixed-airport check is skipped |
| 14 | "Table IA-1" | Main cites it for the size of the surprise (cloudy 0.73 SD vs clear 0.82 SD); the macro check described it as stock and commodity indices | **Resolved (26 Nov):** Table IA-1 has an inventory panel (the size of the surprise) and the macro rows (stock, energy and industrial commodity indices, Baltic Dry Index), so main's reference is correct | Keep main's citation; the macro rows stay out of our notebook (no data) |

**Note: two different mechanisms, keep them apart.** The paper's mechanism is a **steeper reaction**: in cloudy weeks
the price reacts more strongly *per unit of inventory surprise* (a slope, signed: more oil, lower price). Our straddle
uses a **bigger move**: it pays when the *absolute* price change is large, whatever its sign and whatever the surprise.
The two can differ: in the paper's half hour we find a steeper reaction in cloudy weeks (−0.16 at 10:30–11:00, −0.42
at 9:30–11:30) but no bigger move (−0.02, p = 0.82). In the final notebook and the slides:
* never call the straddle result "the paper's mechanism" or a test of it;
* label charts and tables with the quantity: "reaction per 1 SD surprise" for (a), "absolute move" or "straddle profit" for (c);
* link (a) and (c) with one sentence: the paper predicts a steeper reaction, which a straddle cannot trade on its own; we test whether cloudy weeks also bring bigger moves.

## 4. Plotting style ("Replication theme")

Defined in `Replication_Group4.ipynb`, cells 3 and 4 (copied unchanged into `Strategy_Group4.ipynb`).

* **Look:** inspired by The Economist. White background, horizontal gridlines only (`#D0D0D0`) behind the data, no top, right or left spines, bold left-aligned titles (14 pt), legend without frame, line width 1.6.
* **Font:** Arial, then Helvetica, then DejaVu Sans.
* **Colours:** red rule `#E3120B` · blue `#006BA2` · cyan `#3EBCD2` · teal `#379A8B` · yellow `#EBB434` · purple `#9A607F` · light red `#DB444B` · dark `#333333` · grey `#758D99` · light grey `#C9D3D9`. Fixed meanings: **yellow = clear weeks, blue = cloudy weeks (and our estimates/gaps), dark dashed lines and hollow diamonds = the paper's numbers**; Strategy adds grey = every week.
* **Helpers:** `show(title)` writes the headline as a full sentence with the message, adds the red rule and tag on top; `annotate()` labels lines directly instead of legends; `minus_sign()` and `SIGNED` print true minus signs; `vertical_grid()` for charts read along x.
* **Sizes:** default 14 × 5.5 in; in use 14 × 4.3 to 14 × 7.6. Strategy uses 14 × 4.8.
* **Not yet in the theme:** both satellite notebooks use their own colours (`#A32D2D` red, `#D3D1C7`/`#B4B2A9` grey), default fonts and smaller sizes (5 × 5 to 14 × 7), without `show()`.

## 5. The `slides/` folder

`slides/Final_project.pptx` (3.5 MB, from main), 10 slides in this order:

1. Title: "Replicating and extending: Eye in the sky (JFE)"
2. Agenda: motivation, the paper, our replication, extension
3. Setup: satellites count oil before the government does (tank and shadow diagram, paper Fig. 4 redrawn)
4. The paper: clouds as a natural experiment (clear week vs cloudy week)
5. Data: the paper's sources, except prices and satellite estimates (no image)
6. Result: the paper's gap, but only in its wider windows (ours −0.16 at 10:30–11:00, −0.42 at 9:30–11:30)
7. Comparison: a gap like the paper's, but it takes an hour
8. Extension: after 2018 the gap is gone (+0.06, p = 0.56)
9. **Placeholder:** "Next: our own satellite estimates" → part (b)
10. **Placeholder:** "Next: simulate a satellite hedge fund" → part (c)

There is no limitations or conclusion slide yet.

## 6. Outline of the final notebook (`Final_Group4.ipynb`, proposed name)

Target runtime about 1 minute from the cache. The experiments notebook stays a separate appendix file.

**0. Setup**
* Take Replication cells 2–4 (imports, theme, helpers). Add the imports the satellite part needs (`rasterio`, `affine`, `skimage`).
* Read the USO bars from `data/lseg/USO_1min.csv.gz` only.

**(a) Replication of the paper** (from `Replication_Group4.ipynb`, almost unchanged)
* Take Tasks 1–5 and the conclusion (cells 5–43); this is main's work, so the text stays as it is.
* Cut: the full Table 1 printout can move to an appendix; Task 4 keeps its forest chart and comments; Table 6 can shrink to its comment cell.
* Add: one line on release times (conflict 5), and run `03_cloudiness.py` first (conflict 13).

**(b) Can a normal person copy the satellite funds?** (from `Satellite_Group4.ipynb`, plus one table from the experiments)
* Take: the cache helpers; the OSM tank map, circles, built filter and dark-roof filter; the shadow geometry figure and `shadow_counts`; the baseline index and test (as the "rules fixed in advance" row); the whole improved-index section (comparison table with 15/18/12 m, chart, comments).
* From `Satellite_experiments.ipynb`: only the summary table (section 7) and two findings as text, namely half a pixel moves the ratio by 12–51% (experiment 6), and levels yes, changes no (7a/7b and 10). The code stays in the appendix notebook.
* Cut: the exploratory first attempts (brightness mask, `blob_log` test, the 0.3/0.4/0.5 threshold printout), the 64 printed ratios, and the duplicate imports in cell 22.
* Restyle: all charts in the Replication theme.
* Rename: `cushing_stocks` and `image_cloud_flag` (conflict 12).
* Message: the index tracks the **level** of Cushing stocks (correlation −0.66), not the weekly change (z −1.8), so it gives no edge on the EIA number.

**(c) What to do instead: the cloud straddle** (from `Strategy_Group4.ipynb`)
* Take sections 2–9: rules, mechanism check, straddle, robustness, diagnostic, verdict, release time, season.
* Cut: section 1 (already in part a); keep only the options-data cells.
* Possible merge: the four robustness tables into one summary table (main, IV cost, 10-day, intraday payoff, Wednesday only, 11:00 assumed, month dummies).
* Decide conflict 4 (cloudy labels) before the final run.

**(d) Limitations**
* New markdown, gathered from the parts.
* Replication: the main-window gap is a third of the paper's and not significant; it is significant only in wider windows; it is gone after 2018; USO, not futures; release times unknown for 145 holiday weeks; NOAA data end in August 2025.
* Satellite: improvements chosen after seeing results; winters only, 67 dates; assumed 15 m height; OSM tank map; levels, not changes.
* Straddle: profits are an upper bound (no spread, no event premium, simplified straddle); significant in 1 of 3 periods; the gain is not in the paper's half hour; about 65 cloudy trades per period.
* Finish with a short verdict and the references (main's, plus Sentinel-2, OpenStreetMap, OptionMetrics, EIA Cushing).

## 7. Figures for the slides (10 at most)

| # | Figure | Message | Status |
|---|---|---|---|
| 1 | Cloudy vs clear week filmstrip (VIIRS) | One clear day is enough for satellites to count the oil. | Exists (Replication §1.3); check it is the image on slide 4 |
| 2 | Cloudy minus clear gap by return window | We find the paper's gap, but significant only in its wider windows. | Exists (Replication §2.1, slide 6) |
| 3 | Figure 5 overlay, ours vs paper | Cloudy weeks react like in the paper, but over an hour instead of 15 minutes. | Exists (Replication §2.2, slide 7) |
| 4 | Rolling five-year gap | After 2018 the cloud effect is gone. | Exists (Replication Task 5, slide 8) |
| 5 | Tank map plus one tank's shadow (two panels: OSM circles on Sentinel-2; largest tank with shadow arrow) | Free 10 m images show 398 Cushing tanks and the shadows inside them. | Exists as two separate figures in `Satellite_Group4`; **redraw** as one figure in the theme |
| 6 | Shadow index vs EIA Cushing stocks, baseline and improved | Our free index tracks Cushing's level (correlation −0.66 after lining up the images). | Exists in `Satellite_Group4`; **redraw** in the theme, with the "chosen after seeing results" label |
| 7 | Levels vs changes (two scatters: ratio vs stocks; change in ratio vs change in stocks, ≤ 30 days apart) | Levels yes, weekly changes no: copying the satellite funds gives no edge. | **New** (data in `Satellite_experiments` §6, exp. 7 and 10) |
| 8 | Mean absolute 10:30–11:00 move, cloudy vs clear | In the paper's half hour, cloudy weeks do not move USO more. | Exists (Strategy §3, in the theme) |
| 9 | Cumulative straddle profit, three periods | Buying only in cloudy weeks paid per trade in 2014–18, not in the placebo, less clearly after 2018. | Exists (Strategy §4, in the theme) |
| 10 | Robustness of the 2014–18 straddle gap (dots with 95% intervals: main, IV cost, 10-day, month dummies, Wednesday only, 11:00 assumed, intraday payoff) | The gap survives the cost and the season, but not the half-hour window. | **New** (numbers exist in Strategy §5, §8 and §9) |

Backup, not in the 10: the OVX caveat chart (Replication §3.1) and the satellite experiment table.

## 8. Open decisions before merging

1. Who builds `Final_Group4.ipynb`, and from which branch: merge `Giuliano` into `main` first, so everyone works from one base.
2. ~~Conflict 4~~ resolved: the straddle uses the replication's cloudy labels.
3. Conflict 13, deferred: running `pipeline/03_cloudiness.py` needs the ISD download (steps 01 and 02, about 400–650 MB); until then the robustness chart shows 18 of 19 specifications.
4. ~~Conflict 14~~ resolved: main's "Table IA-1" reference is correct.
5. The two slide placeholders (9 and 10) become parts (b) and (c); add a limitations and conclusion slide.
