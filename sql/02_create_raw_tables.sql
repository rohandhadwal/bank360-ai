--Creating Tables
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id    TEXT,
    first_name     TEXT,
    last_name      TEXT,
    email          TEXT,
    phone          TEXT,
    date_of_birth  TEXT,
    segment        TEXT,
    country        TEXT,
    signup_date    TEXT,
    annual_income  TEXT,
    credit_score   TEXT,
    is_test        TEXT,
    _loaded_at     TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.accounts (
    account_id     TEXT,
    customer_id    TEXT,
    account_type   TEXT,
    open_date      TEXT,
    close_date     TEXT,
    status         TEXT,
    balance        TEXT,
    currency       TEXT,
    _loaded_at     TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.loans (
    loan_id        TEXT,
    customer_id    TEXT,
    loan_type      TEXT,
    principal      TEXT,
    interest_rate  TEXT,
    start_date     TEXT,
    term_months    TEXT,
    status         TEXT,
    _loaded_at     TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.loan_payments (
    payment_id     TEXT,
    loan_id        TEXT,
    due_date       TEXT,
    paid_date      TEXT,
    amount_due     TEXT,
    amount_paid    TEXT,
    _loaded_at     TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.transactions (
    transaction_id    TEXT,
    account_id        TEXT,
    txn_timestamp     TEXT,
    amount            TEXT,
    txn_type          TEXT,
    merchant_category TEXT,
    channel           TEXT,
    country           TEXT,
    _loaded_at        TIMESTAMP DEFAULT now()
);