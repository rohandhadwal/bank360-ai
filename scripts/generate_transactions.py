from datetime import date

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from generate_accounts import generate_accounts
from generate_customers import generate_customers

SEED = 46
HISTORY_MONTHS = 6
TXN_PER_MONTH = {"checking": 6, "savings": 1, "credit_card": 8}
STATUS_FACTOR = {"active": 1.0, "dormant": 0.1, "closed": 1.0}

TXN_TYPE_MIX = {
    "checking": (["purchase", "withdrawal", "deposit", "transfer"], [0.55, 0.10, 0.20, 0.15]),
    "savings": (["deposit", "transfer", "withdrawal"], [0.50, 0.40, 0.10]),
    "credit_card": (["purchase", "payment"], [0.90, 0.10]),
}
AMOUNT_PROFILE = {  # (median, spread) for a lognormal draw
    "purchase": (40, 1.0),
    "withdrawal": (100, 0.6),
    "deposit": (1200, 0.9),
    "transfer": (300, 1.0),
    "payment": (250, 0.8),
}
CHANNEL_MIX = {
    "purchase": (["pos", "online"], [0.6, 0.4]),
    "withdrawal": (["atm", "branch"], [0.85, 0.15]),
    "deposit": (["ach", "mobile", "branch"], [0.5, 0.3, 0.2]),
    "transfer": (["online", "mobile"], [0.5, 0.5]),
    "payment": (["online", "mobile", "ach"], [0.5, 0.3, 0.2]),
}
MERCHANTS = (
    ["grocery", "restaurant", "fuel", "retail", "travel", "utilities", "entertainment", "healthcare"],
    [0.25, 0.18, 0.12, 0.18, 0.06, 0.08, 0.08, 0.05],
)
FOREIGN_NORMAL = ["CA", "MX", "GB", "FR"]
FOREIGN_RISKY = ["NG", "RU", "BR", "IN"]

# relative chance of a transaction in each hour of the day (0-23): mostly daytime
HOUR_WEIGHTS = np.array([1, 1, 1, 1, 1, 2, 4, 6, 8, 9, 9, 9, 10, 9, 8, 8, 8, 9, 9, 8, 6, 4, 3, 2], dtype=float)
HOUR_P = HOUR_WEIGHTS / HOUR_WEIGHTS.sum()


def generate_transactions(accounts, seed=SEED):
    """Return a DataFrame of transactions linked to accounts by account_id.

    Includes a hidden _is_fraud column; drop it before loading into Postgres.
    """
    rng = np.random.default_rng(seed)
    today = date.today()
    window_start = today - relativedelta(months=HISTORY_MONTHS)
    now = pd.Timestamp.now().floor("s").to_datetime64().astype("datetime64[s]")

    acc = accounts.reset_index(drop=True)

    # each account's active window within the history period
    open_dates = pd.to_datetime(acc["open_date"]).values.astype("datetime64[D]")
    close_dates = pd.to_datetime(acc["close_date"]).values.astype("datetime64[D]")
    start = np.maximum(open_dates, np.datetime64(window_start))
    end = np.where(acc["close_date"].notna().to_numpy(), close_dates, np.datetime64(today))
    span_days = np.clip((end - start).astype("int64") + 1, 0, None)

    # number of transactions per account (Poisson = random counts around an average)
    rate = acc["account_type"].map(TXN_PER_MONTH).to_numpy() * acc["status"].map(STATUS_FACTOR).to_numpy()
    counts = rng.poisson(rate * span_days / 30.4)
    idx = np.repeat(np.arange(len(acc)), counts)  # one entry per transaction, pointing at its account
    total = len(idx)

    # random timestamp inside each account's window
    day_offset = np.floor(rng.random(total) * span_days[idx]).astype("int64")
    hour = rng.choice(24, size=total, p=HOUR_P)
    second = rng.integers(0, 3600, size=total)
    seconds = (day_offset * 86400 + hour * 3600 + second).astype("timedelta64[s]")
    ts = np.minimum(start[idx].astype("datetime64[s]") + seconds, now)

    df = pd.DataFrame(
        {"account_idx": idx, "account_type": acc["account_type"].to_numpy()[idx], "txn_ts": ts}
    )

    # transaction type depends on the account type
    df["txn_type"] = ""
    for account_type, (choices, probs) in TXN_TYPE_MIX.items():
        mask = df["account_type"] == account_type
        df.loc[mask, "txn_type"] = rng.choice(choices, size=int(mask.sum()), p=probs)

    # amount and channel depend on the transaction type
    df["amount"] = 0.0
    df["channel"] = ""
    for txn_type, (median, sigma) in AMOUNT_PROFILE.items():
        mask = df["txn_type"] == txn_type
        n = int(mask.sum())
        df.loc[mask, "amount"] = np.round(rng.lognormal(np.log(median), sigma, n), 2)
        channels, probs = CHANNEL_MIX[txn_type]
        df.loc[mask, "channel"] = rng.choice(channels, size=n, p=probs)

    df["merchant_category"] = None
    purchase = df["txn_type"] == "purchase"
    df.loc[purchase, "merchant_category"] = rng.choice(
        MERCHANTS[0], size=int(purchase.sum()), p=MERCHANTS[1]
    )

    df["country"] = np.where(
        rng.random(len(df)) < 0.02, rng.choice(FOREIGN_NORMAL, size=len(df)), "US"
    )
    df["_is_fraud"] = False

    # plant fraud on 1% of active checking/credit card accounts for each pattern
    candidates = acc[(acc["status"] == "active") & acc["account_type"].isin(["credit_card", "checking"])]
    burst_accounts = candidates.sample(frac=0.01, random_state=seed)
    foreign_accounts = candidates.drop(burst_accounts.index).sample(frac=0.01, random_state=seed + 1)

    def night_time(i):
        """A random night-time moment (1am-5am) inside account i's window."""
        day = int(rng.integers(0, span_days[i]))
        offset = day * 86400 + int(rng.integers(1, 5)) * 3600 + int(rng.integers(0, 3600))
        return start[i].astype("datetime64[s]") + np.timedelta64(offset, "s")

    fraud_rows = []

    def add_fraud(i, when, amount, merchant, country):
        fraud_rows.append(
            {
                "account_idx": i,
                "account_type": acc.at[i, "account_type"],
                "txn_ts": when,
                "txn_type": "purchase",
                "amount": round(float(amount), 2),
                "channel": "online",
                "merchant_category": merchant,
                "country": country,
                "_is_fraud": True,
            }
        )

    for i in burst_accounts.index:
        if span_days[i] < 1:
            continue
        t = night_time(i)
        for _ in range(int(rng.integers(5, 16))):  # card-testing burst: tiny purchases seconds apart
            add_fraud(i, t, rng.uniform(1, 5), "retail", "US")
            t = t + np.timedelta64(int(rng.integers(20, 90)), "s")
        add_fraud(i, t, rng.uniform(800, 3000), "retail", "US")  # then one large purchase

    for i in foreign_accounts.index:
        if span_days[i] < 1:
            continue
        add_fraud(
            i,
            night_time(i),
            rng.uniform(1500, 5000),
            str(rng.choice(["travel", "retail", "entertainment"])),
            str(rng.choice(FOREIGN_RISKY)),
        )

    fraud_df = pd.DataFrame(fraud_rows)
    out = pd.concat([df, fraud_df], ignore_index=True)
    out["txn_ts"] = pd.to_datetime(out["txn_ts"])
    out = out.sort_values("txn_ts").reset_index(drop=True)

    out["transaction_id"] = ["T%08d" % n for n in range(1, len(out) + 1)]
    out["account_id"] = acc["account_id"].to_numpy()[out["account_idx"].to_numpy()]
    out["txn_timestamp"] = out["txn_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return out[
        [
            "transaction_id",
            "account_id",
            "txn_timestamp",
            "amount",
            "txn_type",
            "merchant_category",
            "channel",
            "country",
            "_is_fraud",
        ]
    ]


if __name__ == "__main__":
    customers = generate_customers(2000)
    accounts = generate_accounts(customers)
    txns = generate_transactions(accounts)
    print(txns.head(10).to_string())
    print(len(txns), "transactions for", len(accounts), "accounts")
    print(txns["txn_type"].value_counts())
    print("fraud rows:", int(txns["_is_fraud"].sum()))
    print(txns.groupby("_is_fraud")["amount"].describe())