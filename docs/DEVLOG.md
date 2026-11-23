# Devlog

Newest entry first.

## 2026-11-21

**What we did**
- Created the `bank360-ai` repo, the `dev` branch, and connected it to GitHub
- Set up the folder layout: `data`, `scripts`, `sql`, `dbt`, `airflow`, `docs`
- Added `.gitignore` (keeps secrets, generated data and build output out of git)
- Added a basic GitHub Actions CI workflow and bumped `actions/checkout` to v5 to clear a Node.js deprecation warning
- Installed Docker Desktop and set up Postgres via docker-compose
- Decided on Tableau Public for dashboards instead of Metabase (portfolio-friendly public link); marts will be exported to CSV
- Wrote the first versions of `docs/project.md` and `docs/architecture.md`

**Why**
- A clean structure from day one keeps later work organized
- CI gives an automatic check on every push
- Documentation records the reasoning behind each tool choice

**Next**
- Verify Postgres is running, then finalize the data model
- Finalize the data model
