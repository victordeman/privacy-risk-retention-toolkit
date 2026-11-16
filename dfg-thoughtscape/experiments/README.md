# Stress test of ThoughtScape's similarity step

Reproducible test described in Section 1.3 of the proposal and Section 5 of the paper.

| File | What it is |
|---|---|
| `probes.json` | 22 probe items: for each selected gold step a light rewording (`light`), a heavy rewording with the same meaning (`heavy`) and a minimal wrong edit (`near`). **Written by an AI assistant; not yet validated by a domain expert.** |
| `selected.json` | The 22 gold steps (seed 7), with course, lab slug, node index |
| `nodes.json` | All 375 gold steps of the six seeded courses at ThoughtScape commit `793795a` |
| `list_nodes.ts`, `select_nodes.py`, `run_probe.ts`, `summarize.py` | Scripts |
| `results.json`, `summary.txt` | Raw per-item distances/ranks and the summary |

Run (Node 22, a ThoughtScape checkout at commit `793795a`; use `npm ci --ignore-scripts`, the native SQLite build is not needed):

```bash
cd thought-scape && npm ci --ignore-scripts
export THOUGHTSCAPE_DIR=$PWD
npx tsx ../experiments/list_nodes.ts > ../experiments/nodes.json
python3 ../experiments/select_nodes.py ../experiments/nodes.json > ../experiments/selected.json
npx tsx ../experiments/run_probe.ts
python3 ../experiments/summarize.py ../experiments/results.json
```

The shipped `results.json` was reproduced exactly from the stored selection when the scripts were re-run.

Limits: n = 22, author-written probes, adversarial to lexical similarity by design, step-level only (alignment and tree rules not tested). See the paper's Section 5.
