"""Render a static scientific overview from saved research outputs, no fitting."""
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.runtime/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def render():
 data=ROOT/'data/processed';out=ROOT/'docs/reviews/figures';out.mkdir(parents=True,exist_ok=True)
 read=lambda d:json.loads((data/d/'summary.json').read_text())
 a,h,p=read('affine_audit'),read('robust_affine_audit'),read('piecewise_audit')
 labels=['M1','M1/B','M1/H','M1/B/P'];values=[a['scores']['M1']['mean_monthly_mae'],a['scores']['M1_B']['mean_monthly_mae'],h['scores']['M1_H']['mean_monthly_mae'],p['scores']['M1_B_P']['mean_monthly_mae']]
 colors=['#596875','#087c82','#b75c18','#7256a6'];plt.rcParams.update({'font.size':10,'svg.hashsalt':'goliat-research-overview-20261114'})
 fig,axes=plt.subplots(1,3,figsize=(17,5.5),layout='constrained')
 ax=axes[0]
 for i,(label,value,color) in enumerate(zip(labels,values,colors)):
  ax.scatter(value,i,color=color,s=70);ax.annotate(f'{value:.4f}',(value,i),xytext=(8,0),textcoords='offset points',va='center')
 ax.set(yticks=range(4),yticklabels=labels,xlim=(1.84,2.10),ylim=(3.5,-.5),xlabel='MAE mensual [celdas-día]',title='1. Comparación anidada\n54 comunas, 8 temporadas')
 ax.grid(axis='x',alpha=.2)
 transport=read('temporal_transport_audit')['directions'];ax=axes[1]
 for i,(method,label,color) in enumerate(zip(['M1_B','M1_H','M1_B_P'],labels[1:],colors[1:])):
  gains=[]
  for direction in ['forward','backward']:
   scores=transport[direction]['scores'];gains.append(100*(1-scores[method]['mean_monthly_mae']/scores['M1']['mean_monthly_mae']))
  ax.plot(gains,[i-.12,i+.12],color=color,alpha=.35)
  ax.scatter(gains[0],i-.12,color=color,marker='o',s=65,label='Hacia adelante' if i==0 else None)
  ax.scatter(gains[1],i+.12,color=color,marker='X',s=70,label='Hacia atrás' if i==0 else None)
 ax.axvline(0,color='#596875',lw=1)
 ax.set(yticks=range(3),yticklabels=labels[1:],ylim=(2.5,-.5),xlabel='Reducción de MAE frente a M1 [%]',title='2. Transporte temporal\n4 temporadas de origen → 4 de destino')
 ax.grid(axis='x',alpha=.2);ax.legend(loc='lower right',fontsize=8)
 f=pd.read_csv(data/'interval_loss_fit_audit/metrics.csv');g=f[(f.period=='nested_2012_2019')&(f.territory=='all54')&(f.policy=='M1_B')]
 ax=axes[2];names={'empirical_quantiles':'Cuantiles','minimum_interval_score':'Ajuste IS','symmetric_active_reference':'Simétrica'}
 for mode,cohort,color,marker in [('empirical_quantiles','active','#acb3bb','o'),('empirical_quantiles','all_months','#acb3bb','s'),('minimum_interval_score','active','#087c82','o'),('minimum_interval_score','all_months','#087c82','s'),('symmetric_active_reference','active','#b75c18','D')]:
  x=g[(g.fit_mode==mode)&(g.calibration_cohort==cohort)];r=x[x.population=='all_months'].iloc[0];active=x[x.population=='active_months'].iloc[0]
  name=names[mode]+('/activos' if cohort=='active' else '/todos')
  ax.scatter(r.mean_width,r.mean_interval_score,color=color,marker=marker,s=65)
  offset=(-10,7) if mode=='symmetric_active_reference' else ((7,-30) if mode=='minimum_interval_score' and cohort=='all_months' else (7,6))
  ax.annotate(f'{name}\nCobertura activa {100*active.coverage:.1f} %',(r.mean_width,r.mean_interval_score),xytext=offset,textcoords='offset points',fontsize=8,ha='right' if mode=='symmetric_active_reference' else 'left')
 ax.set(xlim=(4.15,7.5),ylim=(8.65,11.1),xlabel='Anchura media en todos los meses [celdas-día]',ylabel='IS medio en todos los meses [celdas-día]',title='3. Bandas M1/B: precisión y anchura\nAnidado; cobertura frente a S-NPP')
 ax.grid(alpha=.2)
 fig.suptitle('Evidencia retrospectiva: una mejora media no garantiza transporte ni cobertura',fontsize=14)
 fig.savefig(out/'research-overview.png',dpi=170,metadata={'Software':'GOLIAT'})
 fig.savefig(out/'research-overview.svg',metadata={'Date':None,'Creator':'GOLIAT'})
 plt.close(fig)
 return out

if __name__=='__main__':print(render())
