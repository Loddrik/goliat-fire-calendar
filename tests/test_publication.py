import datetime as dt
import json
import math
import sys
import shutil
import subprocess
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from publication_contract import finite_json, season_window_predicate


class ContractTests(unittest.TestCase):
    def test_non_finite_diagnostics_are_explicitly_unavailable(self):
        unavailable = []
        value = finite_json({"a": math.inf, "b": [math.nan, 2.35]}, "params", unavailable)
        self.assertEqual(value, {"a": None, "b": [None, 2.35]})
        self.assertEqual(unavailable, ["params.a", "params.b[0]"])
        json.dumps(value, allow_nan=False)

    def test_cutoffs_use_the_elapsed_part_of_the_season(self):
        import duckdb
        con = duckdb.connect()
        dates = [dt.date(2022, 7, 1) + dt.timedelta(days=i) for i in range(365)]
        con.execute("create table days(acq_date date)")
        con.executemany("insert into days values (?)", [(d,) for d in dates])
        for month, day in [(7, 1), (11, 13), (12, 31), (1, 1), (3, 20), (6, 30)]:
            cutoff = dt.date(2022 if month >= 7 else 2023, month, day)
            result = con.execute(f"select acq_date from days where {season_window_predicate(month, day)} order by 1").fetchall()
            self.assertEqual([r[0] for r in result], [d for d in dates if d <= cutoff])
        with self.assertRaises(ValueError):
            season_window_predicate(13, 1)

    def test_all_published_accumulations_match_independent_daily_counts(self):
        import duckdb
        con = duckdb.connect()
        rows = con.execute(f"""
          select c.cut, c.season, c.acq_date from read_parquet('{ROOT}/data/processed/celldays.parquet') c
          where c.season >= 2012 and c.sat = case when c.season <= 2017 then 'SNPP' else 'NOAA20' end
          and not exists (select 1 from read_parquet('{ROOT}/data/processed/static_mask.parquet') s
                          where s.cell_x=c.cell_x and s.cell_y=c.cell_y)
        """).fetchall()
        index = json.loads((ROOT / 'web/public/data/index.json').read_text())
        cutoff = dt.date.fromisoformat(index['cutoff'])
        actual = Counter()
        for cut, season, day in rows:
            # Independent, date-based oracle; no SQL month predicate reused.
            end = dt.date(season if cutoff.month >= 7 else season + 1, cutoff.month, cutoff.day)
            if dt.date(season, 7, 1) <= day <= end:
                actual[cut, season] += 1
        for commune in index['comunas']:
            cut = commune['cut']
            doc = json.loads((ROOT / f'web/public/data/comunas/{cut}.json').read_text())
            sc = doc['season_compare']
            self.assertEqual(sc['current'], actual[cut, sc['season']])
            values = []
            for season, value in sc['observed_seasons'].items():
                self.assertEqual(value, actual[cut, int(season)])
                values.append(value)
            values.sort()
            self.assertEqual(sc['median'], values[min(len(values) - 1, int(.5 * len(values)))])
            self.assertEqual(commune['median'], sc['median'])


    def test_republishing_reordered_cell_days_keeps_all_commune_values_and_order(self):
        import pandas as pd
        source = ROOT / 'data/processed'
        published = ROOT / 'web/public/data/comunas'
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            pipeline = fixture / 'pipeline'; pipeline.mkdir()
            processed = fixture / 'data/processed'; processed.mkdir(parents=True)
            for name in ['publish.py', 'publication_contract.py']:
                shutil.copyfile(ROOT / 'pipeline' / name, pipeline / name)
            for name in ['params.json', 'gates.csv', 'comunas_biobio_nuble.geojson']:
                shutil.copyfile(source / name, processed / name)
            for name in ['celldays_comuna_month_masked.parquet', 'celldays_comuna_month.parquet',
                         'cells_comuna.parquet', 'static_mask.parquet', 'detections.parquet']:
                (processed / name).symlink_to(source / name)
            cells = pd.read_parquet(source / 'celldays.parquet')
            first = None
            for seed in [6114, 6115]:
                cells.sample(frac=1, random_state=seed).to_parquet(processed / 'celldays.parquet', index=False)
                result = subprocess.run([sys.executable, str(pipeline / 'publish.py')], cwd=fixture,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                current = {}
                for original in sorted(published.glob('*.json')):
                    old = json.loads(original.read_text())
                    expected = dict(old)
                    expected['recurrence'] = sorted(old['recurrence'], key=lambda row: (row['x'], row['y']))
                    actual = json.loads((fixture / 'web/public/data/comunas' / original.name).read_text())
                    self.assertEqual(actual, expected, original.name)
                    current[original.name] = actual
                self.assertEqual(len(current), 54)
                if first is not None: self.assertEqual(current, first)
                first = current


if __name__ == '__main__':
    unittest.main()
