"""Export reproducible TraceLab telemetry summaries from the public DuckDB mirror."""

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DUCKDB = Path('/tmp/duckdb-bin/duckdb')
DB = Path('/data/workspace/telemetry_audit/samples/tracelab.duckdb')
OUT = ROOT / 'outputs' / 'tracelab_telemetry'

QUERIES = {
    'scale.csv': "SELECT (SELECT COUNT(*) FROM rounds) rounds,(SELECT COUNT(DISTINCT session_id) FROM rounds) sessions,(SELECT COUNT(*) FROM tool_calls) tool_calls,(SELECT COUNT(DISTINCT model) FROM rounds) models",
    'token_cache_summary.csv': "SELECT MEDIAN(input_tokens_total) med_input,MEDIAN(output_tokens) med_output,MEDIAN(claude_cache_read_input_tokens) med_cache_read,AVG(CASE WHEN input_tokens_total>0 THEN claude_cache_read_input_tokens::DOUBLE/input_tokens_total END) mean_cache_share,MEDIAN(newly_append_tokens) med_new_append,QUANTILE_CONT(input_tokens_total,0.95) p95_input FROM rounds",
    'session_growth.csv': "WITH s AS (SELECT session_id,COUNT(*) rounds,MIN(input_tokens_total) first_input,MAX(input_tokens_total) max_input,MAX(input_tokens_total)-MIN(input_tokens_total) growth,SUM(output_tokens) output_sum,SUM(newly_append_tokens) append_sum FROM rounds GROUP BY 1) SELECT COUNT(*) sessions,MEDIAN(rounds) med_rounds,MEDIAN(growth) med_growth,QUANTILE_CONT(growth,0.9) p90_growth,QUANTILE_CONT(growth,0.99) p99_growth,MEDIAN(output_sum) med_output_sum FROM s",
    'tool_error_latency.csv': "SELECT is_error,COUNT(*) calls,MEDIAN(tool_wall_latency_ms) med_ms,QUANTILE_CONT(tool_wall_latency_ms,0.95) p95_ms,MEDIAN(result_chars) med_chars FROM tool_calls GROUP BY 1",
    'tools.csv': "SELECT tool_name,COUNT(*) calls,AVG(is_error::INT) error_rate,MEDIAN(tool_wall_latency_ms) med_wall_ms,QUANTILE_CONT(tool_wall_latency_ms,0.95) p95_wall_ms,MEDIAN(result_chars) med_result_chars FROM tool_calls GROUP BY 1 HAVING COUNT(*)>=100 ORDER BY calls DESC",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not DUCKDB.exists() or not DB.exists():
        raise FileNotFoundError('DuckDB CLI or TraceLab DB missing')
    for name, sql in QUERIES.items():
        result = subprocess.run([str(DUCKDB), '-csv', str(DB), sql], check=True, capture_output=True, text=True)
        (OUT / name).write_text(result.stdout)
    (OUT / 'README.md').write_text(
        '# TraceLab telemetry analysis\n\n'
        'Source: dharshanrai/tracelab-syfi-coding-trace, public CC-BY-4.0 DuckDB mirror. '
        'This analysis describes real coding-agent session telemetry. It does not include benchmark task outcomes or dollar billing, so results concern context/cache/tool anatomy rather than task efficiency or cost per success.\n'
    )


if __name__ == '__main__':
    main()
