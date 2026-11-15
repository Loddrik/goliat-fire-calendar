import copy
import sys
import unittest
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import box,Polygon

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from landcover_context_audit import polygon_weights,descriptor,validate_schema,grid_from_metadata,validate_pinned_metadata,transport_headers,PIXEL,RADIUS


class LandcoverContextTests(unittest.TestCase):
    def grid(self):return dict(ulx=0.,uly=2.,lrx=2.,lry=0.,dx=1.,dy=1.,nx=2,ny=2)

    def metadata(self):
        x=-20015109.354+12*2400*PIXEL;y=10007554.677-12*2400*PIXEL
        structure=f'XDim=2400\nYDim=2400\nUpperLeftPointMtrs=({x},{y})\nLowerRightMtrs=({x+2400*PIXEL},{y-2400*PIXEL})\nProjection=GCTP_SNSOID\nProjParams=({RADIUS},0,0,0,0,0,0,0,0,0,0,0,0)'
        return {'global_attributes':{'StructMetadata.0':structure,'identifier_product_doi':'10.5067/MODIS/MCD12Q1.061'},'SDS_attributes':{k:{'_FillValue':255,'valid_range':v} for k,v in {'LC_Type1':[1,17],'QC':[0,10],'LW':[1,2]}.items()}}

    def test_native_rectangles_fractional_border_not_center_assignment(self):
        p=box(.75,.25,1.25,1.75)
        r,c,a,m=polygon_weights(p,self.grid())
        self.assertEqual(len(a),4);np.testing.assert_allclose(a,[.1875]*4,atol=1e-14)
        self.assertAlmostEqual(sum(a),.75);self.assertEqual(m['partial_native_cells'],4)
        self.assertEqual(m['outside_tile_area_m2'],0)

    def test_full_cells_holes_and_outside_tile_close_without_repair(self):
        p=Polygon([(0,0),(2,0),(2,2),(0,2)],holes=[[(.5,.5),(1.5,.5),(1.5,1.5),(.5,1.5)]])
        r,c,a,m=polygon_weights(p,self.grid());self.assertAlmostEqual(sum(a),3.)
        r,c,a,m=polygon_weights(box(-1,0,1,2),self.grid())
        self.assertAlmostEqual(sum(a),2);self.assertAlmostEqual(m['outside_tile_area_m2'],2)
        row,classes,reasons=descriptor(np.array([1]*len(a)),np.array([0]*len(a)),np.array([2]*len(a)),a,4.,2.,'retained')
        self.assertAlmostEqual(row['forest_fraction_total'],.5);self.assertAlmostEqual(row['unknown_fraction'],.5)
        self.assertFalse(row['context_available'])
        invalid=Polygon([(0,0),(2,2),(0,2),(2,0)])
        with self.assertRaisesRegex(ValueError,'no repair'):polygon_weights(invalid,self.grid())

    def test_fractional_coast_keeps_water_and_land_denominators_separate(self):
        r,c,a,g=polygon_weights(box(.25,0,1.5,1),self.grid())
        lc=np.where(c==0,17,12);qc=np.where(c==0,2,0);lw=np.where(c==0,1,2)
        primary,classes,_=descriptor(lc,qc,lw,a,1.25,0.,'retained')
        self.assertAlmostEqual(primary['crop_fraction_total'],.4)
        self.assertAlmostEqual(next(v['fraction_total'] for v in classes if v['class_code']==17),.6)
        self.assertAlmostEqual(primary['crop_fraction_classified_land'],1.)
        strict,_,_=descriptor(lc,qc,lw,a,1.25,0.,'QC0')
        self.assertAlmostEqual(strict['unknown_fraction'],.6)
        self.assertFalse(strict['context_available'])

    def test_QC1_barren_and_QC3_QC10_fill_stay_unknown(self):
        lc=np.array([16,17,1,255,12,14,13]);qc=np.array([1,3,10,0,8,9,2]);lw=np.array([2,1,255,255,2,2,255])
        row,classes,reasons=descriptor(lc,qc,lw,np.ones(7),7.,0.,'retained')
        self.assertAlmostEqual(row['unknown_fraction'],4/7)
        self.assertEqual(next(r['area_m2'] for r in classes if r['class_code']==16),0)
        self.assertAlmostEqual(row['crop_fraction_total'],1/7);self.assertAlmostEqual(row['mosaic_fraction_total'],1/7)
        self.assertAlmostEqual(row['urban_fraction_total'],1/7) # LW255 is diagnostic only.
        self.assertAlmostEqual(sum(r['fraction_total'] for r in classes),1.)
        self.assertEqual(set(reasons),{'outside_tile','LC_fill','QC_1','QC_3','QC_10'})

    def test_QC0_is_separate_sensitivity_and_zero_land_returns_NA(self):
        row,classes,_=descriptor(np.array([17,1,12]),np.array([2,9,255]),np.array([1,2,2]),np.ones(3),3.,0.,'QC0')
        self.assertEqual(row['retained_fraction'],0);self.assertIsNone(row['forest_fraction_classified_land'])
        self.assertEqual(row['unknown_fraction'],1)
        water,_,_=descriptor(np.array([17]),np.array([2]),np.array([1]),np.array([1.]),1.,0.,'retained')
        self.assertTrue(water['context_available']);self.assertIsNone(water['crop_fraction_classified_land'])

    def test_threshold_and_no_three_feature_renormalization(self):
        row,classes,_=descriptor(np.array([1,12,13,14,10,255]),np.zeros(6,dtype=int),np.full(6,2),np.array([10.,10.,10.,20.,45.,5.]),100.,0.,'retained')
        self.assertTrue(row['context_available']);self.assertAlmostEqual(row['retained_fraction'],.95)
        self.assertAlmostEqual(sum(row[k+'_fraction_total'] for k in ['forest','crop','urban']),.3)
        self.assertAlmostEqual(row['mosaic_fraction_total'],.2)
        self.assertEqual(len(classes),18)

    def test_actual_schema_CRS_ranges_and_unknown_codes_rejected(self):
        arrays={k:np.ones((2400,2400),dtype='uint8') for k in ['LC_Type1','QC','LW']};meta=self.metadata()
        g=validate_schema(arrays,meta);self.assertAlmostEqual(g['dx'],PIXEL,places=6)
        arrays['LC_Type1'][0,0]=0
        with self.assertRaisesRegex(ValueError,'categorical code'):validate_schema(arrays,meta)
        arrays['LC_Type1'][0,0]=1
        broken=copy.deepcopy(meta);broken['global_attributes']['StructMetadata.0']=broken['global_attributes']['StructMetadata.0'].replace('GCTP_SNSOID','GCTP_GEO')
        with self.assertRaisesRegex(ValueError,'CRS'):validate_schema(arrays,broken)
        broken=copy.deepcopy(meta);broken['SDS_attributes']['QC']['_FillValue']=0
        with self.assertRaisesRegex(ValueError,'fill'):validate_schema(arrays,broken)
        broken=copy.deepcopy(meta);broken['SDS_attributes']['QC']['valid_range']=[0,255]
        with self.assertRaisesRegex(ValueError,'valid_range'):validate_schema(arrays,broken)
        broken=copy.deepcopy(meta);broken['global_attributes']['identifier_product_doi']='10.5067/MODIS/MCD12Q1.006'
        with self.assertRaisesRegex(ValueError,'DOI'):validate_schema(arrays,broken)

    def test_native_granule_year_identity_and_bearer_host_scope(self):
        filename='MCD12Q1.A2010001.h12v12.061.example.hdf'
        values={'SHORTNAME':'MCD12Q1','VERSIONID':'61','RANGEBEGINNINGDATE':'2010-01-01','RANGEENDINGDATE':'2010-12-31','LOCALGRANULEID':filename}
        core='\n'.join('OBJECT = '+k+'\nVALUE = "'+v+'"\nEND_OBJECT = '+k for k,v in values.items())
        meta={'file':filename,'global_attributes':{'CoreMetadata.0':core}}
        pin={'producer_granule_id':filename[:-4],'nominal_year':2010}
        self.assertTrue(validate_pinned_metadata(meta,pin)['native_dates_verified'])
        bad=copy.deepcopy(meta);bad['global_attributes']['CoreMetadata.0']=core.replace('2010-12-31','2011-12-31')
        with self.assertRaisesRegex(ValueError,'dates'):validate_pinned_metadata(bad,pin)
        self.assertIn('Authorization',transport_headers('data.lpdaac.earthdatacloud.nasa.gov','synthetic'))
        for host in ['d1nklfio7vscoe.cloudfront.net','urs.earthdata.nasa.gov','evil.example','data.lpdaac.earthdatacloud.nasa.gov.evil.example']:
            self.assertNotIn('Authorization',transport_headers(host,'synthetic'))

    def test_unexpected_categories_or_nonclosing_weights_fail(self):
        with self.assertRaisesRegex(ValueError,'Unexpected category'):
            descriptor(np.array([0]),np.array([0]),np.array([2]),np.array([1.]),1.,0.,'retained')
        with self.assertRaisesRegex(ValueError,'do not close'):
            descriptor(np.array([1]),np.array([0]),np.array([2]),np.array([1.]),2.,0.,'retained')


if __name__=='__main__':unittest.main()
