import os
import argparse
import pandas as pd


def stats(runtype, n):
    avg_tts = []
    avg_ideal_tts = []
    for i in range(1, n + 1):
        f = os.path.join(runtype, 'tripinfo-{}.csv'.format(str(i)))
        df = pd.DataFrame.from_csv(f, index_col='tripinfo_id')
        avg_tt = df['tripinfo_duration'].mean()
        avg_tts.append(avg_tt)
        avg_timeloss = df['tripinfo_timeLoss'].mean()
        avg_ideal_tt = avg_tt / (avg_tt - avg_timeloss)
        avg_ideal_tts.append(avg_ideal_tt)
    return pd.Series(avg_tts).mean(), pd.Series(avg_ideal_tts).mean()


def parse_options():
    ap = argparse.ArgumentParser()
    ap.add_argument('baseline')
    ap.add_argument('adaptive')
    ap.add_argument('-n', type=int, required=False, default=10)
    args = ap.parse_args()
    return args


if __name__ == '__main__':
    options = parse_options()
    baseline_att, baseline_tti = stats(options.baseline, options.n)
    adaptive_att, adaptive_tti = stats(options.adaptive, options.n)

    print('Baseline ATT: {}'.format(baseline_att))
    print('Adaptive ATT: {}'.format(adaptive_att))
    print('Adaptive % improvement: {:.2f}%'.format(
        ((baseline_att - adaptive_att) / baseline_att) * 100)
    )
    print('Baseline TTI: {}'.format(baseline_tti))
    print('Adaptive TTI: {}'.format(adaptive_tti))
    print('Adaptive % improvement: {:.2f}%'.format(
        ((baseline_tti - adaptive_tti) / baseline_tti) * 100)
    )
