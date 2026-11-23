# Architecture and Data Schema

> Maintained by Claude as the project evolves. Last updated: 2026-11-21.
> Status: **design stage**. Tables below are the plan and will be refined.

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

## 2. Planned raw tables (draft)

| Table | One row per | Key columns (draft) |
|---|---|---|
| `customers` | Customer | customer_id, name, date_of_birth, segment, signup_date, country |
| `accounts` | Account | account_id, customer_id, account_type, open_date, status |
| `loans` | Loan | loan_id, customer_id, principal, interest_rate, start_date, term_months, status |
| `loan_payments` | Scheduled payment | payment_id, loan_id, due_date, paid_date, amount_due, amount_paid |
| `transactions` | Transaction | transaction_id, account_id, txn_timestamp, amount, merchant_category, channel |

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
