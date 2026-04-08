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

    # Helper to compute 95% CI from a dataframe of raw values grouped by jitter
    def compute_ci(df, col):
        groups = df.groupby('jitter')[col]
        means = groups.mean()
        sems = groups.sem().fillna(0)
        ci = 1.96 * sems  # 95% CI
        return means, ci

    # ── Graph 1: Avg %CSS and %SS vs Jitter ──────────────────────────────────
    means_css, ci_css = compute_ci(result_df, 'percentCSS')
    means_ss,  ci_ss  = compute_ci(result_df, 'percentSS')

    jitter_labels = means_css.index.astype(str)
    x = np.arange(len(jitter_labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, means_css, width, yerr=ci_css, capsize=5,
           label='Avg % CSS', color='steelblue', alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.bar(x + width/2, means_ss,  width, yerr=ci_ss,  capsize=5,
           label='Avg % SS',  color='coral',     alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.set_xlabel('Jitter')
    ax.set_ylabel('Percentage')
    ax.set_title('Avg % CSS and % SS by Jitter (95% CI)')
    ax.set_xticks(x)
    ax.set_xticklabels(jitter_labels)
    ax.legend()
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'graph1_css_ss_percentage-{suffix}.png'), dpi=150)
    plt.close()
    print(f"Saved graph1_css_ss_percentage-{suffix}.png")

    # ── Graph 2: Avg Total Slow Start Phase Time vs Jitter ───────────────────
    means_time, ci_time = compute_ci(result_df, 'totalTime')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(jitter_labels, means_time, yerr=ci_time, capsize=5,
           color='mediumseagreen', alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.set_xlabel('Jitter')
    ax.set_ylabel('Time (s)')
    ax.set_title('Avg Total Slow Start Phase Time by Jitter (95% CI)')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'graph2_total_time-{suffix}.png'), dpi=150)
    plt.close()
    print(f"Saved graph2_total_time-{suffix}.png")

    # ── Graph 3: Avg First CSS Time vs Jitter ────────────────────────────────
    means_fcss, ci_fcss = compute_ci(result_df, 'firstCSSTime')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(jitter_labels, means_fcss, yerr=ci_fcss, capsize=5,
           color='mediumpurple', alpha=0.8, error_kw={'elinewidth': 1.5})
    ax.set_xlabel('Jitter')
    ax.set_ylabel('Time (s)')
    ax.set_title('Avg First CSS Time by Jitter (95% CI)')
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'graph3_first_css_time-{suffix}.png'), dpi=150)
    plt.close()
    print(f"Saved graph3_first_css_time{suffix}.png")

def main():
    df = pd.read_csv(datastoreFile)
    df = df.loc[df.index >0 ]
    df = df.drop_duplicates(subset=['filename'])
    mpc = df.loc[df['jitterType']=='PC']
    print(mpc)
    # print()
    mms = df.loc[df['jitterType']=='MS']
    print(mms)
    # print()
    dataPC =  aggregateOnJitter(mpc)
    dataMS =  aggregateOnJitter(mms)
    # print(dataPC)
    # print(dataMS)

    plot_jitter_graphs(mpc,'PC')
    plot_jitter_graphs(mms,'MS')


    pass

if __name__ == '__main__':
    main()