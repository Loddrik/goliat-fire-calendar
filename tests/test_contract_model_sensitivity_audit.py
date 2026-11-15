import csv
import hashlib
import io
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from contract_model_sensitivity_audit import validate_platform_csv, materiality, bounded_contrasts, fixed_populations, require_equal

class ContractSensitivityTests(unittest.TestCase):
    def fixture(self,platform='aqua-history',**changes):
        row=dict(cut_com='A',comuna='Name',acq_date='2020-07-01',instrument='MODIS' if platform=='aqua-history' else 'VIIRS',
            satellite='Aqua' if platform=='aqua-history' else 'N20',daynight='D',type='0',confidence='30' if platform=='aqua-history' else 'n',
            source_file='source.csv',version='v',longitude='-73.295',latitude='-36.805',grid_x='10670',grid_y='5319')
        from contract_gap_audit import observed_grid
        row['grid_x'],row['grid_y']=map(str,observed_grid(-73.295,-36.805));row.update(changes)
        buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(row));w.writeheader();w.writerow(row);payload=buf.getvalue().encode()
        segment=dict(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),rows=1)
        source=dict(id=platform,instrument='MODIS' if platform=='aqua-history' else 'VIIRS',available_years=[2020],versions=['v'],files=[dict(filename='source.csv',year=2020)])
        return payload,segment,dict(cut='A',name='Name'),source
    def test_two_platforms_and_boundaries(self):
        for platform in ['aqua-history','noaa20-history']:
            self.assertEqual(len(validate_platform_csv(*self.fixture(platform))),1)
        self.assertEqual(len(validate_platform_csv(*self.fixture(confidence='100'))),1)
    def test_wrong_platform_type_confidence_or_year_rejected(self):
        for changes in [dict(satellite='Terra'),dict(type='1'),dict(confidence='29'),dict(instrument='VIIRS'),dict(acq_date='2021-07-01')]:
            with self.assertRaises(ValueError):validate_platform_csv(*self.fixture(**changes))
        with self.assertRaises(ValueError):validate_platform_csv(*self.fixture('noaa20-history',confidence='l'))
    def test_hash_rejected(self):
        p,s,c,f=self.fixture()
        with self.assertRaises(ValueError):validate_platform_csv(p+b' ',s,c,f)
    def test_materiality_change_and_strict_inversion(self):
        self.assertTrue(materiality(-2,2,100)['material_sign_inversion'])
        self.assertFalse(materiality(-1,2,100)['material_sign_inversion'])
        self.assertTrue(materiality(-1,2,100)['sign_inversion'])
        self.assertTrue(materiality(0,1,100)['material_change'])
    def test_fixed_extremes_do_not_follow_target(self):
        f=pd.DataFrame(dict(Y_C=[50,49,0],Y_O=[49,50,0],aqua_C=[0,1,0]))
        p=fixed_populations(f)
        self.assertEqual(p['YC_50_plus_FIXED'].tolist(),[True,False,False])
        self.assertEqual(p['YO_50_plus_DIAGNOSTIC'].tolist(),[False,True,False])
    def test_bounds_both_axes_and_empty(self):
        f=pd.DataFrame(dict(Y_C=[2.,5],Y_O=[0.,6],E_coherent_C=[3.,1],E_coherent_O=[5.,2],M1_B_C=[2.,3],M1_B_O=[1.,6]))
        r=bounded_contrasts(f);self.assertEqual(r['target_bound'],3);self.assertEqual(r['input_bound'],3.5)
        self.assertEqual(bounded_contrasts(f.iloc[:0]),{'n':0})
    def test_identity_fails_on_unknown_not_zero_keys_and_values(self):
        f=pd.DataFrame(dict(cut=['A'],season=[2020],m=[7],x=[0.]))
        for g in [f.assign(x=np.nan),f.assign(x=1),f.assign(cut='B'),pd.concat([f,f])]:
            with self.assertRaises(ValueError):require_equal(f,g,['x'])

if __name__=='__main__':unittest.main()
