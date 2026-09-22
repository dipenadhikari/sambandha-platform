# Sambandha Platform

A working quotation and project-intake system for **Sambandha Interior & Exterior Pvt. Ltd., Nepal**.

This repository demonstrates a real business workflow:

1. A customer describes the project and chooses services.
2. The server calculates an itemized preliminary estimate.
3. The customer submits contact details and consent.
4. Sambandha receives a project record in a staff pipeline.
5. Staff assign ownership, schedule a site visit, record notes, and move the opportunity through its lifecycle.

The estimate is deliberately described as preliminary. A site visit, measurement, material selection, and technical review are required before a final proposal or contract.

## Current release: v0.1

Included:

- Public project estimator with Basic, Medium, and Premium pricing
- Server-side price calculation and validation
- Saved leads, estimates, projects, and activity history
- Protected staff workspace using Django authentication
- Status, assignment, site-visit, next-action, and notes workflow
- Django admin interface
- Demo seed command
- Automated tests for pricing, intake, permissions, and status changes
- SQLite for local use and PostgreSQL through `DATABASE_URL`
- Responsive interface without a frontend build step

Not yet included:

- Final contractual quotations or invoices
- Customer accounts and customer-facing project tracking
- Photo uploads or AI design generation
- Email/SMS notifications
- Material catalog and vendor purchasing
- Payment collection

Those are intentionally excluded from v0.1. The first release proves the highest-risk operational connection: **customer scope → estimate → staff follow-up**.

## Technology

- Python 3.12–3.14
- Django 5.2 LTS
- SQLite locally; PostgreSQL-ready for deployment
- HTML, CSS, and small progressive JavaScript enhancements
- Gunicorn and WhiteNoise for production serving

## Run locally with `uv`

Install [`uv`](https://docs.astral.sh/uv/) if it is not already available.

```bash
git clone https://github.com/dipenadhikari/sambandha-platform.git
cd sambandha-platform
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

Open:

- Customer site: <http://127.0.0.1:8000/>
- Quotation: <http://127.0.0.1:8000/quotation/>
- Staff workspace: <http://127.0.0.1:8000/staff/>
- Django admin: <http://127.0.0.1:8000/admin/>

The demo command prints the local staff credentials when it creates the user. Change the password before using anything beyond local development.

## Run tests

```bash
uv run python manage.py test
uv run python manage.py check
```

Before a production deployment, configure production environment variables and run:

```bash
DJANGO_DEBUG=false uv run python manage.py check --deploy
```

## Production environment variables

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Long, secret production key |
| `DJANGO_DEBUG` | Set to `false` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated production hostnames |
| `DATABASE_URL` | PostgreSQL connection URL |

Never commit `.env`, database files, customer data, API keys, or production credentials.

## Pricing model

Planning prices live in [`projects/pricing.py`](projects/pricing.py). The browser displays a live preview, but the server recalculates every submitted estimate. This prevents a customer from changing browser-side prices and saving a false total.

The range is calculated as follows:

```text
configured work = sum(quantity × price for selected finish level)
coordination fee = configured work × 6%
planning midpoint = configured work + coordination fee
low estimate = planning midpoint × 90%
high estimate = planning midpoint × 112%
```

These numbers are product assumptions, not verified market prices. Sambandha must review every price and exclusion before real customer use.

## Repository guide

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) explains the models, workflow, and trust boundaries.
- [`docs/GITHUB_SETUP.md`](docs/GITHUB_SETUP.md) gives Dipendra the exact first-push workflow.
- [`docs/PRODUCT_ROADMAP.md`](docs/PRODUCT_ROADMAP.md) defines what to build next and what not to build yet.

## Portfolio case-study angle

The value of this project is not “I made an interior-design website.” The defensible story is:

> I converted an informal quotation and follow-up process into a testable workflow. Customers receive a transparent planning range, while staff receive structured records, ownership, next actions, and an audit trail. I separated preliminary estimates from final contracts to avoid creating false price certainty.

## Data and security warning

The seeded names and phone numbers are fictional. Do not put real customer information in a public demonstration database. Public portfolio deployments should use synthetic data and a clearly labeled demo environment.

