# Devlog

Newest entry first.

## 2026-11-23

**What we did**
- Created `docker-compose.yml` defining two services: PostgreSQL 16 (the warehouse) and Metabase (dashboards)
- Created `.env` (real credentials, ignored by git) and `.env.example` (committed template with fake values)
- Created the `raw`, `staging` and `marts` schemas (`sql/01_create_schemas.sql`)
- Created the five raw tables, all TEXT columns plus `_loaded_at`, with no primary keys so duplicates can load (`sql/02_create_raw_tables.sql`)
- Added `credit_score` to `raw.customers` (needed for credit risk analysis; values will be calibrated on real score distributions)
- Set up a Python virtual environment and `requirements.txt` (faker, pandas, psycopg2-binary, python-dotenv), documented in `docs/project.md`
- Planned how real and official datasets will be used: calibration and benchmarks (architecture.md section 7)
- Decided the synthetic generator will inject realistic data quality problems (duplicates, nulls, inconsistent formats, orphan keys), documented in `docs/architecture.md`
- Defined how real and official data (FRED, a public loan performance dataset) combines with synthetic data: calibration, benchmarking and context (see `docs/project.md`)
- Persisted data in Docker volumes (`postgres_data`, `metabase_data`) so it survives container restarts
- Started the stack and confirmed Postgres and Metabase run; connected VS Code to Postgres via the SQLTools extension
- Created `sql/01_create_schemas.sql` and ran it: schemas `raw`, `staging` and `marts` now exist

**Why**
- Schemas separate data by stage (raw, staging, marts), so each layer has one clear job
- A SQL file in the repo makes the database setup repeatable; `IF NOT EXISTS` makes it safe to re-run
- Docker makes the environment reproducible: anyone can start the same stack with one command
- Messy raw data gives the staging layer and dbt tests real work, mirroring production banking data
- Keeping credentials in `.env` keeps secrets out of GitHub; `.env.example` documents what is needed
- Volumes separate data from containers, so containers can be rebuilt without losing data

**Next**
- Define the raw tables (customers, accounts, loans, loan_payments, transactions) in SQL
- Build the synthetic data generator

## 2026-11-21

**What we did**
- Created the `bank360-ai` repo, the `dev` branch, and connected it to GitHub
- Set up the folder layout: `data`, `scripts`, `sql`, `dbt`, `airflow`, `docs`
- Added `.gitignore` (keeps secrets, generated data and build output out of git)
- Added a basic GitHub Actions CI workflow and bumped `actions/checkout` to v5 to clear a Node.js deprecation warning
- Installed Docker Desktop
- Decided on Metabase as the primary BI tool (connects live to Postgres, runs in Docker); Tableau Public is an optional extra at the end, using CSV exports of the marts
- Wrote the first versions of `docs/project.md` and `docs/architecture.md`

**Why**
- A clean structure from day one keeps later work organized
- CI gives an automatic check on every push
- Documentation records the reasoning behind each tool choice

**Next**
- Set up docker-compose with Postgres and Metabase
- Finalize the data model
