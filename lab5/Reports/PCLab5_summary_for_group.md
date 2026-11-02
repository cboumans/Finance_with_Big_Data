# PC Lab 5 in 10 minutes: what we did and why

Hi both, this is the short guide to our hackathon notebook `PCLab5_Group4.ipynb`. Read this first, then open the notebook. It runs from top to bottom in about a minute.

**To run it you need:** the notebook, `Exchange_Rates_LSEG.xlsx` in the same folder, the course data folders (`sigwatch_data`, `banks_data_bocconi`), and internet (the notebook downloads the Fama French factors itself). Task 3 also needs `torch` and `transformers`; without them it simply skips itself.

---

## 1. The question and our answer

**Question:** do bank share prices fall when NGOs launch campaigns against them? We copy the event study of Krüger (2015), who found that bad CSR news costs US firms about 1.3% over 21 days.

**Our answer: markets barely react to NGO campaigns against banks.**
* Negative events: −0.46% over 21 trading days, about a third of Krüger's −1.31%.
* But positive events fall just as much (−0.56%). So the fall is not about bad news: bank shares drift down around all events.
* The clean test, negative minus positive, is +0.17 points (p = 0.679). It stays near zero in all 12 robustness checks and all 10 group comparisons.
* Careful: this is "we find nothing", not "there is nothing". Our test has only 52% power against a gap as big as Krüger's.

The one plot that sums it up is the last figure of the notebook.

---

## 2. The pipeline in five steps

| Step | What it does | Key output |
|---|---|---|
| **Day 1** | Sigwatch rows become bank events | 2,631 events on 64 banks |
| **Day 2** | Datastream prices become daily USD returns | 126 banks, 314,917 bank days |
| **Task 4** | Normal behaviour of each bank (betas), estimated before each event | 2,548 events with betas |
| **Task 5** | Abnormal return = actual minus normal, summed over the window (CAR) | 2,547 events with CARs |
| **Task 6** | Tests: do negative events lose more than positive ones? | +0.17 points, p = 0.679 |

Plus two optional extras: **Task 3** (can a language model read the tone better than Sigwatch?) and **Task 7** (do banks in climate concerned countries react more?).

---

## 3. The main choices, and why

| Choice | Why |
|---|---|
| Only banks we have prices for; subsidiaries mapped to their parent | A campaign against Santander UK hits Santander's share price. |
| Several rows of one bank on one day merged into one event | One day can only have one price reaction. |
| Opposite signs for one bank on the same day: both dropped | Good and bad news on one day cancel out. Krüger does the same. (The professor's 5 day rule removed 31% of positive events, so it is only a robustness check.) |
| All returns in US dollars | The Fama French factors are in dollars, so returns must be too. |
| Holidays detected from the prices | Datastream repeats the last price on holidays, which gives fake zero returns. |
| Betas from 250 days ending 50 days before the event | The event must never enter its own "normal" model. A safeguard proves this for 120 cases. |
| Market model as baseline, five factors plus momentum as check | The market model is what Krüger uses; the factor model fits banks better. |
| Errors clustered by event day | Many banks get named in the same report, so their returns move together. |
| CARs winsorised at 1% and 99% | Bankia's 2013 rescue gives a CAR of −138%, which would dominate an average. |
| **Negative minus positive as the main test** | All event days drift down by about −0.02% a day. Comparing the two groups removes that drift. |

---

## 4. Problems we hit, and what we did

1. **Sigwatch names don't match Datastream names.** We extended the professor's name map and fixed its wrong renames (for example an electric utility mapped to a bank).
2. **The Fama French files can't mark holidays** (they list every weekday). So we found holidays from the prices themselves.
3. **The Brexit vote inflated betas** for 297 European events. We flag them and rerun without them: the gap to positive events stays near zero.
4. **61% of event windows overlap** with the previous event of the same bank. We rerun without them: the gap still stays near zero.
5. **The Sigwatch texts are fragments:** 64% start in mid sentence. That limits Task 3.
6. **No news filter:** Krüger removed events with other company news (Factiva). We can't, so earnings or crises can sit inside a window. The median and sign test reduce this.
7. **Our first headline was too strong.** A final review showed that on Krüger's own tests negative events do fall a little. So the headline says "barely react", not "do not react".

---

## 5. The side results

* **Task 3:** FinBERT and RoBERTa barely agree with Sigwatch's label (Spearman 0.10 and 0.17). One report often names several banks with different labels, so the model reads the tone of the report, not the tone towards one bank.
* **Task 4:** the factor model explains bank returns better (R² about 0.6 against 0.5). Bank risk did not change after COP21 or Trump.
* **Task 7:** banks in the four continental countries (higher climate concern) lose 0.73 points more than in the US and UK, but p = 0.084 and it rests on six countries. Suggestive at best.
* **COP21 and Trump:** no change in how markets react. A placebo date one year before COP21 shows an even bigger gap, which is why we write "after", never "because of".

---

## 6. How to read the notebook

| Section | Read this for |
|---|---|
| Day 1 (D1.1 to D1.8) | How campaigns become events; who, when, what, where |
| Optional Task 3 | The language models against Sigwatch |
| Day 2 (D2.1 to D2.13) | Cleaning the prices, holidays, dollars, factors |
| Task 4 (4.1 to 4.7) | The timing of the betas and the safeguard |
| Task 5 (5.1 to 5.7) | The CARs and the first look at the result |
| Task 6 (6.1 to 6.5) | **All the tests: the heart of the notebook** |
| Optional Task 7 | Climate concern by country |
| Conclusion | The answer, the one plot, what we'd do with more time |

Every section follows the same rhythm: one markdown sentence on what we do, the code, the figure, then a **Comments** block with what we found.

---

## 7. What's still left

1. The 4 board slides (the conclusion figure is the key plot).
2. The real number of hours we spent, for the email.
3. Tasks 1 and 2 (press and social media coverage) were dropped on purpose; they go on the slides under "with more time".
