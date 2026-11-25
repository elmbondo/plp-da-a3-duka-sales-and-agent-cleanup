"""Cleaning pipeline for the mobile money agent network extract.

Usage in a notebook:

    from cleaning_pipeline import clean_agent_data
    clean_df, log = clean_agent_data(txns, agents)
"""

import pandas as pd

# the only two transaction types the business uses
TXN_TYPE_MAP = {"deposit": "Deposit", "withdrawal": "Withdrawal"}


def clean_agent_data(txns, agents):
    """Clean the agent transactions and join them to the agent register.

    The raw data is never changed. The function works on a copy and applies
    these rules in order:
      1. remove repeated transactions (same txn_id), keeping the first
      2. standardise txn_type to "Deposit" or "Withdrawal"
      3. convert amount to numbers and txn_date to real dates
      4. flag missing or invalid amounts, then fill them with the median
      5. flag outliers with the IQR rule (they are flagged, never deleted)
      6. merge with the agent register; unknown agents are kept as "Unknown"

    Returns (clean_df, log), where log is a list of plain-English messages.
    """
    log = []
    df = txns.copy()
    log.append(f"Start: {len(df)} transaction rows")

    # -- 1. Uniqueness: a txn_id should appear only once --
    before = len(df)
    df = df.drop_duplicates(subset="txn_id", keep="first").reset_index(drop=True)
    log.append(f"Removed {before - len(df)} duplicate transactions (same txn_id)")

    # -- 2. Consistency: one spelling for each transaction type --
    original_type = df["txn_type"]
    df["txn_type"] = df["txn_type"].str.strip().str.lower().map(TXN_TYPE_MAP)
    n_fixed = int((original_type != df["txn_type"]).sum())
    n_unknown_type = int(df["txn_type"].isna().sum())
    log.append(f"Standardised txn_type on {n_fixed} rows; {n_unknown_type} rows had an unknown type")

    # -- 3a. Validity: amounts must be numbers --
    amount_text = df["amount"].astype(str).str.replace(",", "", regex=False)
    df["amount"] = pd.to_numeric(amount_text, errors="coerce")

    # -- 3b. Validity and consistency: dates in one format, as real dates --
    date_text = df["txn_date"].astype(str).str.strip()
    n_slash = int(date_text.str.contains("/", regex=False).sum())
    df["txn_date"] = pd.to_datetime(date_text.str.replace("/", "-", regex=False),
                                    format="%Y-%m-%d", errors="coerce")
    n_bad_dates = int(df["txn_date"].isna().sum())
    log.append(f"Converted {n_slash} dates written with '/' to ISO format; {n_bad_dates} dates could not be read")

    # -- 4. Completeness: flag first, then fill --
    df["amount_imputed"] = df["amount"].isna()
    valid_amounts = df.loc[~df["amount_imputed"], "amount"]
    median_amount = valid_amounts.median()
    df["amount"] = df["amount"].fillna(median_amount)
    log.append(f"Flagged and filled {int(df['amount_imputed'].sum())} missing or invalid amounts "
               f"with the median (KES {median_amount:,.2f})")

    # -- 5. Outliers: IQR fences worked out from the real (not filled) amounts --
    q1, q3 = valid_amounts.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    df["is_outlier"] = (df["amount"] < lower) | (df["amount"] > upper)
    log.append(f"Flagged {int(df['is_outlier'].sum())} outliers outside KES {max(lower, 0):,.0f} "
               f"to {upper:,.0f} (flagged, not removed)")

    # -- 6. Merge with the agent register --
    rows_before_merge = len(df)
    register = agents[["agent_id", "county"]].drop_duplicates(subset="agent_id")
    merged = df.merge(register, on="agent_id", how="left",
                      validate="many_to_one", indicator=True)
    merged["agent_known"] = merged["_merge"] == "both"
    merged["county"] = merged["county"].fillna("Unknown")
    merged = merged.drop(columns="_merge")
    n_unknown_agents = int((~merged["agent_known"]).sum())
    log.append(f"Merged with the agent register: {rows_before_merge} rows before, {len(merged)} after; "
               f"{n_unknown_agents} transactions have an unknown agent (kept, county = 'Unknown')")

    log.append(f"Finish: {len(merged)} clean rows")
    return merged, log
