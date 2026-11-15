import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
import context_cdf_audit as audit
from cold_region_audit import fit_source,predict_all,FEATURES


class ContextAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cuts=[f'08{i:03d}' for i in range(101,134)]+[f'16{i:03d}' for i in range(101,122)]
        cls.source=cls.cuts[:2];cls.origin=(2012,2013,2014,2015)
        x=pd.MultiIndex.from_product([cls.cuts,range(2012,2020),range(1,13)],names=['cut','season','m']).to_frame(index=False)
        x['g']=x.m.map(lambda m:'JJA' if m in (6,7,8) else str(m));x['aqua']=(x.season+x.m)%4;x['snpp']=2*x.aqua+x.season%2
        cls.panel=x;cls.model,_=fit_source(x,cls.source,cls.origin)
        cls.features=x[(x.season==2016)&(x.m==1)][FEATURES].copy().reset_index(drop=True)
        cls.contexts={c:{'available':True,'vector':np.eye(18)[i%3].tolist()} for i,c in enumerate(cls.cuts)}

    def setUp(self):
        # Synthetic fixtures must remain runnable after the historical experiment cap.
        deadline = patch.object(audit, "deadline_check", return_value=None)
        deadline.start()
        self.addCleanup(deadline.stop)

    def test_uniform_base_controls_and_real54_invariance_synthetic_labels(self):
        out,checks,diagnostics=audit.infer(self.features,self.model,self.contexts,self.cuts)
        old,_=predict_all(self.features,self.model,self.cuts)
        self.assertTrue(audit.verify_original21(out,old))
        proof=audit.check_invariance(self.panel,'type0',self.source,self.origin,self.features,self.model,self.contexts,self.cuts,out,self.model)
        self.assertTrue(proof['removed']['model_identical']);self.assertTrue(proof['changed']['all54_predictions_identical'])
        for c in checks:self.assertLessEqual(c['allocated_expected_risk'],c['baseline_expected_risk']+1e-8)
        for name in ['C00_coherent','C11_coherent','C00_proportional','C11_proportional']:self.assertAlmostEqual(out[name].sum(),out.B.sum(),places=9)
        with self.assertRaisesRegex(ValueError,'exact54'):audit.infer(self.features.iloc[:-1],self.model,self.contexts,self.cuts)

    def test_relative_gain_uses_equal_loss_means_not_mean_percentages(self):
        rows=[dict(regime=str(i),n=n,C00_mae=a,C11_mae=b,absolute_error_delta=n*(b-a)) for i,(n,a,b) in enumerate([(1,10,9),(2,1,2),(3,1,2),(4,1,2)])]
        r=audit.primary_summary(rows)
        self.assertAlmostEqual(r['equal_four_regime_delta_mae'],.5)
        self.assertAlmostEqual(r['relative_gain_from_equal_MAE'],-.5/3.25)
        self.assertAlmostEqual(r['row_weighted_delta_mae'],.8)

    def test_code_freeze_rejects_mutation_before_metrics(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);f=root/'source.py';f.write_text('version1')
            with patch.object(audit,'ROOT',root),patch.object(audit,'OUT',root/'outputs'),patch.object(audit,'CODE',[f]),patch.object(audit,'inputs',return_value=[f]):
                audit.freeze_code();audit.validate_freeze();f.write_text('changed')
                with self.assertRaisesRegex(ValueError,'changed'):audit.validate_freeze()

    def test_type0_both_sensors_before_cell_day_dedup_and_unknown_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)
            pd.DataFrame(dict(cell_x=[1,2],cell_y=[1,1],cut=[self.cuts[0],self.cuts[0]])).to_parquet(path/'cells_comuna.parquet',index=False)
            rows=[]
            for sat in ['Aqua','SNPP']:
                for typ in [1,0,0,None]:rows.append(dict(sat=sat,cell_x=1,cell_y=1,acq_date=pd.Timestamp('2012-07-04'),type=typ))
                rows.append(dict(sat=sat,cell_x=2,cell_y=1,acq_date=pd.Timestamp('2012-07-04'),type=None))
            con=duckdb.connect();con.register('det',pd.DataFrame(rows));data=SimpleNamespace(con=con,cuts=self.cuts)
            with patch.object(audit,'DATA',path):x=audit.load_type0_panel(data,set())
            selected=x[(x.cut==self.cuts[0])&(x.season==2012)&(x.m==7)]
            self.assertEqual(selected.aqua.iloc[0],1);self.assertEqual(selected.snpp.iloc[0],1)
            self.assertEqual(len(x),5184)

    def test_context_loader_requires54_complete_compositions(self):
        f=pd.DataFrame([dict(cut=c,year=2010,geography='legacy',policy='retained',context_available=True,layout_valid=True) for c in self.cuts])
        rows=[dict(cut=c,year=2010,geography='legacy',policy='retained',class_code=str(k),fraction_total=1. if k=='1' else 0.) for c in self.cuts for k in [*map(str,range(1,18)),'unknown']]
        c=pd.DataFrame(rows);self.assertEqual(len(audit.contexts_for_year(2010,f,c)),54)
        with self.assertRaisesRegex(ValueError,'incomplete'):audit.contexts_for_year(2010,f,c.iloc[:-1])


if __name__=='__main__':unittest.main()
