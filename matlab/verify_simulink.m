function verify_simulink(name,mode)
% Simulate an existing saved Simulink model and compare with MATLAB.
if nargin<1,name='hill';end
if nargin<2,mode='PI_AW';end
model=['cruise_' name '_' mode];
target=fullfile(fileparts(mfilename('fullpath')),[model '.slx']);
if ~bdIsLoaded(model)
    if ~exist(target,'file')
        error('Model not found: %s. Open or restore the saved .slx file.',target);
    end
    load_system(target);
end
out=sim(model);s=simulate_case(name,mode);
v=out.get('speed_log');u=out.get('force_log');
assert(numel(v.Time)==numel(s.t),'Unexpected sample count');
assert(max(abs(v.Time(:)-s.t))<1e-8,'Time grid differs');
ev=max(abs(v.Data(:)-s.v));eu=max(abs(u.Data(:)-s.u));
assert(ev<1e-7 && eu<1e-5,'Model mismatch: speed=%g, force=%g',ev,eu);
fprintf('PASS %s: speed error %.3g m/s; force error %.3g N\n',model,ev,eu);
figure('Color','w');plot(s.t,s.v*3.6,'k--',v.Time,v.Data*3.6);
xlabel('Time [s]');ylabel('Speed [km/h]');legend('MATLAB loop','Simulink');grid on;
end
