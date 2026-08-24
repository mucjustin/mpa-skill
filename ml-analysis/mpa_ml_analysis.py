"""
MPA Skill ML Analysis Pipeline
================================
Analyzes the MPA skill using local Anaconda + scikit-learn.

Four experiments:
  1. Route semantic similarity (TF-IDF + cosine, heatmap)
  2. Knowledge domain clustering (TF-IDF + KMeans + PCA, scatter)
  3. Benchmark statistical analysis (v2.3 vs v2.4, bar chart)
  4. Risk taxonomy clustering (TF-IDF + DBSCAN, dendrogram-style)
"""

import json
import re
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import jieba

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# --- paths ---
REPO = r"E:\CodexProjects\mpa-skill-public"
OUT = os.path.join(REPO, "ml-analysis", "output")
os.makedirs(OUT, exist_ok=True)

# --- helpers ---
def cn_tokenize(text):
    """Chinese-aware tokenizer using jieba."""
    words = list(jieba.cut(text))
    return [w.strip() for w in words if len(w.strip()) > 1]

def read_file(rel_path):
    with open(os.path.join(REPO, rel_path), encoding="utf-8") as f:
        return f.read()


# ============================================================
# Experiment 1: Route Semantic Similarity Analysis
# ============================================================
def experiment1_route_similarity():
    print("\n" + "="*60)
    print("Experiment 1: Route Semantic Similarity")
    print("="*60)

    routing = read_file("skills/mpa-skill/references/routing.md")

    # extract route table rows
    route_pattern = r'\| (\w[\w\s-]+?) \| (.+?) \| (.+?) \|'
    matches = re.findall(route_pattern, routing)

    routes = []
    for name, output, sequence in matches:
        name = name.strip()
        if name in ("Route", "---"):
            continue
        routes.append({
            "name": name,
            "output": output.strip(),
            "sequence": sequence.strip(),
            "full_text": f"{name} {output.strip()} {sequence.strip()}"
        })

    print(f"  Extracted {len(routes)} routes")
    for r in routes:
        print(f"    - {r['name']}")

    # TF-IDF with Chinese+English support
    texts = [r["full_text"] for r in routes]
    vectorizer = TfidfVectorizer(
        tokenizer=cn_tokenize,
        token_pattern=None,
        max_features=500,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    cos_sim = cosine_similarity(tfidf_matrix)

    # heatmap
    labels = [r["name"][:15] for r in routes]
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(cos_sim, dtype=bool), k=1)
    sns.heatmap(cos_sim, annot=True, fmt=".2f", cmap="YlOrRd",
                xticklabels=labels, yticklabels=labels, mask=mask,
                vmin=0, vmax=1, ax=ax, square=True)
    ax.set_title("Route semantic similarity (TF-IDF cosine)", fontsize=13, pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "exp1_route_similarity_heatmap.png"), dpi=150)
    plt.close()
    print("  -> saved exp1_route_similarity_heatmap.png")

    # find high-similarity pairs (potential confusion)
    print("\n  High-similarity route pairs (>0.30):")
    pairs = []
    for i in range(len(routes)):
        for j in range(i+1, len(routes)):
            sim = cos_sim[i][j]
            if sim > 0.30:
                pairs.append((routes[i]["name"], routes[j]["name"], sim))
                print(f"    {sim:.3f}  {routes[i]['name']}  <->  {routes[j]['name']}")
    if not pairs:
        print("    (no pairs above 0.30)")

    # route coverage analysis: generate test queries and see which route they match
    test_queries = [
        ("帮我做文献综述", "literature"),
        ("我要写一篇关于政策执行的案例分析", "case analysis"),
        ("帮我分析调研数据", "data analysis"),
        ("我要准备毕业论文答辩", "defence"),
        ("帮我写政策备忘录", "policy memo"),
        ("我要参加公共管理案例大赛", "case competition entry"),
        ("帮我设计研究方案", "research design"),
        ("我要做田野调查", "fieldwork"),
        ("帮我写硕士论文", "thesis"),
        ("我要把非公共管理的论文转成MPA方向", "non-MPA to MPA conversion"),
        ("帮我选一个分析理论", "theory grounding"),
        ("这个结论在中国适用吗", "china-context check"),
        ("帮我复习课程", "course"),
        ("帮我写政策分析报告", "policy memo"),
    ]

    query_texts = [q[0] for q in test_queries]
    query_vecs = vectorizer.transform(query_texts)
    query_sim = cosine_similarity(query_vecs, tfidf_matrix)

    correct = 0
    print("\n  Query-to-route matching test:")
    for idx, (query, expected_route) in enumerate(test_queries):
        best_match = np.argmax(query_sim[idx])
        matched_route = routes[best_match]["name"]
        score = query_sim[idx][best_match]
        is_correct = matched_route == expected_route or \
                     (expected_route == "policy memo" and matched_route == "policy memo")
        status = "OK" if is_correct else "MISS"
        if is_correct:
            correct += 1
        print(f"    [{status}] '{query}' -> {matched_route} (score={score:.3f}, expected={expected_route})")

    print(f"\n  Query routing accuracy: {correct}/{len(test_queries)} ({correct/len(test_queries)*100:.1f}%)")

    return {
        "routes": len(routes),
        "high_sim_pairs": len(pairs),
        "query_accuracy": f"{correct}/{len(test_queries)}",
        "query_accuracy_pct": round(correct/len(test_queries)*100, 1)
    }


# ============================================================
# Experiment 2: Knowledge Domain Clustering
# ============================================================
def experiment2_knowledge_clustering():
    print("\n" + "="*60)
    print("Experiment 2: Knowledge Domain Clustering")
    print("="*60)

    # extract theories from theory-map.md
    theory_map = read_file("skills/mpa-skill/references/mpa-theory-map.md")
    theory_rows = re.findall(r'\| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|', theory_map)
    theories = []
    for cells in theory_rows:
        if cells[0].strip() == "理论" or cells[0].strip() == "---":
            continue
        theories.append({
            "name": cells[0].strip(),
            "proposition": cells[1].strip(),
            "china_context": cells[2].strip(),
            "paper_types": cells[3].strip(),
            "misuse": cells[4].strip(),
            "text": f"{cells[0]} {cells[1]} {cells[2]} {cells[4]}"
        })

    # extract china contexts
    china_ctx = read_file("skills/mpa-skill/references/mpa-china-contexts.md")
    ctx_rows = re.findall(r'\| (.+?) \| (.+?) \| (.+?) \|', china_ctx)
    contexts = []
    for cells in ctx_rows:
        if "维度" in cells[0] or cells[0].strip() == "---":
            continue
        contexts.append({
            "name": cells[0].strip(),
            "text": f"{cells[0]} {cells[1]} {cells[2]}"
        })

    # extract thinking checklist
    checklist = read_file("skills/mpa-skill/references/mpa-thinking-checklist.md")
    check_rows = re.findall(r'\| (.+?) \| (.+?) \|', checklist)
    principles = []
    for cells in check_rows:
        c0 = cells[0].strip()
        if "原则" in c0 or c0 == "---":
            continue
        principles.append({
            "name": c0,
            "text": f"{c0} {cells[1].strip()}"
        })

    # extract courses
    course_map = read_file("skills/mpa-skill/references/mpa-course-map.md")
    course_rows = re.findall(r'\| (.+?) \| (.+?) \|', course_map)
    courses = []
    for cells in course_rows:
        c0 = cells[0].strip()
        if "课程" in c0 or c0 == "---":
            continue
        courses.append({
            "name": c0,
            "text": f"{c0} {cells[1].strip()}"
        })

    print(f"  Theories: {len(theories)}")
    print(f"  China contexts: {len(contexts)}")
    print(f"  Thinking principles: {len(principles)}")
    print(f"  Courses: {len(courses)}")

    # combine all knowledge items
    all_items = []
    all_labels = []
    all_types = []

    for t in theories:
        all_items.append(t["text"])
        all_labels.append(t["name"])
        all_types.append("theory")

    for c in contexts:
        all_items.append(c["text"])
        all_labels.append(c["name"])
        all_types.append("context")

    for p in principles:
        all_items.append(p["text"])
        all_labels.append(p["name"])
        all_types.append("principle")

    for c in courses:
        all_items.append(c["text"])
        all_labels.append(c["name"])
        all_types.append("course")

    # TF-IDF
    vectorizer = TfidfVectorizer(
        tokenizer=cn_tokenize,
        token_pattern=None,
        max_features=800,
        ngram_range=(1, 2)
    )
    tfidf = vectorizer.fit_transform(all_items)

    # KMeans clustering
    n_clusters = min(8, len(all_items))
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = km.fit_predict(tfidf)

    # PCA for visualization
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf.toarray())

    # plot
    fig, ax = plt.subplots(figsize=(14, 10))
    type_colors = {"theory": "#534AB7", "context": "#0F6E56", "principle": "#D85A30", "course": "#185FA5"}
    type_markers = {"theory": "o", "context": "s", "principle": "^", "course": "D"}

    for typ in ["theory", "context", "principle", "course"]:
        mask = [t == typ for t in all_types]
        xs = [coords[i][0] for i in range(len(coords)) if mask[i]]
        ys = [coords[i][1] for i in range(len(coords)) if mask[i]]
        ax.scatter(xs, ys, c=type_colors[typ], marker=type_markers[typ],
                   label=f"{typ} ({sum(mask)})", s=60, alpha=0.7, edgecolors="white", linewidth=0.5)

    # annotate points
    for i, label in enumerate(all_labels):
        ax.annotate(label[:10], (coords[i][0], coords[i][1]),
                    fontsize=6, alpha=0.6, xytext=(3, 3), textcoords="offset points")

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=11)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=11)
    ax.set_title("MPA knowledge domain map (TF-IDF + PCA)", fontsize=13, pad=12)
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "exp2_knowledge_domain_pca.png"), dpi=150)
    plt.close()
    print("  -> saved exp2_knowledge_domain_pca.png")

    # cluster analysis
    print("\n  Cluster composition:")
    for c in range(n_clusters):
        members = [(all_labels[i], all_types[i]) for i in range(len(all_labels)) if cluster_labels[i] == c]
        type_counts = {}
        for _, t in members:
            type_counts[t] = type_counts.get(t, 0) + 1
        print(f"    Cluster {c}: {len(members)} items, types={type_counts}")
        for name, typ in members[:3]:
            print(f"      [{typ}] {name}")
        if len(members) > 3:
            print(f"      ... and {len(members)-3} more")

    # gap analysis: compute average pairwise similarity within and across types
    cos_sim = cosine_similarity(tfidf)
    type_avg_sim = {}
    for t1 in ["theory", "context", "principle", "course"]:
        for t2 in ["theory", "context", "principle", "course"]:
            idx1 = [i for i in range(len(all_types)) if all_types[i] == t1]
            idx2 = [i for i in range(len(all_types)) if all_types[i] == t2]
            if idx1 and idx2:
                sims = [cos_sim[i][j] for i in idx1 for j in idx2 if i != j]
                if sims:
                    type_avg_sim[f"{t1}->{t2}"] = round(np.mean(sims), 4)

    print("\n  Cross-type average similarity:")
    for k, v in type_avg_sim.items():
        print(f"    {k}: {v}")

    return {
        "total_items": len(all_items),
        "theories": len(theories),
        "contexts": len(contexts),
        "principles": len(principles),
        "courses": len(courses),
        "clusters": n_clusters,
        "pc1_variance_pct": round(pca.explained_variance_ratio_[0]*100, 1),
        "pc2_variance_pct": round(pca.explained_variance_ratio_[1]*100, 1),
    }


# ============================================================
# Experiment 3: Benchmark Statistical Analysis
# ============================================================
def experiment3_benchmark_analysis():
    print("\n" + "="*60)
    print("Experiment 3: Benchmark Statistical Analysis")
    print("="*60)

    results = json.loads(read_file("docs/validation/v2.4.0-results.json"))

    # synthetic scenarios comparison
    synth = results["synthetic_cases"]
    conditions = ["none", "v2.3.0", "v2.4.0"]

    # per-scenario pass rates
    scenario_data = []
    for case in synth:
        cid = case["id"]
        for cond in conditions:
            c = case["conditions"][cond]
            scenario_data.append({
                "scenario": cid,
                "condition": cond,
                "pass": c["pass"],
                "expected_met": c["expected_met"],
                "forbidden_hit": c["forbidden_hit"],
            })

    df = pd.DataFrame(scenario_data)

    # summary stats
    metrics = results["metrics"]
    print(f"  Synthetic: none={metrics['synthetic']['none']['rate']:.1%}, "
          f"v2.3={metrics['synthetic']['v2.3.0']['rate']:.1%}, "
          f"v2.4={metrics['synthetic']['v2.4.0']['rate']:.1%}")
    print(f"  Papers: route_accuracy={metrics['papers']['v2.4.0']['route_accuracy']:.1%}, "
          f"risk_recall={metrics['papers']['v2.4.0']['confirmed_risk_recall']:.1%}, "
          f"fabrications={metrics['papers']['v2.4.0']['fabrications']}")
    print(f"  Improvement: +{metrics['synthetic']['v2.4_minus_v2.3_percentage_points']:.1f}pp (v2.4 vs v2.3)")

    # bar chart: synthetic scenario comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # left: synthetic pass rates by condition
    ax = axes[0]
    rates = [metrics["synthetic"][c]["rate"] for c in conditions]
    bars = ax.bar(conditions, rates, color=["#888780", "#378ADD", "#1D9E75"], edgecolor="white", width=0.6)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Pass rate", fontsize=11)
    ax.set_title("Synthetic scenarios pass rate by condition", fontsize=12, pad=10)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{rate:.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.axhline(y=1.0, color="#1D9E75", linestyle="--", alpha=0.5, label="100% target")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # right: per-scenario comparison
    ax2 = axes[1]
    scenario_names = [c["id"][:20] for c in synth]
    x = np.arange(len(synth))
    width = 0.25
    for i, cond in enumerate(conditions):
        passes = [1 if synth[j]["conditions"][cond]["pass"] else 0 for j in range(len(synth))]
        ax2.bar(x + i*width, passes, width, label=cond,
                color=["#888780", "#378ADD", "#1D9E75"][i], edgecolor="white")
    ax2.set_xticks(x + width)
    ax2.set_xticklabels([s[:15] for s in scenario_names], rotation=45, ha="right", fontsize=8)
    ax2.set_ylabel("Pass (1) / Fail (0)", fontsize=11)
    ax2.set_title("Per-scenario pass/fail", fontsize=12, pad=10)
    ax2.legend(fontsize=9)
    ax2.set_ylim(-0.1, 1.3)
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "exp3_benchmark_analysis.png"), dpi=150)
    plt.close()
    print("  -> saved exp3_benchmark_analysis.png")

    # paper analysis: risk detection per paper
    papers = results["paper_cases"]
    paper_data = []
    for p in papers:
        split = p["split"]
        n_risks = len(p["confirmed_risks"])
        for cond in ["v2.3.0", "v2.4.0"]:
            c = p["conditions"][cond]
            paper_data.append({
                "source_id": p["source_id"][:20],
                "split": split,
                "condition": cond,
                "route_correct": c["route_correct"],
                "risks_found": len(c["risks_found"]),
                "risks_total": n_risks,
                "unsupported_claim": c["unsupported_claim_generated"],
                "data_before_writing": c["data_before_writing"],
                "page_support": c["page_support_present"],
            })

    df_papers = pd.DataFrame(paper_data)

    # risk recall by paper
    fig, ax = plt.subplots(figsize=(14, 6))
    paper_ids = [p["source_id"][:15] for p in papers]
    x = np.arange(len(papers))
    width = 0.35
    v23_recall = [len(p["conditions"]["v2.3.0"]["risks_found"]) / len(p["confirmed_risks"]) for p in papers]
    v24_recall = [len(p["conditions"]["v2.4.0"]["risks_found"]) / len(p["confirmed_risks"]) for p in papers]
    ax.bar(x - width/2, v23_recall, width, label="v2.3.0", color="#378ADD", edgecolor="white")
    ax.bar(x + width/2, v24_recall, width, label="v2.4.0", color="#1D9E75", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{p['split'][:3]}-{i+1}" for i, p in enumerate(papers)], fontsize=9)
    ax.set_ylabel("Risk recall", fontsize=11)
    ax.set_title("Per-paper risk recall: v2.3.0 vs v2.4.0", fontsize=12, pad=10)
    ax.axhline(y=1.0, color="#1D9E75", linestyle="--", alpha=0.5)
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "exp3_paper_risk_recall.png"), dpi=150)
    plt.close()
    print("  -> saved exp3_paper_risk_recall.png")

    # compute precision/recall/F1 for risk detection
    print("\n  Risk detection metrics (v2.4.0):")
    total_found = sum(len(p["conditions"]["v2.4.0"]["risks_found"]) for p in papers)
    total_confirmed = sum(len(p["confirmed_risks"]) for p in papers)
    total_fabrications = metrics["papers"]["v2.4.0"]["fabrications"]
    recall = total_found / total_confirmed if total_confirmed > 0 else 0
    # precision: found / (found + fabrications) — fabrications = false positives
    precision = total_found / (total_found + total_fabrications) if (total_found + total_fabrications) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"    Total confirmed risks: {total_confirmed}")
    print(f"    Total risks found: {total_found}")
    print(f"    Fabrications (FP): {total_fabrications}")
    print(f"    Precision: {precision:.4f}")
    print(f"    Recall: {recall:.4f}")
    print(f"    F1 Score: {f1:.4f}")

    # v2.3.0 for comparison
    total_found_v23 = sum(len(p["conditions"]["v2.3.0"]["risks_found"]) for p in papers)
    fab_v23 = metrics["papers"]["v2.3.0"]["fabrications"]
    prec_v23 = total_found_v23 / (total_found_v23 + fab_v23) if (total_found_v23 + fab_v23) > 0 else 1.0
    rec_v23 = total_found_v23 / total_confirmed if total_confirmed > 0 else 0
    f1_v23 = 2 * prec_v23 * rec_v23 / (prec_v23 + rec_v23) if (prec_v23 + rec_v23) > 0 else 0

    print(f"\n  v2.3.0: precision={prec_v23:.4f}, recall={rec_v23:.4f}, F1={f1_v23:.4f}")
    print(f"  v2.4.0: precision={precision:.4f}, recall={recall:.4f}, F1={f1:.4f}")
    print(f"  F1 improvement: {f1 - f1_v23:+.4f}")

    return {
        "synthetic_none_rate": metrics["synthetic"]["none"]["rate"],
        "synthetic_v23_rate": metrics["synthetic"]["v2.3.0"]["rate"],
        "synthetic_v24_rate": metrics["synthetic"]["v2.4.0"]["rate"],
        "v24_precision": round(precision, 4),
        "v24_recall": round(recall, 4),
        "v24_f1": round(f1, 4),
        "v23_f1": round(f1_v23, 4),
        "f1_improvement": round(f1 - f1_v23, 4),
    }


# ============================================================
# Experiment 4: Risk Taxonomy Clustering
# ============================================================
def experiment4_risk_clustering():
    print("\n" + "="*60)
    print("Experiment 4: Risk Taxonomy Clustering")
    print("="*60)

    results = json.loads(read_file("docs/validation/v2.4.0-results.json"))
    papers = results["paper_cases"]

    # extract all risks
    risks = []
    for p in papers:
        for r in p["confirmed_risks"]:
            risks.append({
                "id": r["id"],
                "description": r["description"],
                "pages": r.get("pdf_pages", []),
                "split": p["split"],
                "source": p["source_id"][:20],
                "text": r["description"]
            })

    print(f"  Total risks: {len(risks)}")

    # TF-IDF
    texts = [r["text"] for r in risks]
    vectorizer = TfidfVectorizer(
        tokenizer=cn_tokenize,
        token_pattern=None,
        max_features=300,
        ngram_range=(1, 2)
    )
    tfidf = vectorizer.fit_transform(texts)
    cos_sim = cosine_similarity(tfidf)

    # DBSCAN clustering
    db = DBSCAN(eps=0.3, min_samples=2, metric="cosine")
    cluster_labels = db.fit_predict(tfidf.toarray())

    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)
    print(f"  DBSCAN clusters: {n_clusters}, noise points: {n_noise}")

    # print clusters
    print("\n  Risk clusters:")
    for c in sorted(set(cluster_labels)):
        members = [(risks[i]["id"], risks[i]["description"][:60]) for i in range(len(risks)) if cluster_labels[i] == c]
        label = f"Cluster {c}" if c >= 0 else "Noise"
        print(f"    {label} ({len(members)} items):")
        for rid, desc in members:
            print(f"      {rid}: {desc}...")

    # PCA visualization
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf.toarray())

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.Set3(np.linspace(0, 1, max(n_clusters + 1, 3)))
    for c in sorted(set(cluster_labels)):
        mask = cluster_labels == c
        label = f"Cluster {c}" if c >= 0 else "Noise"
        color = "#CCCCCC" if c == -1 else colors[c]
        ax.scatter(coords[mask, 0], coords[mask, 1], c=[color], label=label, s=80, edgecolors="white", linewidth=0.5)

    for i, r in enumerate(risks):
        ax.annotate(r["id"][:15], (coords[i][0], coords[i][1]),
                    fontsize=6, alpha=0.7, xytext=(3, 3), textcoords="offset points")

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=11)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=11)
    ax.set_title("Risk taxonomy map (TF-IDF + DBSCAN + PCA)", fontsize=13, pad=12)
    ax.legend(fontsize=8, loc="best")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "exp4_risk_taxonomy_cluster.png"), dpi=150)
    plt.close()
    print("  -> saved exp4_risk_taxonomy_cluster.png")

    # risk category analysis
    print("\n  Risk category distribution:")
    categories = {}
    for r in risks:
        prefix = r["id"].split("-")[0]
        categories[prefix] = categories.get(prefix, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"    {cat}: {count} risks")

    # similarity heatmap of risks
    fig, ax = plt.subplots(figsize=(12, 10))
    risk_labels = [r["id"][:15] for r in risks]
    mask = np.triu(np.ones_like(cos_sim, dtype=bool), k=1)
    sns.heatmap(cos_sim, annot=False, cmap="YlOrRd",
                xticklabels=risk_labels, yticklabels=risk_labels, mask=mask,
                vmin=0, vmax=1, ax=ax, square=True)
    ax.set_title("Risk similarity matrix", fontsize=13, pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "exp4_risk_similarity_heatmap.png"), dpi=150)
    plt.close()
    print("  -> saved exp4_risk_similarity_heatmap.png")

    return {
        "total_risks": len(risks),
        "clusters": n_clusters,
        "noise_points": n_noise,
        "categories": categories,
    }


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("MPA Skill ML Analysis Pipeline")
    print("=" * 60)
    print(f"Repo: {REPO}")
    print(f"Output: {OUT}")

    results = {}
    results["exp1"] = experiment1_route_similarity()
    results["exp2"] = experiment2_knowledge_clustering()
    results["exp3"] = experiment3_benchmark_analysis()
    results["exp4"] = experiment4_risk_clustering()

    # save summary
    summary_path = os.path.join(OUT, "ml_analysis_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n{'='*60}")
    print(f"Summary saved to {summary_path}")
    print(f"All figures saved to {OUT}")
    print("Done!")
