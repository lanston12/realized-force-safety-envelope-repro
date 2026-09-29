from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
(R/'sections').mkdir(exist_ok=True)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.realization import realized_family
from src.envelope import PacketError,displacement,distance
co,_=realized_family([34000],16,.65,8,.001,0)
vp=16-PacketError().radii(.2)[1];t=np.linspace(0,co.rho+(16+co.a_plus*co.rho)/co.b,500)
vf=np.where(t<co.rho,16+co.a_plus*t,np.maximum(0,16+co.a_plus*co.rho-co.b*(t-co.rho)))
vpcurve=np.maximum(0,vp-10*t)
closure=displacement(t,16,*co.braking())-displacement(t,vp,10)
plt.rcParams.update({'font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(2,1,figsize=(3.45,3.3),sharex=True,constrained_layout=True)
ax[0].plot(t,vf,color='#a83448',label='Follower upper');ax[0].plot(t,vpcurve,color='#3c78a8',ls='--',label='Predecessor lower');ax[0].set_ylabel('Speed (m/s)');ax[0].legend(fontsize=7)
ax[1].plot(t,closure,color='#5c6470');ax[1].axhline(closure[-1],color='#777777',ls=':',lw=.8);ax[1].set(xlabel='Time since contingency (s)',ylabel='Relative displacement (m)')
for a in ax:a.grid(alpha=.2);a.axvline(co.rho,color='#a66c24',ls='--',lw=.8)
fig.savefig(R/'figures_v5/fig2_comparison.pdf');fig.savefig(R/'figures_v5/fig2_comparison.png',dpi=180);plt.close(fig)
np.savetxt(R/'results_processed_v5/comparator_curve.csv',np.c_[t,vf,vpcurve,closure],delimiter=',',header='t_s,follower_upper_mps,predecessor_lower_mps,closure_m',comments='')
