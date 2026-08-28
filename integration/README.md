# Reader integration reference

`SeriesArticlePage.tsx` is copied from the validated RRM implementation that made A Day in the Life data-driven.

It is stored here as a **reference implementation**, not as an independently runnable application. It currently imports the RRM asset resolver. When the magazine is deliberately switched to `Joliel21/rare-revolution-magazine`, update the reader's repository asset resolver/base URL so that paths from `rare-insights/manifest.json` and each `articles.json` resolve against this repository.

Do not point the live magazine at this repository until all required AP inventories are migrated and regression-tested.
