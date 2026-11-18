"""List fund series (names) available per family by reading only filing headers."""
import json, ssl, urllib.request, re, time
from collections import defaultdict
ctx = ssl._create_unverified_context()
H = {'User-Agent': 'research jaysubbu@gmail.com'}
FAM = {'PIMCO': 810893, 'Vanguard': 106444, 'BlackRock': 276463}

def get(u, nbytes=None):
    with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=45, context=ctx) as r:
        return (r.read(nbytes) if nbytes else r.read()).decode('utf-8', 'replace')

out = {}
for fam, cik in FAM.items():
    r = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json'))['filings']['recent']
    acc = [(dt, a) for fm, a, dt in zip(r['form'], r['accessionNumber'], r['filingDate']) if fm == 'NPORT-P']
    names = {}
    for dt, a in acc:
        try:
            x = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{a.replace('-','')}/primary_doc.xml", 12000)
        except Exception as e:
            continue
        m = re.search(r'<seriesName>([^<]+)</seriesName>', x)
        rp = re.search(r'<repPdDate>([^<]+)</repPdDate>', x)
        if m:
            names.setdefault(m.group(1), []).append((dt, a, rp.group(1) if rp else None))
        time.sleep(0.12)
    out[fam] = names
    print(fam, len(acc), 'filings,', len(names), 'series')
    for n, v in sorted(names.items()):
        print('   ', n, len(v))
json.dump(out, open('bond_cache/series_index.json', 'w'))
