from pathlib import Path
import base64
import csv
import io
import json
import re
import shutil
import unicodedata
import zipfile

ROOT = Path.cwd()
ZIP_B64 = "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[... ELLIPSIZATION ...]rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "scottish-based-liver-charity-pbc-foundation-celebrates-success-of-its-first-global-online-event",
      "title": "Scottish based liver charity PBC foundation celebrates success of its first global online event",
      "author": null,
      "date": "29 September 2020",
      "url": "https://rarerevolutionmagazine.com/scottish-based-liver-charity-pbc-foundation-celebrates-success-of-its-first-global-online-event/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fscottish-based-liver-charity-pbc-foundation-celebrates-success-of-its-first-global-online-event%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "cmt-research-foundation-fighting-to-shorten-the-time-to-diagnosis-and-put-cmt-on-the-radar-of-pharma",
      "title": "CMT Research Foundation fighting to shorten the time to diagnosis and put CMT on the radar of pharma",
      "author": null,
      "date": "24 September 2020",
      "url": "https://rarerevolutionmagazine.com/cmt-research-foundation-fighting-to-shorten-the-time-to-diagnosis-and-put-cmt-on-the-radar-of-pharma/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fcmt-research-foundation-fighting-to-shorten-the-time-to-diagnosis-and-put-cmt-on-the-radar-of-pharma%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "a-race-against-time",
      "title": "A race against time",
      "author": null,
      "date": "18 August 2020",
      "url": "https://rarerevolutionmagazine.com/a-race-against-time/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fa-race-against-time%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "the-albinism-fellowship-uk-and-ireland-are-proud-to-support-a-campaign-to-end-discrimination-within-international-blind-sport",
      "title": "The Albinism Fellowship UK and Ireland are proud to support a campaign to end discrimination within international blind sport",
      "author": null,
      "date": "5 August 2020",
      "url": "https://rarerevolutionmagazine.com/the-albinism-fellowship-uk-and-ireland-are-proud-to-support-a-campaign-to-end-discrimination-within-international-blind-sport/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fthe-albinism-fellowship-uk-and-ireland-are-proud-to-support-a-campaign-to-end-discrimination-within-international-blind-sport%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "i-stay-home-for-rare-financial-assistance-campaign-launched-by-living-in-the-light",
      "title": "“I Stay Home for RARE” financial assistance campaign launched by Living in the Light.",
      "author": null,
      "date": "8 July 2020",
      "url": "https://rarerevolutionmagazine.com/i-stay-home-for-rare-financial-assistance-campaign-launched-by-living-in-the-light/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fi-stay-home-for-rare-financial-assistance-campaign-launched-by-living-in-the-light%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "kawasaki-disease-uk",
      "title": "Kawasaki disease UK",
      "author": null,
      "date": "1 July 2020",
      "url": "https://rarerevolutionmagazine.com/kawasaki-disease-uk/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fkawasaki-disease-uk%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "global-commission-progresses-technology-health-pilots-to-accelerate-time-to-diagnosis-for-children-with-a-rare-disease",
      "title": "Global Commission progresses technology health pilots to accelerate time to diagnosis for children with a rare disease",
      "author": null,
      "date": "29 June 2020",
      "url": "https://rarerevolutionmagazine.com/global-commission-progresses-technology-health-pilots-to-accelerate-time-to-diagnosis-for-children-with-a-rare-disease/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fglobal-commission-progresses-technology-health-pilots-to-accelerate-time-to-diagnosis-for-children-with-a-rare-disease%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "nystagmus-awareness-day-20-june-2020",
      "title": "Nystagmus awareness day – 20 June 2020",
      "author": null,
      "date": "17 June 2020",
      "url": "https://rarerevolutionmagazine.com/nystagmus-awareness-day-20-june-2020/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fnystagmus-awareness-day-20-june-2020%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "welcome-new-boost-for-mums-and-dads-of-young-children-with-albinism",
      "title": "Welcome new boost for mums and dads of young children with albinism",
      "author": null,
      "date": "11 June 2020",
      "url": "https://rarerevolutionmagazine.com/welcome-new-boost-for-mums-and-dads-of-young-children-with-albinism/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fwelcome-new-boost-for-mums-and-dads-of-young-children-with-albinism%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "local-charity-thanks-the-north-east-for-the-gift-of-time",
      "title": "Local charity thanks the north-east for the gift of time",
      "author": null,
      "date": "5 June 2020",
      "url": "https://rarerevolutionmagazine.com/local-charity-thanks-the-north-east-for-the-gift-of-time/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Flocal-charity-thanks-the-north-east-for-the-gift-of-time%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "my-little-lockdown-life-created-by-kate-read-rebecca-atkinson",
      "title": "My Little Lockdown Life created by Kate Read & Rebecca Atkinson",
      "author": null,
      "date": "12 May 2020",
      "url": "https://rarerevolutionmagazine.com/my-little-lockdown-life-created-by-kate-read-and-rebecca-atkinson/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fmy-little-lockdown-life-created-by-kate-read-and-rebecca-atkinson%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    },
    {
      "id": "making-sense-of-the-headlines-empowered-and-informed-treatment-choice-in-haemophilia",
      "title": "Making sense of the headlines: empowered and informed treatment choice in haemophilia",
      "author": null,
      "date": "15 April 2020",
      "url": "https://rarerevolutionmagazine.com/making-sense-of-the-headlines-empowered-and-informed-treatment-choice-in-haemophilia/",
      "image": "https://api.microlink.io/?url=https%3A%2F%2Frarerevolutionmagazine.com%2Fmaking-sense-of-the-headlines-empowered-and-informed-treatment-choice-in-haemophilia%2F&embed=image.url",
      "series": "Charity & Advocacy",
      "titlePageAsset": "rare-insights/sub-series-title-pages/charity-and-advocacy.png",
      "sourceArchivePage": "https://rarerevolutionmagazine.com/category/rare-insights/charity-advocacy/page/6/",
      "metadataStatus": "partial"
    }
  ]
}PK     ]...