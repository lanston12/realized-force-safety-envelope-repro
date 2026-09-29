"""Directional realization contract for an imposed tire-demand domain.

This module does NOT certify invariance of that domain or wheel lock.
The lag state is demanded axle force per unit mass, not actual force.
"""
from dataclasses import dataclass,asdict
import math
from .envelope import parameters,wind_load,lag,braking_family

def sector(ubar):
    if not math.isfinite(ubar) or ubar<0:raise ValueError('finite nonnegative sector radius required')
    return math.tanh(ubar)/ubar if ubar else 1.

def directional_lower(B,Yf,delta,ubar=.9):
    """Guaranteed -Fx_body for B>=0, |Fy_front_demand|<=Yf."""
    if min(B,Yf,delta)<0 or delta>=math.pi/2:raise ValueError('invalid directional domain')
    return sector(ubar)*B*(.62+.38*math.cos(delta))-Yf*math.sin(delta)

def demand_domain(m,v,mu,wind,kappa,grade,ubar=.9,demand_limit=8.5):
    if m<=0 or mu<=0 or v<0:raise ValueError('invalid physical tuple')
    _,_,lf,lr,h,_,_=parameters(m); L=lf+lr
    normal=m*9.81/math.sqrt(1+grade*grade)
    nf=normal*lr/L-m*h*1.2/L
    nr=normal*lf/L-m*h*8.5/L
    fw,mw=wind_load(v,abs(wind)); lateral=m*v*v*abs(kappa)+fw
    # These are IMPOSED demand caps. Force balance alone does not prove them.
    yf=(lr*lateral+abs(mw))/L+m*.2*lr/L
    yr=(lf*lateral+abs(mw))/L+m*.2*lf/L
    delta=math.atan(L*abs(kappa))+.02
    rf=(ubar*mu*nf)**2-yf*yf; rr=(ubar*mu*nr)**2-yr*yr
    cap=0. if min(nf,nr,rf,rr)<=0 else min(260000.,demand_limit*m,math.sqrt(rf)/.38,math.sqrt(rr)/.62)
    # A positive initial demand 1.2 is also required to lie in the sector.
    initial_ok=math.hypot(.38*m*1.2,yf)<=ubar*mu*nf and math.hypot(.62*m*1.2,yr)<=ubar*mu*nr
    return dict(B_demand_N=cap,Nf_min_N=nf,Nr_min_N=nr,Yf_demand_cap_N=yf,
                Yr_demand_cap_N=yr,delta_bound_rad=delta,initial_sector_valid=bool(initial_ok))

@dataclass
class Contract:
    q_demand:float
    q_real:float
    Q_demand:float
    Q_real:float
    c:float
    rotation_loss:float
    b:float
    rho:float
    a_plus:float
    peak_speed:float
    eta:float
    status:str='admissible_conditional'
    def braking(self):return self.b,self.rho,self.a_plus
    def record(self):return asdict(self)

def realized_family(masses,v,mu,wind,kappa,grade,tau=.8,ubar=.9,common=False,demand_limit=8.5,kin=.15):
    if not math.isfinite(kin) or kin<0:raise ValueError('nonnegative finite kinematic bound required')
    upper=v;eta=sector(ubar)
    gd=max(0.,-9.81*grade/math.sqrt(1+grade*grade))
    for _ in range(200):
        domains=[demand_domain(m,upper,mu,wind,kappa,grade,ubar,demand_limit) for m in masses]
        if not all(d['initial_sector_valid'] for d in domains):return None,'initial_demand_outside_sector'
        caps=[d['B_demand_N'] for d in domains]
        # Common specific-force target or the previous common-force reserve.
        capq=min(caps)/max(masses) if common else min(B/m for B,m in zip(caps,masses))
        # Reserve negative actuator disturbance so |demand state| stays in cap.
        qd=capq-tau*.025
        delta=max(d['delta_bound_rad'] for d in domains)
        c=eta*(.62+.38*math.cos(delta))
        ell=max(d['Yf_demand_cap_N']/m*math.sin(delta) for d,m in zip(domains,masses))
        Qd=qd-tau*.025;qr=c*qd-ell;Qr=c*Qd-ell
        if Qr<=gd+kin:return None,'nonpositive_realized_deceleration'
        b=.8*(Qr-gd-kin)
        threshold=(b+gd+kin+ell)/c
        rho=.05+tau*math.log((1.2+Qd)/(Qd-threshold))
        ap=1.2+ell+gd+kin;needed=v+ap*rho
        if needed<=upper:
            return Contract(qd,qr,Qd,Qr,c,ell,b,rho,ap,upper,eta),'admissible_conditional'
        upper=needed+1e-8
        if upper>100:break
    return None,'peak_speed_closure_failed'

def interface_result(name,masses,v,mu,wind,kappa,grade):
    if name=='realized':
        obj,status=realized_family(masses,v,mu,wind,kappa,grade)
        return (obj.braking() if obj else None),status,(obj.record() if obj else {})
    b,peak,q,qn=braking_family(masses,v,mu,wind,kappa,grade,interface='common' if name=='common_force' else 'specific')
    return b,('admissible_conditional' if b else 'inadmissible'),dict(peak_speed=peak,q_real=(qn if name=='common_force' else q))
