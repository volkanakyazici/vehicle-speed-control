function s = simulate_case(name, mode, dt)
% Explicit sampled-data implementation, no Control System Toolbox required.
p=parameters(); if nargin<3,dt=p.dt;end
s=scenario(name,dt); N=numel(s.t);
s.v=zeros(N,1); s.v(1)=p.v0;
s.integral=zeros(N,1); s.raw=zeros(N,1); s.u=zeros(N,1);
ki=p.Ki; kaw=0;
if strcmp(mode,'P'),ki=0;end
if strcmp(mode,'PI_AW'),kaw=p.Kaw;end
assert(any(strcmp(mode,{'P','PI','PI_AW'})),'Unknown controller');
for k=1:N
    e=s.ref(k)-s.v(k);
    s.raw(k)=p.Kp*e+s.integral(k);
    s.u(k)=min(max(s.raw(k),0),s.limit(k));
    R=0.5*p.rho*p.Cd*p.A*s.v(k)*abs(s.v(k)) ...
      +s.m*p.g*p.Crr*cos(s.theta(k))*tanh(s.v(k)/0.1) ...
      +s.m*p.g*sin(s.theta(k));
    if k<N
        s.v(k+1)=s.v(k)+dt*(s.u(k)-R)/s.m;
        s.integral(k+1)=s.integral(k)+dt*(ki*e+kaw*(s.u(k)-s.raw(k)));
    end
end
end
