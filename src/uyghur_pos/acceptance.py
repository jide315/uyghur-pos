"""Pre-registered point-estimate gates; uncertainty is reported separately."""
import statistics

def verdict(checks):
    values=list(checks.values())
    if False in values:return 'FAIL'
    if None in values:return 'INCONCLUSIVE'
    return 'PASS'

def quality_gates(baseline, candidates):
    if len(candidates)!=3:return dict(three_seeds=None)
    b=baseline['groups'];groups=[r['groups'] for r in candidates]
    checks={}
    for key in ['overall','nonpunct']:
        checks[f'{key}_mean_loss_le_1pp']=b[key]['accuracy']-statistics.mean(r[key]['accuracy'] for r in groups)<=.01+1e-12
    checks['worst_overall_loss_le_1_5pp']=b['overall']['accuracy']-min(r['overall']['accuracy'] for r in groups)<=.015+1e-12
    checks['oov_loss_le_2pp']=(b['oov']['accuracy']-statistics.mean(r['oov']['accuracy'] for r in groups)<=.02+1e-12) if b['oov']['n']>=100 else None
    return checks

def resource_gates(baseline, candidates, target):
    checks={}
    for name,r in candidates.items():
        checks[f'{name}_measurement_stable']=True if baseline['stable'] and r['stable'] else None
        if target=='latency':
            checks[f'{name}_speedup_ge_2x']=baseline['p50']/r['p50']>=2.-1e-12
            checks[f'{name}_p95_not_worse']=r['p95']<=baseline['p95']
        elif target=='memory':checks[f'{name}_rss_half']=r['rss']/baseline['rss']<=.5+1e-12
        else:raise ValueError('unknown resource target')
    return checks
