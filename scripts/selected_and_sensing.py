from pathlib import Path
import sys,json,csv,math,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.realization import interface_result
from src.envelope import gap,age_inverse,PacketError
plt.rcParams.update({'font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
def save(rows,path):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
sel=[]
for v in [15,16,18]:
    for grade in [0,-.03,-.06]:
        for name in ['ideal_identity','common_force','realized']:
            b,st,detail=interface_result(name,[34000],v,.65,8,.001,grade)
            age,adm=age_inverse(110,v,v,b)
            sel.append(dict(v=v,grade=grade,interface=name,Tmax=age if math.isfinite(age) else None,admission=adm,fresh_gap=gap(0,v,v,b),headway=(gap(.2,v,v,b)-5)/v))
save(sel,R/'tables_v5/selected_analytical_results.csv')
mix=[]
for name in ['ideal_identity','common_force','realized']:
    b,st,detail=interface_result(name,[24000,34000,44000],18,.7,12,.002,-.03)
    mix.append(dict(interface=name,mu=.7,age=.2,hmin=(gap(.2,18,18,b)-5)/18,dsafe=gap(.2,18,18,b)))
save(mix,R/'tables_v5/interface_comparison.csv')

rows=[];fig,ax=plt.subplots(figsize=(3.45,2.6),constrained_layout=True)
for name,clr in [('ideal_identity','#3c78a8'),('realized','#a83448')]:
    b,_,_=interface_result(name,[34000],16,.65,8,.001,0)
    y=[];ys=[]
    for t in np.linspace(0,2,201):
        es,ev,_=PacketError().radii(t)
        ordinary=gap(t,16,16,b)
        sensed=gap(0,16,16,b,errors=PacketError(min(es,.5),min(ev,.2),0,0))
        rows.append(dict(interface=name,age=t,position_radius=es,speed_radius=ev,intersect_position_radius=min(es,.5),intersect_speed_radius=min(ev,.2),required_gap=ordinary,required_gap_sensor=sensed,sensor_position_bound=.5,sensor_speed_bound=.2))
        y.append(ordinary);ys.append(sensed)
    ax.plot(np.linspace(0,2,201),y,color=clr,marker='o' if name=='ideal_identity' else '^',markevery=30,markersize=3,markerfacecolor='none',label={'ideal_identity':'Ideal specific force','realized':'Realized-force bound'}[name])
    ax.plot(np.linspace(0,2,201),ys,color=clr,ls='--',marker='o' if name=='ideal_identity' else '^',markevery=(15,30),markersize=3,markerfacecolor='none')
ax.axhline(110,color='#555555',ls=':',label='Available gap')
ax.set(xlabel='Current information age (s)',ylabel='Required gap (m)',ylim=(70,160));ax.legend(fontsize=6.5);ax.grid(alpha=.2)
fig.savefig(R/'figures_v5/fig5_sensing.pdf');fig.savefig(R/'figures_v5/fig5_sensing.png',dpi=180);plt.close(fig)
save(rows,R/'results_processed_v5/analytical_sensing.csv')

