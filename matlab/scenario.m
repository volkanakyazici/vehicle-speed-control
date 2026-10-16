function s = scenario(name, dt)
if nargin<2, dt=0.01; end
s.t=(0:round(120/dt))'*dt;
s.ref=20*ones(size(s.t)); s.theta=zeros(size(s.t));
s.limit=4000*ones(size(s.t)); s.m=1500;
switch name
    case 'flat'
    case 'hill'
        s.theta(s.t>=30 & s.t<70)=atan(0.05);
    case 'heavy'
        s.m=1950; s.theta(s.t>=30 & s.t<70)=atan(0.05);
    case 'windup'
        s.ref(:)=30; s.ref(s.t>=45)=15; s.limit(:)=1200;
    otherwise
        error('Unknown scenario: %s',name);
end
end
