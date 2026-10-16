"""Plot archived MATLAB CSV results without rerunning the simulations."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'figures'
STYLES = [('P', '#526477', '-'), ('PI', '#d56b22', '-'),
          ('PI_AW', '#087f8c', '--')]


def read(folder, case, mode):
    return np.genfromtxt(ROOT / 'results' / folder / f'{case}_{mode}.csv',
                         delimiter=',', names=True)


def case_plot(folder, case, kp):
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True,
                             layout='constrained')
    for mode, color, style in STYLES:
        data = read(folder, case, mode)
        for ax, field, factor in zip(axes,
                ['speed_mps', 'force_N', 'integral_force_N'], [3.6, 1, 1]):
            ax.plot(data['time_s'], data[field] * factor, color=color,
                    linestyle=style, linewidth=1.7, label=mode.replace('_', ' '))
    axes[0].plot(data['time_s'], data['reference_mps'] * 3.6,
                 color='#202020', linestyle=':', label='Reference')
    axes[1].plot(data['time_s'], data['force_limit_N'],
                 color='#202020', linestyle=':', label='Force limit')
    axes[1].axhline(0, color='#202020', linewidth=.7)
    if case in ['hill', 'heavy']:
        for ax in axes:
            ax.axvspan(30, 70, color='#e7edf3', alpha=.65, zorder=0)
    elif case == 'windup':
        for ax in axes:
            ax.axvline(45, color='#999999', linestyle=':', linewidth=1)
    for ax in axes:
        ax.grid(alpha=.22)
        ax.set_xlim(0, 120)
    axes[0].set_ylabel('Speed [km/h]')
    axes[1].set_ylabel('Applied force [N]')
    axes[2].set_ylabel('Integral contribution [N]')
    axes[2].set_xlabel('Time [s]')
    axes[0].legend(ncol=4, loc='best')
    axes[1].legend(loc='best', ncol=4)
    title = {'flat': 'Flat road', 'hill': '5% uphill grade',
             'heavy': 'Heavy vehicle: 1950 kg', 'windup': 'Traction-force saturation'}[case]
    fig.suptitle(f'{title} | Kp = {kp}, Ki = 80, Kaw = 0.5\n'
                 'Archived MATLAB results | sample time 0.01 s', fontsize=13)
    fig.savefig(OUT / f'{folder}_{case}.png', dpi=160)
    plt.close(fig)


def gain_plot():
    fig, ax = plt.subplots(figsize=(10, 4.5), layout='constrained')
    for folder, kp, color in [('01_baseline', 600, '#087f8c'),
                               ('02_lower_kp', 300, '#d56b22')]:
        for mode, style in [('P', '--'), ('PI', '-')]:
            data = read(folder, 'flat', mode)
            ax.plot(data['time_s'], data['speed_mps'] * 3.6, color=color,
                    linestyle=style, linewidth=1.8, label=f'{mode}, Kp = {kp}')
    ax.axhline(72, color='#202020', linestyle=':', label='Reference')
    ax.set(xlabel='Time [s]', ylabel='Speed [km/h]', xlim=(0, 120))
    ax.grid(alpha=.22)
    ax.legend(ncol=3, loc='lower right')
    ax.set_title('Proportional-gain sensitivity on flat road\n'
                 'Archived MATLAB results | Ki = 80 for PI')
    fig.savefig(OUT / 'kp_comparison.png', dpi=160)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for case in ['flat', 'hill', 'heavy', 'windup']:
        case_plot('01_baseline', case, 600)
    case_plot('02_lower_kp', 'flat', 300)
    gain_plot()
    print('Archived MATLAB figures written to', OUT)


if __name__ == '__main__':
    main()
