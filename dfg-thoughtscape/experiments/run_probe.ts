// Stress test of ThoughtScape's similarity step (commit 793795a).
// Usage, from a ThoughtScape checkout after `npm ci --ignore-scripts`:
//   THOUGHTSCAPE_DIR=$PWD npx tsx /path/to/run_probe.ts   (run inside experiments/)
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
async function main() {
  const here = dirname(fileURLToPath(import.meta.url));
  const root = process.env.THOUGHTSCAPE_DIR ?? process.cwd();
  const { embed, cosineSimilarity } = await import(`${root}/src/lib/engine/embeddingUtils.ts`);
  const { COURSE_LABS } = await import(`${root}/src/lib/seededLabs/index.ts`);
  const sel = JSON.parse(readFileSync(join(here, 'selected.json'), 'utf8'));
  const probes = JSON.parse(readFileSync(join(here, 'probes.json'), 'utf8'));
  const dist = (a: string, b: string) => 1 - cosineSimilarity(embed(a), embed(b));
  const rows: any[] = [];
  for (const p of probes) {
    const s = sel[p.i];
    const lab = COURSE_LABS[s.course][s.slug];
    const gold = lab.goldTree.nodes[s.i].content;
    if (gold !== s.content) throw new Error('gold step changed for probe ' + p.i);
    const peers: string[] = lab.goldTree.nodes.map((n: any) => n.content);
    const rank = (txt: string) => {
      const ds = peers.map((c) => dist(txt, c));
      const own = ds[s.i];
      return 1 + ds.filter((d, j) => j !== s.i && d < own).length; // 1 = own gold step is nearest
    };
    rows.push({
      i: p.i, course: s.course, slug: s.slug, gold,
      d_light: dist(gold, p.light), d_heavy: dist(gold, p.heavy), d_near: dist(gold, p.near),
      rank_light: rank(p.light), rank_heavy: rank(p.heavy), rank_near: rank(p.near), n_peers: peers.length,
    });
  }
  writeFileSync(join(here, 'results.json'), JSON.stringify(rows, null, 1));
  console.log('wrote results.json,', rows.length, 'probes');
}
main();
