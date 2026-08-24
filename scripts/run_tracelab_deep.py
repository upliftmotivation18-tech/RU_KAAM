"""Export deep TraceLab sequence/tail/error-cascade summaries."""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DUCKDB = Path('/tmp/duckdb-bin/duckdb')
DB = Path('/data/workspace/telemetry_audit/samples/tracelab.duckdb')
OUT = ROOT / 'outputs' / 'tracelab_deep'

QUERIES = {
'round_position.csv': '''WITH x AS (SELECT *,NTILE(10) OVER(PARTITION BY session_id ORDER BY round_index) pos_decile FROM rounds WHERE input_tokens_total>0) SELECT pos_decile,COUNT(*) rounds,MEDIAN(input_tokens_total) med_input,MEDIAN(newly_append_tokens) med_append,MEDIAN(output_tokens) med_output,AVG(CASE WHEN input_tokens_total>0 THEN claude_cache_read_input_tokens::DOUBLE/input_tokens_total END) mean_cache_share FROM x GROUP BY 1 ORDER BY 1''',
'concentration.csv': '''WITH s AS (SELECT session_id,SUM(input_tokens_total) input_sum FROM rounds GROUP BY 1), r AS (SELECT *,PERCENT_RANK() OVER(ORDER BY input_sum DESC) pr FROM s), totals AS (SELECT SUM(input_sum) total FROM s) SELECT SUM(CASE WHEN pr<=0.01 THEN input_sum ELSE 0 END)/(SELECT total FROM totals) top1_share,SUM(CASE WHEN pr<=0.1 THEN input_sum ELSE 0 END)/(SELECT total FROM totals) top10_share,QUANTILE_CONT(input_sum,0.5) median,QUANTILE_CONT(input_sum,0.9) p90,QUANTILE_CONT(input_sum,0.99) p99,MAX(input_sum) max FROM r''',
'first_last_context.csv': '''WITH x AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY session_id ORDER BY round_index) rn_first,ROW_NUMBER() OVER(PARTITION BY session_id ORDER BY round_index DESC) rn_last FROM rounds WHERE input_tokens_total>0), p AS (SELECT session_id,MAX(CASE WHEN rn_first=1 THEN input_tokens_total END) first_input,MAX(CASE WHEN rn_last=1 THEN input_tokens_total END) last_input FROM x GROUP BY 1) SELECT COUNT(*) sessions,MEDIAN(first_input) med_first,MEDIAN(last_input) med_last,MEDIAN(last_input::DOUBLE/NULLIF(first_input,0)) med_ratio,QUANTILE_CONT(last_input::DOUBLE/NULLIF(first_input,0),0.9) p90_ratio FROM p''',
'error_burden.csv': '''WITH te AS (SELECT r.session_id,COUNT(*) tool_calls,SUM(t.is_error::INT) errors,SUM(t.tool_wall_latency_ms) wall_ms FROM tool_calls t JOIN rounds r USING(round_pk) GROUP BY 1), s AS (SELECT session_id,SUM(input_tokens_total) input_sum,COUNT(*) rounds FROM rounds GROUP BY 1) SELECT CASE WHEN errors=0 THEN '0' WHEN errors=1 THEN '1' WHEN errors BETWEEN 2 AND 5 THEN '2-5' ELSE '6+' END error_bin,COUNT(*) sessions,MEDIAN(tool_calls) med_tools,MEDIAN(wall_ms) med_wall_ms,MEDIAN(input_sum) med_input_sum,MEDIAN(rounds) med_rounds FROM te JOIN s USING(session_id) GROUP BY 1 ORDER BY CASE error_bin WHEN '0' THEN 1 WHEN '1' THEN 2 WHEN '2-5' THEN 3 ELSE 4 END''',
'error_cascade.csv': '''WITH x AS (SELECT r.session_id,t.emitted_at,t.is_error,LEAD(t.is_error) OVER(PARTITION BY r.session_id ORDER BY t.emitted_at) next_error FROM tool_calls t JOIN rounds r USING(round_pk) WHERE t.is_error IS NOT NULL) SELECT is_error,COUNT(*) antecedents,AVG(next_error::INT) next_error_rate FROM x WHERE next_error IS NOT NULL GROUP BY 1''',
'tool_result_growth.csv': '''WITH rr AS (SELECT session_id,round_index,input_tokens_total,LAG(input_tokens_total) OVER(PARTITION BY session_id ORDER BY round_index) prev_input,current_tool_result_chars FROM rounds WHERE input_tokens_total>0) SELECT CASE WHEN current_tool_result_chars=0 THEN '0' WHEN current_tool_result_chars<1000 THEN '<1k' WHEN current_tool_result_chars<10000 THEN '1k-10k' ELSE '10k+' END result_bin,COUNT(*) rounds,MEDIAN(input_tokens_total-prev_input) med_input_delta,QUANTILE_CONT(input_tokens_total-prev_input,0.9) p90_delta FROM rr WHERE prev_input IS NOT NULL GROUP BY 1''',
'top_tail_errors.csv': '''WITH te AS (SELECT r.session_id,SUM(t.is_error::INT) errors FROM tool_calls t JOIN rounds r USING(round_pk) GROUP BY 1), s AS (SELECT session_id,SUM(input_tokens_total) input_sum FROM rounds GROUP BY 1), z AS (SELECT *,NTILE(100) OVER(ORDER BY input_sum DESC) pct FROM s) SELECT SUM(CASE WHEN pct=1 THEN 1 ELSE 0 END) top_sessions,AVG(CASE WHEN pct=1 THEN COALESCE(errors,0) END) top1_mean_errors,AVG(CASE WHEN pct>1 THEN COALESCE(errors,0) END) rest_mean_errors FROM z LEFT JOIN te USING(session_id)''',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name,sql in QUERIES.items():
        r=subprocess.run([str(DUCKDB),'-csv',str(DB),sql],check=True,capture_output=True,text=True)
        (OUT/name).write_text(r.stdout)
    (OUT/'README.md').write_text('# Deep TraceLab telemetry\n\nObservational sequence/tail summaries without task outcomes or dollar billing. Associations must not be interpreted as causal failure-cost effects.\n')

if __name__=='__main__': main()
