import math
import numpy as np
import pytest
from src.envelope import PacketError,gap,age_inverse,distance,intersect
from src.realization import realized_family,demand_domain

def test_admission_boundaries_and_zero_growth():
 br=(3.,1.,1.);f0=gap(0,15,15,br);fc=gap(1,15,15,br)
 assert age_inverse(f0-1e-6,15,15,br)[1]=='inadmissible'
 t,st=age_inverse(f0,15,15,br);assert st=='root' and t<1e-7
 t,st=age_inverse((f0+fc)/2,15,15,br);assert 0<t<1 and st=='root'
 assert gap(t,15,15,br)==pytest.approx((f0+fc)/2)
 assert age_inverse(fc,15,15,br)==(1.,'age_cap')
 err=PacketError(.1,0,0,0);d=gap(0,15,15,br,err)
 assert age_inverse(d,15,15,br,errors=err)==(1.,'age_cap')

def test_unequal_center_relaxation_without_recentering():
 rng=np.random.default_rng(2026092705)
 for _ in range(400):
  oldlo=np.array([90.,8.]);oldhi=np.array([110.,18.])
  # Arbitrary intersecting local rectangles, not necessarily concentric.
  p=rng.uniform(oldlo,oldhi);local=(p-rng.uniform(0,4,2),p+rng.uniform(0,4,2))
  lo,hi=intersect((oldlo,oldhi),local)
  f=lambda l:5+100-l[0]+distance(15,3,1,1)-min(15,max(0,l[1]))**2/20
  assert f(lo)<=f(oldlo)+1e-12

def test_interface_capacity_order_finite_family():
 rng=np.random.default_rng(2026092706)
 for _ in range(500):
  m=rng.uniform(24000,44000,3);B=rng.uniform(10000,260000,3)
  assert min(B)/max(m)<=min(B/m)+1e-12

def test_closure_order_across_predecessor_braking_branches():
 for vp in [0,5,15]:
  for rho in [0.,.5,2.]:
   bb=np.linspace(.1,20,300)
   closure=[distance(15,b,rho,1)-vp**2/(2*max(10,b)) for b in bb]
   assert np.all(np.diff(closure)<=1e-10)

def test_friction_disk_order_at_shared_peak():
 caps=[demand_domain(34000,20,mu,8,.001,0)['B_demand_N'] for mu in np.linspace(.3,.9,80)]
 assert np.all(np.diff(caps)>=-1e-10)

def test_jerk_changes_no_fresh_gap_and_kin_default_regression():
 co,st=realized_family([34000],16,.65,8,.001,0)
 assert co==realized_family([34000],16,.65,8,.001,0,kin=.15)[0]
 gg=[gap(0,16,16,co.braking(),PacketError(jerk=J)) for J in [10,40,80]]
 assert gg[0]==gg[1]==gg[2]
 tt=[age_inverse(110,16,16,co.braking(),errors=PacketError(jerk=J))[0] for J in [10,40,80]]
 assert tt[0]>=tt[1]>=tt[2]
