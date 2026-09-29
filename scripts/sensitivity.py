from pathlib import Path
import sys,csv,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.realization import realized_family
from src.envelope import PacketError,age_inverse,gap
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
spec=[('J',np.linspace(10,80,15),40.,'Road jerk bound (m/s³)'),('tau',np.linspace(.4,1.2,17),.8,'Lag upper bound (s)'),('kin',np.linspace(0,.3,13),.15,'Kinematic residual (m/s²)'),('ubar',np.linspace(.6,1.2,19),.9,'Demand sector cap')]
rows=[]
for case,v,grade in [('level16',16.,0.),('descent15',15.,-.03)]:
 for par,values,baseline,label in spec:
  for x in values:
   settings=dict(J=40.,tau=.8,kin=.15,ubar=.9);settings[par]=float(x)
   co,status=realized_family([34000.],v,.65,8.,.001,grade,tau=settings['tau'],kin=settings['kin'],ubar=settings['ubar'])
   errors=PacketError(jerk=settings['J']);br=co.braking() if co else None
   t,admission=age_inverse(110.,v,v,br,errors=errors)
   rows.append(dict(case=case,v_mps=v,grade=grade,parameter=par,value=float(x),baseline=baseline,**settings,fresh_gap_m=gap(0,v,v,br,errors=errors),Tmax_s=t,admission=admission,physical_status=status,b_mps2=co.b if co else math.nan,rho_s=co.rho if co else math.nan,peak_speed_mps=co.peak_speed if co else math.nan))
with (R/'certificate_sensitivity_v5.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
# Plot only CSV-reloaded values.
with (R/'certificate_sensitivity_v5.csv').open() as f:data=list(csv.DictReader(f))
fig,axes=plt.subplots(2,4,figsize=(7.2,4.25),constrained_layout=True)
for j,(par,values,base,label) in enumerate(spec):
 for case,ls,mk,clr,leg in [('level16','-','o','#235b8e','16 m/s, level'),('descent15','--','^','#a04b23','15 m/s, -3% grade')]:
  rr=[r for r in data if r['case']==case and r['parameter']==par];xx=[float(r['value']) for r in rr]
  tt=np.array([float(r['Tmax_s']) for r in rr]);gg=np.array([float(r['fresh_gap_m']) for r in rr])
  axes[0,j].plot(xx,tt,color=clr,ls=ls,marker=mk,markevery=3,ms=3,mfc='none',label=leg)
  axes[0,j].scatter(np.array(xx)[np.isnan(tt)],np.full(np.isnan(tt).sum(),-.07),marker='x',color=clr,s=15)
  axes[1,j].plot(xx,np.where(np.isfinite(gg),gg,np.nan),color=clr,ls=ls,marker=mk,markevery=3,ms=3,mfc='none')
 for ax in axes[:,j]:ax.axvline(base,color='.4',ls=':',lw=.7);ax.grid(alpha=.15)
 axes[0,j].set(ylim=(-.13,1.08),title=par if par!='kin' else 'epsilon_kin')
 axes[1,j].set(xlabel=label)
 axes[1,j].axhline(110,color='.5',ls=':',lw=.8)
axes[0,0].set_ylabel('Admissible age (s)');axes[1,0].set_ylabel('Fresh required gap (m)')
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=2)
fig.savefig(R/'certificate_sensitivity_v5.pdf');fig.savefig(R/'figures_v5/certificate_sensitivity_v5.png',dpi=180)
summary=[]
for case in ['level16','descent15']:
 for par,_,_,_ in spec:
  rr=[r for r in rows if r['case']==case and r['parameter']==par]
  summary.append({'case':case,'parameter':par,'first':rr[0],'last':rr[-1],'fresh_gap_span_m':max(r['fresh_gap_m'] for r in rr)-min(r['fresh_gap_m'] for r in rr),'states':sorted(set(r['admission'] for r in rr))})
(R/'results_processed_v5/sensitivity_summary.json').write_text(json.dumps(summary,indent=2))
lines=[r'\begin{tabular}{llrr}',r'\toprule',r'Case & Contract range & Fresh gap (m) & Age (s)\\\midrule']
for s in summary:
 a,b=s['first'],s['last']
 def age(r):return 'reject' if not math.isfinite(r['Tmax_s']) else f"{r['Tmax_s']:.3f}"+('c' if r['admission']=='age_cap' else '')
 tag={'J':'$J$','tau':r'$\bar\tau$','kin':r'$\epsilon_{\rm kin}$','ubar':r'$\bar u$'}[s['parameter']]
 case_label={'level16':'16 m/s, level','descent15':'15 m/s, descent'}[s['case']]
 lines.append(f"{case_label} & {tag}: {a['value']:g}--{b['value']:g} & {a['fresh_gap_m']:.2f} $\\to$ {b['fresh_gap_m']:.2f} & {age(a)} $\\to$ {age(b)}"+r'\\')
lines += [r'\bottomrule\end{tabular}']
(R/'tables_v5/sensitivity.tex').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps(summary,indent=2))
