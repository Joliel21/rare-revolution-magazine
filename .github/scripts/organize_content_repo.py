from pathlib import Path
import csv
import json
import shutil
import sys

ROOT = Path.cwd()
RRM = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/rrm')
LEGACY = ROOT / 'a-day-in-a-life'
DEST = ROOT / 'rare-insights'

EXPECTED_SSTPS = [
    'a-day-in-a-life.png',
    'charity-and-advocacy.png',
    'editors-letters.png',
    'industry-insights.png',
    'medical.png',
    'news-and-press-releases.png',
    'patient-voice.png',
    'rare-caregiving.png',
    'rare-ramblings.png',
    'rare-rev-inar.png',
    'reviews.png',
    'science-and-tech.png',
    'sunday-sessions.png',
    'travel-series.png',
    'turning-the-tide.png',
]

if not LEGACY.exists():
    raise SystemExit('Expected legacy a-day-in-a-life directory was not found')
if not RRM.exists():
    raise SystemExit('RRM source checkout was not found')

# Start from a deterministic canonical content tree.
if DEST.exists():
    shutil.rmtree(DEST)

(DEST / 'series-cover-spread').mkdir(parents=True)
(DEST / 'sub-series-title-pages').mkdir(parents=True)
(DEST / 'a-day-in-a-life' / 'source').mkdir(parents=True)
(DEST / 'a-day-in-a-life' / 'images').mkdir(parents=True)
(ROOT / 'docs').mkdir(parents=True, exist_ok=True)
(ROOT / 'integration').mkdir(parents=True, exist_ok=True)

# Preserve and normalize the RARE INSIGHTS SCS artwork.
scs_candidates = list((LEGACY / 'series-cover-spread').glob('*.png'))
if len(scs_candidates) != 1:
    raise SystemExit(f'Expected exactly one SCS PNG, found {len(scs_candidates)}')
shutil.copy2(
    scs_candidates[0],
    DEST / 'series-cover-spread' / 'rare-insights-spread-title-page.png',
)

# Preserve all 15 approved SSTP artworks in a clean shared directory.
legacy_sstp_dir = LEGACY / 'sub-series-title-page'
missing_sstps = [name for name in EXPECTED_SSTPS if not (legacy_sstp_dir / name).exists()]
if missing_sstps:
    raise SystemExit(f'Missing SSTP artwork: {missing_sstps}')
for name in EXPECTED_SSTPS:
    shutil.copy2(legacy_sstp_dir / name, DEST / 'sub-series-title-pages' / name)

# Keep the source CSV as archival/import evidence rather than runtime data.
csv_source = LEGACY / 'csv' / 'a-day-in-a-life.csv'
if not csv_source.exists():
    raise SystemExit('A Day in the Life source CSV was not found')
csv_dest = DEST / 'a-day-in-a-life' / 'source' / 'a-day-in-a-life.csv'
shutil.copy2(csv_source, csv_dest)

# Import the validated data-driven AP inventory from the current RRM source.
rrm_articles_path = RRM / 'magazine-source/public/series/rare-insights/a-day-in-a-life/articles.json'
if not rrm_articles_path.exists():
    raise SystemExit('RRM A Day in the Life articles.json was not found')
articles_payload = json.loads(rrm_articles_path.read_text(encoding='utf-8'))
articles = articles_payload.get('articles', [])
if len(articles) != 23:
    raise SystemExit(f'Expected 23 A Day in the Life articles, found {len(articles)}')

# Verify the legacy CSV and JSON represent the same article set.
with csv_dest.open('r', encoding='utf-8-sig', newline='') as handle:
    csv_rows = list(csv.DictReader(handle))
csv_urls = [row['Article link'].strip() for row in csv_rows]
json_urls = [str(article.get('url') or '').strip() for article in articles]
if csv_urls != json_urls:
    missing_from_json = sorted(set(csv_urls) - set(json_urls))
    missing_from_csv = sorted(set(json_urls) - set(csv_urls))
    raise SystemExit(
        'CSV/JSON article mismatch. '
        f'Missing from JSON: {missing_from_json}; missing from CSV: {missing_from_csv}'
    )

# Make article data self-contained in this new repository.
rrm_image_dir = RRM / 'magazine-source/public/images/a-day-in-life'
used_images = set()
for article in articles:
    old_image = str(article.get('image') or '').strip()
    if old_image:
        basename = Path(old_image).name
        source_image = rrm_image_dir / basename
        if not source_image.exists():
            raise SystemExit(f'Referenced AP image is missing from RRM: {basename}')
        if basename not in used_images:
            shutil.copy2(source_image, DEST / 'a-day-in-a-life' / 'images' / basename)
            used_images.add(basename)
        article['image'] = f'rare-insights/a-day-in-a-life/images/{basename}'
    article['series'] = 'A Day in the Life'
    article['titlePageAsset'] = 'rare-insights/sub-series-title-pages/a-day-in-a-life.png'

articles_payload['repository'] = 'Joliel21/rare-revolution-magazine'
articles_payload['runtimeRole'] = 'canonical-ap-content'
articles_payload['sourceCsv'] = 'rare-insights/a-day-in-a-life/source/a-day-in-a-life.csv'
articles_dest = DEST / 'a-day-in-a-life' / 'articles.json'
articles_dest.write_text(json.dumps(articles_payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Transform the RRM RARE INSIGHTS manifest to paths owned by this repository.
rrm_manifest_path = RRM / 'magazine-source/public/series/rare-insights/manifest.json'
manifest = json.loads(rrm_manifest_path.read_text(encoding='utf-8'))
manifest['repository'] = 'Joliel21/rare-revolution-magazine'
manifest['repositoryRole'] = 'canonical-content-staging'
manifest['liveMagazineSource'] = False
for entry in manifest.get('entries', []):
    if entry.get('type') == 'section-divider':
        entry['asset'] = 'rare-insights/series-cover-spread/rare-insights-spread-title-page.png'
    elif entry.get('type') == 'series':
        slug = entry.get('slug')
        if slug:
            entry['asset'] = f'rare-insights/sub-series-title-pages/{slug}.png'
        if slug == 'a-day-in-a-life':
            entry['articlesFile'] = 'rare-insights/a-day-in-a-life/articles.json'
            entry['articlePageRenderer'] = 'data-driven'
            entry['articleMigrationStatus'] = 'complete'
        else:
            entry.pop('articlesFile', None)
            entry.pop('articlePageRenderer', None)
            entry['articleMigrationStatus'] = 'pending'
(DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Keep the existing metadata schema as the baseline contract.
rrm_schema_path = RRM / 'magazine-source/public/series/rare-insights/schema.json'
shutil.copy2(rrm_schema_path, DEST / 'schema.json')

# Preserve the validated reusable AP component as an integration reference.
rrm_component = RRM / 'src/app/components/SeriesArticlePage.tsx'
if not rrm_component.exists():
    raise SystemExit('Validated SeriesArticlePage.tsx was not found in RRM')
shutil.copy2(rrm_component, ROOT / 'integration' / 'SeriesArticlePage.tsx')

# Bring over the current data-driven guide and styling rules as reference docs.
rrm_ap_guide = RRM / 'DATA_DRIVEN_AP_GUIDE.md'
rrm_style_rules = RRM / 'SERIES_STYLING_RULES.md'
if rrm_ap_guide.exists():
    shutil.copy2(rrm_ap_guide, ROOT / 'docs' / 'AP_DATA_GUIDE.md')
if rrm_style_rules.exists():
    shutil.copy2(rrm_style_rules, ROOT / 'docs' / 'PAGE_TYPES_AND_STYLING.md')

root_readme = '''# RARE Revolution Magazine — Content Repository

This repository is being organized as the future canonical content and asset source for the RARE Revolution Magazine reader.

## Important current state

**The live magazine does not pull from this repository yet.** The active magazine remains in `Joliel21/RRM` until the source switch is deliberately implemented and tested.

This repository currently combines the original RARE INSIGHTS source package with the validated data-driven AP work from RRM.

## Repository structure

- `rare-insights/manifest.json` — section/series registry and canonical paths.
- `rare-insights/series-cover-spread/` — the main RARE INSIGHTS SCS artwork.
- `rare-insights/sub-series-title-pages/` — all 15 approved SSTP artworks.
- `rare-insights/a-day-in-a-life/articles.json` — **active/canonical A Day in the Life AP data**.
- `rare-insights/a-day-in-a-life/images/` — local AP card images referenced by `articles.json`.
- `rare-insights/a-day-in-a-life/source/a-day-in-a-life.csv` — source/archive CSV; not the runtime AP database.
- `integration/SeriesArticlePage.tsx` — validated RRM data-driven AP renderer kept as an integration reference.
- `docs/` — AP data and page-type/styling rules.

## Data ownership rule

For A Day in the Life:

- `articles.json` is the runtime/canonical AP content source.
- The CSV is retained as source/archive material only.
- SSTP and SCS PNG files are artwork, not article databases.
- The old one-byte `article-page/a` placeholder has been removed.

## Page types

- **SCS — Series Cover Spread:** major series divider; no generated bottom colored bar.
- **SSTP — Sub-Series Title Page:** title/introduction artwork; no generated bottom colored bar.
- **AP — Article Page:** article/archive/gallery page; series color is used behind the article field and in the AP bottom bar. AP scrollbar controls are black.

## Current migration status

A Day in the Life is the first AP whose article inventory has been migrated to repository-owned JSON. The other RARE INSIGHTS AP inventories remain pending and should be migrated using the same pattern before the magazine is switched to this repository.
'''
(ROOT / 'README.md').write_text(root_readme, encoding='utf-8')

ri_readme = '''# RARE INSIGHTS

This directory is the canonical RARE INSIGHTS content tree for the new `rare-revolution-magazine` repository.

## Major section artwork

`series-cover-spread/rare-insights-spread-title-page.png` is the RARE INSIGHTS **SCS**.

## Sub-series title artwork

`sub-series-title-pages/` contains the approved **SSTP** artwork for all 15 RARE INSIGHTS sub-series.

## Article pages

Each migrated sub-series should receive its own directory containing an `articles.json` inventory and any repository-owned article images/source material needed by that AP.

A Day in the Life is the first completed example:

- `a-day-in-a-life/articles.json` — canonical AP inventory.
- `a-day-in-a-life/images/` — article-card images.
- `a-day-in-a-life/source/a-day-in-a-life.csv` — archival/source CSV.

Do not duplicate article inventories in TypeScript. The reader should consume the JSON inventory when the magazine is later switched to this repository.
'''
(DEST / 'README.md').write_text(ri_readme, encoding='utf-8')

integration_readme = '''# Reader integration reference

`SeriesArticlePage.tsx` is copied from the validated RRM implementation that made A Day in the Life data-driven.

It is stored here as a **reference implementation**, not as an independently runnable application. It currently imports the RRM asset resolver. When the magazine is deliberately switched to `Joliel21/rare-revolution-magazine`, update the reader's repository asset resolver/base URL so that paths from `rare-insights/manifest.json` and each `articles.json` resolve against this repository.

Do not point the live magazine at this repository until all required AP inventories are migrated and regression-tested.
'''
(ROOT / 'integration' / 'README.md').write_text(integration_readme, encoding='utf-8')

# The old top-level package is now fully represented in the canonical tree.
shutil.rmtree(LEGACY)

# Final structural validation.
required = [
    ROOT / 'README.md',
    DEST / 'README.md',
    DEST / 'manifest.json',
    DEST / 'schema.json',
    DEST / 'series-cover-spread/rare-insights-spread-title-page.png',
    DEST / 'a-day-in-a-life/articles.json',
    DEST / 'a-day-in-a-life/source/a-day-in-a-life.csv',
    ROOT / 'integration/SeriesArticlePage.tsx',
]
required.extend(DEST / 'sub-series-title-pages' / name for name in EXPECTED_SSTPS)
missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
if missing:
    raise SystemExit(f'Canonical repository validation failed; missing: {missing}')

print(f'Canonical RARE INSIGHTS repository created with {len(articles)} AP records, {len(used_images)} unique AP images, and {len(EXPECTED_SSTPS)} SSTPs.')
