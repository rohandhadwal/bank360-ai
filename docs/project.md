# Project Overview: Bank 360 AI

> Maintained by Claude as the project evolves. Last updated: 2026-11-21.

## 1. Business problem

In a typical bank, data lives in silos: customers, accounts, loans and transactions sit in different systems. Questions that cut across them, such as "which customers with late loan payments also show unusual card activity?", are slow to answer and hard to audit.

**Goal:** one governed warehouse where those questions are answered from a single, tested, documented source.

## 2. What the platform delivers

| Capability | Business question it answers | Built in |
|---|---|---|
| Customer 360 | Who is this customer across all products? What is their total exposure and activity? | dbt mart (planned Dec 1-7) |
| Credit risk | Which loans are late or defaulting? How is the portfolio's health trending? | dbt mart (planned Dec 8-14) |
| Fraud monitoring | Which transactions or customers look suspicious? | dbt mart (planned Dec 8-14) |
| Dashboards | Visual views of all of the above | Tableau Public |

## 3. Tech stack and why (interview talking points)

| Tool | Role | Why this one |
|---|---|---|
| **Python** | Synthetic data generator, loading scripts | The standard language for data work; strong libraries (Faker, pandas) for realistic fake data |
| **SQL** | Schema creation, analysis | The core skill for every data role; the warehouse logic is SQL |
| **PostgreSQL** | Dev warehouse | Free, runs locally in Docker, and its SQL is close to Snowflake's, so the later move is easy |
| **dbt** | Transformations (staging, marts), tests, docs | Turns SQL into version-controlled, tested, documented models with lineage. Industry standard for the "T" in ELT |
| **Airflow** | Orchestration | Schedules and monitors the pipeline as a DAG with dependencies and retries; widely used in industry |
| **Docker / docker-compose** | Local environment | One command starts Postgres identically on any machine; reproducible |
| **Tableau Public** | Dashboards | Free, widely used in industry, and publishes to a shareable public link for a portfolio. It cannot connect to Postgres, so marts are exported to CSV by a pipeline step. Only suitable for synthetic data, since dashboards are public |
| **GitHub Actions** | CI | Automatic checks on every push; shows the work is tested |
| **Snowflake** (roadmap) | Cloud warehouse | What many banks and finance firms use; shows the project can move from local to cloud |
| **AI agents** (roadmap) | Text-to-SQL, data quality, risk reporting | Layered on top of a trusted data foundation, so AI answers are grounded in governed data |

**Why ELT (load raw first, transform in the warehouse):** raw data is kept untouched for auditability, and all business logic lives in versioned, testable SQL. This matters in banking, where being able to trace a number back to its source is essential.

**Why synthetic data:** real bank data is confidential. A generator lets us control volume and plant realistic patterns (late payments, fraud) so the analytics have something to find.

## 4. Finance concepts (defined as we build each model)

Each metric below will be linked to the dbt model that computes it.

| Concept | Plain-words meaning | Model |
|---|---|---|
| Delinquency bucket | How late a loan payment is, grouped: 1-29, 30-59, 60-89, 90+ days past due | TBD (credit risk mart) |
| Default rate | Share of loans that have stopped being repaid (commonly 90+ days past due) | TBD (credit risk mart) |
| Fraud patterns | Transaction behavior that looks abnormal, such as unusually large amounts or many transactions in a short time | TBD (fraud mart) |

## 5. How to run it locally

Not available yet. Will be added once docker-compose and the data generator exist.

## 6. Roadmap

- Snowflake deployment
- Text-to-SQL agent
- Data quality agent
- Risk reporting agent
- Core platform target: **Dec 17, 2026**
