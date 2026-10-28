"""Run the scraping, cleaning, reporting, and visualization pipeline."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.scraper import scrape_quotes

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize text, remove empty rows and duplicate quote/author pairs."""
    required = ["quote", "author", "tags", "source_page"]
    missing = set(required) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    clean = raw.copy()
    for column in required:
        clean[column] = clean[column].fillna("").astype(str).str.strip()

    clean = clean[(clean["quote"] != "") & (clean["author"] != "")]
    clean = clean.drop_duplicates(subset=["quote", "author"]).reset_index(drop=True)
    clean["tag_count"] = clean["tags"].apply(
        lambda value: len([tag for tag in value.split(",") if tag.strip()])
    )
    return clean


def create_summary(clean: pd.DataFrame) -> str:
    """Create a concise Markdown report from cleaned records."""
    tag_counts: dict[str, int] = {}
    for tags in clean["tags"]:
        for tag in tags.split(","):
            tag = tag.strip()
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    top_tags = sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))[:10]
    lines = [
        "# Scraping Pipeline Summary",
        "",
        f"- Records after cleaning: **{len(clean)}**",
        f"- Unique authors: **{clean['author'].nunique()}**",
        f"- Records with at least one tag: **{int((clean['tag_count'] > 0).sum())}**",
        "",
        "## Most common tags",
        "",
        "| Tag | Count |",
        "|---|---:|",
    ]
    lines.extend(f"| {tag} | {count} |" for tag, count in top_tags)
    if not top_tags:
        lines.append("| No tags found | 0 |")
    return "\n".join(lines) + "\n"


def save_chart(clean: pd.DataFrame, output_path: Path) -> bool:
    """Save a bar chart of the ten most frequent tags, if matplotlib is installed."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    counts: dict[str, int] = {}
    for tags in clean["tags"]:
        for tag in tags.split(","):
            tag = tag.strip()
            if tag:
                counts[tag] = counts.get(tag, 0) + 1

    top = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:10]
    if not top:
        return False

    labels = [item[0] for item in top][::-1]
    values = [item[1] for item in top][::-1]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels, values)
    ax.set_title("Most Common Quote Tags")
    ax.set_xlabel("Number of quotes")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return True


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching practice-site pages...")
    records = scrape_quotes(max_pages=5, delay_seconds=1.0)
    if not records:
        raise RuntimeError(
            "No records were scraped. Check your internet connection and the demo site's HTML."
        )

    raw = pd.DataFrame(records)
    raw_path = DATA_DIR / "quotes_raw.csv"
    clean_path = DATA_DIR / "quotes_clean.csv"
    report_path = REPORTS_DIR / "summary.md"
    chart_path = REPORTS_DIR / "top_tags.png"

    raw.to_csv(raw_path, index=False, encoding="utf-8")
    clean = clean_data(raw)
    clean.to_csv(clean_path, index=False, encoding="utf-8")
    report_path.write_text(create_summary(clean), encoding="utf-8")
    chart_created = save_chart(clean, chart_path)

    print(f"Scraped records: {len(raw)}")
    print(f"Clean records:   {len(clean)}")
    print(f"Clean CSV:       {clean_path.relative_to(ROOT)}")
    print(f"Summary report:  {report_path.relative_to(ROOT)}")
    if chart_created:
        print(f"Tag chart:       {chart_path.relative_to(ROOT)}")
    else:
        print("Chart skipped (matplotlib unavailable or no tags).")


if __name__ == "__main__":
    main()
