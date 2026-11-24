# Architecture and Data Schema

> Maintained by Claude as the project evolves. Last updated: 2026-11-21.
> Status: **design stage**. Raw tables are final for version 1; marts are still a draft.

## 1. Data flow

```
Python generator -> PostgreSQL (raw) -> dbt staging -> dbt marts -> CSV export -> Tableau Public
  (synthetic data)   (untouched copy)   (clean, typed)  (business logic)  (script)     (dashboards)
                                  ^
                          Airflow runs and monitors every step
```

| Layer | Schema | What happens | Why |
|---|---|---|---|
| Raw | `raw` | Data loaded exactly as generated | Audit trail; can always re-run transformations |
| Staging | `staging` | Rename columns, fix types, light cleaning | One clean version of each source table |
| Marts | `marts` | Joins and business metrics | What analysts and dashboards actually use |

## 2. Raw tables (version 1)

Five tables. Every raw column is stored as `TEXT`, plus a `_loaded_at` timestamp, because real source extracts arrive untyped and messy. Typing and cleaning happen in staging, never in raw.

| Table | One row per | Columns |
|---|---|---|
| `raw.customers` | Customer | customer_id, first_name, last_name, email, phone, date_of_birth, segment, country, signup_date, annual_income, credit_score, is_test |
| `raw.accounts` | Account | account_id, customer_id, account_type, open_date, close_date, status, balance, currency |
| `raw.loans` | Loan | loan_id, customer_id, loan_type, principal, interest_rate, start_date, term_months, status |
| `raw.loan_payments` | Scheduled payment | payment_id, loan_id, due_date, paid_date, amount_due, amount_paid |
| `raw.transactions` | Transaction | transaction_id, account_id, txn_timestamp, amount, txn_type, merchant_category, channel, country |

Relationships: customer 1-to-many accounts and loans; loan 1-to-many loan_payments; account 1-to-many transactions. Fraud labels are not stored in raw; the fraud mart derives risk flags from rules.

## 3. Planned marts (draft)

- `customer_360`: one row per customer with accounts, balances, loans and activity
- Credit risk mart: loan-level delinquency bucket and portfolio default rate
- Fraud mart: flagged transactions and risk signals per customer

## 4. Design decisions

| Decision | Choice | Reason |
|---|---|---|
| Project name | Bank 360 AI (repo `bank360-ai`) | Does not depend on a final fictional bank name |
| Load pattern | ELT with a `raw` schema | Auditability and reproducibility |
| Dev warehouse | PostgreSQL in Docker | Free, local, Snowflake-compatible SQL style |
| Dashboards | Tableau Public instead of Metabase | Free, shareable portfolio link; needs a mart-to-CSV export step because it cannot connect to Postgres |
| Docs | Three files only: `project.md`, `architecture.md`, `DEVLOG.md` | Keeps documentation lean and current |

## 5. Local environment

Defined in `docker-compose.yml`.

| Service | Image | Port | Purpose |
|---|---|---|---|
| `postgres` | postgres:16 | 5432 | Warehouse holding the `raw`, `staging` and `marts` schemas |
| `metabase` | metabase/metabase | 3000 | Dashboards that read from Postgres |

- Credentials come from `.env` (git-ignored); `.env.example` is the committed template.
- Named volumes (`postgres_data`, `metabase_data`) keep data when containers are removed.
- Metabase stores its own settings in a local file database, which is fine for development.

## 6. Deliberately messy raw data

The generator will inject real-world data problems into `raw`, so the staging layer has real cleaning work and dbt tests catch real issues. Each problem is tracked here and mapped to the fix.

| Problem in raw | Real-world cause | Fix in staging / test |
|---|---|---|
| Duplicate rows (same ID twice) | Source system retries or double loads | Deduplicate, keep latest; `unique` test |
| Missing values (null email, DOB, income) | Optional form fields, system gaps | Standardize nulls; `not_null` tests where required |
| Inconsistent formats (dates as text in mixed formats, phone formats) | Different source systems | Cast and standardize types |
| Inconsistent categories ("Checking", "checking ", "CHK") | Manual entry, legacy codes | Trim, lowercase, map to a standard list; `accepted_values` test |
| Orphan keys (transaction for a missing account) | Late or partial loads | `relationships` test; flag or exclude |
| Invalid values (negative principal, future birth date) | Entry errors | Filter or flag; range tests |
| Late-arriving and out-of-order records | Batch delays | Use event vs load timestamps correctly |
| Test or internal accounts mixed in | Left over from system testing | Exclude by rule |

Raw tables are never edited. All cleaning happens in dbt, so every change is visible and traceable.

## 7. Real and official data (planned, Nov 24-30 and later)

No public dataset contains a whole bank's linked customers, accounts, loans and transactions, so the synthetic data is the bank's own internal data. Real and official data play two other roles:

| Role | Source examples | How it is used |
|---|---|---|
| Calibration | Public loan performance data (e.g. Lending Club), public labeled fraud data (e.g. ULB credit card fraud) | Shape the generator: realistic credit score distribution, default rates by score band, fraud rate. Optionally loaded into their own `raw` tables |
| Official benchmarks | Federal Reserve / FRED delinquency and charge-off rates, CFPB complaints database, FDIC bank statistics | Loaded as separate `raw` reference tables. A mart compares our portfolio against the national benchmark |

Check each dataset's license and terms before use. Final dataset choices will be recorded here.
