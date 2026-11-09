"""Generate LaTeX structures of neurotransmitters from SMILES."""

import argparse
import csv
import sys
from pathlib import Path
from typing import Optional

from mol2chemfigPy3 import mol2chemfig

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data/raw"
PROCESSED_DIR = ROOT / "data/processed"
REPORT_DIR = ROOT / "report"
REQUIRED_COLUMNS = ("id", "name", "smiles", "pubchem_cid")


def convert_smiles(smiles: str) -> str:
    """Convert one SMILES string to a LaTeX chemfig expression."""
    result = mol2chemfig(smiles, aromatic=False, inline=True)
    if result is None or not result.lstrip().startswith(r"\chemfig{"):
        raise ValueError(f"Could not convert SMILES: {result}")
    return result


def read_molecules(path: Path) -> list[dict[str, str]]:
    """Read molecules from a CSV file and validate required columns."""
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or any(column not in reader.fieldnames for column in REQUIRED_COLUMNS):
            raise ValueError("ERROR: The CSV file must contain the columns id, name, smiles, and pubchem_cid.")

        molecules = []
        ids = set()
        for row in reader:
            if None in row or None in row.values():
                raise ValueError(f"ERROR: CSV line {reader.line_num}: incorrect number of columns.")
            molecule = {column: row[column].strip() for column in REQUIRED_COLUMNS}
            molecule_id = molecule["id"]
            letters = molecule_id.replace("-", "").replace("_", "")
            if not letters.isascii() or not letters.isalnum():
                raise ValueError(f"ERROR: Invalid ID: {molecule_id}")
            if molecule_id in ids:
                raise ValueError(f"ERROR: Duplicate ID: {molecule_id}")
            if not molecule["name"] or not molecule["smiles"]:
                raise ValueError(f"ERROR: {molecule_id}: Name and SMILES must not be empty.")
            ids.add(molecule_id)
            molecules.append(molecule)
    if not molecules:
        raise ValueError("ERROR: The CSV file contains no molecules.")
    return molecules


def generate(molecules: list[dict[str, str]], output: Path) -> int:
    """Generate LaTeX structures for the given molecules and save them to the output directory."""
    output.mkdir(parents=True, exist_ok=True)
    failed = 0
    for molecule in molecules:
        molecule_id = molecule["id"]
        target = output / "tex" / f"{molecule_id}.tex"
        print(f"[MOLECULE] {molecule['name']}", flush=True)
        try:
            result = convert_smiles(molecule["smiles"])
        except ValueError as error:
            print(f"ERROR: {molecule_id}: {error}", file=sys.stderr)
            for subdir, suffix in (("tex", ".tex"), ("pdf", ".pdf"), ("svg", ".svg")):
                (output / subdir / f"{molecule_id}{suffix}").unlink(missing_ok=True)
            failed += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result + "\n", encoding="utf-8")
        print(f"OK: {molecule_id}")
    print(f"SUCCESS: {len(molecules) - failed}; ERROR: {failed}")
    return 1 if failed else 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate LaTeX structures from SMILES.")
    parser.add_argument("--smiles", help="convert one SMILES string and print its LaTeX")
    args = parser.parse_args(argv)
    if args.smiles is not None:
        try:
            print(convert_smiles(args.smiles))
        except ValueError as error:
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        return 0

    try:
        molecules = read_molecules(RAW_DIR / "molecules.csv")
        return generate(molecules, PROCESSED_DIR)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())