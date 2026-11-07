import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_structures import PROCESSED_DIR, RAW_DIR, REPORT_DIR, read_molecules


def export_structure(molecule_id: str, output: Path) -> None:
    fragment = output / f"{molecule_id}.tex"
    for suffix in (".pdf", ".svg"):
        fragment.with_suffix(suffix).unlink(missing_ok=True)
    env = os.environ.copy()
    env["TEXINPUTS"] = f"{REPORT_DIR / 'vendor'}//:{env.get('TEXINPUTS', '')}"
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        shutil.copyfile(fragment, temporary / "molecule.tex")
        latex = [
            "xelatex", "-no-shell-escape", "-halt-on-error",
            "-interaction=nonstopmode",
        ]
        subprocess.run(
            latex + [f"-jobname={molecule_id}", str(REPORT_DIR / "structure.tex")],
            cwd=temporary,
            env=env,
            check=True,
        )
        pdf = temporary / f"{molecule_id}.pdf"
        svg = temporary / f"{molecule_id}.svg"
        xdv = temporary / f"{molecule_id}-svg.xdv"
        subprocess.run(
            latex + [
                "-no-pdf",
                f"-jobname={molecule_id}-svg",
                rf"\def\svgexport{{1}}\input{{{REPORT_DIR / 'structure.tex'}}}",
            ],
            cwd=temporary,
            env=env,
            check=True,
        )
        subprocess.run(
            ["dvisvgm", "--no-fonts", "--bbox=papersize", f"--output={svg}", str(xdv)],
            cwd=temporary,
            check=True,
        )
        for graphic in (pdf, svg):
            shutil.copyfile(graphic, output / graphic.name)
    print(f"EXPORT: {molecule_id}.pdf und {molecule_id}.svg")


def main() -> int:
    try:
        for molecule in read_molecules(RAW_DIR / "molecules.csv"):
            print(f"[MOLECULE] {molecule['name']}", flush=True)
            export_structure(molecule["id"], PROCESSED_DIR)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR during export: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
