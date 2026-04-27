import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

datastoreFile = "aggregrateTransitions.csv"

def aggregateOnJitter(df:pd.DataFrame):
    out = df.groupby('jitter').agg(
    avgPercentCSS=('percentCSS', 'mean'),
    avgPercentSS=('percentSS', 'mean'),
    avgTotalSlowStartPhaseTime=('totalTime', 'mean'),
    avgTransitions=('transitions', 'mean'),
    avgFirstCSS=('firstCSSTime', 'mean')
).reset_index()
    return out

def plot_jitter_graphs(result_df,suffix:str, output_dir='jitterDataGraph'):
    os.makedirs(output_dir, exist_ok=True)
    file = open("dataNumbers","wt")

    # Helper to compute 95% CI from a dataframe of raw values grouped by jitter
    def compute_ci(df, col):
        groups = df.groupby('jitter')[col]
        means = groups.mean()
        sems = groups.sem().fillna(0)
        ci = 1.96 * sems  # 95% CI
        return means, ci

    # ── Graph 1: Avg %CSS and %SS vs Jitter ──────────────────────────────────
    means_css, ci_css = compute_ci(result_df, 'percentCSS')
    # means_ss,  ci_ss  = compute_ci(result_df, 'percentSS')

    jitter_labels = means_css.index.astype(str)
    x = np.arange(len(jitter_labels))
    width = .5

    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.bar(x - width/2, means_css, width,  capsize=5,
    #        label='Avg % CSS', color='steelblue', alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.plot(means_css, color='steelblue')
    # ax.bar(x + width/2, means_ss,  width,  capsize=5,
    #        label='Avg % SS',  color='coral',     alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.set_xlabel('Jitter (RTT%)')
    ax.set_ylabel('Percentage')
    ax.set_title('Avg % CSS by Jitter')
    jitter_labels = jitter_labels[::2]
    ax.set_xticks([float(ll) for ll in jitter_labels])
    ax.set_xticklabels(jitter_labels)
    # ax.legend()
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.ylim((0,1))
    # plt.xlim((0,1))
    plt.rcParams.update({'font.size':14})
    plt.setp(ax.get_xticklabels(),rotation=30,horizontalalignment='right')
    # plt.rcParams.update({'font.weight':'bold'})

    plt.savefig(os.path.join(output_dir, f'graph1_css_ss_percentage-{suffix}.png'), dpi=300)
    plt.close()
    print(f"Saved graph1_css_ss_percentage-{suffix}.png")

    # ── Graph 2: Avg Total Slow Start Phase Time vs Jitter ───────────────────
    means_time, ci_time = compute_ci(result_df, 'totalTime')

    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.bar(jitter_labels, means_time, capsize=5,
    #        color='mediumseagreen', alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.plot(means_time,
           color='mediumseagreen', alpha=0.8)
    ax.set_xlabel('Jitter (RTT%)')
    ax.set_ylabel('Time (s)')
    ax.set_title('Avg Total Slow Start Phase Time by Jitter')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)

    ax.set_xticks([float(ll) for ll in jitter_labels])
    ax.set_xticklabels(jitter_labels)

    ax.set_axisbelow(True)
    plt.ylim(bottom=0)
    # plt.xlim((0,1))
    plt.tight_layout()
    plt.rcParams.update({'font.size':14})
    plt.setp(ax.get_xticklabels(),rotation=30,horizontalalignment='right')
    plt.savefig(os.path.join(output_dir, f'graph2_total_time-{suffix}.png'), dpi=300)
    plt.close()
    print(f"Saved graph2_total_time-{suffix}.png")

    # ── Graph 3: Avg First CSS Time vs Jitter ────────────────────────────────
    means_fcss, ci_fcss = compute_ci(result_df, 'firstCSSTime')

    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.bar(jitter_labels, means_fcss,  capsize=5,
    #        color='mediumpurple', alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.plot(means_fcss, color='mediumpurple', alpha=0.8)
    ax.set_xlabel('Jitter (RTT%)')
    ax.set_ylabel('Time (s)')
    ax.set_title('Avg First CSS Time')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)

    ax.set_xticks([float(ll) for ll in jitter_labels])
    ax.set_xticklabels(jitter_labels)

    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.ylim(bottom=0)
    # plt.xlim((0,1))
    plt.rcParams.update({'font.size':14})
    plt.setp(ax.get_xticklabels(),rotation=30,horizontalalignment='right')
    plt.savefig(os.path.join(output_dir, f'graph3_first_css_time-{suffix}.png'), dpi=300)
    plt.close()
    print(f"Saved graph3_first_css_time{suffix}.png")
    file.write("PercentCSS: "+str(means_css)+"\n")
    file.write("FirstCSS: "+str(means_fcss)+"\n")
    file.write("ExitTimes: "+str(means_time)+"\n")
    groups = result_df.groupby('jitter')['transitions']
    transitionCOuntmeans = groups.mean()
    file.write("ExitTimes: "+str(transitionCOuntmeans)+"\n")


def main():
    df = pd.read_csv(datastoreFile)
    df = df.loc[df.index >0 ]
    df = df.loc[df['transitions'] >0 ]
    df = df.drop_duplicates(subset=['filename'])
    mpc = df.loc[df['jitterType']=='PC']
    print(mpc)
    # print()
    # mms = df.loc[df['jitterType']=='MS']
    # print(mms)
    # print()
    dataPC =  aggregateOnJitter(mpc)
    # dataMS =  aggregateOnJitter(mms)
    # print(dataPC)
    # print(dataMS)

    plot_jitter_graphs(mpc,'PC')
    # plot_jitter_graphs(mms,'MS')


    pass

if __name__ == '__main__':
    main()