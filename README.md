# RARE Revolution Magazine — Content Repository

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
