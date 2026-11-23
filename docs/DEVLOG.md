# Devlog

Newest entry first.

## 2026-11-23

**What we did**
- Created `docker-compose.yml` defining two services: PostgreSQL 16 (the warehouse) and Metabase (dashboards)
- Created `.env` (real credentials, ignored by git) and `.env.example` (committed template with fake values)
- Persisted data in Docker volumes (`postgres_data`, `metabase_data`) so it survives container restarts

**Why**
- Docker makes the environment reproducible: anyone can start the same stack with one command
- Keeping credentials in `.env` keeps secrets out of GitHub; `.env.example` documents what is needed
- Volumes separate data from containers, so containers can be rebuilt without losing data

**Next**
- Run `docker compose up -d` and verify Postgres and Metabase start
- Finalize the data model and create the `raw` schema

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
