# Data-driven Article Pages (AP)

The magazine's Article Page (AP) content should live in GitHub data files rather than being hardcoded inside React components.

## Current template

**A Day in the Life** is the first migrated data-driven AP.

Its article inventory is:

`magazine-source/public/series/rare-insights/a-day-in-a-life/articles.json`

Its SSTP artwork remains:

`series/rare-insights/a-day-in-a-life.png`

The reusable renderer is:

`src/app/components/SeriesArticlePage.tsx`

## Updating an AP

To add an article to A Day in the Life:

1. Add the article image to the repository, preferably under the appropriate series/content image directory.
2. Add one record to the `articles` array in `articles.json`.
3. Preserve the existing JSON structure and valid JSON syntax.
4. Push the change to GitHub.
5. The AP reads the JSON at runtime; no React article array should be edited.

To remove an article, remove its record from `articles.json`.

To reorder articles, reorder the records in the `articles` array.

## Article record

```json
{
  "id": "stable-article-slug",
  "title": "Exact published title",
  "author": null,
  "date": "1 April 2026",
  "url": "https://rarerevolutionmagazine.com/example/",
  "image": "images/a-day-in-life/example.png",
  "series": "A Day in the Life",
  "titlePageAsset": "series/rare-insights/a-day-in-a-life.png",
  "metadataStatus": "partial"
}
```

## Metadata rules

- Do not invent a missing title, author, date, URL, or image.
- Use `null` for unverified/missing metadata.
- Use the exact published title, byline, date, URL, and article image when verified.
- Repository-relative image paths are resolved from `magazine-source/public/`.
- `metadataStatus` should remain `partial` until all required metadata is verified.

## Adding another data-driven AP

For a new series with slug `example-series`:

1. Create `magazine-source/public/series/rare-insights/example-series/articles.json` using the same structure.
2. Add `articlesFile` to that series entry in `magazine-source/public/series/rare-insights/manifest.json`.
3. Point that series' AP layout at the reusable `SeriesArticlePage` component with its `sourcePath`.
4. Keep page styling in React and article content in JSON.

The intended separation is:

- **React:** AP layout, cards, scrolling, series styling, footer behavior.
- **GitHub JSON:** article title, author, date, URL, image, ordering, and metadata status.

## Page-type rules

- **SCS — Series Cover Spread:** no generated bottom colored bar.
- **SSTP — Sub-Series Title Page:** no generated bottom colored bar.
- **AP — Article Page:** keeps the series-colored article-field background and AP bottom bar; AP scrollbar controls remain black.
