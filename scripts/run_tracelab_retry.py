"""TraceLab tool-retry behavior after errors.

New deep-telemetry mechanism analysis: do agents retry the same tool after a
failed call, and do retries succeed? Observational only; no task outcomes.
"""

from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT.parent / 'workspace' / 'telemetry_audit' / 'samples' / 'tracelab.duckdb'
OUT = ROOT / 'outputs' / 'tracelab_deep'

SCHEMA_CHECK = "DESCRIBE tool_calls"

QUERIES = {
    # Retry = same session, same tool name, next call of that tool after an error.
    'retry_after_error.csv': '''
WITH seq AS (
  SELECT r.session_id, t.tool_name, t.emitted_at, t.is_error,
         LEAD(t.is_error) OVER w AS same_tool_next_is_error,
         LEAD(t.tool_name) OVER w AS same_tool_next_name,
         LEAD(t.emitted_at) OVER w AS same_tool_next_at
  FROM tool_calls t JOIN rounds r USING(round_pk)
  WINDOW w AS (PARTITION BY r.session_id, t.tool_name ORDER BY t.emitted_at)
)
SELECT
  COUNT(*) FILTER (WHERE is_error) errored_calls,
  COUNT(*) FILTER (WHERE is_error AND same_tool_next_is_error IS NOT NULL) errored_with_followup,
  COUNT(*) FILTER (WHERE is_error AND same_tool_next_is_error = false) retried_then_success,
  COUNT(*) FILTER (WHERE is_error AND same_tool_next_is_error) retried_then_error
FROM seq WHERE is_error IS NOT NULL''',
    # Baseline: success rate of first-attempt calls per tool usage sequence.
    'error_run_lengths.csv': '''
WITH marked AS (
  SELECT r.session_id, t.emitted_at, t.is_error,
         CASE WHEN t.is_error THEN 0 ELSE 1 END AS ok,
         ROW_NUMBER() OVER (PARTITION BY r.session_id ORDER BY t.emitted_at) -
         ROW_NUMBER() OVER (PARTITION BY r.session_id, CASE WHEN t.is_error THEN 0 ELSE 1 END ORDER BY t.emitted_at) AS grp
  FROM tool_calls t JOIN rounds r USING(round_pk)
  WHERE t.is_error IS NOT NULL
), runs AS (
  SELECT session_id, grp, MAX(CASE WHEN is_error THEN 1 ELSE 0 END) is_err_run, COUNT(*) len
  FROM marked GROUP BY session_id, grp
), err_runs AS (
  SELECT len FROM runs WHERE is_err_run = 1
), ok_runs AS (
  SELECT len FROM runs WHERE is_err_run = 0
)
SELECT
  (SELECT COUNT(*) FROM err_runs) error_runs,
  (SELECT MEDIAN(len) FROM err_runs) median_error_run_len,
  (SELECT QUANTILE_CONT(len, 0.9) FROM err_runs) p90_error_run_len,
  (SELECT MAX(len) FROM err_runs) max_error_run_len,
  (SELECT MEDIAN(len) FROM ok_runs) median_ok_run_len
FROM err_runs LIMIT 1''',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB))
    cols = [row[0] for row in con.execute(SCHEMA_CHECK).fetchall()]
    assert 'tool_name' in cols, f'tool_name missing: {cols}'
    for name, sql in QUERIES.items():
        df = con.execute(sql).df()
        df.to_csv(OUT / name, index=False)
    con.close()


if __name__ == '__main__':
    main()
