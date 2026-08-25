"""Export defensible MIMO Claude Code telemetry summaries.

Audit note (2026-08): in every one of the 1,017 released sessions the
per-round usage block repeats a single constant tuple (uncached input,
cache creation, cache read, output are identical for all rounds in a
session). Within-session token dynamics therefore cannot be validated in
this source and are not exported here. Session/round counts, corpus
totals, cross-session concentration, and tool-error sequences (from
message content, not usage fields) remain analyzable.

Mirrors scripts/run_tracelab_deep.py definitions where applicable.
Observational only: no task outcomes or dollar billing in this source.
"""

from pathlib import Path
import json
import math
from collections import Counter, defaultdict

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MIMO_DIR = ROOT.parent / 'workspace' / 'telemetry_audit' / 'mimo_all'
OUT = ROOT / 'outputs' / 'mimo_deep'


def result_chars(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(len(i.get('text', '') or '') for i in content
                   if isinstance(i, dict) and i.get('type') == 'text')
    return 0


def parse_session(path):
    """Return (n_rounds, session_token_tuple_or_None, tool_error_flags)."""
    n_rounds = 0
    usage_sig = set()
    totals = [0, 0, 0, 0]
    tool_errors = []
    for line in open(path):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('isSidechain'):
            continue
        t = d.get('type')
        if t == 'assistant':
            u = (d.get('message') or {}).get('usage')
            if not u:
                continue
            sig = (u.get('input_tokens') or 0, u.get('cache_creation_input_tokens') or 0,
                   u.get('cache_read_input_tokens') or 0, u.get('output_tokens') or 0)
            usage_sig.add(sig)
            for i, v in enumerate(sig):
                totals[i] += v
            n_rounds += 1
        elif t == 'user':
            c = (d.get('message') or {}).get('content')
            if isinstance(c, list):
                for item in c:
                    if isinstance(item, dict) and item.get('type') == 'tool_result':
                        tool_errors.append(bool(item.get('is_error')))
    return n_rounds, (totals if len(usage_sig) == 1 else None), usage_sig, tool_errors


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return float('nan')
    mid = n // 2
    return xs[mid] if n % 2 else (xs[mid - 1] + xs[mid]) / 2


def quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return float('nan')
    pos = (len(xs) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo] if lo == hi else xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(MIMO_DIR.glob('session__*.jsonl'))

    grand = Counter()
    session_inputs = {}
    session_rounds = {}
    session_tools = {}
    session_errors = {}
    constant_sessions = 0
    cascade = Counter()

    for path in files:
        n_rounds, totals, usage_sig, tool_errors = parse_session(path)
        if totals is not None:
            constant_sessions += 1
        for i, key in enumerate(['uncached', 'append', 'cache_read', 'output']):
            grand[key] += totals[i] if totals else 0
        s_in = sum(totals[:3]) if totals else 0
        session_inputs[path.name] = s_in
        session_rounds[path.name] = n_rounds
        session_tools[path.name] = len(tool_errors)
        session_errors[path.name] = sum(tool_errors)
        for a, b in zip(tool_errors, tool_errors[1:]):
            cascade[(a, b)] += 1

    pd.DataFrame([{
        'sessions': len(files),
        'sessions_constant_per_round_usage': constant_sessions,
        'rounds': sum(session_rounds.values()),
        'uncached_input_tokens': grand['uncached'],
        'cache_creation_tokens': grand['append'],
        'cache_read_tokens': grand['cache_read'],
        'output_tokens': grand['output'],
    }]).to_csv(OUT / 'scale.csv', index=False)

    inputs = sorted(session_inputs.values())
    total_in = sum(inputs)
    top1 = inputs[-max(1, int(round(0.01 * len(inputs)))):]
    top10 = inputs[-max(1, int(round(0.10 * len(inputs)))):]
    pd.DataFrame([{
        'top1_share': sum(top1) / total_in,
        'top10_share': sum(top10) / total_in,
        'median': median(inputs),
        'p90': quantile(inputs, 0.9),
        'p99': quantile(inputs, 0.99),
        'max': max(inputs),
    }]).to_csv(OUT / 'concentration.csv', index=False)

    ok_then = cascade[(False, False)] + cascade[(False, True)]
    err_then = cascade[(True, False)] + cascade[(True, True)]
    pd.DataFrame([
        {'is_error': False, 'antecedents': ok_then,
         'next_error_rate': cascade[(False, True)] / ok_then if ok_then else float('nan')},
        {'is_error': True, 'antecedents': err_then,
         'next_error_rate': cascade[(True, True)] / err_then if err_then else float('nan')},
    ]).to_csv(OUT / 'error_cascade.csv', index=False)

    bins = [('0', lambda e: e == 0), ('1', lambda e: e == 1),
            ('2-5', lambda e: 2 <= e <= 5), ('6+', lambda e: e >= 6)]
    rows = []
    for label, cond in bins:
        names = [n for n, e in session_errors.items() if cond(e)]
        if not names:
            continue
        rows.append({
            'error_bin': label,
            'sessions': len(names),
            'med_rounds': median([session_rounds[n] for n in names]),
            'med_tools': median([session_tools[n] for n in names]),
            'med_input_sum': median([session_inputs[n] for n in names]),
        })
    pd.DataFrame(rows).to_csv(OUT / 'error_burden.csv', index=False)

    # Spearman correlation between round count and summed input at session level.
    # Mechanical under constant per-round usage (input = k * rounds); kept as an
    # explicit audit artifact rather than a finding.
    from scipy.stats import spearmanr
    ns = [session_rounds[n.name] for n in files]
    ins = [session_inputs[n.name] for n in files]
    rho, p = spearmanr(ns, ins)
    pd.DataFrame([{'spearman_rounds_vs_input': rho, 'p_value': p}]).to_csv(
        OUT / 'session_size_correlation.csv', index=False)

    (OUT / 'README.md').write_text(
        '# Deep MIMO telemetry\n\n'
        'Defensible session-level summaries of the MIMO Claude Code corpus.\n\n'
        f'- Sessions: {len(files)}; sessions with constant per-round usage: {constant_sessions} '
        '(within-session token dynamics unverifiable; not analyzed).\n'
        '- Tool-error sequences derive from message content flags, independent of usage fields.\n'
        '- Observational only; no task outcomes or dollar billing.\n')


if __name__ == '__main__':
    main()
