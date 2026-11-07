# Drawing Structural Formulae with LaTeX

This project converts SMILES strings into molecular structure diagrams using LaTeX. A CSV file containing molecular metadata serves as input. The program generates LaTeX fragments, individual PDF and SVG graphics, and a consolidated PDF report for manual review and curation.

## Requirements

- Python: 3.10 or later, including venv and pip
- Build tools: GNU Make
- TeX distribution: XeLaTeX, latexmk, chemfig, standalone and dvisvgm
- Python dependencies: listed in requirements.txt

## Installation

1. Clone or download the project.
2. Open a terminal in the project directory.
3. Run `make` 

The Makefile automatically creates a Python virtual environment and installs the required Python packages from requirements.txt.

## Input

- **File:** `data/raw/molecules.csv`
- **Columns:** `id`, `name`, `smiles`, `pubchem_cid`
- Each row represents one molecule.
- The `id` column must contain unique identifiers.

## Available Commands 

- `make`: Generate molecular structures, graphics and the PDF report.
- `make test`: Run the test suite.
- `make clean`: Remove generated files and build artifacts.

## Output

- `data/processed/`: Generated LaTeX fragments and individual PDF/SVG molecular structure diagrams.
- `report/report.pdf`: Compiled PDF report containing the molecular structures.
- `report/main.tex`: Manually maintained LaTeX report template.
- `make.log`: Detailed build and test log.

## License

- Project license: add once chosen.
- Third-party LaTeX dependency: see `report/vendor/README.md`.