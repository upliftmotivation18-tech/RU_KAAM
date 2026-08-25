"""Create compact figures/tables for the verified cross-source telemetry anatomy."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'paper'/'figures'
APP=ROOT/'paper'/'appendix'
FIG.mkdir(parents=True,exist_ok=True); APP.mkdir(parents=True,exist_ok=True)
base=ROOT/'outputs'/'tracelab_telemetry'
deep=ROOT/'outputs'/'tracelab_deep'
cache=pd.read_csv(base/'token_cache_summary.csv').iloc[0]
growth=pd.read_csv(deep/'first_last_context.csv').iloc[0]
concentration=pd.read_csv(deep/'concentration.csv').iloc[0]
errors=pd.read_csv(deep/'error_burden.csv')

fig,axes=plt.subplots(1,2,figsize=(7.2,2.65),constrained_layout=True)
axes[0].bar(['Top 1%','Top 10%'],[concentration.top1_share*100,concentration.top10_share*100],color=['#D55E00','#0072B2'])
axes[0].set_ylim(0,100); axes[0].set_ylabel('Share of summed input tokens (%)'); axes[0].set_title('Input burden is concentrated')
for i,v in enumerate([concentration.top1_share*100,concentration.top10_share*100]): axes[0].text(i,v+2,f'{v:.1f}%',ha='center',fontsize=8)
axes[1].scatter(errors.error_bin,errors.med_input_sum/1e6,color='#0072B2',s=38)
axes[1].set_ylabel('Median summed input tokens (millions)',fontsize=8); axes[1].set_xlabel('Observed tool errors per session',fontsize=8); axes[1].set_title('Higher error counts are associated with heavier sessions',fontsize=9)
axes[1].set_ylim(bottom=0)
fig.savefig(FIG/'tracelab_tail_error_burden.pdf',bbox_inches='tight')
fig.savefig(FIG/'tracelab_tail_error_burden.png',dpi=300,bbox_inches='tight')
plt.close(fig)

rows=pd.DataFrame([
 {'Source':'TraceLab','Sessions / rounds':'8,058 / 665,453','Context/cache result':'93.7% mean cache-read share; median last/first context 3.6x','Scope':'Real sessions; no task outcome or dollars'},
 {'Source':'MIMO Claude Code','Sessions / rounds':'1,017 / 4,690','Context/cache result':'753M cache-read vs 46M uncached input; error cascade 4.33x after a tool error','Scope':'One model; per-round usage constant within session; outcome unverified'},
 {'Source':'Open-SWE','Sessions / rounds':'977 matched pairs','Context/cache result':'OpenHands/SWE-agent tool-call ratio 0.85 [0.82, 0.86]','Scope':'Exact task/model match; no tokens or dollars'},
])
def tex_escape_pct(df):
    return df.applymap(lambda v: v.replace('%', '\\%') if isinstance(v, str) else v)

rows=tex_escape_pct(rows)
(APP/'telemetry_anatomy.tex').write_text(rows.to_latex(index=False,escape=False,column_format='lp{3cm}p{5cm}p{4cm}'))

summary=pd.DataFrame([
 {'Metric':'TraceLab rounds','Value':'665,453'},
 {'Metric':'TraceLab sessions','Value':'8,058'},
 {'Metric':'Median input / output tokens per round','Value':'132,092 / 249'},
 {'Metric':'Mean cache-read share','Value':'93.7\\%'},
 {'Metric':'Median context growth per session','Value':'47,267 tokens'},
 {'Metric':'Top 1\\% input-token share','Value':'48.3\\%'},
 {'Metric':'Next tool error after success / error','Value':'4.9\\% / 21.0\\%'},
])
mimo_scale=pd.read_csv(ROOT/'outputs'/'mimo_deep'/'scale.csv').iloc[0]
mimo_cascade=pd.read_csv(ROOT/'outputs'/'mimo_deep'/'error_cascade.csv')
mimo_ok=mimo_cascade.loc[mimo_cascade.is_error==False,'next_error_rate'].iloc[0]
mimo_err=mimo_cascade.loc[mimo_cascade.is_error==True,'next_error_rate'].iloc[0]
retry=pd.read_csv(deep/'retry_after_error.csv').iloc[0]
runs=pd.read_csv(deep/'error_run_lengths.csv').iloc[0]
summary=pd.concat([summary,pd.DataFrame([
 {'Metric':'MIMO sessions / rounds','Value':f"{int(mimo_scale.sessions):,} / {int(mimo_scale.rounds):,}"},
 {'Metric':'MIMO next tool error after success / error','Value':f"{mimo_ok*100:.1f}\\% / {mimo_err*100:.1f}\\%"},
 {'Metric':'Errored calls with a later same-tool retry / retry succeeds','Value':f"{retry.errored_with_followup/retry.errored_calls*100:.1f}\\% / {retry.retried_then_success/retry.errored_with_followup*100:.1f}\\%"},
 {'Metric':'Consecutive-error run length, median / P90 / max','Value':f"{int(runs.median_error_run_len)} / {int(runs.p90_error_run_len)} / {int(runs.max_error_run_len)}"},
])],ignore_index=True)
(APP/'tracelab_key_metrics.tex').write_text(summary.to_latex(index=False,escape=False,column_format='lr'))
