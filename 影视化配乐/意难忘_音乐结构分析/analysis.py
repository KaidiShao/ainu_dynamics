"""Offline, auditable recording analysis. No audio is copied to the output tree.

Usage: python analysis.py --audio /path/to/recording.flac
Or use --config audio_config.local.json. See README for interpretation limits.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import sys
import os
import inspect

os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.cache'/'matplotlib'))

import numpy as np
import scipy
from scipy import signal, ndimage
import soundfile as sf
import librosa
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
SR, HOP, DT = 22050, 512, 0.1
EPS = 1e-10


def log(s):
    print(s, flush=True)


def write_json(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')


def write_csv(p, rows):
    if not rows:
        return
    with p.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def unit(x):
    return x / np.maximum(np.linalg.norm(x, axis=0, keepdims=True), EPS)


def fold(x, first_midi):
    z = np.zeros((12, x.shape[1]))
    for i in range(x.shape[0]):
        z[(first_midi+i) % 12] += x[i]
    return z


def grid(x, times):
    x = np.atleast_2d(x)
    old = np.arange(x.shape[1]) * HOP / SR
    return np.array([np.interp(times, old, row) for row in x])


def savefig(fig, name):
    fig.savefig(ROOT/'figures'/name, dpi=160, bbox_inches='tight')
    plt.close(fig)


def extract(path, cache):
    info = sf.info(path)
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    log(str(info))
    raw, sr0 = sf.read(path, dtype='float32', always_2d=True)
    duration = len(raw)/sr0
    metadata = dict(filename=path.name, sha256=digest, bytes=path.stat().st_size,
                    sample_rate=sr0, channels=info.channels, frames=info.frames,
                    subtype=info.subtype, format=info.format, duration_s=duration,
                    sample_peak=float(np.max(np.abs(raw))),
                    samples_at_or_above_1=int(np.sum(np.abs(raw)>=1)),
                    python=sys.version, platform=platform.platform(),
                    versions={p: importlib.metadata.version(p) for p in
                              ['numpy','scipy','librosa','soundfile','matplotlib']},
                    analysis_sr=SR, hop=HOP, grid_s=DT,
                    auditory_verified=False)
    # Stereo quantities at native resolution; RMS remains electrical, not LUFS/SPL.
    stereo=[]
    for a in np.arange(0,duration,DT):
        r=raw[int(a*sr0):int(min(a+DT,duration)*sr0)]
        mid=r.mean(axis=1)
        side=(r[:,0]-r[:,1])/2 if info.channels==2 else np.zeros_like(mid)
        stereo.append((np.sqrt(np.mean(r*r)),
                       np.sqrt(np.mean(side*side))/max(np.sqrt(np.mean(mid*mid)),EPS)))
    mono=raw.mean(axis=1)
    y=librosa.resample(mono,orig_sr=sr0,target_sr=SR)
    del raw,mono
    log('STFT and harmonic/percussive separation')
    S=librosa.stft(y,n_fft=2048,hop_length=HOP)
    H,P=librosa.decompose.hpss(S, kernel_size=31, margin=2.0)
    yh=librosa.istft(H,hop_length=HOP,length=len(y))
    log('Harmonic CQT (C2-B7, 72 semitone bins)')
    cq=np.abs(librosa.cqt(yh,sr=SR,hop_length=HOP,fmin=librosa.note_to_hz('C2'),n_bins=72))
    mag=np.abs(S)
    rms=librosa.feature.rms(y=y,frame_length=2048,hop_length=HOP)[0]
    centroid=librosa.feature.spectral_centroid(S=mag,sr=SR)[0]
    onset=librosa.onset.onset_strength(S=librosa.amplitude_to_db(mag,ref=np.max),sr=SR,hop_length=HOP)
    times=np.arange(0,duration,DT)
    c=grid(cq,times)
    # Remove per-frame spectral floor, preserving relative pitch salience.
    clean=np.maximum(c-np.median(c,axis=0,keepdims=True),0)
    chroma=unit(fold(clean,36))
    upper=clean[24:60]  # C4-B6; includes harmonics/inner voices, NOT isolated melody
    upchroma=unit(fold(upper,60))
    pitch=unit(np.sqrt(upper))
    bass=unit(fold(clean[:24],36))
    freq=librosa.fft_frequencies(sr=SR,n_fft=2048)
    power=mag**2
    low=power[freq<250].sum(axis=0)/np.maximum(power.sum(axis=0),EPS)
    high=power[freq>=2000].sum(axis=0)/np.maximum(power.sum(axis=0),EPS)
    # Spectral occupancy is a proxy, never an instrument/voice count.
    occupancy=np.mean(c>c.max(axis=0,keepdims=True)*0.15,axis=0)
    arrays=dict(t=times,cqt=c,chroma=chroma,upchroma=upchroma,pitch=pitch,bass=bass,
                rms=grid(rms,times)[0],centroid=grid(centroid,times)[0],onset=grid(onset,times)[0],
                low=grid(low,times)[0],high=grid(high,times)[0],occupancy=occupancy,
                stereo_rms=np.array(stereo)[:,0],side_mid=np.array(stereo)[:,1],
                harmonic_fraction=grid((np.abs(H)**2).sum(axis=0)/np.maximum(power.sum(axis=0),EPS),times)[0])
    write_json(ROOT/'data'/'audio_metadata.json',metadata)
    np.savez_compressed(cache,**arrays)
    write_json(cache.with_suffix('.json'),dict(sha256=digest,SR=SR,HOP=HOP,DT=DT))
    return arrays,metadata


def overview(z,m):
    t=z['t']; db=20*np.log10(np.maximum(z['rms'],EPS))
    rows=[dict(time_s=round(float(ti),3),rms_dbfs=float(db[i]),
               stereo_rms_dbfs=float(20*np.log10(max(z['stereo_rms'][i],EPS))),
               centroid_hz=float(z['centroid'][i]),low_power_fraction=float(z['low'][i]),
               high_power_fraction=float(z['high'][i]),onset_strength=float(z['onset'][i]),
               spectral_occupancy=float(z['occupancy'][i]),side_mid_ratio=float(z['side_mid'][i]))
          for i,ti in enumerate(t)]
    write_csv(ROOT/'data'/'features_100ms.csv',rows)
    fig,ax=plt.subplots(5,1,figsize=(15,12),sharex=True)
    ax[0].plot(t,db,lw=.7); ax[0].set(ylabel='Mono RMS dBFS',ylim=(-65,0))
    ax[1].plot(t,z['centroid'],lw=.6); ax[1].set(ylabel='Centroid Hz')
    ax[2].plot(t,z['low'],label='<250 Hz'); ax[2].plot(t,z['high'],label='>=2 kHz');ax[2].legend();ax[2].set(ylabel='Power fraction')
    ax[3].plot(t,z['onset'],lw=.6);ax[3].set(ylabel='Onset strength')
    ax[4].plot(t,z['occupancy'],label='CQT occupancy');ax[4].plot(t,z['side_mid'],label='Side/mid RMS',alpha=.7);ax[4].legend();ax[4].set(xlabel='Time (s)',ylabel='Proxy / ratio',ylim=(0,1.5))
    for a in ax:a.grid(alpha=.2)
    savefig(fig,'01_acoustic_overview.png')
    # Waveform peak envelope in native audio; no audio is exported.
    fig,ax=plt.subplots(2,1,figsize=(15,7),sharex=True)
    with sf.SoundFile(m['_path']) as f:
        blocks=[]
        for b in f.blocks(blocksize=max(1,int(f.samplerate*.05)),dtype='float32',always_2d=True):
            blocks.append((b.min(),b.max()))
    b=np.array(blocks);tt=np.arange(len(b))*.05
    ax[0].fill_between(tt,b[:,0],b[:,1],color='#366b95',lw=0);ax[0].set(ylabel='Sample amplitude',title='Native stereo peak envelope (50 ms bins)')
    ax[1].imshow(librosa.amplitude_to_db(z['cqt'],ref=np.max),origin='lower',aspect='auto',extent=[0,m['duration_s'],35.5,107.5],vmin=-60,vmax=0,cmap='magma');ax[1].set(ylabel='MIDI bin (not transcription)',xlabel='Time (s)')
    savefig(fig,'02_waveform_cqt.png')
    fig,ax=plt.subplots(1,1,figsize=(15,4))
    ax.imshow(z['chroma'],origin='lower',aspect='auto',extent=[0,m['duration_s'],-.5,11.5]);ax.set(yticks=range(12),yticklabels=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'],xlabel='Time (s)',title='Harmonic pitch-class energy (not chord labels)')
    savefig(fig,'03_chromagram.png')
    # Multi-scale change score: mean descriptor vectors before/after each point.
    f=np.vstack([z['chroma'],db[None]/15,z['centroid'][None]/2000,z['low'][None],z['high'][None]])
    nov=[]
    for radius in [2.,4.,8.]:
        n=int(radius/DT);cs=np.pad(np.cumsum(f,axis=1),((0,0),(1,0)))
        v=np.zeros(len(t))
        for i in range(n,len(t)-n):
            v[i]=np.linalg.norm((cs[:,i]-cs[:,i-n])/n-(cs[:,i+n]-cs[:,i])/n)
        nov.append(v)
    fig,ax=plt.subplots(figsize=(15,4))
    rows=[]
    for r,v in zip([2,4,8],nov):
        ax.plot(t,v,label=f'+/- {r}s');pk,_=signal.find_peaks(v,distance=int(6/DT),prominence=.1)
        for i in pk:rows.append(dict(time_s=float(t[i]),radius_s=r,change_score=float(v[i])))
    ax.legend();ax.set(xlabel='Time (s)',ylabel='Descriptor change',title='Boundary candidates; not automatic phrase boundaries')
    savefig(fig,'04_boundary_candidates.png');write_csv(ROOT/'data'/'boundary_candidates.csv',rows)


def discover(z):
    log('Sequence recurrence search, 2/4/6/8/10-second windows')
    # Absolute-register pitch and octave-folded upper chroma are separate evidence.
    ps=z['pitch'].T@z['pitch'];cs=z['upchroma'].T@z['upchroma']
    ss=.5*ps+.5*cs
    fig,ax=plt.subplots(1,2,figsize=(14,6))
    for a,v,title in zip(ax,[cs,ps],['Upper pitch-class similarity','C4-B6 pitch-bin similarity']):
        a.imshow(v[::3,::3],origin='lower',extent=[0,z['t'][-1],0,z['t'][-1]],vmin=0,vmax=1,cmap='magma',aspect='equal');a.set(title=title,xlabel='Time (s)',ylabel='Time (s)')
    savefig(fig,'05_self_similarity.png')
    rows=[];N=len(z['t'])
    sequence_map=np.full((N,N),np.nan,dtype='float32')
    for secs in [2,4,6,8,10]:
        n=round(secs/DT);candidates=[]
        for lag in range(n+10,N-n):
            d=np.diagonal(ss,offset=lag)
            if len(d)<n:continue
            scores=np.convolve(d,np.ones(n)/n,'valid')
            if secs==6:
                ii=np.arange(len(scores));sequence_map[ii,ii+lag]=scores;sequence_map[ii+lag,ii]=scores
            pk,_=signal.find_peaks(scores,distance=max(1,n//2))
            for p in pk:
                if scores[p]>.72:
                    candidates.append((float(scores[p]),int(p),int(p+lag)))
        candidates.sort(reverse=True);chosen=[]
        for score,a,b in candidates:
            if any(abs(a-x)<n*.65 and abs(b-y)<n*.65 for _,x,y in chosen):continue
            if np.mean(z['rms'][a:a+n])<.006 or np.mean(z['rms'][b:b+n])<.006:continue
            chosen.append((score,a,b))
            rows.append(dict(window_s=secs,start_a_s=round(a*DT,2),start_b_s=round(b*DT,2),
                             score=score,pitch_cos=float(np.mean(np.sum(z['pitch'][:,a:a+n]*z['pitch'][:,b:b+n],axis=0))),
                             upper_chroma_cos=float(np.mean(np.sum(z['upchroma'][:,a:a+n]*z['upchroma'][:,b:b+n],axis=0)))))
            if len(chosen)>=100:break
    write_csv(ROOT/'data'/'repeat_candidates.csv',rows)
    fig,ax=plt.subplots(figsize=(9,8))
    cmap=plt.get_cmap('magma').copy();cmap.set_bad('#eeeeea')
    im=ax.imshow(sequence_map[::3,::3],origin='lower',extent=[0,z['t'][-1],0,z['t'][-1]],vmin=.72,vmax=.93,cmap=cmap)
    ax.set(xlabel='Window start (s)',ylabel='Window start (s)',title='6-second ordered similarity (overlaps excluded; not melody identity)')
    fig.colorbar(im,ax=ax,label='Mean aligned cosine')
    savefig(fig,'08_sequence_similarity.png')
    log('Top 6s matches: '+str([r for r in rows if r['window_s']==6][:12]))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audio',type=Path);ap.add_argument('--config',type=Path)
    ap.add_argument('--recompute',action='store_true');ap.add_argument('--skip-discovery',action='store_true')
    args=ap.parse_args()
    path=args.audio
    if not path:
        config=args.config or ROOT/'audio_config.local.json'
        if not config.exists():ap.error('Supply --audio or a local configuration; no audio is downloaded.')
        path=Path(json.loads(config.read_text(encoding='utf-8'))['audio_path'])
    if not path.is_file():ap.error(f'Audio does not exist: {path}')
    for d in ['data','figures','.cache']:(ROOT/d).mkdir(exist_ok=True)
    cache=ROOT/'.cache'/'features.npz'
    with path.open('rb') as f:
        digest=hashlib.file_digest(f,'sha256').hexdigest()
    if (ROOT/'annotations.json').exists():
        expected=json.loads((ROOT/'annotations.json').read_text(encoding='utf-8')).get('audio_sha256')
        if expected and expected!=digest:
            ap.error('The annotations target a different audio hash. Use the original recording or prepare a separate analysis directory and new annotations.')
    extractor_hash=hashlib.sha256(inspect.getsource(extract).encode()).hexdigest()
    cache_identity=dict(sha256=digest,SR=SR,HOP=HOP,DT=DT,extractor_sha256=extractor_hash,
                        librosa=librosa.__version__,numpy=np.__version__,scipy=scipy.__version__)
    valid=cache.exists() and cache.with_suffix('.json').exists() and json.loads(cache.with_suffix('.json').read_text())==cache_identity
    if valid and not args.recompute:
        log('Loading source-hash-validated local feature cache')
        z=dict(np.load(cache));m=json.loads((ROOT/'data'/'audio_metadata.json').read_text(encoding='utf-8'))
    else:
        z,m=extract(path,cache)
        write_json(cache.with_suffix('.json'),cache_identity)
    m['_path']=str(path)
    overview(z,m)
    if not args.skip_discovery:discover(z)
    if (ROOT/'annotations.json').exists():
        from motif_review import review
        review(z,ROOT)
        from build_listening_page import build
        build()
    manifest=dict(audio_sha256=digest,auditory_verified=False,
                  feature_cache_identity=cache_identity,
                  files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         [ROOT/'analysis.py',ROOT/'motif_review.py',ROOT/'annotations.json',ROOT/'requirements-lock.txt',ROOT/'build_listening_page.py']})
    write_json(ROOT/'data'/'run_manifest.json',manifest)
    log('Done. No audio exported; all motif identities await auditory verification.')


if __name__=='__main__':main()
