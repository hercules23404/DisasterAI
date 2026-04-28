"""
DisasterAI — Knowledge Tree via graphify
Extracts code graph, clusters communities, exports interactive HTML.
"""

from pathlib import Path
from graphify.extract import collect_files, extract
from graphify.build import build
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections
from graphify.report import generate
from graphify.export import to_html

ROOT = Path("/Users/hercules/DisasterAI")
OUT  = ROOT / "results" / "knowledge_tree"
OUT.mkdir(parents=True, exist_ok=True)

# ── 1. Collect Python files (skip venv / epymarl / __pycache__) ──────────────
all_files = collect_files(ROOT)
py_files = [
    f for f in all_files
    if f.suffix == ".py"
    and "epymarl" not in f.parts
    and "__pycache__" not in f.parts
    and "env" not in [p for p in f.parts if p not in ("env",)]  # keep env/ subdir
]

# be explicit: only DisasterAI's own Python
py_files = [
    f for f in all_files
    if f.suffix == ".py"
    and not any(skip in f.parts for skip in ("epymarl", "__pycache__", "site-packages"))
]

print(f"Extracting {len(py_files)} Python files …")
for f in py_files:
    print(f"  {f.relative_to(ROOT)}")

# ── 2. Extract AST nodes + edges ─────────────────────────────────────────────
extractions = extract(py_files, cache_root=ROOT)

# extract() returns a dict (single merged result) or list — normalise
if isinstance(extractions, dict):
    extractions = [extractions]

print(f"\nExtraction complete. Building graph …")

# ── 3. Build NetworkX graph ───────────────────────────────────────────────────
G = build(extractions, directed=True)
print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# ── 4. Cluster into communities ───────────────────────────────────────────────
print("Running Leiden community detection …")
communities = cluster(G)
print(f"Found {len(communities)} communities:")
for cid, members in sorted(communities.items()):
    print(f"  Community {cid}: {len(members)} nodes")

# ── 5. Generate human-readable community labels ───────────────────────────────
community_labels = {
    cid: f"Module-{cid} ({len(members)} nodes)"
    for cid, members in communities.items()
}

# ── 6. Export interactive HTML knowledge tree ─────────────────────────────────
html_path = str(OUT / "knowledge_tree.html")
print(f"\nExporting interactive HTML → {html_path}")
to_html(G, communities, html_path, community_labels=community_labels)

# ── 7. Text report ────────────────────────────────────────────────────────────
cohesion_scores  = score_all(G, communities)
god_node_list    = god_nodes(G, top_n=15)
surprise_list    = surprising_connections(G, communities, top_n=10)

report_path = OUT / "knowledge_tree_report.md"
report_text = generate(
    G,
    communities,
    cohesion_scores   = cohesion_scores,
    community_labels  = community_labels,
    god_node_list     = god_node_list,
    surprise_list     = surprise_list,
    detection_result  = {
        "total_files": len(py_files),
        "total_words": sum(
            len(f.read_text(errors="ignore").split()) for f in py_files
        ),
    },
    token_cost        = {},
    root              = str(ROOT),
)
report_path.write_text(report_text)
print(f"Report → {report_path}")

print("\nDone. Open results/knowledge_tree/knowledge_tree.html in a browser.")
