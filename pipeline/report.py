"""REPORT: turn the marts into a findings page and charts.

Everything in reports/ is written by this step from the marts, never by
hand. If the data changes, run the pipeline and the report updates.
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from pipeline import config  # noqa: E402

# Chart colours, checked for colour-blind safety.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
USERS = "#2a78d6"      # Marketplace users (and single-series charts)
NON_USERS = "#eb6834"  # people who never use Marketplace


def _style(ax, title: str, subtitle: str) -> None:
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK_2, length=0, labelsize=10)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.figure.text(0.02, 0.97, title, fontsize=14, fontweight="bold", color=INK, va="top")
    ax.figure.text(0.02, 0.905, subtitle, fontsize=10, color=INK_2, va="top")


def _ranked_bar(rows, title, subtitle, path: Path) -> None:
    rows = list(reversed(rows))  # biggest at the top
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 0.55 * len(rows) + 1.6))
    fig.subplots_adjust(left=0.36, right=0.95, top=0.78, bottom=0.12)
    ax.barh(labels, values, height=0.5, color=USERS)
    for i, v in enumerate(values):
        ax.text(v + 0.012, i, f"{v:.0%}", va="center", fontsize=10, color=INK)
    _style(ax, title, subtitle)
    ax.tick_params(axis="y", labelcolor=INK)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _segment_chart(con, path: Path) -> None:
    rows = con.execute("""
        SELECT label,
               max(pct) FILTER (segment = 'marketplace_users') AS users,
               max(pct) FILTER (segment = 'non_users')         AS non_users,
               max(sort_order) AS s
        FROM marts.mart_headline_metrics
        WHERE segment <> 'all'
        GROUP BY label ORDER BY s DESC
    """).fetchall()
    n = dict(con.execute("""
        SELECT segment, count(*) FROM marts.fct_survey_responses GROUP BY segment
    """).fetchall())
    fig, ax = plt.subplots(figsize=(9, 6.2))
    fig.subplots_adjust(left=0.42, right=0.95, top=0.80, bottom=0.08)
    y = range(len(rows))
    h = 0.34
    ax.barh([i + h / 2 + 0.02 for i in y], [r[1] for r in rows], height=h, color=USERS,
            label=f"Use Facebook Marketplace (n={n.get('marketplace_users', 0)})")
    ax.barh([i - h / 2 - 0.02 for i in y], [r[2] for r in rows], height=h, color=NON_USERS,
            label=f"Never use it (n={n.get('non_users', 0)})")
    ax.set_yticks(list(y))
    ax.set_yticklabels([r[0] for r in rows], fontsize=10, color=INK)
    for i, r in enumerate(rows):
        ax.text(r[1] + 0.01, i + h / 2 + 0.02, f"{r[1]:.0%}", va="center", fontsize=9, color=INK)
        ax.text(r[2] + 0.01, i - h / 2 - 0.02, f"{r[2]:.0%}", va="center", fontsize=9, color=INK_2)
    _style(ax, "Marketplace users and non-users answer differently",
           "Share of people who answered each question")
    ax.legend(loc="upper left", bbox_to_anchor=(-0.75, 1.13), ncol=2, frameon=False,
              fontsize=10, labelcolor=INK)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _pct(x: float | None) -> str:
    return "–" if x is None else f"{x:.0%}"


def write_report(con: duckdb.DuckDBPyConnection, reports_dir: Path = config.REPORTS_DIR) -> Path:
    charts = reports_dir / "charts"
    charts.mkdir(parents=True, exist_ok=True)

    concerns = con.execute(
        "SELECT example_label, pct_of_answered, answered FROM marts.mart_concerns ORDER BY pct_of_answered DESC"
    ).fetchall()
    features = con.execute(
        "SELECT example_label, pct_of_answered, answered FROM marts.mart_features ORDER BY pct_of_answered DESC"
    ).fetchall()
    fees = con.execute("""
        SELECT answer, pct_of_answered, answered FROM marts.mart_question_breakdown
        WHERE question = 'fee_willingness'
        ORDER BY CASE answer WHEN 'none' THEN 1 WHEN 'r5_to_r10' THEN 2 WHEN 'r10_to_r20' THEN 3
                             WHEN 'r20_plus' THEN 4 WHEN 'percentage' THEN 5 END
    """).fetchall()
    fee_names = {"none": "Nothing (R0)", "r5_to_r10": "R5 – R10", "r10_to_r20": "R10 – R20",
                 "r20_plus": "R20 or more", "percentage": "4–7% of item price"}

    _segment_chart(con, charts / "users_vs_non_users.png")
    _ranked_bar([(c[0], c[1]) for c in concerns], "What people worry about most",
                f"Share who ticked each concern (n={concerns[0][2]})", charts / "concerns.png")
    _ranked_bar([(f[0], f[1]) for f in features], "What would make people feel safer",
                f"Share who ticked each feature (n={features[0][2]})", charts / "wanted_features.png")
    _ranked_bar([(fee_names[f[0]], f[1]) for f in fees], "How much people would pay per deal",
                f"Share choosing each option (n={fees[0][2]})", charts / "fee_willingness.png")

    total = con.execute("SELECT count(*) FROM marts.fct_survey_responses").fetchone()[0]
    received = con.execute("SELECT count(*) FROM staging.stg_survey_responses").fetchone()[0]
    headline = con.execute("""
        SELECT label,
               max(pct) FILTER (segment = 'all'),
               max(pct) FILTER (segment = 'marketplace_users'),
               max(pct) FILTER (segment = 'non_users'),
               max(sort_order) s
        FROM marts.mart_headline_metrics GROUP BY label ORDER BY s
    """).fetchall()
    scorecard = con.execute("""
        SELECT criterion_no, criterion, value_marketplace_users, value_all_respondents, threshold, status
        FROM marts.mart_validation_scorecard ORDER BY criterion_no
    """).fetchall()
    quality_line = (reports_dir / "quality_report.md")
    lines = [
        "# SafeTrade findings",
        "",
        "_Written by the pipeline from the marts. Do not edit by hand; run `python -m pipeline.run`._",
        "",
        f"**Responses:** {total} ({received} received, {received - total} double submission left out) · "
        "Percentages use the people who answered each question.",
        "",
        "## Key numbers",
        "",
        "| Finding | All | Marketplace users | Never use Marketplace |",
        "|---|---|---|---|",
    ]
    lines += [f"| {h[0]} | {_pct(h[1])} | {_pct(h[2])} | {_pct(h[3])} |" for h in headline]
    lines += [
        "",
        "![Marketplace users vs non-users](charts/users_vs_non_users.png)",
        "",
        "## Proposal success criteria",
        "",
        "| # | Criterion | Marketplace users | All | Bar | Status |",
        "|---|---|---|---|---|---|",
    ]
    lines += [
        f"| {s[0]} | {s[1]} | {_pct(s[2])} | {_pct(s[3])} | {_pct(s[4]) if s[4] is not None else '–'} | {s[5].replace('_', ' ')} |"
        for s in scorecard
    ]
    lines += [
        "",
        "## Concerns",
        "",
        "![Concerns](charts/concerns.png)",
        "",
        "## Wanted features",
        "",
        "![Wanted features](charts/wanted_features.png)",
        "",
        "## Fees",
        "",
        "![Fee willingness](charts/fee_willingness.png)",
        "",
        f"Data quality for this run: see [{quality_line.name}]({quality_line.name}).",
    ]
    out = reports_dir / "findings.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
