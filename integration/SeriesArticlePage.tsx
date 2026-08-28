import { useEffect, useMemo, useState } from "react";
import { resolveRepositoryAssetUrl } from "@/app/config/repository-assets";

type ArticleRecord = {
  id?: string;
  title: string | null;
  author?: string | null;
  date?: string | null;
  url: string | null;
  image: string | null;
  series?: string;
  titlePageAsset?: string;
  metadataStatus?: "complete" | "partial" | "pending-migration" | string;
};

type ArticlePageConfig = {
  eyebrow?: string;
  heading?: string;
  summary?: string;
  maxTitleLength?: number;
};

type SeriesArticlesPayload = {
  schemaVersion?: number;
  series: string;
  slug?: string;
  articlePage?: ArticlePageConfig;
  articles: ArticleRecord[];
};

type SeriesArticlePageProps = {
  sourcePath: string;
  fallbackSeriesName: string;
  ariaLabel?: string;
};

const shortenTitle = (title: string, maxLength: number) => {
  if (title.length <= maxLength) return title;
  const shortened = title.slice(0, maxLength - 3).replace(/\s+\S*$/, "");
  return `${shortened}...`;
};

const articleImageUrl = (value?: string | null) => {
  const rawValue = String(value || "").trim();
  if (!rawValue) return "";
  return resolveRepositoryAssetUrl(rawValue);
};

export const SeriesArticlePage = ({
  sourcePath,
  fallbackSeriesName,
  ariaLabel,
}: SeriesArticlePageProps) => {
  const [payload, setPayload] = useState<SeriesArticlesPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const sourceUrl = resolveRepositoryAssetUrl(sourcePath);

    setPayload(null);
    setError(null);

    fetch(sourceUrl, { signal: controller.signal, cache: "no-cache" })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Article inventory returned ${response.status}`);
        }
        return response.json() as Promise<SeriesArticlesPayload>;
      })
      .then((data) => {
        if (cancelled) return;
        if (!data || !Array.isArray(data.articles)) {
          throw new Error("Article inventory is missing an articles array");
        }
        setPayload(data);
      })
      .catch((reason) => {
        if (cancelled || reason?.name === "AbortError") return;
        console.warn(`Could not load article inventory ${sourcePath}`, reason);
        setError("Article information could not be loaded.");
      });

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [sourcePath]);

  const seriesName = payload?.series || fallbackSeriesName;
  const display = payload?.articlePage || {};
  const articles = useMemo(
    () => (payload?.articles || []).filter((article) => article?.title && article?.url),
    [payload],
  );
  const maxTitleLength = display.maxTitleLength || 58;
  const summary = (display.summary || "{count} articles")
    .replace("{count}", String(articles.length));

  return (
    <div className="relative flex h-full w-full flex-col overflow-hidden bg-[#f4f9fb] text-[#17384b]">
      <div className="shrink-0 border-b border-[#d5e7ed] bg-white px-8 pb-5 pt-7">
        <p className="mb-1 text-[9px] font-bold uppercase tracking-[0.27em] text-[#2b9bc0]">
          {display.eyebrow || seriesName}
        </p>
        <h2 className="text-[28px] font-light leading-none tracking-[-0.035em] text-[#222d33]">
          {display.heading || "Explore the series"}
        </h2>
        <p className="mt-2 text-[11px] text-[#54707d]">
          {payload ? summary : error || "Loading articles…"}
        </p>
      </div>

      <div
        className="series-data-article-scroll min-h-0 flex-1 overflow-y-auto overscroll-contain px-5 py-5"
        onWheel={(event) => event.stopPropagation()}
        onWheelCapture={(event) => event.stopPropagation()}
        onTouchMove={(event) => event.stopPropagation()}
        aria-label={ariaLabel || `${seriesName} article archive`}
      >
        {error ? (
          <div className="rounded-[10px] border border-[#d5e7ed] bg-white p-5 text-[11px] text-[#54707d]">
            {error}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 pb-8">
            {articles.map((item, index) => {
              const title = String(item.title || "");
              const image = articleImageUrl(item.image);
              return (
                <a
                  key={item.id || item.url || `${seriesName}-${index}`}
                  href={String(item.url)}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={title}
                  aria-label={`Open ${title} in a new tab`}
                  className="group flex h-[250px] min-h-[250px] max-h-[250px] flex-col overflow-hidden rounded-[10px] border border-[#d5e7ed] bg-white no-underline shadow-[0_2px_10px_rgba(20,60,75,0.07)] transition-transform hover:-translate-y-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2b9bc0]"
                >
                  <div className="flex h-[170px] min-h-[170px] max-h-[170px] shrink-0 items-center justify-center overflow-hidden bg-[#edf4f6] p-1">
                    {image ? (
                      <img
                        src={image}
                        alt=""
                        className="h-full w-full object-contain scale-[1.08]"
                        loading={index < 4 ? "eager" : "lazy"}
                        draggable={false}
                      />
                    ) : null}
                  </div>
                  <div className="flex h-[80px] min-h-[80px] max-h-[80px] flex-col overflow-hidden px-3 pb-3 pt-2.5">
                    <span className="mb-1.5 text-[8px] font-semibold uppercase tracking-[0.12em] text-[#2b9bc0]">
                      {seriesName}
                    </span>
                    <h3 className="text-[11px] font-semibold leading-[1.28] text-[#203b48]">
                      {shortenTitle(title, maxTitleLength)}
                    </h3>
                  </div>
                </a>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
