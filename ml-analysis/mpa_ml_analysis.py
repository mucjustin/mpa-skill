"""
MPA Skill ML Analysis — Nature/Science aesthetic
==================================================
Clean, publication-grade figures with benchmark scores.
"""

import json, re, os, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import jieba

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# ── paths ──
REPO = r"E:\CodexProjects\mpa-skill-public"
OUT = os.path.join(REPO, "ml-analysis", "output")
os.makedirs(OUT, exist_ok=True)

# ── Nature/Science palette ──
PAL = {
    "blue":    "#3B6EA5",
    "teal":    "#4FB0A6",
    "coral":   "#E8645A",
    "amber":   "#E8A33D",
    "purple":  "#7C6FA8",
    "green":   "#5BA053",
    "gray":    "#9E9E9E",
    "dark":    "#2C2C2A",
    "light":   "#F5F5F3",
}
SEQ = [PAL["blue"], PAL["teal"], PAL["coral"], PAL["amber"], PAL["purple"], PAL["green"], PAL["gray"]]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
    "font.size": 10,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#CCCCCC",
    "axes.labelcolor": PAL["dark"],
    "text.color": PAL["dark"],
    "xtick.color": PAL["dark"],
    "ytick.color": PAL["dark"],
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

def cn_tok(t):
    return [w.strip() for w in jieba.cut(t) if len(w.strip()) > 1]

def read_file(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return f.read()

# ── helper: clean spines ──
def clean_axes(ax, grid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(axis="y", alpha=0.25, linewidth=0.5, linestyle="--")

# ── helper: big score label on bars ──
def score_labels(ax, bars, fmt="{:.1%}", dy=0.02, fs=10):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + dy, fmt.format(h),
                ha="center", va="bottom", fontsize=fs, fontweight="bold", color=PAL["dark"])


# ============================================================
# Fig 1: Route similarity heatmap + query accuracy comparison
# ============================================================
def fig1_route_analysis():
    print("Fig 1: Route analysis ...")
    routing = read_file("skills/mpa-skill/references/routing.md")
    matches = re.findall(r'\| (\w[\w\s-]+?) \| (.+?) \| (.+?) \| (.+?) \|', routing)
    routes = []
    for name, output, cn_kw, seq in matches:
        name = name.strip()
        if name in ("Route", "---"):
            continue
        routes.append({"name": name, "cn": cn_kw.strip(), "full": f"{name} {output} {cn_kw} {seq}"})

    # similarity
    vec = TfidfVectorizer(tokenizer=cn_tok, token_pattern=None, max_features=500, ngram_range=(1,2))
    tfidf = vec.fit_transform([r["full"] for r in routes])
    sim = cosine_similarity(tfidf)

    # query test
    queries = [
        ("文献综述", "literature"), ("案例分析", "case analysis"),
        ("调研数据", "data analysis"), ("论文答辩", "defence"),
        ("政策备忘录", "policy memo"), ("案例大赛", "case competition entry"),
        ("研究方案", "research design"), ("田野调查", "fieldwork"),
        ("硕士论文", "thesis"), ("非公管转公管", "non-MPA to MPA conversion"),
        ("分析理论", "theory grounding"), ("中国适用性", "china-context check"),
        ("课程复习", "course"), ("政策分析报告", "policy memo"),
    ]
    q_vecs = vec.transform([q[0] for q in queries])
    q_sim = cosine_similarity(q_vecs, tfidf)

    correct = sum(1 for i, (_, exp) in enumerate(queries) if routes[np.argmax(q_sim[i])]["name"] == exp)

    # ── figure: 2 panels ──
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [1.1, 1]})

    # left: heatmap
    labels = [r["name"][:14] for r in routes]
    mask = np.triu(np.ones_like(sim, dtype=bool), k=1)
    im = ax1.imshow(np.where(mask, np.nan, sim), cmap="YlGnBu", vmin=0, vmax=0.5, aspect="equal")
    ax1.set_xticks(range(len(labels)))
    ax1.set_yticks(range(len(labels)))
    ax1.set_xticklabels(labels, rotation=50, ha="right", fontsize=7)
    ax1.set_yticklabels(labels, fontsize=7)
    for i in range(len(routes)):
        for j in range(i+1, len(routes)):
            v = sim[i][j]
            if v > 0.15:
                ax1.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6, color=PAL["dark"] if v < 0.3 else "white")
    ax1.set_title("Route similarity matrix", fontsize=11, pad=8, fontweight="bold")
    cb = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cb.set_label("Cosine similarity", fontsize=8)
    cb.ax.tick_params(labelsize=7)

    # right: query accuracy gauge
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.5, 3)
    ax2.axis("off")

    # gauge bar
    acc = correct / len(queries)
    ax2.barh(1.5, 1.0, height=0.4, color=PAL["light"], edgecolor="#DDD", linewidth=0.5)
    ax2.barh(1.5, acc, height=0.4, color=PAL["teal"] if acc > 0.8 else PAL["amber"], edgecolor="none")
    ax2.text(acc/2, 1.5, f"{acc:.0%}", ha="center", va="center", fontsize=20, fontweight="bold", color="white")
    ax2.text(0, 2.1, "Chinese query → route accuracy", fontsize=11, fontweight="bold", color=PAL["dark"])
    ax2.text(0, 0.9, f"{correct}/{len(queries)} queries matched correctly", fontsize=9, color=PAL["gray"])

    # per-query dots
    for i, (q, exp) in enumerate(queries):
        best = np.argmax(q_sim[i])
        hit = routes[best]["name"] == exp
        y = 0.4 - i * 0.04
        ax2.plot(0.02, y, "o", color=PAL["green"] if hit else PAL["coral"], markersize=3)
        ax2.text(0.04, y, f"{q} → {routes[best]['name']}", fontsize=6.5, va="center", color=PAL["dark"] if hit else PAL["coral"])

    fig.suptitle("MPA Skill — bilingual route matching", fontsize=13, fontweight="bold", y=1.01, color=PAL["dark"])
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "fig1_route_analysis.png"), dpi=200)
    plt.close()
    print(f"  -> fig1_route_analysis.png  (accuracy={correct}/{len(queries)})")


# ============================================================
# Fig 2: Knowledge domain PCA scatter
# ============================================================
def fig2_knowledge_pca():
    print("Fig 2: Knowledge domain ...")
    files = {
        "theory":  ("skills/mpa-skill/references/mpa-theory-map.md", "理论"),
        "context": ("skills/mpa-skill/references/mpa-china-contexts.md", "情境"),
        "principle": ("skills/mpa-skill/references/mpa-thinking-checklist.md", "原则"),
        "course":  ("skills/mpa-skill/references/mpa-course-map.md", "课程"),
    }
    items, labels, types = [], [], []
    for typ, (path, _) in files.items():
        text = read_file(path)
        rows = re.findall(r'\| (.+?) \| (.+?) \|', text)
        for cells in rows:
            c0 = cells[0].strip()
            if "理论" == c0 or "维度" in c0 or "原则" in c0 or "课程" in c0 or c0 == "---":
                continue
            items.append(f"{c0} {cells[1].strip()}")
            labels.append(c0)
            types.append(typ)

    vec = TfidfVectorizer(tokenizer=cn_tok, token_pattern=None, max_features=800, ngram_range=(1,2))
    tfidf = vec.fit_transform(items)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf.toarray())

    fig, ax = plt.subplots(figsize=(12, 8))
    type_cfg = {
        "theory":    (PAL["blue"], "o", "Theory"),
        "context":   (PAL["teal"], "s", "Context"),
        "principle": (PAL["coral"], "^", "Principle"),
        "course":    (PAL["amber"], "D", "Course"),
    }
    for typ in ["theory", "context", "principle", "course"]:
        mask = [t == typ for t in types]
        xs = [coords[i][0] for i in range(len(coords)) if mask[i]]
        ys = [coords[i][1] for i in range(len(coords)) if mask[i]]
        c, m, lbl = type_cfg[typ]
        ax.scatter(xs, ys, c=c, marker=m, label=f"{lbl} ({sum(mask)})", s=55, alpha=0.75, edgecolors="white", linewidth=0.4)

    for i, lbl in enumerate(labels):
        ax.annotate(lbl[:8], (coords[i][0], coords[i][1]), fontsize=5.5, alpha=0.55, xytext=(2, 2), textcoords="offset points")

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=10)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=10)
    ax.set_title("MPA knowledge domain — PCA projection", fontsize=12, fontweight="bold", pad=10)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.7, edgecolor="#DDD")
    clean_axes(ax)
    ax.set_facecolor("#FAFAFA")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "fig2_knowledge_pca.png"), dpi=200)
    plt.close()
    n = len(items)
    print(f"  -> fig2_knowledge_pca.png  ({n} items)")


# ============================================================
# Fig 3: Benchmark — the money chart
# ============================================================
def fig3_benchmark():
    print("Fig 3: Benchmark ...")
    R = json.loads(read_file("docs/validation/v2.4.0-results.json"))
    m = R["metrics"]

    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)

    # ── Panel A: synthetic pass rate bar ──
    axA = fig.add_subplot(gs[0, 0])
    conds = ["no skill", "v2.3.0", "v2.4.0"]
    rates = [m["synthetic"]["none"]["rate"], m["synthetic"]["v2.3.0"]["rate"], m["synthetic"]["v2.4.0"]["rate"]]
    colors = [PAL["gray"], PAL["blue"], PAL["teal"]]
    bars = axA.bar(conds, rates, color=colors, width=0.55, edgecolor="white", linewidth=0.5)
    axA.set_ylim(0, 1.2)
    score_labels(axA, bars, "{:.0%}", 0.03, 9)
    axA.axhline(1.0, color=PAL["coral"], linestyle="--", linewidth=0.8, alpha=0.6)
    axA.text(2.4, 1.02, "100% target", fontsize=7, color=PAL["coral"], ha="right")
    axA.set_ylabel("Pass rate", fontsize=9)
    axA.set_title("A  Synthetic scenarios", fontsize=10, fontweight="bold", loc="left")
    clean_axes(axA)

    # ── Panel B: paper metrics radar-like bar ──
    axB = fig.add_subplot(gs[0, 1:])
    p = m["papers"]["v2.4.0"]
    metrics = ["Route\naccuracy", "Risk\nrecall", "Data-before\nwriting", "Office\nconditionality", "Page\nsupport"]
    vals = [p["route_accuracy"], p["confirmed_risk_recall"], p["data_before_writing"]/10, p["office_conditionality_correct"]/10, p["page_support_present"]/10]
    bars = axB.bar(metrics, vals, color=[PAL["teal"]]*5, width=0.5, edgecolor="white", linewidth=0.5)
    score_labels(axB, bars, "{:.0%}", 0.03, 8)
    axB.set_ylim(0, 1.2)
    axB.set_ylabel("Score", fontsize=9)
    axB.set_title("B  Paper benchmark (v2.4.0, 10 papers)", fontsize=10, fontweight="bold", loc="left")
    clean_axes(axB)
    axB.tick_params(axis="x", labelsize=7)

    # ── Panel C: risk detection per paper ──
    axC = fig.add_subplot(gs[1, 0])
    papers = R["paper_cases"]
    x = np.arange(len(papers))
    w = 0.35
    r23 = [len(paper["conditions"]["v2.3.0"]["risks_found"])/len(paper["confirmed_risks"]) for paper in papers]
    r24 = [len(paper["conditions"]["v2.4.0"]["risks_found"])/len(paper["confirmed_risks"]) for paper in papers]
    axC.bar(x - w/2, r23, w, color=PAL["blue"], label="v2.3.0", edgecolor="white", linewidth=0.3)
    axC.bar(x + w/2, r24, w, color=PAL["teal"], label="v2.4.0", edgecolor="white", linewidth=0.3)
    axC.set_xticks(x)
    axC.set_xticklabels([f"{p['split'][:3]}-{i+1}" for i, p in enumerate(papers)], fontsize=6)
    axC.set_ylim(0, 1.2)
    axC.set_ylabel("Risk recall", fontsize=9)
    axC.set_title("C  Per-paper risk recall", fontsize=10, fontweight="bold", loc="left")
    axC.legend(fontsize=7, loc="lower right")
    clean_axes(axC)

    # ── Panel D: key metrics summary ──
    axD = fig.add_subplot(gs[1, 1:])
    axD.axis("off")
    axD.set_xlim(0, 1)
    axD.set_ylim(0, 1)

    # big numbers
    nums = [
        (f"{m['synthetic']['v2.4.0']['rate']:.0%}", "Synthetic pass", PAL["teal"]),
        (f"{m['papers']['v2.4.0']['route_accuracy']:.0%}", "Route accuracy", PAL["blue"]),
        (f"{m['papers']['v2.4.0']['confirmed_risk_recall']:.0%}", "Risk recall", PAL["coral"]),
        (str(m["papers"]["v2.4.0"]["fabrications"]), "Fabrications", PAL["green"]),
    ]
    for i, (val, lbl, col) in enumerate(nums):
        cx = 0.12 + i * 0.25
        axD.text(cx, 0.7, val, ha="center", va="center", fontsize=28, fontweight="bold", color=col)
        axD.text(cx, 0.35, lbl, ha="center", va="center", fontsize=9, color=PAL["gray"])
        # underline
        axD.plot([cx-0.08, cx+0.08], [0.55, 0.55], color=col, linewidth=1.5, solid_capstyle="round")

    axD.text(0.5, 0.1, f"10 papers × 3 risks = 30 total · development: 7 · holdout: 3",
             ha="center", va="center", fontsize=8, color=PAL["gray"], style="italic")
    axD.set_title("D  Key benchmark metrics (v2.4.0)", fontsize=10, fontweight="bold", loc="left")

    fig.suptitle("MPA Skill v2.6.0 — validation benchmark", fontsize=14, fontweight="bold", y=0.98, color=PAL["dark"])
    plt.savefig(os.path.join(OUT, "fig3_benchmark.png"), dpi=200)
    plt.close()
    print("  -> fig3_benchmark.png")


# ============================================================
# Fig 4: Risk taxonomy — compact dendrogram-style
# ============================================================
def fig4_risks():
    print("Fig 4: Risk taxonomy ...")
    R = json.loads(read_file("docs/validation/v2.4.0-results.json"))
    papers = R["paper_cases"]
    risks = []
    for p in papers:
        for r in p["confirmed_risks"]:
            risks.append({"id": r["id"], "desc": r["description"][:70], "split": p["split"]})

    vec = TfidfVectorizer(max_features=200, ngram_range=(1,2))
    tfidf = vec.fit_transform([r["desc"] for r in risks])
    sim = cosine_similarity(tfidf)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf.toarray())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1, 1]})

    # left: PCA scatter
    dev = [i for i, r in enumerate(risks) if r["split"] == "development"]
    hold = [i for i, r in enumerate(risks) if r["split"] == "holdout"]
    ax1.scatter(coords[dev, 0], coords[dev, 1], c=PAL["blue"], s=40, alpha=0.7, edgecolors="white", linewidth=0.4, label=f"Development ({len(dev)})")
    ax1.scatter(coords[hold, 0], coords[hold, 1], c=PAL["coral"], s=40, alpha=0.7, edgecolors="white", linewidth=0.4, label=f"Holdout ({len(hold)})")
    for i, r in enumerate(risks):
        ax1.annotate(r["id"][:12], (coords[i][0], coords[i][1]), fontsize=5, alpha=0.5, xytext=(2, 2), textcoords="offset points")
    ax1.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=9)
    ax1.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=9)
    ax1.set_title("Risk distribution (PCA)", fontsize=11, fontweight="bold", loc="left")
    ax1.legend(fontsize=8, loc="upper right")
    clean_axes(ax1)

    # right: similarity matrix
    mask = np.triu(np.ones_like(sim, dtype=bool), k=1)
    im = ax2.imshow(np.where(mask, np.nan, sim), cmap="YlOrRd", vmin=0, vmax=0.5, aspect="equal")
    ax2.set_title("Risk similarity matrix", fontsize=11, fontweight="bold", loc="left")
    ax2.set_xticks(range(len(risks)))
    ax2.set_yticks(range(len(risks)))
    ax2.set_xticklabels([r["id"][:8] for r in risks], rotation=50, ha="right", fontsize=5)
    ax2.set_yticklabels([r["id"][:8] for r in risks], fontsize=5)
    cb = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cb.set_label("Cosine similarity", fontsize=8)
    cb.ax.tick_params(labelsize=6)

    fig.suptitle(f"MPA Skill — risk taxonomy ({len(risks)} risks across 10 papers)", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "fig4_risk_taxonomy.png"), dpi=200)
    plt.close()
    print(f"  -> fig4_risk_taxonomy.png  ({len(risks)} risks)")


# ============================================================
# Run all
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("MPA Skill ML Analysis — Nature aesthetic")
    print("=" * 50)
    fig1_route_analysis()
    fig2_knowledge_pca()
    fig3_benchmark()
    fig4_risks()
    print("\nDone. All figures saved to", OUT)
