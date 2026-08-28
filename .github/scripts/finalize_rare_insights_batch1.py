from pathlib import Path
import base64,csv,io,json,re,unicodedata,zlib

ROOT=Path.cwd()
RI=ROOT/'rare-insights'
META={
 'charity-and-advocacy': {'name':'Charity & Advocacy','asset':'charity-and-advocacy.png','count':98,'manifest':True},
 'industry-insights': {'name':'Industry Insights','asset':'industry-insights.png','count':33,'manifest':True},
 'editors-letters': {'name':'Editors’ Letters','asset':'editors-letters.png','count':10,'manifest':True},
 'medical': {'name':'Medical','asset':'medical.png','count':33,'manifest':True},
 'rare-employment': {'name':'RARE Employment','asset':None,'count':4,'manifest':False},
}

# Reconstruct the two larger source CSVs from compressed staging text.
for slug in ('charity-and-advocacy','medical'):
    enc=(ROOT/'.github/tmp'/f'{slug}.z64').read_text(encoding='utf-8').strip()
    raw=zlib.decompress(base64.b64decode(enc)).decode('utf-8-sig')
    d=RI/slug/'source'; d.mkdir(parents=True,exist_ok=True)
    (d/f'{slug}.csv').write_text(raw,encoding='utf-8')

def slugify(value):
    value=unicodedata.normalize('NFKD',value)
    value=''.join(c for c in value if not unicodedata.combining(c))
    value=value.lower().replace('’',"'")
    return re.sub(r'[^a-z0-9]+','-',value).strip('-') or 'article'

for slug,m in META.items():
    csv_path=RI/slug/'source'/f'{slug}.csv'
    if not csv_path.exists(): raise SystemExit(f'Missing source CSV: {csv_path}')
    raw=csv_path.read_text(encoding='utf-8-sig')
    rows=list(csv.DictReader(io.StringIO(raw)))
    if len(rows)!=m['count']: raise SystemExit(f'{slug}: expected {m["count"]} rows, found {len(rows)}')
    seen={}; articles=[]
    for row in rows:
        aid=slugify(row['Title']); seen[aid]=seen.get(aid,0)+1
        if seen[aid]>1: aid=f'{aid}-{seen[aid]}'
        articles.append({
          'id':aid,'title':row['Title'].strip() or None,'author':None,
          'date':row['Publication date'].strip() or None,'url':row['Article link'].strip() or None,
          'image':row['Image URL'].strip() or None,'series':m['name'],
          'titlePageAsset':f"rare-insights/sub-series-title-pages/{m['asset']}" if m['asset'] else None,
          'sourceArchivePage':row['Source archive page'].strip() or None,'metadataStatus':'partial'
        })
    payload={
      'schemaVersion':1,'series':m['name'],'slug':slug,
      'articlePage':{'eyebrow':m['name'],'heading':'Explore the series','summary':'{count} articles','maxTitleLength':58},
      'repository':'Joliel21/rare-revolution-magazine',
      'runtimeRole':'canonical-ap-content' if m['manifest'] else 'staged-ap-content',
      'sourceCsv':f'rare-insights/{slug}/source/{slug}.csv','imageStrategy':'external-microlink','articles':articles
    }
    d=RI/slug; d.mkdir(parents=True,exist_ok=True)
    (d/'articles.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    note='This series is part of the current RARE INSIGHTS manifest.' if m['manifest'] else 'This series is staged separately and is not currently one of the 15 RARE INSIGHTS manifest entries.'
    (d/'README.md').write_text(
      f"# {m['name']}\n\n- `articles.json` contains {len(articles)} article records.\n- `source/{slug}.csv` preserves the uploaded source CSV.\n- Article images currently use the source CSV's external Microlink image URLs; no local image mapping was invented.\n- Author values remain `null` because the source CSV does not provide authors.\n- {note}\n",
      encoding='utf-8')

manifest_path=RI/'manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
for entry in manifest.get('entries',[]):
    slug=entry.get('slug')
    if slug in META and META[slug]['manifest']:
        entry['articlesFile']=f'rare-insights/{slug}/articles.json'
        entry['articlePageRenderer']='data-driven'
        entry['articleMigrationStatus']='complete'
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Batch 1 complete:', ', '.join(f"{s}={META[s]['count']}" for s in META))
