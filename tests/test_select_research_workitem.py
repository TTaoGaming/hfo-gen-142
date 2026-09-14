import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELECTOR = ROOT / "tools" / "select_research_workitem.py"


def task(wid, priority):
    return {
        "schema": "hfo.research-workitem.v1", "work_id": wid,
        "priority": priority, "admitted": True,
        "question": "q", "cloudflare_health_url": "https://example.invalid",
        "sources": [],
    }


class SelectorTest(unittest.TestCase):
    def run_selector(self, files, ledger=""):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); tasks = root / "tasks"; tasks.mkdir()
            for name, value in files.items():
                (tasks / name).write_text(json.dumps(value, indent=2), encoding="utf-8")
            retire = root / "retired.txt"; retire.write_text(ledger, encoding="utf-8")
            out = root / "selection.json"
            subprocess.run([sys.executable, str(SELECTOR), str(tasks), str(retire), str(out)], check=True, capture_output=True, text=True)
            return json.loads(out.read_text(encoding="utf-8")), tasks

    def test_priority_then_retirement_then_none(self):
        files = {"a.json": task("A", 200), "b.json": task("B", 100)}
        first, _ = self.run_selector(files)
        self.assertEqual(first["selected_work"]["work_id"], "A")
        marker_a = first["selected_work"]["marker"]
        second, _ = self.run_selector(files, marker_a)
        self.assertEqual(second["selected_work"]["work_id"], "B")
        marker_b = second["selected_work"]["marker"]
        third, _ = self.run_selector(files, marker_a + "\n" + marker_b)
        self.assertFalse(third["selected"])
        self.assertEqual(third["retired"], 2)

    def test_duplicate_work_id_fails(self):
        files = {"a.json": task("A", 1), "b.json": task("A", 2)}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); tasks = root / "tasks"; tasks.mkdir()
            for name, value in files.items():
                (tasks / name).write_text(json.dumps(value), encoding="utf-8")
            retire = root / "retired.txt"; retire.write_text("", encoding="utf-8")
            out = root / "selection.json"
            p = subprocess.run([sys.executable, str(SELECTOR), str(tasks), str(retire), str(out)], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)


if __name__ == "__main__":
    unittest.main()
