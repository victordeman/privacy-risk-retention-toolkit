"""Summary statistics for results.json (Wilson intervals, tie rule |diff| <= 1e-9)."""
import json, math, statistics as st, sys
r = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'results.json')); n = len(r); eps = 1e-9
def wilson(k, n, z=1.96):
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return round(c-h, 2), round(c+h, 2)
lw = sum(1 for x in r if x['d_light'] < x['d_near']-eps); lt = sum(1 for x in r if abs(x['d_light']-x['d_near']) <= eps)
print('n', n)
print('light closer than near:', lw, 'ties', lt, 'near closer', n-lw-lt)
print('heavy closer than near:', sum(1 for x in r if x['d_heavy'] < x['d_near']-eps))
for k in ('light', 'heavy', 'near'):
    v = [x['d_'+k] for x in r]; print('mean d_%s %.3f  median %.3f' % (k, st.mean(v), st.median(v)))
for t in (0.6, 0.7):
    for k in ('light', 'heavy', 'near'):
        c = sum(1 for x in r if x['d_'+k] > t); print('d_%s > %.1f: %d/%d CI %s' % (k, t, c, n, wilson(c, n)))
c = sum(1 for x in r if x['rank_heavy'] == 1)
print('heavy gold ranked first: %d/%d CI %s ; chance %.2f (=%.1f items)' % (c, n, wilson(c, n), st.mean(1/x['n_peers'] for x in r), sum(1/x['n_peers'] for x in r)))
print('mean rank heavy %.2f of mean %.2f candidates' % (st.mean(x['rank_heavy'] for x in r), st.mean(x['n_peers'] for x in r)))
