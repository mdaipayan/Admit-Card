"""
Admit Card Generator — Streamlit app
=====================================
Pick an admit-card type (Regular / Resit / Ex), upload the source CSV, and
download a single combined PDF with one admit card per student.

The app reuses the existing LaTeX templates that live next to this file:
    Regular_V1.tex   Resit.tex   Ex.tex
plus the shared assets:
    Admit_card_background.png   signAND-removebg-preview.png

Requirement: a LaTeX distribution providing `pdflatex` must be installed and on
PATH (MiKTeX or TeX Live). Run with:  streamlit run app.py
"""

import os
import re
import shutil
import subprocess
import tempfile

import streamlit as st

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# admit-card type -> template file living in APP_DIR
TEMPLATES = {
    "Regular": "Regular_V1.tex",
    "Resit": "Resit.tex",
    "Ex": "Ex.tex",
}

# assets that each template expects to find in its working directory
ASSETS = [
    "Admit_card_background.png",
    "signAND-removebg-preview.png",
]

# name the CSV is rewritten to inside the template before compiling
CSV_NAME = "data.csv"

# regex that swaps the hard-coded CSV filename in  \csvreader[...]{FILE.csv}
CSVREADER_RE = re.compile(r"(\\csvreader\[.*?\]\s*\{)[^}]*\}", re.DOTALL)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def find_pdflatex() -> str | None:
    """Return the path to pdflatex, or None if it is not installed."""
    return shutil.which("pdflatex")


def inject_csv(template_text: str) -> str:
    """Replace the template's hard-coded CSV filename with CSV_NAME."""
    new_text, n = CSVREADER_RE.subn(r"\1" + CSV_NAME + "}", template_text, count=1)
    if n == 0:
        raise ValueError(
            "Could not locate the \\csvreader{...} statement in the template."
        )
    return new_text


def build_pdf(card_type: str, csv_bytes: bytes) -> tuple[bytes | None, str]:
    """
    Compile the chosen template with the uploaded CSV.
    Returns (pdf_bytes_or_None, log_text).
    """
    template_path = os.path.join(APP_DIR, TEMPLATES[card_type])
    if not os.path.exists(template_path):
        return None, f"Template not found: {template_path}"

    with open(template_path, "r", encoding="utf-8") as fh:
        tex = inject_csv(fh.read())

    with tempfile.TemporaryDirectory() as work:
        # main .tex
        with open(os.path.join(work, "main.tex"), "w", encoding="utf-8") as fh:
            fh.write(tex)

        # uploaded CSV
        with open(os.path.join(work, CSV_NAME), "wb") as fh:
            fh.write(csv_bytes)

        # assets (copied if present; templates degrade gracefully if missing)
        for asset in ASSETS:
            src = os.path.join(APP_DIR, asset)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(work, asset))

        log = ""
        # run twice so counters / shipout backgrounds settle
        for _ in range(2):
            proc = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "main.tex",
                ],
                cwd=work,
                capture_output=True,
                text=True,
            )
            log = proc.stdout + "\n" + proc.stderr

        pdf_path = os.path.join(work, "main.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as fh:
                return fh.read(), log
        return None, log


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Admit Card Generator", page_icon="🎓")

st.title("🎓 Admit Card Generator")
st.caption("Select the card type, upload the source CSV, and download a combined PDF.")

pdflatex = find_pdflatex()
if pdflatex is None:
    st.error(
        "**pdflatex was not found on this machine.**\n\n"
        "Install a LaTeX distribution (MiKTeX or TeX Live) and make sure "
        "`pdflatex` is on your PATH, then restart the app."
    )

card_type = st.radio(
    "Admit card type",
    list(TEMPLATES.keys()),
    horizontal=True,
    help="Regular = all courses · Resit = courses graded F · Ex = courses graded F or Z",
)

uploaded = st.file_uploader("Source CSV file", type=["csv"])

if uploaded is not None:
    st.success(f"Loaded **{uploaded.name}** ({uploaded.size:,} bytes)")

generate = st.button(
    "Generate admit cards",
    type="primary",
    disabled=(uploaded is None or pdflatex is None),
)

if generate and uploaded is not None:
    with st.spinner(f"Compiling {card_type} admit cards…"):
        csv_bytes = uploaded.getvalue()
        pdf_bytes, log = build_pdf(card_type, csv_bytes)

    if pdf_bytes:
        out_name = f"AdmitCards_{card_type}.pdf"
        st.success("PDF generated successfully.")
        st.download_button(
            "⬇️ Download combined PDF",
            data=pdf_bytes,
            file_name=out_name,
            mime="application/pdf",
            type="primary",
        )
    else:
        st.error("PDF generation failed. See the LaTeX log below.")

    with st.expander("LaTeX compilation log"):
        st.code(log or "(no output)", language="text")

with st.expander("CSV column reference"):
    st.markdown(
        """
The CSV header row must use these exact column names (LaTeX `head to column names`
requires letters only — no spaces or digits):

**Student fields (all types):**
`roll`, `name`, `Gender`, `Programme`, `examination`, `Semester`,
`mothername`, `session`, and `Category` (Regular/Resit) **or** `type` (Ex).

**Course fields:** `codeOne`…`codeEleven`, `subOne`…`subEleven`.

**Grades (Resit & Ex only):** `gradeOne`…`gradeEleven`.

- **Regular** prints every course.
- **Resit** prints only courses whose grade is `F`.
- **Ex** prints only courses whose grade is `F` or `Z`.
- Rows with an empty `roll` are skipped.
"""
    )
