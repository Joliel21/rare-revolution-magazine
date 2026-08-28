#!/usr/bin/env python3
import csv
import gzip
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INCOMING = ROOT / ".github" / "incoming"
MANIFEST_PATH = ROOT / "rare-insights" / "manifest.json"

SERIES = {
    "charity-and-advocacy": {
        "name": "Charity & Advocacy",
        "csv_name": "charity-and-advocacy.csv",
        "target": ROOT / "rare-insights" / "charity-and-advocacy",
        "title_page": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
        "runtime_role": "canonical-ap-content",
        "manifest": True,
    },
    "industry-insights": {
        "name": "Industry Insights",
        "csv_name": "industry-insights.csv",
        "target": ROOT / "rare-insights" / "industry-insights",
        "title_page": "rare-insights/sub-series-title-pages/industry-insights.png",
        "runtime_role": "canonical-ap-content",
        "manifest": True,
    },
    "editors-letters": {
        "name": "Editors’ Letters",
        "csv_name": "editors-letters.csv",
        "target": ROOT / "rare-insights" / "editors-letters",
        "title_page": "rare-insights/sub-series-title-pages/editors-letters.png",
        "runtime_role": "canonical-ap-content",
        "manifest": True,
    },
    "medical": {
        "name": "Medical",
        "csv_name": "medical.csv",
        "target": ROOT / "rare-insights" / "medical",
        "title_page": "rare-insights/sub-series-title-pages/medical.png",
        "runtime_role": "canonical-ap-content",
        "manifest": True,
    },
    "rare-employment": {
        "name": "RARE Employment",
        "csv_name": "rare-employment.csv",
        "target": ROOT / "staged-series" / "rare-employment",
        "title_page": None,
        "runtime_role": "staged-ap-content",
        "manifest": False,
    },
}


def slugify(value: str) -> str:
    value = value.replace("&", " and ")
    value = value.replace("’", "").replace("'", "")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def load_csv_bytes(path: Path):
    raw = gzip.decompress(path.read_bytes())
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(text.splitlines()))
    return raw, rows


def build_payload(slug: str, config: dict, rows: list[dict]) -> dict:
    if config["manifest"]:
        source_csv = f"rare-insights/{slug}/source/{config['csv_name']}"
    else:
        source_csv = f"staged-series/{slug}/source/{config['csv_name']}"

    payload = {
        "schemaVersion": 1,
        "series": config["name"],
        "slug": slug,
        "repository": "Joliel21/rare-revolution-magazine",
        "runtimeRole": config["runtime_role"],
        "sourceCsv": source_csv,
        "articlePage": {
            "eyebrow": config["name"],
            "heading": "Explore the series",
            "summary": "{count} articles",
            "maxTitleLength": 58,
        },
        "articles": [],
    }

    for row in rows:
        title = (row.get("Title") or "").strip()
        date = (row.get("Publication date") or "").strip() or None
        url = (row.get("Article link") or "").strip() or None
        image = (row.get("Image URL") or "").strip() or None
        archive = (row.get("Source archive page") or "").strip() or None

        article = {
            "id": slugify(title) if title else slugify(url or "article"),
            "title": title or None,
            "author": None,
            "date": date,
            "url": url,
            "image": image,
            "sourceImageUrl": image,
            "imageStatus": "remote-source" if image else "missing",
            "series": config["name"],
            "metadataStatus": "partial",
            "sourceArchivePage": archive,
        }
        if config["title_page"]:
            article["titlePageAsset"] = config["title_page"]
        payload["articles"].append(article)

    if not config["manifest"]:
        payload["manifestStatus"] = "not-in-current-rare-insights-15-series-manifest"

    return payload


def update_manifest(slug: str):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    changed = False
    for entry in manifest.get("entries", []):
        if entry.get("type") == "series" and entry.get("slug") == slug:
            entry["articlesFile"] = f"rare-insights/{slug}/articles.json"
            entry["articlePageRenderer"] = "data-driven"
            entry["articleMigrationStatus"] = "complete"
            changed = True
            break
    if not changed:
        raise RuntimeError(f"Manifest series not found: {slug}")
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    incoming_files = sorted(INCOMING.glob("*.csv.gz"))
    if not incoming_files:
        raise SystemExit("No incoming CSV archives found.")

    for incoming in incoming_files:
        slug = incoming.name[:-7]
        if slug not in SERIES:
            raise RuntimeError(f"Unknown incoming series: {slug}")
        config = SERIES[slug]
        raw_csv, rows = load_csv_bytes(incoming)
        target = config["target"]
        source_dir = target / "source"
        source_dir.mkdir(parents=True, exist_ok=True)
        source_path = source_dir / config["csv_name"]
        source_path.write_bytes(raw_csv)

        payload = build_payload(slug, config, rows)
        if len(payload["articles"]) != len(rows):
            raise RuntimeError(f"Article count mismatch for {slug}")
        (target / "articles.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        if config["manifest"]:
            update_manifest(slug)

        incoming.unlink()
        print(f"Imported {config['name']}: {len(rows)} articles")


if __name__ == "__main__":
    main()
