# GitHub setup for Dipendra

Use the professional GitHub account **`dipenadhikari`**.

## 1. Put the folder on your Mac

Download and unzip the project. Move the folder to a stable location such as:

```bash
mkdir -p ~/Developer/portfolio-projects
mv ~/Downloads/sambandha-platform ~/Developer/portfolio-projects/
cd ~/Developer/portfolio-projects/sambandha-platform
```

Do not run Git commands from `/`, `Downloads`, or a parent folder containing unrelated files.

## 2. Verify the application before GitHub

```bash
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py test
uv run python manage.py seed_demo
uv run python manage.py runserver
```

Visit <http://127.0.0.1:8000/>. Stop the server with `Control-C`.

## 3. Create the local Git history

```bash
git init
git branch -M main
git add .
git status
git commit -m "feat: build Sambandha quotation and project workflow"
```

Before committing, `git status` must **not** list `.env`, `db.sqlite3`, or `.venv`.

## 4. Create the empty GitHub repository

On GitHub:

1. Sign in as `dipenadhikari`.
2. Select **New repository**.
3. Repository name: `sambandha-platform`.
4. Description: `Quotation and project-intake workflow for Sambandha Interior & Exterior.`
5. Choose **Public** only if the code contains no real customer or confidential company data.
6. Do not add a README, `.gitignore`, or license on GitHub; they already exist locally.
7. Create the repository.

## 5. Connect and push

Copy the repository URL shown by GitHub, then run:

```bash
git remote add origin https://github.com/dipenadhikari/sambandha-platform.git
git remote -v
git push -u origin main
```

Open <https://github.com/dipenadhikari/sambandha-platform> and confirm the README renders.

## 6. Use small future commits

```bash
git status
git add path/to/the/files-you-changed
git commit -m "fix: explain the specific change"
git push
```

Do not use `git add .` automatically after adding customer exports, screenshots, or environment files. Check `git status` first.

## Suggested GitHub topics

`django`, `python`, `crm`, `quotation-system`, `project-management`, `nepal`, `portfolio-project`

## Suggested first issues

1. Verify every service rate and exclusion with Sambandha.
2. Add email acknowledgement with delivery-failure handling.
3. Add customer photo uploads with private storage and file validation.
4. Add proposal versioning after site verification.
5. Add deployment, backups, monitoring, and a privacy policy.

