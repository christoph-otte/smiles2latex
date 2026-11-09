import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import generate_structures as structures


class GenerationTests(unittest.TestCase):
    def test_convert_smiles(self) -> None:
        with patch.object(structures, "mol2chemfig", return_value=r"\chemfig{C}"):
            self.assertEqual(structures.convert_smiles("C"), r"\chemfig{C}")
        with patch.object(structures, "mol2chemfig", return_value="invalid"):
            with self.assertRaisesRegex(ValueError, "Could not convert SMILES"):
                structures.convert_smiles("invalid")

    def test_main_prints_single_smiles_latex(self) -> None:
        with patch.object(structures, "convert_smiles", return_value=r"\chemfig{C}"):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(structures.main(["--smiles", "C"]), 0)
        self.assertEqual(output.getvalue(), r"\chemfig{C}" + "\n")

    def test_invalid_csv(self) -> None:
        samples = (
            "",
            "id,smiles\nethanol,CCO\n",
            "id,name,smiles,pubchem_cid\n",
            "id,name,smiles,pubchem_cid\n../escape,Ethanol,CCO,702\n",
            "id,name,smiles,pubchem_cid\ncaf\u00e9,Ethanol,CCO,702\n",
            "id,name,smiles,pubchem_cid\nethanol,Ethanol,,702\n",
            "id,name,smiles,pubchem_cid\nethanol,Ethanol,CCO\n",
            "id,name,smiles,pubchem_cid\nethanol,Ethanol,CCO,702,extra\n",
            "id,name,smiles,pubchem_cid\nethanol,Ethanol,CCO,702\nethanol,Ethanol,CCO,702\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            for sample in samples:
                with self.subTest(sample=sample):
                    path.write_text(sample, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        structures.read_molecules(path)

    def test_failed_conversion_removes_stale_fragment(self) -> None:
        rows = structures.read_molecules(ROOT / "tests/fixtures/molecules.csv")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for result in (None, "", "Failed to parse SMILES", "Invalid input data"):
                with self.subTest(result=result):
                    for subdir, suffix in (("tex", ".tex"), ("pdf", ".pdf"), ("svg", ".svg")):
                        (output / subdir).mkdir(exist_ok=True)
                        (output / subdir / f"ethanol{suffix}").write_text("stale")
                    with patch.object(structures, "mol2chemfig", return_value=result):
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                            self.assertEqual(structures.generate(rows, output), 1)
                    self.assertFalse((output / "tex" / "ethanol.tex").exists())
                    self.assertFalse((output / "pdf" / "ethanol.pdf").exists())
                    self.assertFalse((output / "svg" / "ethanol.svg").exists())
                    self.assertFalse((output / "tex" / "index.tex").exists())

    def test_real_converter(self) -> None:
        rows = structures.read_molecules(ROOT / "tests/fixtures/molecules.csv")
        rows.append({
            "id": "invalid",
            "name": "Invalid",
            "smiles": "invalid-smiles",
            "pubchem_cid": "",
        })
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(structures.generate(rows, output), 1)
            self.assertIn(r"\chemfig{", (output / "tex" / "ethanol.tex").read_text())
            self.assertFalse((output / "tex" / "invalid.tex").exists())
            self.assertFalse((output / "tex" / "index.tex").exists())

    def test_main_missing_input_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(structures, "RAW_DIR", Path(directory)):
                with contextlib.redirect_stderr(io.StringIO()) as errors:
                    self.assertEqual(structures.main([]), 1)
            self.assertIn("ERROR:", errors.getvalue())
            self.assertIn("molecules.csv", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
