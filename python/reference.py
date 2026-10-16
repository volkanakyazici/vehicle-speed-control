"""Numerical reference for longitudinal vehicle speed control."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
P = dict(m=1500., g=9.81, rho=1.225, Cd=0.29, A=2.2, Crr=0.012,
         Kp=600., Ki=80., Kaw=0.5, dt=0.01, v0=15.)

def scenario(name, dt=0.01):
    t = np.arange(round(120/dt)+1)*dt
    ref = np.full_like(t, 20.)
    grade = np.zeros_like(t)
    limit = np.full_like(t, 4000.)
    mass = 1500.
    if name == 'hill': grade[(t>=30)&(t<70)] = np.arctan(0.05)
    elif name == 'heavy':
        mass = 1950.
        grade[(t>=30)&(t<70)] = np.arctan(0.05)
    elif name == 'windup':
        ref[:] = 30.; ref[t>=45] = 15.
        limit[:] = 1200.
    elif name != 'flat': raise ValueError(name)
    return t, ref, grade, limit, mass

def resistance(v, theta, m):
    return (0.5*P['rho']*P['Cd']*P['A']*v*abs(v)
            + m*P['g']*P['Crr']*np.cos(theta)*np.tanh(v/0.1)
            + m*P['g']*np.sin(theta))

def simulate(name, mode, dt=0.01):
    t, ref, theta, limit, m = scenario(name, dt)
    v=np.empty_like(t); integ=np.zeros_like(t); raw=np.empty_like(t); u=np.empty_like(t)
    v[0]=P['v0']
    ki=0. if mode=='P' else P['Ki']
    kaw=P['Kaw'] if mode=='PI_AW' else 0.
    for k in range(len(t)):
        e=ref[k]-v[k]
        raw[k]=P['Kp']*e+integ[k]
        u[k]=np.clip(raw[k],0,limit[k])
        if k<len(t)-1:
            v[k+1]=v[k]+dt*(u[k]-resistance(v[k],theta[k],m))/m
            integ[k+1]=integ[k]+dt*(ki*e+kaw*(u[k]-raw[k]))
    return dict(t=t,ref=ref,theta=theta,v=v,u=u,raw=raw,integ=integ,limit=limit)

def metrics(s):
    e=s['ref']-s['v']; dt=s['t'][1]-s['t'][0]
    # Left-rectangle measures use intervals, excluding the final sample.
    return dict(rmse_mps=np.sqrt(np.mean(e[:-1]**2)),
                iae_m=np.sum(np.abs(e[:-1]))*dt,
                final_mean_error_mps=np.mean(e[s['t']>=115]),
                saturated_time_s=np.sum(np.abs(s['raw'][:-1]-s['u'][:-1])>1e-9)*dt)

def recovery(s):
    """Time after reference decrease to remain within +/-0.5 m/s until end."""
    bad=np.where((s['t']>=45)&(np.abs(s['v']-s['ref'])>0.5))[0]
    if len(bad)==0:return 0.
    if bad[-1]==len(s['t'])-1:return float('nan')
    return s['t'][bad[-1]+1]-45

def main():
    out=ROOT/'results'/'python';out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name in ['flat','hill','heavy','windup']:
        fig,ax=plt.subplots(3,1,figsize=(10,8),sharex=True,layout='constrained')
        for mode,c in zip(['P','PI','PI_AW'],['#74818c','#e18b39','#147b85']):
            s=simulate(name,mode)
            rows.append(dict(scenario=name,controller=mode,**metrics(s)))
            ax[0].plot(s['t'],s['v']*3.6,label=mode,color=c)
            ax[1].plot(s['t'],s['u'],color=c)
            ax[2].plot(s['t'],s['integ'],color=c)
            data=np.column_stack([s[k] for k in ['t','ref','v','u','raw','integ','theta','limit']])
            np.savetxt(out/f'{name}_{mode}.csv',data,delimiter=',',
                       header='time_s,reference_mps,speed_mps,force_N,raw_force_N,integral_force_N,grade_rad,force_limit_N',comments='',fmt='%.7g')
        ax[0].plot(s['t'],s['ref']*3.6,'k--',label='Reference',linewidth=1)
        ax[1].plot(s['t'],s['limit'],'k--',linewidth=1,label='Force limit')
        ax[0].legend(ncol=4);ax[1].legend()
        for a in ax:a.grid(alpha=.2)
        ax[0].set_ylabel('Speed [km/h]');ax[1].set_ylabel('Applied force [N]')
        ax[2].set_ylabel('Integral contribution [N]');ax[2].set_xlabel('Time [s]')
        fig.suptitle(f'{name.upper()} | P vs PI vs PI with anti-windup\nPython reference simulation - forward Euler, dt = 0.01 s',fontsize=13)
        fig.savefig(out/f'{name}.png',dpi=150);plt.close(fig)
    with (out/'metrics_python.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('Python reference results written to',out)
    for mode in ['PI','PI_AW']:
        print(mode,'windup recovery [s]:',recovery(simulate('windup',mode)))

if __name__=='__main__':main()
