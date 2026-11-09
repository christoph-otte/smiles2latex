PYTHON ?= python3
VENV = .venv
VENV_PYTHON = $(VENV)/bin/python -B
LOG = make.log
RUN = sh scripts/run_logged.sh "$(LOG)"
TEX_AUX = report/report.aux report/report.fdb_latexmk report/report.fls \
	report/report.log report/report.out report/report.toc \
	report/report.synctex.gz report/report.xdv

.PHONY: all venv smiles structures graphics pdf test clean

all: pdf

venv: $(VENV)/.ready

$(VENV)/.ready: requirements.txt Makefile scripts/run_logged.sh
	@$(RUN) "Virtual Environment" $(PYTHON) -m venv $(VENV)
	@$(RUN) "Python Packages" $(VENV_PYTHON) -m pip install -r requirements.txt
	@touch $@

smiles: venv
	@test -n "$(SMILES)" || { echo "Usage: make smiles SMILES='...'" >&2; exit 2; }
	@$(VENV_PYTHON) scripts/generate_structures.py --smiles "$(SMILES)"

structures: venv
	@$(RUN) "Structural Formulas" $(VENV_PYTHON) scripts/generate_structures.py

graphics: structures
	@$(RUN) "Individual Graphics PDF/SVG" $(VENV_PYTHON) scripts/export_structures.py

pdf: graphics
	@$(RUN) "PDF Report" env TEXINPUTS="$(CURDIR)/report/vendor//:$$TEXINPUTS" latexmk -xelatex -halt-on-error -interaction=nonstopmode -jobname=report -outdir=report report/main.tex
	@$(RUN) "Remove LaTeX Auxiliary Files" rm -f $(TEX_AUX)
	@$(RUN) "Remove make log" rm -f $(LOG)

test: venv
	@$(RUN) "Python-Tests" $(VENV_PYTHON) -m unittest discover -s tests -v

clean:
	@$(RUN) "Remove Python Caches" sh -c 'find scripts tests -type f -path "*/__pycache__/*.pyc" -delete && find scripts tests -depth -type d -name __pycache__ -empty -delete'
	@$(RUN) "Remove Generated Files" rm -f \
		data/processed/*.tex data/processed/*.pdf data/processed/*.svg \
		report/report.pdf $(TEX_AUX)
	@$(RUN) "Remove Virtual Environment" rm -rf $(VENV)
	@$(RUN) "Remove make log" rm -f $(LOG)
	@$(RUN) "Clean Complete" echo "Clean complete."