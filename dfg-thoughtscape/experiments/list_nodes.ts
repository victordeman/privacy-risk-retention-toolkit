// Dump every gold-tree node of every seeded lab (ThoughtScape commit 793795a).
// Usage, from a ThoughtScape checkout after `npm ci --ignore-scripts`:
//   THOUGHTSCAPE_DIR=$PWD npx tsx /path/to/list_nodes.ts > nodes.json
async function main() {
  const root = process.env.THOUGHTSCAPE_DIR ?? process.cwd();
  const { COURSE_LABS } = await import(`${root}/src/lib/seededLabs/index.ts`);
  let total = 0;
  const out: unknown[] = [];
  for (const [course, labs] of Object.entries<any>(COURSE_LABS)) {
    total += Object.keys(labs).length;
    for (const [slug, t] of Object.entries<any>(labs)) {
      t.goldTree.nodes.forEach((nd: any, i: number) => out.push({ course, slug, i, kind: nd.kind, content: nd.content }));
    }
  }
  console.error('labs', total, 'gold nodes', out.length);
  console.log(JSON.stringify(out));
}
main();
