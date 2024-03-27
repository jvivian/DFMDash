import unittest
from pathlib import Path
from covid19_drdfm.dfm import ModelRunner
from anndata import AnnData
from covid19_drdfm.covid19 import get_project_h5ad
from covid19_drdfm.io import DataLoader

COLUMNS = ["PCE", "CPIU", "Hosp1", "Deaths1"]
STATES = ["AK", "CA"]


class TestModelRunner(unittest.TestCase):
    def setUp(self):
        # Create a dummy AnnData object for testing
        self.ad = get_project_h5ad()
        self.ad = self.ad[self.ad.obs.State.isin(STATES), :]
        self.outdir = Path("./test-output")
        self.batch = "State"
        self.model_runner = ModelRunner(self.ad, self.outdir, self.batch)

    def test_init(self):
        self.assertIsInstance(self.model_runner.ad, AnnData)
        self.assertEqual(self.model_runner.outdir, self.outdir)
        self.assertEqual(self.model_runner.batch, self.batch)

    def test_run(self):
        maxiter = 1000
        global_multiplier = 1
        result = self.model_runner.run(maxiter, global_multiplier, COLUMNS)
        self.assertIsInstance(result, ModelRunner)

    def test_write_failures(self):
        self.model_runner.failures = {"Test": "Test-Failure!"}
        self.model_runner.write_failures()
        assert (self.model_runner.outdir / "failed.txt").exists()

    def test_get_batches(self):
        batches = self.model_runner.get_batches()
        self.assertIsInstance(batches, dict)


if __name__ == "__main__":
    unittest.main()
