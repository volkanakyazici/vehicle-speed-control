"""Physics, control and step-size checks for the numerical reference only."""
import numpy as np
from reference import P,simulate,resistance,recovery

def main():
    # Newton's law: equilibrium force gives zero acceleration.
    assert abs(resistance(20.,0.,1500.)-332.89)<1e-9
    assert resistance(20.,np.arctan(.05),1500.)>resistance(20.,0.,1500.)
    # P-only steady speed predicted by solving Kp*(r-v)=a*v^2+b.
    a=.5*P['rho']*P['Cd']*P['A'];b=1500*P['g']*P['Crr']
    eq=(-P['Kp']+np.sqrt(P['Kp']**2-4*a*(b-P['Kp']*20)))/(2*a)
    assert abs(simulate('flat','P')['v'][-1]-eq)<1e-7
    for name in ['flat','hill','heavy','windup']:
        for mode in ['P','PI','PI_AW']:
            s=simulate(name,mode)
            assert np.isfinite(s['v']).all() and (s['v']>0).all()
            assert (s['u']>=0).all() and (s['u']<=s['limit']).all()
            fine=simulate(name,mode,.005)
            assert np.max(np.abs(s['v']-fine['v'][::2]))<.05
    assert abs(simulate('flat','PI')['v'][-1]-20)<1e-6
    aw=recovery(simulate('windup','PI_AW')); plain=recovery(simulate('windup','PI'))
    assert np.isfinite(aw) and (not np.isfinite(plain) or aw<plain)
    print('PASS: resistance, analytic P equilibrium, force limits, finite positive speed, dt refinement, PI tracking, anti-windup recovery.')
if __name__=='__main__':main()
