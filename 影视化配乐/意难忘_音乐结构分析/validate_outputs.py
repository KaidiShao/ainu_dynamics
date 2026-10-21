"""Artifact consistency checks and a positive/negative recurrence diagnostic."""
from pathlib import Path
import argparse
import ast
import csv
import hashlib
import json
import re
import numpy as np

ROOT=Path(__file__).resolve().parent


def rows(name):
    with (ROOT/'data'/name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio',type=Path);args=ap.parse_args()
    checks=[]
    def check(name,ok):
        checks.append(dict(check=name,passed=bool(ok)))
        if not ok:raise AssertionError(name)
    metadata=json.loads((ROOT/'data/audio_metadata.json').read_text(encoding='utf-8'))
    annot=json.loads((ROOT/'annotations.json').read_text(encoding='utf-8'))
    duration=metadata['duration_s']
    check('annotations bound to recording',annot['audio_sha256']==metadata['sha256'])
    check('sample-derived duration',abs(metadata['frames']/metadata['sample_rate']-duration)<1e-9)
    sections=annot['sections']
    check('continuous full coverage',sections[0]['start']==0 and abs(sections[-1]['end']-duration)<1e-9 and all(a['end']==b['start'] for a,b in zip(sections,sections[1:])))
    occurrences=[o for m in annot['motifs'] for o in m['occurrences']]
    check('all reported windows within audio, 2-10s',all(0<=o['start']<o['end']<=duration and 2<=o['end']-o['start']<=10 for o in occurrences))
    csv_occ=rows('motif_occurrences.csv')
    check('annotation/export count',len(csv_occ)==len(occurrences)==18)
    check('explicit auditory limitation',metadata['auditory_verified'] is False and all(r['auditory_verified']=='False' for r in csv_occ))
    check('bounded scores',all(-1e-8<=float(r[k])<=1+1e-8 for r in csv_occ for k in ['dtw_score','linear_score','pitch_cos','upper_chroma_cos','bass_chroma_cos']))
    for r in csv_occ:
        if r['status']=='strong_candidate':
            check('strong candidate criteria '+r['motif']+' '+r['start_s'],float(r['dtw_score'])>=.84 and float(r['order_gain_over_shuffle95'])>=.05)
    frames=rows('features_100ms.csv');t=np.array([float(r['time_s']) for r in frames])
    check('feature timestamps',t[0]==0 and np.allclose(np.diff(t),.1) and t[-1]<=duration<t[-1]+.1)
    check('finite feature values',all(np.isfinite(float(v)) for r in frames for v in r.values()))
    check('no commercial audio copied',not any(p.suffix.lower() in {'.flac','.wav','.mp3','.m4a','.ogg','.aac'} for p in ROOT.rglob('*') if p.is_file()))
    broken=[]
    for p in ROOT.glob('*.md'):
        for link in re.findall(r'!?\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if '://' not in link and not (ROOT/link.split('#')[0]).exists():broken.append((p.name,link))
    check('report local links',not broken)
    figs=list((ROOT/'figures').glob('*.png'))
    check('14 expected figures',len(figs)==14 and all(p.stat().st_size>10000 for p in figs))
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    check('Python syntax',True)
    manifest=json.loads((ROOT/'data/run_manifest.json').read_text(encoding='utf-8'))
    check('manifest matches source and annotations',all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in manifest['files'].items()))
    if args.audio:
        with args.audio.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        check('original audio hash unchanged',digest==metadata['sha256']==manifest['audio_sha256'])
    if (ROOT/'.cache/features.npz').exists():
        from motif_review import compare
        z=dict(np.load(ROOT/'.cache/features.npz'))
        positive=compare(z,57.8,86.5,7.)
        background=compare(z,57.8,24.3,7.)
        check('ordered recurrence beats similar background',positive['dtw_score']>background['dtw_score'] and positive['order_gain_over_shuffle95']>.1 and background['order_gain_over_shuffle95']<.08)
    else:positive=background=None
    report=dict(status='passed',checks=checks,positive_pair=positive,background_pair=background,
                limitations=['No auditory verification','No melody or harmony ground truth','Player JavaScript syntax checked separately; FLAC playback not human-audited'])
    (ROOT/'data/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(checks)} checks passed; no listening verification implied.')


if __name__=='__main__':main()
