import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from hurdle_experiment import (choose,apply_choices,transport,verify_controls,probability_metrics,factorial,
    fit_predict,pack_model,write_model,load_model,model_signature,estimate_frozen,METHODS,HURDLE_METHODS,KAPPAS)
from affine_experiment import LAMBDAS,b_name,fit_affine
from scientific_audit import TRAIN,fit_models
from test_temporal_transport import FakeData


def candidates(y=(0.,),base=50.,estimate=49.):
    frame=pd.DataFrame({'cut':['A']*len(y),'snpp':y,'M1':[base*2]*len(y)})
    for lam in LAMBDAS:frame[b_name(lam)]=base
    for k in KAPPAS:frame[f'E11_{k}']=estimate
    return frame


def synthetic_predictions(frame):
    x=frame.copy();x['M0']=x.aqua;x['M1']=2*x.aqua;x['M2']=1.
    for lam in LAMBDAS:x[b_name(lam)]=x.M1+.2
    for method in HURDLE_METHODS:x[method]=x.M1+.1
    x['p_parent']=.7;x['p_local_10']=.8
    return x


class HurdleExperimentTests(unittest.TestCase):
    def test_selection_threshold_and_ties_keep_baseline_or_stronger_shrinkage(self):
        choices,_=choose(candidates(estimate=49.));self.assertEqual(choices['M1_B']['A'],'B_10');self.assertEqual(choices['B_E']['A'],'E11_30')
        choices,_=choose(candidates(estimate=49.5));self.assertEqual(choices['B_E']['A'],'B_10')
        frame=candidates(base=100.,estimate=101.)
        choices,_=choose(frame);self.assertEqual(choices['M1_B']['A'],'B_10');self.assertEqual(choices['B_E']['A'],'B_10')

    def test_nested_origin_excludes_destination_and_selection_ignores_its_labels(self):
        data=FakeData();held=2012;origin=tuple(s for s in TRAIN if s!=held);calls=[]
        def spy(data,allowed,destination):
            self.assertNotIn(held,allowed);self.assertFalse(set(allowed)&set(destination));calls.append((allowed,destination))
            return synthetic_predictions(data.frame[data.frame.season.isin(destination)]),pd.DataFrame(),{'allowed':list(allowed)}
        a,sa,pa,ma,record,la=transport(data,origin,(held,),fit=spy)
        self.assertEqual(len(calls),8);self.assertEqual(len(record),8)
        self.assertTrue(all(len(allowed)==6 for allowed,_ in calls[:-1]));self.assertEqual(calls[-1],(origin,(held,)))
        data.frame.loc[data.frame.season==held,'snpp']=1e9
        b,sb,pb,mb,_,lb=transport(data,origin,(held,),fit=spy)
        pd.testing.assert_frame_equal(sa,sb);pd.testing.assert_frame_equal(la,lb);self.assertEqual(ma,mb)
        np.testing.assert_array_equal(a[list(METHODS)],b[list(METHODS)])

    def test_probability_bins_include_endpoints_and_preserve_empty_bins(self):
        frame=pd.DataFrame({'snpp':[0.,1.,0.,1.,0.,1.],'p_parent':[0.,.2,.4,.6,.8,1.],
                            'p_local_10':[.5]*6})
        report=probability_metrics(frame)
        self.assertEqual([b['n'] for b in report['p_parent']['bins']],[1,1,1,1,2])
        self.assertAlmostEqual(report['p_parent']['brier'],np.mean((frame.p_parent-(frame.snpp>0))**2))
        self.assertEqual(report['p_local_10']['bins'][0]['n'],0);self.assertIsNone(report['p_local_10']['bins'][0]['positive_fraction'])
        frame['p_parent']=1.1
        with self.assertRaises(ValueError):probability_metrics(frame)

    def test_factorial_interaction_uses_same_rows_and_is_not_sum_of_percentages(self):
        frame=pd.DataFrame({'season':[2012,2013],'snpp':[0.,0.],
                            'E00_10':[4.,4.],'E10_10':[3.,3.],'E01_10':[2.,2.],'E11_10':[.5,.5]})
        result=factorial(frame)
        self.assertEqual(result['delta_probability'],-1.);self.assertEqual(result['delta_positive_distribution'],-2.)
        self.assertEqual(result['interaction'],-.5);self.assertEqual(len(result['per_season']),2)

    def test_control_guard_rejects_target_and_point_changes(self):
        data=FakeData();a=synthetic_predictions(data.frame);a['M1_B']=a.B_10
        verify_controls(a,a.iloc[::-1])
        b=a.copy();b.loc[0,'snpp']+=1
        with self.assertRaises(ValueError):verify_controls(a,b)
        b=a.copy();b.loc[0,'M1_B']+=1
        with self.assertRaises(ValueError):verify_controls(a,b)

    def test_saved_model_restores_and_future_labels_cannot_change_predictions(self):
        from hurdle_model import fit_hurdle
        data=FakeData();tr=data.frame;ref=fit_models(tr);affine=fit_affine(tr,ref);hurdle=fit_hurdle(tr,ref)
        raw=synthetic_predictions(tr);choices,_=choose(raw);model=pack_model(ref,affine,hurdle,choices)
        future=tr[tr.season==2012].copy();future.season=2020
        before=model_signature(model);expected=estimate_frozen(future,model)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'model.json';write_model(model,path);restored=load_model(path)
            self.assertEqual(model_signature(restored),before)
            pd.testing.assert_frame_equal(expected,estimate_frozen(future,restored))
            for variant in [future.assign(snpp=1e9),future.assign(snpp=np.nan),future.drop(columns='snpp')]:
                actual=estimate_frozen(variant,restored)
                np.testing.assert_array_equal(actual[list(METHODS)],expected[list(METHODS)])
                np.testing.assert_array_equal(actual[['p_parent','p_local_10']],expected[['p_parent','p_local_10']])
            import json
            wrapper=json.loads(path.read_text());wrapper['model']['r_const']+=1;path.write_text(json.dumps(wrapper))
            with self.assertRaisesRegex(ValueError,'hash mismatch'):load_model(path)
        self.assertEqual(model_signature(model),before)

    def test_real_fit_interface_fits_only_origin_and_never_reads_destination_target(self):
        data=FakeData();origin=(2012,2013,2014,2015);destination=(2016,2017,2018,2019)
        a,pa,ma=fit_predict(data,origin,destination)
        data.frame.loc[data.frame.season.isin(destination),'snpp']=1e9
        b,pb,mb=fit_predict(data,origin,destination)
        pd.testing.assert_frame_equal(pa,pb);self.assertEqual(ma,mb)
        np.testing.assert_array_equal(a[['M1',*HURDLE_METHODS,'p_parent','p_local_10']],b[['M1',*HURDLE_METHODS,'p_parent','p_local_10']])
        self.assertEqual(data.calls,[('fold_fitted',origin)]*2)


if __name__=='__main__':unittest.main()
