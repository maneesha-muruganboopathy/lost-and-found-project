import csv
from datetime import datetime
from pathlib import Path
from extractor import extract_report
from scoring import score_pair
ROOT=Path(__file__).parent; DATA=ROOT/'data'; OUT=ROOT/'output'
def read_reports(path, kind):
    reports=[]; errors=[]
    with open(path, newline='', encoding='utf-8-sig') as f:
        for n,row in enumerate(csv.DictReader(f),2):
            try:
                rid=(row.get('id') or '').strip(); date=(row.get('date') or '').strip(); report=(row.get('report') or '').strip()
                if not rid: raise ValueError('missing id')
                datetime.strptime(date,'%Y-%m-%d')
                if not report: raise ValueError('empty report')
                reports.append({'id':rid,'date':date,'report':report,'details':extract_report(report)})
            except Exception as e: errors.append(f'{kind}.csv row {n}: skipped ({e})')
    return reports,errors
def write_csv(path,rows,fields):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def run_matcher():
    OUT.mkdir(exist_ok=True)
    lost,errors=read_reports(DATA/'lost.csv','lost'); found,e2=read_reports(DATA/'found.csv','found'); errors+=e2
    matches=[]
    for l in lost:
        for f in found:
            m=score_pair(l,f)
            if m: matches.append(m)
    matches.sort(key=lambda x:(-x['score'],x['lost_id'],x['found_id']))
    lm={m['lost_id'] for m in matches}; fm={m['found_id'] for m in matches}
    write_csv(OUT/'matches.csv',matches,['lost_id','found_id','score','category','reasons','lost_report','found_report'])
    write_csv(OUT/'no_match.csv',[{'id':x['id'],'date':x['date'],'report':x['report']} for x in lost if x['id'] not in lm],['id','date','report'])
    write_csv(OUT/'unclaimed.csv',[{'id':x['id'],'date':x['date'],'report':x['report']} for x in found if x['id'] not in fm],['id','date','report'])
    claims={}
    for m in matches: claims.setdefault(m['found_id'],[]).append(m['lost_id'])
    double={k:v for k,v in claims.items() if len(v)>1}
    with open(OUT/'summary.txt','w',encoding='utf-8') as fp:
        fp.write('LOST AND FOUND MATCHER SUMMARY\n')
        fp.write(f'Valid lost reports: {len(lost)}\nValid found reports: {len(found)}\nSuggested pairs: {len(matches)}\nLikely: {sum(m["category"]=="Likely" for m in matches)}\nPossible: {sum(m["category"]=="Possible" for m in matches)}\n')
        fp.write(f'Lost reports with no suggestion: {len(lost)-len(lm)}\nFound items matched to none: {len(found)-len(fm)}\n\nDOUBLE CLAIM ALERTS\n')
        if double:
            for fid,lids in double.items(): fp.write(f'{fid} claimed by: {", ".join(lids)}\n')
            fp.write('Help desk must request an extra detail not mentioned in either report. Never assign ownership automatically.\n')
        else: fp.write('None detected.\n')
        if errors: fp.write('\nINVALID ROWS SKIPPED\n'+'\n'.join(errors)+'\n')
    print('Run complete. Output files are in output/.')
    print(f'Suggested pairs: {len(matches)} | Double-claim alerts: {len(double)}')
    print('Open output/matches.csv and output/summary.txt')
