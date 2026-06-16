<<<<<<< HEAD
# Admit Card Generator

A small Streamlit app that turns a student CSV into a print-ready PDF of admit
cards, reusing the existing LaTeX templates in this folder.

## What it does

1. Choose the admit-card type: **Regular**, **Resit**, or **Ex**.
2. Upload the source **CSV** file.
3. Click **Generate** to download a single combined **PDF** — one card per student.

| Type | What it prints |
|------|----------------|
| Regular | Every course for the student |
| Resit | Only courses graded `F` |
| Ex | Only courses graded `F` or `Z` |

## Prerequisites

- **Python 3.10+**
- **A LaTeX distribution** providing `pdflatex` on your PATH — [MiKTeX](https://miktex.org/) (recommended on Windows) or TeX Live. The app warns you if `pdflatex` isn't found.
- Python package: `streamlit` (see `requirements.txt`).

## Setup & run

```bat
pip install -r requirements.txt
```

Then double-click **`run.bat`**, or from a terminal in this folder:

```bat
python -m streamlit run app.py
```

The app opens in your browser. Keep `app.py` in this folder so it can find the
templates (`Regular_V1.tex`, `Resit.tex`, `Ex.tex`) and the shared images
(`Admit_card_background.png`, `signAND-removebg-preview.png`).

## CSV format

Header names must be letters only (LaTeX `head to column names` rule — no spaces
or digits):

- **Student fields (all types):** `roll`, `name`, `Gender`, `Programme`,
  `examination`, `Semester`, `mothername`, `session`, and `Category`
  (Regular/Resit) **or** `type` (Ex).
- **Course fields:** `codeOne`…`codeEleven`, `subOne`…`subEleven`.
- **Grades (Resit & Ex only):** `gradeOne`…`gradeEleven`.

Rows with an empty `roll` are skipped. If a compile fails, open the
**LaTeX compilation log** expander in the app to see the exact error.

## Put it on GitHub

From a terminal in this folder (requires [git](https://git-scm.com/)):

```bat
git init
git add .
git commit -m "Admit card generator: Streamlit + LaTeX"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

Create the empty `<repo-name>` on GitHub first (via **New repository** —
don't add a README/license there, since this folder already has them).

> Note: the `.gitignore` keeps build artifacts and generated `AdmitCards_*.pdf`
> out of the repo. The template `.tex` files, the background image, and the
> signature image **are** committed so the app works anywhere it's cloned.
> If the signature image is sensitive, remove it before pushing.

## Deploy on Streamlit Community Cloud

This app calls `pdflatex`, so the cloud container must install TeX Live. That's
handled by **`packages.txt`** in this repo (apt packages installed at build
time).

1. Push the repo to GitHub (above).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo,
   and set the main file to `app.py`.
3. First build is slow (several minutes) because TeX Live is large; later
   cold starts are also heavier than a plain Python app. This is the trade-off
   for keeping the exact LaTeX output.

If a deploy build times out or runs out of space, trim `packages.txt` to the
smallest set your templates need, or self-host instead (any server with
`pdflatex` works).

=======
# Admit-Card
>>>>>>> 973e17aa02f1f2069333b05ba2d0ffb06919a7f2
