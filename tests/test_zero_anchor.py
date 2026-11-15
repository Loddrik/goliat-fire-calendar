import json
from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from zero_anchor_experiment import add_anchors,choose,apply_choices,fit_origin,raw_predict,transport,freeze,restore,verify_controls,oracle_bound,KEYS,METHODS
from scientific_audit import CANDIDATES,TRAIN
from affine_experiment import LAMBDAS,b_name
from test_frozen_temporal import past_fixture

class Data:
 def __init__(self):
  self.frame=past_fixture()[0];self.frame.loc[(self.frame.season+self.frame.m)%4==0,'aqua']=0.;self.calls=[]
 def monthly(self,policy,allowed):self.calls.append(tuple(allowed));return self.frame.copy()

class ZeroAnchorTests(unittest.TestCase):
 def test_anchor_preserves_every_positive_and_zeros_only_predictor_zero(self):
  x=pd.DataFrame({'aqua':[0.,1.,10.]})
  for lam in LAMBDAS:x[b_name(lam)]=[1.,2.+lam,15.+lam]
  y=add_anchors(x)
  for lam in LAMBDAS:
   self.assertEqual(y[f'Z_{lam:g}'].iloc[0],0.)
   np.testing.assert_array_equal(y[f'Z_{lam:g}'].iloc[1:],x[b_name(lam)].iloc[1:])

 def test_locked_selection_keeps_original_lambda_and_strictly_improves_gate(self):
  x=pd.DataFrame({'cut':['A']*4,'aqua':[0.,0.,2.,3.],'snpp':[0.,0.,4.,6.],'M1':[0.,0.,2.,3.]})
  for c in CANDIDATES:
   if c!='M1':x[c]=x.M1
  for lam in LAMBDAS:x[b_name(lam)]=[.2,.2,4.,6.]
  choices,_=choose(add_anchors(x));self.assertEqual(choices['M1_B']['A'],'B_10');self.assertEqual(choices['Z_locked']['A'],'Z_10');self.assertEqual(choices['B_Z_locked']['A'],'Z_10')

 def test_real_fit_interface_excludes_outer_targets_from_all_choices(self):
  data=Data();origin=tuple(s for s in TRAIN if s!=2012)
  a,_,ma,_=transport(data,origin,(2012,));self.assertEqual(len(data.calls),8)
  self.assertTrue(all(2012 not in c for c in data.calls))
  data.frame.loc[data.frame.season==2012,'snpp']=1e9
  b,_,mb,_=transport(data,origin,(2012,));self.assertEqual(ma['choices'],mb['choices'])
  np.testing.assert_array_equal(a[list(METHODS)],b[list(METHODS)])

 def test_full_frozen_model_restores_exact_points_and_ignores_target(self):
  data=Data()
  full,model=fit_origin(data,TRAIN);raw=raw_predict(full,model);model['choices']=choose(raw)[0]
  frozen=freeze(model);restored=restore(json.loads(json.dumps(frozen,allow_nan=False)))
  future=full[full.season==2012].copy();future.season=2020
  expected=apply_choices(raw_predict(future,model),model['choices'])
  for changed in [future.assign(snpp=np.nan),future.assign(snpp=1e9),future.drop(columns='snpp')]:
   actual=apply_choices(raw_predict(changed,restored),restored['choices'])
   np.testing.assert_array_equal(expected[list(METHODS)],actual[list(METHODS)])
  partial=dict(model,training_seasons=[2012,2013,2014])
  with self.assertRaisesRegex(ValueError,'full'):freeze(partial)

 def test_control_guard_rejects_changed_target_and_duplicate_keys(self):
  data=Data();full,model=fit_origin(data,TRAIN);model['choices']=choose(raw_predict(full,model))[0]
  point=apply_choices(raw_predict(full,model),model['choices']);verify_controls(point,point)
  altered=point.copy();altered.loc[0,'snpp']+=1
  with self.assertRaisesRegex(ValueError,'Control differs'):verify_controls(point,altered)
  with self.assertRaisesRegex(ValueError,'Duplicate'):raw_predict(pd.concat([full,full.iloc[:1]]),model)

 def test_oracle_is_only_a_retrospective_bound_not_a_fitted_prediction(self):
  x=pd.DataFrame({'aqua':[0.,0.,1.],'M1_B':[.5,.5,1.],'snpp':[0.,2.,3.]});before=x.copy(deep=True)
  bound=oracle_bound(x);self.assertLessEqual(bound['oracle_mae'],bound['baseline_mae']);self.assertAlmostEqual(bound['max_gain_mae'],.5/3)
  pd.testing.assert_frame_equal(x,before)

if __name__=='__main__':unittest.main()
