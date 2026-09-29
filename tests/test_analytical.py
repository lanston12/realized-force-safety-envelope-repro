import math
import numpy as np
from src.realization import sector,directional_lower,realized_family,demand_domain
from src.envelope import age_inverse,gap,distance,PacketError,intersect

def test_exact_sector_and_monotonicity():
    assert sector(0)==1
    assert abs(sector(.9)-.7958865224)<1e-9
    u=np.linspace(0,8,10001)
    assert np.all(np.diff([sector(t) for t in u])<=0)

def test_directional_rotation_cannot_be_ignored():
    B=1.;yf=100.;d=.1
    assert directional_lower(B,yf,d)<0
    assert sector(.9)*B>0 # radial magnitude alone would give a false guarantee


def test_sector_bound_random_rotations():
    rng=np.random.default_rng(100)
    for _ in range(1000):
        B=rng.uniform(0,2e5);Y=rng.uniform(0,1e5);d=rng.uniform(-.2,.2)
        sf,sr=rng.uniform(sector(.9),1,2);fy=rng.uniform(-Y,Y)
        actual=sf*(.38*B*math.cos(d)+fy*math.sin(d))+sr*.62*B
        assert actual+1e-8>=directional_lower(B,Y,abs(d))

def test_lag_threshold_realized_deceleration():
    co,status=realized_family([34000],12,.65,8,.001,-.03)
    assert co is not None
    t=co.rho-.05
    upper=-co.Q_demand+(1.2+co.Q_demand)*math.exp(-t/.8)
    tire_upper=co.c*upper+co.rotation_loss
    gd=9.81*.03/math.sqrt(1+.03**2)
    assert abs(tire_upper+gd+.15+co.b)<1e-12

def test_negative_disturbance_sector_margin():
    co,_=realized_family([34000],12,.65,8,.001,0)
    dom=demand_domain(34000,co.peak_speed,.65,8,.001,0)
    assert co.q_demand+.8*.025<=dom['B_demand_N']/34000+1e-12

def test_peak_speed_and_age_root():
    co,_=realized_family([34000],12,.65,8,.001,0)
    assert co.peak_speed>=12+co.a_plus*co.rho
    age,status=age_inverse(110,12,12,co.braking())
    assert status in ['root','age_cap']
    assert gap(age,12,12,co.braking())<=110+1e-9

def test_rejected_initial_demand():
    co,status=realized_family([34000],18,.1,22,.004,-.06)
    assert co is None
    assert status!='admissible_conditional'

def test_bounded_sensing_intersection():
    b=intersect((np.array([-10.,-2.]),np.array([10.,2.])),(np.array([-1.,-.2]),np.array([1.,.2])))
    assert np.all(b[0]==[-1,-.2]) and np.all(b[1]==[1,.2])




def test_stopping_comparison_breakpoints():
    from src.envelope import displacement
    v=23.;vp=17.;b=1.7;B=9.;rho=2.5;a=1.4
    ts=np.sort(np.r_[np.linspace(0,25,1000),rho,vp/B,rho+(v+a*rho)/b])
    rel=displacement(ts,v,b,rho,a)-displacement(ts,vp,B)
    assert rel.max()<=distance(v,b,rho,a)-vp*vp/(2*B)+1e-10
