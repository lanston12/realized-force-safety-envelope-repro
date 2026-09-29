"""SI scalar certificate; admissibility requires separately certified lateral backup.

The synthetic mass-normalized servo is an explicit extra assumption. A common
force command and a common specific-force command have different quantifiers.
"""
from dataclasses import dataclass
import math
import numpy as np

@dataclass(frozen=True)
class PacketError:
    sigma_s: float = .1
    sigma_v: float = .05
    sigma_a: float = .1
    jerk: float = 40.
    def radii(self,T):
        values=(T,self.sigma_s,self.sigma_v,self.sigma_a,self.jerk)
        if not all(math.isfinite(x) for x in values) or min(values)<0:
            raise ValueError('nonnegative finite inputs required')
        return (self.sigma_s+self.sigma_v*T+self.sigma_a*T*T/2+self.jerk*T**3/6,
                self.sigma_v+self.sigma_a*T+self.jerk*T*T/2,self.sigma_a+self.jerk*T)

def parameters(mass):
    f=(mass-24000)/20000
    lf=6.5*(.56+.08*f); lr=6.5-lf; h=1.35+.35*f
    iz=mass*(6.5**2+2.55**2)/12*2.2
    cf=mass*9.81*lr/6.5*7.; cr=mass*9.81*lf/6.5*7.
    return np.array([mass,iz,lf,lr,h,cf,cr])

def wind_load(v,wind):
    # C_y(beta)=sin(beta), relative wind magnitude hypot(v,wind).
    fy=.5*1.225*45.*math.hypot(v,wind)*wind
    return fy,fy*1.0

def brake_capacity(mass,v,mu,wind,kappa,grade,derating=1.,transient=.2):
    """Point parameter tuple. Lower loads include all ax in [-8.5,1.2]."""
    _,_,lf,lr,h,_,_=parameters(mass); L=lf+lr
    normal=mass*9.81/math.sqrt(1+grade*grade)
    fz=np.array([normal*lr/L-mass*h*1.2/L,
                 normal*lf/L-mass*h*8.5/L])
    fw,mw=wind_load(v,abs(wind))
    demand=mass*v*v*abs(kappa)+fw
    y=np.array([(lr*demand+abs(mw))/L+mass*transient*lr/L,
                (lf*demand+abs(mw))/L+mass*transient*lf/L])
    rad=(.9*mu*fz)**2-y*y
    if min(fz)<=0 or min(rad)<=0: return 0.
    return min(260000*derating,math.sqrt(rad[0])/.38,math.sqrt(rad[1])/.62)

def joint_reserve(masses,v,mu,wind,kappa,grade,derating=1.):
    """Exact min over a declared finite physical family, not continuum proof."""
    cap=np.array([brake_capacity(m,v,mu,wind,kappa,grade,derating) for m in masses])
    m=np.asarray(masses)
    return float(np.min(cap/m)),float(np.min(cap)/np.max(m)),cap

def lag(q,tau=.8,grade=0.,axmax=1.2,kin=.15,Ts=.05):
    Q=q-tau*.025; gd=max(0.,-9.81*grade/math.sqrt(1+grade*grade))
    if Q<=gd+kin: return None
    b=.8*(Q-gd-kin); req=b+gd+kin
    rho=Ts+tau*math.log((axmax+Q)/(Q-req))
    return b,rho,axmax+gd+kin

def distance(v,b,rho,a):
    if not all(math.isfinite(x) for x in (v,b,rho,a)) or min(v,rho,a)<0 or b<=0: raise ValueError('invalid comparison')
    return v*rho+a*rho*rho/2+(v+a*rho)**2/(2*b)

def displacement(t,v,b,rho=0.,a=0.):
    t=np.asarray(t); tr=np.minimum(t,rho); tb=np.minimum(np.maximum(t-rho,0.),(v+a*rho)/b)
    return v*tr+a*tr*tr/2+(v+a*rho)*tb-b*tb*tb/2

def gap(age,v,vp,braking,errors=PacketError(),B=10.,d0=5.):
    if braking is None: return math.inf
    b,rho,a=braking; es,ev,_=errors.radii(age)
    pred=min(v,max(0.,vp-ev)); B=max(B,b)
    return d0+es+distance(v,b,rho,a)-pred*pred/(2*B)

def age_inverse(d,v,vp,braking,cap=1.,errors=PacketError(),B=10.):
    if not all(math.isfinite(x) for x in (d,v,vp,cap,B)) or min(d,v,cap)<0 or B<=0:
        raise ValueError('invalid age-inversion tuple')
    if gap(0.,v,vp,braking,errors,B)>d: return math.nan,'inadmissible'
    if gap(cap,v,vp,braking,errors,B)<=d: return cap,'age_cap'
    lo=0.; hi=cap
    for _ in range(60):
        mid=(hi+lo)/2
        if gap(mid,v,vp,braking,errors,B)<=d: lo=mid
        else: hi=mid
    return lo,'root'

def explicit_age(d,v,braking,cap=1.,J=40.,errors=None):
    if braking is None: return math.nan
    b,rho,a=braking; budget=d-5-distance(v,b,rho,a)
    if errors is not None:
        budget-=errors.sigma_s+errors.sigma_v*cap+errors.sigma_a*cap*cap/2
    if budget<0: return math.nan
    return min(cap,(6*budget/J)**(1/3))

def braking_family(masses,v,mu,wind,kappa,grade,tau=.8,interface='specific'):
    """Self-consistent speed bound over the entire comparison build-up.
    A fixed-point closure is essential: current speed alone does not bound the
    lateral demand during the positive-acceleration response interval.
    """
    upper=v
    for _ in range(200):
        q,qn,_=joint_reserve(masses,upper,mu,wind,kappa,grade)
        use=q if interface=='specific' else qn
        braking=lag(use,tau=tau,grade=grade)
        if braking is None:return None,upper,q,qn
        b,rho,a=braking;needed=v+a*rho
        if needed<=upper:
            return braking,upper,q,qn
        upper=needed+1e-8
        if upper>100:break
    return None,upper,0.,0.

def intersect(a,b):
    lo=np.maximum(a[0],b[0]); hi=np.minimum(a[1],b[1])
    if np.any(lo>hi): raise ValueError('inconsistent information')
    return lo,hi
