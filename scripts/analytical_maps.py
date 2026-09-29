from pathlib import Path
import sys,csv,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.realization import interface_result,sector,directional_lower
from src.envelope import age_inverse,gap,distance
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
NAMES=['ideal_identity','common_force','realized']
LABELS=['Ideal specific force','Ideal common force','Realized-force bound']
COLORS=['#3c78a8','#a66c24','#a83448']
def save(rows,path):
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)

rows=[];fig,axes=plt.subplots(2,2,figsize=(7.1,5),constrained_layout=True)
slices=[('Grade',[-0.,-.03,-.06]),('Friction',[.35,.55,.75]),('Wind',[0.,12.,22.]),('Mass',[24000.,34000.,44000.])]
for ax,(kind,values) in zip(axes.flat,slices):
    for j,val in enumerate(values):
        for name,color in zip(NAMES,COLORS):
            yy=[]
            for v in np.linspace(12,25,105):
                m=[34000.];mu=.65;wind=8.;grade=0.;kap=.001
                if kind=='Grade':grade=val
                if kind=='Friction':mu=val
                if kind=='Wind':wind=val
                if kind=='Mass':m=[val]
                b,status,detail=interface_result(name,m,v,mu,wind,kap,grade)
                age,admission=age_inverse(110,v,v,b)
                row=dict(slice=kind,slice_value=val,interface=name,v_mps=v,mu=mu,wind_mps=wind,grade=grade,mass_kg=m[0],Tmax_s=age,admission=admission,contract_status=status)
                row.update(detail)
                if b:row.update(b_mps2=b[0],rho_s=b[1],a_plus_mps2=b[2],D_stop_m=distance(v,*b),Dsafe_fresh_m=gap(0,v,v,b))
                rows.append(row);yy.append(age)
            # The common-force and identity curves coincide for singleton mass.
            if name!='common_force':
                vv=np.linspace(12,25,105);ax.plot(vv,yy,color=color,ls=['-','--',':'][j],lw=1.25,marker='o' if name=='ideal_identity' else '^',markevery=(j*3,13),markersize=3,markerfacecolor='none')
                bad=np.isnan(yy);ax.scatter(vv[bad][::12],np.full(len(vv[bad][::12]),-.035),color=color,marker='x',s=8)
    title={'Grade':'Grade (rise/run)','Friction':'Friction coefficient','Wind':'Wind (m/s)','Mass':'Mass (kg)'}[kind]
    ax.set(xlabel='Current road speed (m/s)',ylabel='Admissible age (s)',ylim=(-.07,1.04),title=title);ax.grid(alpha=.2)
    ax.legend([plt.Line2D([],[],color='#555555',ls=ls) for ls in ['-','--',':']],[f'{0 if x==0 else x:g}' for x in values],fontsize=6.5,loc='upper right')
fig.legend([plt.Line2D([],[],color=COLORS[0],marker='o',markerfacecolor='none'),plt.Line2D([],[],color=COLORS[2],marker='^',markerfacecolor='none')],[LABELS[0],LABELS[2]],loc='outside upper center',ncol=2)
fig.savefig(R/'figures_v5/fig3_v5.pdf');fig.savefig(R/'figures_v5/fig3_v5.png',dpi=180);plt.close(fig)
save(rows,R/'results_processed_v5/fig3_v5.csv')

rows=[];ages=np.linspace(0,1,101);mus=np.linspace(.15,.85,141)
fig,axes=plt.subplots(1,3,figsize=(7.1,3.1),constrained_layout=True)
for ax,name,label in zip(axes,NAMES,LABELS):
    z=np.full((len(mus),len(ages)),np.nan)
    for i,mu in enumerate(mus):
        b,status,detail=interface_result(name,[24000.,34000.,44000.],18.,mu,12.,.002,-.03)
        for j,age in enumerate(ages):
            ds=gap(age,18,18,b);head=(ds-5)/18 if math.isfinite(ds) else math.nan
            z[i,j]=head
            row=dict(interface=name,mu=mu,age_s=age,d_safe_m=ds if b else math.nan,h_min_s=head,contract_status=status)
            if b:row.update(detail);row.update(b_mps2=b[0],rho_s=b[1],a_plus_mps2=b[2],D_stop_m=distance(18.,*b))
            rows.append(row)
    cmap=plt.get_cmap('viridis').copy();cmap.set_bad('#eeeeee')
    im=ax.pcolormesh(ages,mus,z,cmap=cmap,vmin=4,vmax=20,shading='auto',rasterized=True,linewidth=0,antialiased=False)
    ax.contourf(ages,mus,np.isnan(z).astype(float),levels=[.5,1.5],colors='none',hatches=['////'])
    if np.nanmin(z)<7<np.nanmax(z):ax.contour(ages,mus,z,levels=[7],colors='white',linewidths=1)
    ax.set(xlabel='Information age (s)',ylabel='Friction coefficient',title=label)
fig.colorbar(im,ax=axes,label='Emergency headway (s)',extend='max',shrink=.85)
fig.savefig(R/'figures_v5/fig4_v5.pdf',dpi=400);fig.savefig(R/'figures_v5/fig4_v5.png',dpi=180);plt.close(fig)
save(rows,R/'results_processed_v5/fig4_v5.csv')

# Independent directional inequality falsification, not a proof or control trial.
rng=np.random.default_rng(2026092701);raw=[]
for j in range(20000):
    ub=float(rng.choice([.3,.9,1.5,3.]));mu=rng.uniform(.1,.9)
    N=rng.uniform(40000,260000,2);d=rng.uniform(-.15,.15)
    B=rng.uniform(0,min(ub*mu*N/np.array([.38,.62])))
    ycap=np.sqrt(np.maximum(0,(ub*mu*N)**2-(B*np.array([.38,.62]))**2))
    y=rng.uniform(-1,1,2)*ycap
    u=np.hypot(-B*np.array([.38,.62]),y)/(mu*N)
    s=np.divide(np.tanh(u),u,out=np.ones(2),where=u!=0)
    actual= s[0]*(.38*B*math.cos(d)+y[0]*math.sin(d))+s[1]*.62*B
    lower=directional_lower(B,abs(y[0]),abs(d),ub)
    raw.append(dict(index=j,ubar=ub,mu=mu,Nf=N[0],Nr=N[1],B_demand=B,Yf=y[0],Yr=y[1],delta=d,u_front=u[0],u_rear=u[1],actual_braking_N=actual,lower_N=lower,margin_N=actual-lower))
save(raw,R/'results_raw/force_sector_verification.csv')
selected=[]
for name in NAMES:
    for grade in [0,-.03,-.06]:
        b,status,d=interface_result(name,[34000.],18,.65,8,.001,grade)
        age,admit=age_inverse(110,18,18,b)
        selected.append(dict(interface=name,grade=grade,Tmax_s=age if math.isfinite(age) else None,admission=admit,**d))
summary={'eta_09':sector(.9),'n_directional_checks':len(raw),'min_directional_margin_N':float(min(r['margin_N'] for r in raw)),'n_directional_violations':int(sum(r['margin_N']< -1e-7 for r in raw)),'selected':selected,'fig3_rows':4*3*3*105,'fig4_rows':len(rows)}
(R/'results_processed_v5/analytical_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
print(json.dumps(summary,indent=2))
