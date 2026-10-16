function run_matlab()
% From the matlab folder: run_matlab
root=fileparts(fileparts(mfilename('fullpath')));
outdir=fullfile(root,'results','matlab');if ~exist(outdir,'dir'),mkdir(outdir);end
names={'flat','hill','heavy','windup'}; modes={'P','PI','PI_AW'};
rows=cell(0,6);
for a=1:numel(names)
    f=figure('Color','w','Name',names{a});
    for b=1:numel(modes)
        s=simulate_case(names{a},modes{b});
        subplot(3,1,1);hold on;plot(s.t,s.v*3.6,'DisplayName',modes{b});ylabel('Speed [km/h]');grid on;
        subplot(3,1,2);hold on;plot(s.t,s.u);ylabel('Force [N]');grid on;
        subplot(3,1,3);hold on;plot(s.t,s.integral);ylabel('Integral [N]');xlabel('Time [s]');grid on;
        e=s.ref-s.v;dt=s.t(2)-s.t(1);
        rows(end+1,:)={names{a},modes{b},sqrt(mean(e(1:end-1).^2)), ...
            sum(abs(e(1:end-1)))*dt,mean(e(s.t>=115)), ...
            sum(abs(s.raw(1:end-1)-s.u(1:end-1))>1e-9)*dt}; %#ok<AGROW>
        T=table(s.t,s.ref,s.v,s.u,s.raw,s.integral,s.theta,s.limit, ...
            'VariableNames',{'time_s','reference_mps','speed_mps','force_N','raw_force_N','integral_force_N','grade_rad','force_limit_N'});
        writetable(T,fullfile(outdir,[names{a} '_' modes{b} '.csv']));
    end
    subplot(3,1,1);plot(s.t,s.ref*3.6,'k--','DisplayName','Reference');legend('show');title(['MATLAB: ' names{a}]);
    saveas(f,fullfile(outdir,[names{a} '.png']));
end
T=cell2table(rows,'VariableNames',{'scenario','controller','rmse_mps','iae_m','final_mean_error_mps','saturated_time_s'});
writetable(T,fullfile(outdir,'metrics_matlab.csv'));disp(T);
fprintf('Results saved to %s\n',outdir);
end
