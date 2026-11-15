import sys
import unittest
from pathlib import Path

import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from training_size_audit import cases,MaskContract,require_same_target,mask_digest


class SourceSpy:
    def __init__(self):self.calls=[]
    def monthly(self,policy,allowed):self.calls.append((policy,allowed));return 'frame'
    def fit_mask(self,allowed):self.calls.append(('mask',allowed));return {(1,2),(3,4)}


class TrainingSizeTests(unittest.TestCase):
    def test_design_contains_all_subsets_and_keeps_destinations_disjoint(self):
        design=cases();self.assertEqual(len(design),64)
        for policy in ['pre_overlap','fold_fitted']:
            for direction in ['forward','backward']:
                group=[c for c in design if c['direction']==direction and c['mask_policy']==policy]
                short=[c for c in group if c['n_train']==4];full=[c for c in group if c['n_train']==6]
                self.assertEqual(len(short),15);self.assertEqual(len(full),1)
                # Each of the six origin seasons occurs in 10 of the 15 four-season subsets.
                self.assertEqual({s:sum(s in c['origin'] for c in short) for s in full[0]['origin']},
                                 {s:10 for s in full[0]['origin']})
                for c in group:self.assertFalse(set(c['origin'])&set(c['destination']))

    def test_pre_overlap_contract_cannot_use_origin_or_destination(self):
        source=SourceSpy();wrapper=MaskContract(source,'pre_overlap')
        wrapper.monthly('fold_fitted',(2014,2015,2016,2017));wrapper.mask((2014,2015,2016,2017))
        self.assertEqual(source.calls,[('pre_overlap',()),('mask',())])
        self.assertEqual(wrapper.calls,[(2014,2015,2016,2017)])
        with self.assertRaises(ValueError):MaskContract(source,'published_fixed')

    def test_fold_fitted_contract_keeps_allowed_seasons(self):
        source=SourceSpy();wrapper=MaskContract(source,'fold_fitted');allowed=(2014,2015,2016)
        wrapper.monthly('fold_fitted',allowed);wrapper.mask(allowed)
        self.assertEqual(source.calls,[('fold_fitted',allowed),('mask',allowed)])

    def test_target_guard_ignores_order_but_rejects_changed_measurement(self):
        frame=pd.DataFrame({'cut':['A','B'],'season':[2012,2012],'m':[7,7],'aqua':[1.,2.],'snpp':[2.,3.]})
        require_same_target(frame,frame.iloc[::-1])
        changed=frame.copy();changed.loc[0,'snpp']=99
        with self.assertRaises(ValueError):require_same_target(frame,changed)
        self.assertEqual(mask_digest({(1,2),(3,4)}),mask_digest({(3,4),(1,2)}))


if __name__=='__main__':unittest.main()
