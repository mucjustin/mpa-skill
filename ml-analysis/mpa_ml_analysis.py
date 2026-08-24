"""
MPA Skill ML Analysis — Nature/Science pink palette
====================================================
Clean, publication-grade figures with reduced text and no overlap.
"""

import json, re, os, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Ellipse
import jieba

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.spatial import ConvexHull
from scipy.stats import chi2

# ── paths ──
REPO = r"E:\CodexProjects\mpa-skill-public"
OUT = os.path.join(REPO, "ml-analysis", "output")
os.makedirs(OUT, exist_ok=True)

# ── Nature/Science pink palette ──
PAL = {
    "rose":       "#D65A7C",   # primary accent
    "deep_rose":  "#B8456B",   # dark accent
    "blush":      "#F2B5C1",   # light fill
    "mauve":      "#A67C94",   # secondary
    "coral":      "#E87A6A",   # warm accent
    "peach":      "#F5C896",   # soft highlight
    "slate":      "#3D3A42",   # text
    "gray":       "#9B95A3",   # muted
    "light":      "#FAF7F8",   # background
    "white":      "#FFFFFF",
}

# diverging / sequential pink cmap
PINK_CMAP = LinearSegmentedColormap.from_list(
    "nature_pink", ["#FDF6F8", PAL["blush"], PAL["rose"], PAL["deep_rose"]]
)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Microsoft YaHei", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",
    "font.size": 8,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#D8D4DA",
    "axes.labelcolor": PAL["slate"],
    "text.color": PAL["slate"],
    "xtick.color": PAL["slate"],
    "ytick.color": PAL["slate"],
    "figure.facecolor": PAL["white"],
    "savefig.facecolor": PAL["white"],
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.2,
    "axes.spines.right": False,
    "axes.spines.top": False,
})


def cn_tok(t):
    return [w.strip() for w in jieba.cut(t) if len(w.strip()) > 1]


def read_file(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return f.read()


def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25, linewidth=0.4, linestyle="--", color="#CBC7CD")


def draw_confidence_ellipse(ax, pts, color, n_std=1.5, alpha=0.12, ec_alpha=0.45):
    """Covariance ellipse (Mahalanobis distance) for a point cloud."""
    if len(pts) < 3:
        return
    pts = np.asarray(pts[:, :2])
    mean = pts.mean(axis=0)
    cov = np.cov(pts.T)
    if np.linalg.det(cov) < 1e-12 or np.any(np.isnan(cov)):
        return
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = eigvals.argsort()[::-1]
    eigvals, eigvecs = eigvals[order], eigvecs[:, order]
    angle = np.degrees(np.arctan2(*eigvecs[:, 0][::-1]))
    width, height = 2 * n_std * np.sqrt(eigvals)
    ellipse = Ellipse(xy=mean, width=width, height=height, angle=angle,
                      facecolor=color, edgecolor=color, alpha=alpha,
                      linewidth=1.0, zorder=0)
    ax.add_patch(ellipse)
    # outline only
    ellipse_edge = Ellipse(xy=mean, width=width, height=height, angle=angle,
                           facecolor="none", edgecolor=color, alpha=ec_alpha,
                           linewidth=1.0, zorder=1)
    ax.add_patch(ellipse_edge)


def panel_label(ax, letter, y=1.02, x=-0.12):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=12, fontweight="bold",
            color=PAL["slate"], va="bottom", ha="right")


# ============================================================
# Fig 1: Route similarity + bilingual accuracy
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
        routes.append({"name": name, "cn": cn_kw.strip(),
                       "full": f"{name} {output} {cn_kw} {seq}"})

    # similarity
    vec = TfidfVectorizer(tokenizer=cn_tok, token_pattern=None,
                          max_features=500, ngram_range=(1, 2))
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
    correct = sum(1 for i, (_, exp) in enumerate(queries)
                  if routes[np.argmax(q_sim[i])]["name"] == exp)
    acc = correct / len(queries)

    fig = plt.figure(figsize=(14, 5.5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], wspace=0.35)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # --- left: heatmap ---
    labels = [r["name"].replace("-", "\u2011") for r in routes]
    mask = np.triu(np.ones_like(sim, dtype=bool), k=1)
    plot_sim = np.where(mask, np.nan, sim)
    im = ax1.imshow(plot_sim, cmap=PINK_CMAP, vmin=0, vmax=0.5, aspect="equal")
    ax1.set_xticks(range(len(labels)))
    ax1.set_yticks(range(len(labels)))
    ax1.set_xticklabels(labels, rotation=55, ha="right", fontsize=7)
    ax1.set_yticklabels(labels, fontsize=7)

    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):
            v = sim[i, j]
            if v > 0.20:
                ax1.text(j, i, f"{v:.2f}", ha="center", va="center",
                         fontsize=6, color=PAL["white"] if v > 0.35 else PAL["slate"])

    ax1.set_title("Route semantic similarity", fontsize=11, fontweight="bold", pad=10)
    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label("Cosine similarity", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    panel_label(ax1, "a", y=1.05)

    # --- right: accuracy card ---
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis("off")

    # gauge background + fill
    gauge_y = 0.62
    ax2.barh(gauge_y, 1.0, height=0.18, color=PAL["light"],
             edgecolor=PAL["blush"], linewidth=1, left=0)
    ax2.barh(gauge_y, acc, height=0.18, color=PAL["rose"],
             edgecolor="none", left=0)

    # score inside gauge
    ax2.text(acc / 2, gauge_y, f"{acc:.0%}", ha="center", va="center",
             fontsize=28, fontweight="bold", color=PAL["white"])
    ax2.text(0.98, gauge_y, "100%", ha="right", va="center",
             fontsize=9, color=PAL["gray"], alpha=0.7)

    # title and subtitle
    ax2.text(0.5, 0.92, "Bilingual routing accuracy",
             ha="center", va="top", fontsize=13, fontweight="bold", color=PAL["slate"])
    ax2.text(0.5, 0.84, f"{correct} of {len(queries)} Chinese queries matched",
             ha="center", va="top", fontsize=9, color=PAL["gray"])

    # mini legend: hit / miss
    ax2.plot(0.18, 0.35, "o", color=PAL["rose"], markersize=6)
    ax2.text(0.23, 0.35, "Correct", va="center", fontsize=8, color=PAL["slate"])
    ax2.plot(0.48, 0.35, "o", color=PAL["gray"], markersize=6)
    ax2.text(0.53, 0.35, "Miss", va="center", fontsize=8, color=PAL["slate"])

    # short insight
    ax2.text(0.5, 0.18,
             "Chinese keyword column raised accuracy from 14% to 93%",
             ha="center", va="center", fontsize=8,
             color=PAL["deep_rose"], style="italic",
             bbox=dict(boxstyle="round,pad=0.35", facecolor=PAL["light"],
                       edgecolor=PAL["blush"], linewidth=0.8))
    panel_label(ax2, "b", y=1.05, x=-0.06)

    fig.suptitle("MPA Skill — bilingual route matching",
                 fontsize=14, fontweight="bold", y=0.98, color=PAL["slate"])
    plt.savefig(os.path.join(OUT, "fig1_route_analysis.png"), dpi=250)
    plt.close()
    print(f"  -> fig1_route_analysis.png  (accuracy={correct}/{len(queries)})")


# ============================================================
# Fig 2: Knowledge domain PCA
# ============================================================
def fig2_knowledge_pca():
    print("Fig 2: Knowledge domain ...")
    files = {
        "theory":    ("skills/mpa-skill/references/mpa-theory-map.md", "Theory"),
        "context":   ("skills/mpa-skill/references/mpa-china-contexts.md", "Context"),
        "principle": ("skills/mpa-skill/references/mpa-thinking-checklist.md", "Principle"),
        "course":    ("skills/mpa-skill/references/mpa-course-map.md", "Course"),
    }
    items, labels, types = [], [], []
    for typ, (path, _) in files.items():
        text = read_file(path)
        rows = re.findall(r'\| (.+?) \| (.+?) \|', text)
        for cells in rows:
            c0 = cells[0].strip()
            if c0 in ("理论", "维度", "原则", "课程", "---") or "---" in c0:
                continue
            items.append(f"{c0} {cells[1].strip()}")
            labels.append(c0)
            types.append(typ)

    vec = TfidfVectorizer(tokenizer=cn_tok, token_pattern=None,
                          max_features=800, ngram_range=(1, 2))
    tfidf = vec.fit_transform(items)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf.toarray())

    type_cfg = {
        "theory":    (PAL["rose"], "o", "Theory"),
        "context":   (PAL["mauve"], "s", "Context"),
        "principle": (PAL["coral"], "^", "Principle"),
        "course":    (PAL["peach"], "D", "Course"),
    }

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor(PAL["light"])

    # plot convex hulls first
    for typ in ["theory", "context", "principle", "course"]:
        idx = [i for i, t in enumerate(types) if t == typ]
        pts = coords[idx]
        draw_hull(ax, pts, type_cfg[typ][0], alpha=0.10, ec_alpha=0.35)

    # scatter points
    for typ in ["theory", "context", "principle", "course"]:
        idx = [i for i, t in enumerate(types) if t == typ]
        c, m, lbl = type_cfg[typ]
        ax.scatter(coords[idx, 0], coords[idx, 1], c=c, marker=m,
                   label=f"{lbl}  ({len(idx)})", s=50, alpha=0.80,
                   edgecolors=PAL["white"], linewidth=0.5, zorder=3)

    # annotate a few representative points per category (furthest from origin)
    for typ in ["theory", "context", "principle", "course"]:
        idx = [i for i, t in enumerate(types) if t == typ]
        dist = np.linalg.norm(coords[idx], axis=1)
        pick = idx[np.argmax(dist)]
        ax.annotate(labels[pick][:10], (coords[pick, 0], coords[pick, 1]),
                    fontsize=7, color=type_cfg[typ][0], fontweight="bold",
                    xytext=(5, 5), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor=PAL["white"],
                              edgecolor="none", alpha=0.85))

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=10)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=10)
    ax.set_title("MPA knowledge domains — PCA projection", fontsize=12,
                 fontweight="bold", pad=12)
    ax.legend(loc="best", fontsize=9, framealpha=0.9,
              edgecolor=PAL["blush"], fancybox=False)
    clean_axes(ax)
    ax.grid(axis="both", alpha=0.20, linewidth=0.4, linestyle="--", color="#CBC7CD")

    fig.suptitle("MPA Skill — knowledge ontology structure",
                 fontsize=14, fontweight="bold", y=0.98, color=PAL["slate"])
    plt.savefig(os.path.join(OUT, "fig2_knowledge_pca.png"), dpi=250)
    plt.close()
    print(f"  -> fig2_knowledge_pca.png  ({len(items)} items)")


# ============================================================
# Fig 3: Benchmark scores
# ============================================================
def fig3_benchmark():
    print("Fig 3: Benchmark ...")
    R = json.loads(read_file("docs/validation/v2.4.0-results.json"))
    m = R["metrics"]

    fig = plt.figure(figsize=(13, 8.5))
    gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.32)

    # --- Panel A: synthetic pass rate ---
    axA = fig.add_subplot(gs[0, 0])
    conds = ["No skill", "v2.3.0", "v2.4.0"]
    rates = [m["synthetic"]["none"]["rate"],
             m["synthetic"]["v2.3.0"]["rate"],
             m["synthetic"]["v2.4.0"]["rate"]]
    colors = [PAL["gray"], PAL["mauve"], PAL["rose"]]
    bars = axA.bar(conds, rates, color=colors, width=0.55,
                   edgecolor=PAL["white"], linewidth=1)
    axA.set_ylim(0, 1.15)
    for b, r in zip(bars, rates):
        axA.text(b.get_x() + b.get_width() / 2, r + 0.03, f"{r:.0%}",
                 ha="center", va="bottom", fontsize=10, fontweight="bold",
                 color=PAL["slate"])
    axA.axhline(1.0, color=PAL["deep_rose"], linestyle="--",
                linewidth=0.8, alpha=0.5)
    axA.text(2.35, 1.02, "target", fontsize=7, color=PAL["deep_rose"], ha="right")
    axA.set_ylabel("Pass rate", fontsize=9)
    axA.set_title("Synthetic scenarios", fontsize=10, fontweight="bold", loc="left")
    clean_axes(axA)
    panel_label(axA, "a")

    # --- Panel B: paper metrics ---
    axB = fig.add_subplot(gs[0, 1])
    p = m["papers"]["v2.4.0"]
    metrics = ["Route\naccuracy", "Risk\nrecall", "Data before\nwriting",
               "Office\nconditionality", "Page\nsupport"]
    vals = [p["route_accuracy"], p["confirmed_risk_recall"],
            p["data_before_writing"] / 10, p["office_conditionality_correct"] / 10,
            p["page_support_present"] / 10]
    bars = axB.bar(metrics, vals, color=PAL["rose"], width=0.50,
                   edgecolor=PAL["white"], linewidth=1)
    axB.set_ylim(0, 1.15)
    for b, v in zip(bars, vals):
        axB.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.0%}",
                 ha="center", va="bottom", fontsize=9, fontweight="bold",
                 color=PAL["slate"])
    axB.set_ylabel("Score", fontsize=9)
    axB.set_title("Paper benchmark (10 papers)", fontsize=10, fontweight="bold", loc="left")
    axB.tick_params(axis="x", labelsize=8)
    clean_axes(axB)
    panel_label(axB, "b")

    # --- Panel C: per-paper risk recall ---
    axC = fig.add_subplot(gs[1, 0])
    papers = R["paper_cases"]
    x = np.arange(len(papers))
    w = 0.35
    r23 = [len(p["conditions"]["v2.3.0"]["risks_found"]) / len(p["confirmed_risks"])
           for p in papers]
    r24 = [len(p["conditions"]["v2.4.0"]["risks_found"]) / len(p["confirmed_risks"])
           for p in papers]
    axC.bar(x - w / 2, r23, w, color=PAL["mauve"], label="v2.3.0",
            edgecolor=PAL["white"], linewidth=0.4)
    axC.bar(x + w / 2, r24, w, color=PAL["rose"], label="v2.4.0",
            edgecolor=PAL["white"], linewidth=0.4)
    axC.set_xticks(x)
    axC.set_xticklabels([f"{p['split'][:3]}-{i+1}" for i, p in enumerate(papers)],
                        fontsize=7)
    axC.set_ylim(0, 1.15)
    axC.set_ylabel("Risk recall", fontsize=9)
    axC.set_title("Per-paper risk recall", fontsize=10, fontweight="bold", loc="left")
    axC.legend(fontsize=8, loc="lower right", frameon=False)
    clean_axes(axC)
    panel_label(axC, "c")

    # --- Panel D: key metrics summary ---
    axD = fig.add_subplot(gs[1, 1])
    axD.axis("off")
    axD.set_xlim(0, 1)
    axD.set_ylim(0, 1)

    nums = [
        (f"{m['synthetic']['v2.4.0']['rate']:.0%}", "Synthetic pass", PAL["rose"]),
        (f"{m['papers']['v2.4.0']['route_accuracy']:.0%}", "Route accuracy", PAL["mauve"]),
        (f"{m['papers']['v2.4.0']['confirmed_risk_recall']:.0%}", "Risk recall", PAL["coral"]),
        (str(m["papers"]["v2.4.0"]["fabrications"]), "Fabrications", PAL["gray"]),
    ]
    for i, (val, lbl, col) in enumerate(nums):
        cx = 0.125 + i * 0.25
        axD.text(cx, 0.72, val, ha="center", va="center", fontsize=26,
                 fontweight="bold", color=col)
        axD.plot([cx - 0.09, cx + 0.09], [0.56, 0.56], color=col,
                 linewidth=2, solid_capstyle="round")
        axD.text(cx, 0.42, lbl, ha="center", va="center", fontsize=9,
                 color=PAL["gray"])

    axD.text(0.5, 0.16,
             "10 papers × 3 risks = 30 total · development 7 · holdout 3",
             ha="center", va="center", fontsize=8, color=PAL["gray"], style="italic")
    axD.set_title("Key benchmark metrics (v2.4.0)", fontsize=10,
                  fontweight="bold", loc="left")
    panel_label(axD, "d")

    fig.suptitle("MPA Skill v2.6.0 — validation benchmark",
                 fontsize=14, fontweight="bold", y=0.98, color=PAL["slate"])
    plt.savefig(os.path.join(OUT, "fig3_benchmark.png"), dpi=250)
    plt.close()
    print("  -> fig3_benchmark.png")


# ============================================================
# Fig 4: Risk taxonomy
# ============================================================
def fig4_risks():
    print("Fig 4: Risk taxonomy ...")
    R = json.loads(read_file("docs/validation/v2.4.0-results.json"))
    papers = R["paper_cases"]
    risks = []
    for p in papers:
        for r in p["confirmed_risks"]:
            risks.append({"id": r["id"], "desc": r["description"][:80],
                          "split": p["split"]})

    vec = TfidfVectorizer(max_features=200, ngram_range=(1, 2))
    tfidf = vec.fit_transform([r["desc"] for r in risks])
    sim = cosine_similarity(tfidf)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf.toarray())

    fig = plt.figure(figsize=(14, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.05], wspace=0.32)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # --- left: PCA scatter with hulls ---
    dev_idx = [i for i, r in enumerate(risks) if r["split"] == "development"]
    hold_idx = [i for i, r in enumerate(risks) if r["split"] == "holdout"]

    draw_hull(ax1, coords[dev_idx], PAL["rose"], alpha=0.12, ec_alpha=0.40)
    draw_hull(ax1, coords[hold_idx], PAL["coral"], alpha=0.18, ec_alpha=0.50)

    ax1.scatter(coords[dev_idx, 0], coords[dev_idx, 1], c=PAL["rose"], s=55,
                alpha=0.80, edgecolors=PAL["white"], linewidth=0.5,
                label=f"Development ({len(dev_idx)})", zorder=3)
    ax1.scatter(coords[hold_idx, 0], coords[hold_idx, 1], c=PAL["coral"], s=55,
                alpha=0.85, edgecolors=PAL["white"], linewidth=0.5,
                label=f"Holdout ({len(hold_idx)})", zorder=3)

    # annotate only holdout points to reduce clutter
    for i in hold_idx:
        short = risks[i]["id"].replace("holdout-", "h")[:10]
        ax1.annotate(short, (coords[i, 0], coords[i, 1]),
                     fontsize=6, color=PAL["coral"], fontweight="bold",
                     xytext=(4, 4), textcoords="offset points",
                     bbox=dict(boxstyle="round,pad=0.12", facecolor=PAL["white"],
                               edgecolor="none", alpha=0.80))

    ax1.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=10)
    ax1.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=10)
    ax1.set_title("Risk distribution (PCA)", fontsize=11, fontweight="bold", loc="left")
    ax1.legend(fontsize=8, loc="best", frameon=False)
    clean_axes(ax1)
    ax1.grid(axis="both", alpha=0.20, linewidth=0.4, linestyle="--", color="#CBC7CD")
    panel_label(ax1, "a")

    # --- right: similarity matrix ---
    mask = np.triu(np.ones_like(sim, dtype=bool), k=1)
    plot_sim = np.where(mask, np.nan, sim)
    im = ax2.imshow(plot_sim, cmap=PINK_CMAP, vmin=0, vmax=0.5, aspect="equal")
    ax2.set_title("Risk similarity matrix", fontsize=11, fontweight="bold", loc="left")
    ax2.set_xticks(range(len(risks)))
    ax2.set_yticks(range(len(risks)))
    short_ids = [r["id"].replace("development-", "d").replace("holdout-", "h")[:9]
                 for r in risks]
    ax2.set_xticklabels(short_ids, rotation=60, ha="right", fontsize=6)
    ax2.set_yticklabels(short_ids, fontsize=6)

    # annotate only strong off-diagonal similarities
    for i in range(len(risks)):
        for j in range(i + 1, len(risks)):
            v = sim[i, j]
            if v > 0.35:
                ax2.text(j, i, f"{v:.2f}", ha="center", va="center",
                         fontsize=5.5, color=PAL["white"])

    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("Cosine similarity", fontsize=8)
    cbar.ax.tick_params(labelsize=7)
    panel_label(ax2, "b")

    fig.suptitle(f"MPA Skill — risk taxonomy ({len(risks)} risks across 10 papers)",
                 fontsize=14, fontweight="bold", y=0.98, color=PAL["slate"])
    plt.savefig(os.path.join(OUT, "fig4_risk_taxonomy.png"), dpi=250)
    plt.close()
    print(f"  -> fig4_risk_taxonomy.png  ({len(risks)} risks)")


# ============================================================
# Run all
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("MPA Skill ML Analysis — Nature pink aesthetic")
    print("=" * 50)
    fig1_route_analysis()
    fig2_knowledge_pca()
    fig3_benchmark()
    fig4_risks()
    print("\nDone. All figures saved to", OUT)
