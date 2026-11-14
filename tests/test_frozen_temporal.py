import sys
import unittest
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from frozen_temporal_audit import freeze,signature,estimate,join_oof,calibrate_radii,calendar_labels,requested_modis_days,BAND_POLICIES,bands,verify_legacy_controls,write_frozen,load_frozen
from scientific_audit import TRAIN,KAPPAS
from affine_experiment import LAMBDAS as B_LAMBDAS,b_name
from robust_affine_experiment import LAMBDAS as H_LAMBDAS,DELTAS,name as h_name
from piecewise_experiment import name as p_name


def past_fixture():
    tr=pd.DataFrame([{'cut':cut,'season':s,'m':m,'g':'JJA' if m in (6,7,8) else str(m),
        'aqua':float(1+(s+m)%5),'snpp':float(2*((s+m)%5)+1+(cut=='B'))}
        for cut in ['A','B'] for s in TRAIN for m in range(1,13)])
    oof=tr.copy();oof['M1']=2*oof.aqua
    for k in KAPPAS:oof['A_'+str(k)]=oof.M1
    for l in B_LAMBDAS:oof[b_name(l)]=oof.M1+.2;oof[p_name(l)]=oof.M1-.1
    for d in DELTAS:
        for l in H_LAMBDAS:oof[h_name(d,l)]=oof.M1+.1
    for p in BAND_POLICIES:
        if p!='M1':oof[p]=oof.M1
    return tr,oof


class FrozenTemporalTests(unittest.TestCase):
    def test_future_targets_do_not_change_estimates_radii_or_frozen_signature(self):
        tr,oof=past_fixture();model=freeze(tr,oof);before=signature(model)
        future=tr[tr.season==2012].copy();future.season=2020
        a=estimate(future,model);future.snpp=1e9;b=estimate(future,model)
        self.assertEqual(signature(model),before)
        for col in [*BAND_POLICIES,*[p+'_abs80_radius' for p in BAND_POLICIES]]:
            np.testing.assert_array_equal(a[col],b[col])

    def test_saved_coefficients_restore_exactly_and_reject_tampering(self):
        tr,oof=past_fixture();model=freeze(tr,oof)
        future=tr[tr.season==2012].copy();future.season=2020
        with tempfile.TemporaryDirectory() as d:
            write_frozen(model,d);restored=load_frozen(d)
            self.assertEqual(signature(model),signature(restored))
            pd.testing.assert_frame_equal(estimate(future,model),estimate(future,restored))
            p=Path(d)/'frozen_affine.csv';p.write_text(p.read_text()+'\n')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):load_frozen(d)

    def test_training_or_selection_cannot_contain_future_seasons(self):
        tr,oof=past_fixture();bad=tr.copy();bad.loc[0,'season']=2020
        with self.assertRaisesRegex(ValueError,'2012'):freeze(bad,oof)
        bad=oof.copy();bad.loc[0,'season']=2020
        with self.assertRaisesRegex(ValueError,'2012'):freeze(tr,bad)
        bad=oof.copy();bad.loc[0,'B_1']=np.nan
        with self.assertRaisesRegex(ValueError,'Nonfinite'):freeze(tr,bad)

    def test_oof_join_rejects_key_control_and_duplicate_differences(self):
        _,oof=past_fixture();merged=join_oof(oof,oof.iloc[::-1]);self.assertEqual(len(merged),len(oof))
        bad=oof.copy();bad.loc[0,'snpp']+=1
        with self.assertRaisesRegex(ValueError,'control'):join_oof(oof,bad)
        with self.assertRaisesRegex(ValueError,'Duplicated'):join_oof(oof,pd.concat([oof,oof.iloc[:1]]))
        with self.assertRaisesRegex(ValueError,'keys'):join_oof(oof,oof.iloc[1:])

    def test_radius_uses_nested_policy_errors_only_in_active_past_months(self):
        frame=pd.DataFrame({'cut':['A']*3,'snpp':[0.,2.,4.]})
        for p in BAND_POLICIES:frame[p]=[999.,1.,1.]
        radii=calibrate_radii(frame)
        self.assertTrue(radii.n_active_calibration.eq(2).all())
        np.testing.assert_allclose(radii.abs80_radius,2.6)

    def test_orbit_transition_uses_calendar_year_not_season_label(self):
        f=pd.DataFrame({'season':[2020,2020,2020,2021,2021,2022], 'm':[8,9,10,12,1,7]})
        x=calendar_labels(f)
        self.assertEqual(len(x),4)
        self.assertEqual(x[x.y==2022].orbit_epoch.unique().tolist(),['calendar_2022_onward'])
        transition=x[(x.season==2021)&(x.m==1)].iloc[0]
        self.assertEqual(transition.block,'legacy_2020_2021');self.assertEqual(transition.y,2022)
        self.assertEqual(x[(x.season==2021)&(x.m==12)].orbit_epoch.iloc[0],'before_calendar_2022')

    def test_modis_source_windows_are_requested_days_not_detection_dates(self):
        days=requested_modis_days(['data/raw/firms_country/modis/modis_2020_Chile.csv','data/raw/firms_api/MODIS_SP/MODIS_SP_2021-01-01_5d.csv'])
        self.assertEqual(len(days),371)
        from datetime import date
        self.assertIn(date(2020,2,29),days);self.assertIn(date(2021,1,5),days);self.assertNotIn(date(2021,1,6),days)

    def test_legacy_control_guard_rejects_changed_observed_target(self):
        frame=pd.DataFrame({'cut':['A','A'],'aqua':[1.,2.],'snpp':[2.,4.],
                            'M0':[1.,2.],'M1':[2.,4.],'M2':[3.,3.]})
        previous=pd.DataFrame({'cut':['A']*3,'method':['M0','M1','M2'],
            'mae':[1.5,0.,1.],'bias':[-1.5,0.,0.],'n':[2]*3,'aqua_sum':[3.]*3})
        verify_legacy_controls(frame,previous)
        frame['A_100']=frame.M1
        extra=pd.DataFrame({'cut':['A'],'method':['A_k'],'mae':[0.],'bias':[0.],'n':[2],'aqua_sum':[3.]})
        verify_legacy_controls(frame,pd.concat([previous,extra]),100.)
        frame.loc[0,'snpp']=3.
        with self.assertRaisesRegex(ValueError,'controls'):verify_legacy_controls(frame,previous)

    def test_coverage_reports_denominator_and_clips_at_zero(self):
        f=pd.DataFrame({'cut':['A','A'],'M1':[0.,4.],'snpp':[0.,6.],'published_mae_radius':[1.,1.]})
        for p in BAND_POLICIES:
            f[p]=f.M1;f[p+'_abs80_radius']=1.
        report=bands(f,['A']);r=report['M1_nested_abs80']['all54']
        self.assertEqual(r['all_months']['n'],2);self.assertEqual(r['all_months']['coverage'],.5)
        self.assertEqual(r['active_months']['coverage'],0.)
        self.assertEqual(r['all_months']['mean_width'],1.5)


if __name__=='__main__':unittest.main()
