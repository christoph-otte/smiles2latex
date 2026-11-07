import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class MakeTests(unittest.TestCase):
    def test_clean_removes_generated_files_and_caches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("scripts", "tests", "data/processed", "report"):
                (root / name).mkdir(parents=True)
            (root / "Makefile").write_bytes((ROOT / "Makefile").read_bytes())
            (root / "scripts/run_logged.sh").write_bytes(
                (ROOT / "scripts/run_logged.sh").read_bytes()
            )
            for name in ("scripts", "tests"):
                cache = root / name / "__pycache__"
                cache.mkdir()
                (cache / "example.pyc").write_bytes(b"cache")
            (root / "data/processed/example.pdf").write_bytes(b"pdf")
            (root / "report/report.pdf").write_bytes(b"pdf")
            subprocess.run(
                ["make", "clean"], cwd=root, capture_output=True, text=True, check=True,
            )
            self.assertFalse((root / "scripts/__pycache__").exists())
            self.assertFalse((root / "tests/__pycache__").exists())
            self.assertFalse((root / "data/processed/example.pdf").exists())
            self.assertFalse((root / "report/report.pdf").exists())
            self.assertTrue((root / "make.log").exists())


if __name__ == "__main__":
    unittest.main()
