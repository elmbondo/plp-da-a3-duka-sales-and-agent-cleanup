# Week 3: Duka Sales Exploration and Agent Network Clean-Up

Two client engagements from my first weeks as a junior analyst.

1. **Duka Electronics:** explore six months of sales (1,000 orders) and answer the Head of Sales' questions with numbers, not just tables.
2. **Mobile money agent network:** audit, clean, merge and summarise an unreliable transaction extract (612 raw rows, 600 after cleaning), and report on its data quality.

## Files

| File | What it is |
|---|---|
| `generate_data.py` | Both dataset generators from the course, unchanged (Duka seed 2026, agent network seed 44) |
| `duka_sales_exploration.ipynb` | Engagement 1 notebook with the Executive Summary and Tasks 1 to 8 |
| `excel/duka_branch_summary.xlsx` | SUMIFS table, XLOOKUP region column and a PivotTable |
| `outputs/premium_online_coast_capital.csv` | Premium online orders from Nairobi and Mombasa |
| `cleaning_pipeline.py` | `clean_agent_data(txns, agents)`, which returns the clean data and a log |
| `agent_cleanup.ipynb` | Engagement 2 notebook: audit, cleaning, merge validation, summaries and the Data Quality Report |
| `outputs/agent_transactions_clean.csv` | The clean agent transactions |
| `requirements.txt` | Libraries used |

## How to run

1. Install the libraries: `pip install -r requirements.txt`
2. Create the data: `python generate_data.py` (this writes `duka_sales.csv`, `agents.csv` and `agent_transactions.csv`; the raw CSV files are not committed).
3. Open `duka_sales_exploration.ipynb` and `agent_cleanup.ipynb` in Jupyter or Google Colab and choose Run all. Keep `cleaning_pipeline.py` and `generate_data.py` in the same folder as the notebooks.

## Duka Executive Summary

- Duka Electronics took 1,000 orders worth KES 71.8 million between 1 January 2026 and 29 June 2026, an average of KES 71,792 per order.
- Nairobi leads with KES 26.1 million (36.4% of revenue), almost double second-placed Mombasa at KES 14.0 million (19.5%), and the ranking is the same by revenue and by orders because average order values are similar across branches.
- Laptops earned KES 41.5 million, which is 57.9% of all revenue, while tablets sold the most units (691), so keeping laptops in stock matters more than any other product decision.
- Weekends are not a sales peak: they brought 277 orders (27.7%) from 52 of the 180 days, at an average order of KES 71,972 against KES 71,724 on weekdays.
- April was the strongest month at KES 13.5 million and June the weakest at KES 10.9 million, a gap of 24.0%, and the 83 Premium online orders from Nairobi and Mombasa are worth KES 10.2 million (14.2% of revenue).

## Agent data: before and after

| Step | Rows |
|---|---|
| Raw transactions | 612 |
| Repeated transactions removed (same `txn_id`) | 12 |
| **Clean transactions** | **600** |

Other results of the cleaning: 376 transaction types standardised to `Deposit` and `Withdrawal`, 5 dates converted to ISO format, 20 missing or invalid amounts flagged and filled with the median, 5 suspicious KES 250,000 values flagged and left out of the summaries, and 7 transactions from an unknown agent kept with the county `Unknown`.

## What I learned

- A duplicate should be defined by its key (`txn_id`), because one repeated transaction differed in a single column and was missed by a plain `drop_duplicates()`.
- Flag first, then fill: the `amount_imputed` and `is_outlier` columns mean nothing is hidden.
- Check the row count after every merge, and keep unknown agents instead of letting an inner join delete them quietly.
- Put every cleaning rule in one function with a log, so the next extract is cleaned the same way.
