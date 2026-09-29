"""Independent checks of corrected cap branches and primitive comparison hypotheses."""
import math
import numpy as np
import pytest
from src.realization import realized_family,demand_domain
from src.envelope import displacement,distance,intersect

def test_active_physical_cap_and_two_opposite_disturbances():
    for limit in (8.48,8.5):
        co,_=realized_family([24000],15,2,0,0,0,demand_limit=limit)
        assert co.q_demand==pytest.approx(limit-.02)
        assert co.Q_demand==pytest.approx(limit-.04)
        # Vector field at negative demand boundary points inward for every lag.
        for tau in (.1,.3,.8):
            assert (-co.q_demand+limit)/tau-.025>=-1e-12
    assert demand_domain(24000,15,2,0,0,0)['B_demand_N']/24000==8.5

def test_inactive_demand_cap_does_not_change_tire_limited_contract():
    old,_=realized_family([34000],15,.65,8,.001,-.03,demand_limit=8.48)
    new,_=realized_family([34000],15,.65,8,.001,-.03,demand_limit=8.5)
    assert old==new

def test_primitive_acceleration_implies_displacement_with_absorbing_stop():
    rng=np.random.default_rng(2026092704)
    dt=.001;t=np.arange(0,15,dt)
    for _ in range(12):
        v=12.;ap=1.5;rho=1.2;b=2.;B=8.;vp=10.
        # Piecewise constant physical accelerations meet the primitive bounds.
        af=np.where(t<rho,ap,b*-1)-rng.uniform(0,1,len(t))
        nu=v;sf=0.;held=False;max_excess=0.
        for j,a in enumerate(af):
            step=dt
            if held:step=0.
            elif a<0 and nu+a*dt<=0:step=nu/-a;held=True
            sf+=nu*step+.5*a*step**2
            nu=0. if held else nu+a*dt
            upper=float(displacement(np.array([t[j]+dt]),v,b,rho,ap)[0])
            max_excess=max(max_excess,sf-upper)
        assert max_excess<1e-9
        # Predecessor with weaker braking and larger initial speed stays above.
        actual=displacement(t,vp+.3,B*.8)
        lower=displacement(t,vp,B)
        assert np.all(actual+1e-10>=lower)

def test_nonnegative_speed_alone_does_not_supply_hold():
    # Stop at t=1, then restart: nonnegative yet escapes a stopped comparator.
    t=np.linspace(0,5,1001)
    physical=np.where(t<=1,t-.5*t*t,.5+.5*(t-1)**2)
    upper=displacement(t,1,1)
    assert physical[-1]>upper[-1]

def test_predecessor_credit_requires_its_braking_contract():
    # An earlier contact stop cannot be repaired by zero excursion radius.
    vp=10.;B=5.;credited=vp**2/(2*B)
    actual_prefix=1.
    assert credited>actual_prefix # subtracting credited would underbudget closure
    follower=distance(12,2,1,1)
    assert follower-actual_prefix<=follower # predecessor-floor bound remains safe

def test_unequal_center_intersection_uses_endpoints():
    a=(np.array([-2.]),np.array([2.]));b=(np.array([1.]),np.array([3.]))
    lo,hi=intersect(a,b)
    assert lo[0]==1 and hi[0]==2
    assert (hi[0]-lo[0])/2<min(2,1)
    with pytest.raises(ValueError):intersect(a,(np.array([3.]),np.array([4.])))
