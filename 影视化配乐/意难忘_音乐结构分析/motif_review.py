"""Template search and conservative numerical diagnostics, not melody transcription."""
import json
from pathlib import Path
import numpy as np
from scipy import signal, ndimage
from analysis import DT,EPS,unit,write_csv,write_json,savefig
import librosa
import matplotlib.pyplot as plt


def feature(z):
    return np.vstack([z['pitch'],z['upchroma']])/np.sqrt(2)


def resample_feature(x,n):
    v=np.array([np.interp(np.linspace(0,1,n),np.linspace(0,1,x.shape[1]),r) for r in x])
    return np.vstack([unit(v[:36]),unit(v[36:])])/np.sqrt(2)


def compare(z,a,b,secs,end=None):
    n=round(secs/DT);m=round(((end-b) if end is not None else secs)/DT)
    i,j=round(a/DT),round(b/DT);f=feature(z);q=f[:,i:i+n];x=f[:,j:j+m]
    xx=resample_feature(x,n)
    lin=float(np.sum(q*xx)/n)
    cost=np.maximum(0,1-q.T@x)
    _,path=librosa.sequence.dtw(C=cost,global_constraints=True,band_rad=.15)
    dtw=float(1-np.mean(cost[path[:,0],path[:,1]]))
    # Shuffles preserve 0.5s blocks; scores are diagnostics, not corrected p-values.
    rng=np.random.default_rng(20261021);blocks=np.array_split(np.arange(n),max(2,n//5))
    null=[float(np.sum(q*xx[:,np.concatenate([blocks[k] for k in rng.permutation(len(blocks))])])/n) for _ in range(200)]
    bass=unit(np.array([np.interp(np.linspace(0,1,n),np.linspace(0,1,m),r) for r in z['bass'][:,j:j+m]]))
    onset_a=z['onset'][i:i+n];onset_b=np.interp(np.linspace(0,1,n),np.linspace(0,1,m),z['onset'][j:j+m])
    corr=float(np.corrcoef(onset_a,onset_b)[0,1]) if onset_a.std()>EPS and onset_b.std()>EPS else 0.
    return dict(linear_score=lin,dtw_score=dtw,order_gain_over_shuffle95=lin-float(np.percentile(null,95)),
                reverse_score=float(np.sum(q*xx[:,::-1])/n),
                pitch_cos=float(np.sum(q[:36]*xx[:36])*2/n),upper_chroma_cos=float(np.sum(q[36:]*xx[36:])*2/n),
                bass_chroma_cos=float(np.mean(np.sum(z['bass'][:,i:i+n]*bass,axis=0))),onset_corr=corr)


def summary(z,a,b):
    ix=(z['t']>=a)&(z['t']<b)
    c=z['cqt'][:,ix];midis=np.arange(36,108)
    weights=c.sum(axis=1);pitch_center=float(np.sum(weights*midis)/max(weights.sum(),EPS))
    bass=z['bass'][:,ix].mean(axis=1);up=z['upchroma'][:,ix].mean(axis=1)
    names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    return dict(rms_dbfs=float(20*np.log10(np.sqrt(np.mean(z['rms'][ix]**2))+EPS)),
                stereo_rms_dbfs=float(20*np.log10(np.sqrt(np.mean(z['stereo_rms'][ix]**2))+EPS)),
                centroid_hz=float(np.mean(z['centroid'][ix])),low_power_fraction=float(z['low'][ix].mean()),
                high_power_fraction=float(z['high'][ix].mean()),occupancy=float(z['occupancy'][ix].mean()),
                cqt_pitch_center=pitch_center,side_mid_median=float(np.median(z['side_mid'][ix])),
                bass_pc_top3='/'.join(names[i] for i in np.argsort(bass)[-3:][::-1]),
                upper_pc_top3='/'.join(names[i] for i in np.argsort(up)[-3:][::-1]))


def search(z,motif):
    a,b=motif['seed'];f=feature(z);q=f[:,round(a/DT):round(b/DT)]
    N=f.shape[1];best=np.full(N,-1.);length=np.zeros(N,dtype=int)
    # Run both mixed and octave-invariant searches. Neither establishes melody identity.
    bestc=np.full(N,-1.)
    for scale in [.90,.95,1.,1.05,1.10]:
        n=round(q.shape[1]*scale);qq=resample_feature(q,n)
        vals=sum(signal.correlate(f[k],qq[k],mode='valid',method='fft') for k in range(f.shape[0]))/n
        cv=sum(signal.correlate(f[k],qq[k],mode='valid',method='fft') for k in range(36,48))*2/n
        improve=vals>best[:len(vals)];best[:len(vals)][improve]=vals[improve];length[:len(vals)][improve]=n
        bestc[:len(cv)]=np.maximum(bestc[:len(cv)],cv)
    peaks,_=signal.find_peaks(best,distance=max(20,round((b-a)*.75/DT)))
    cpeaks,_=signal.find_peaks(bestc,distance=max(20,round((b-a)*.75/DT)))
    candidates=sorted(set(sorted(peaks,key=lambda x:best[x],reverse=True)[:25]+sorted(cpeaks,key=lambda x:bestc[x],reverse=True)[:15]))
    rows=[]
    for j in candidates:
        if abs(j*DT-a)<b-a:continue
        n=length[j]
        if n<=0 or np.mean(z['rms'][j:j+n])<.005:continue
        d=compare(z,a,j*DT,b-a,j*DT+n*DT)
        rows.append(dict(motif=motif['id'],seed_start_s=a,seed_end_s=b,start_s=round(j*DT,2),end_s=round((j+n)*DT,2),
                         duration_ratio=n/q.shape[1],**d))
    return sorted(rows,key=lambda x:x['dtw_score'],reverse=True)


def review(z,root):
    annot=json.loads((root/'annotations.json').read_text(encoding='utf-8'))
    allrows=[];occ=[];peaks=[]
    for motif in annot['motifs']:
        print('Review '+motif['id'],flush=True)
        rows=search(z,motif);allrows.extend(rows)
        print([(r['start_s'],round(r['dtw_score'],3),round(r['order_gain_over_shuffle95'],3)) for r in rows[:12]],flush=True)
        a,b=motif['seed']
        for item in motif.get('occurrences',[]):
            t,e=item['start'],item['end'];d=compare(z,a,t,b-a,e)
            occ.append(dict(motif=motif['id'],start_s=t,end_s=e,status=item['status'],auditory_verified=False,**d,**summary(z,t,e)))
        # Local comparisons show all selected occurrences; no inferred note labels.
        items=motif.get('occurrences',[])
        if items:
            fig,axs=plt.subplots(len(items),2,figsize=(13,2.2*len(items)),squeeze=False)
            for axsrow,item in zip(axs,items):
                t,e=item['start'],item['end'];i,j=round(t/DT),round(e/DT)
                c=z['cqt'][12:60,i:j]
                db=librosa.amplitude_to_db(c/np.maximum(c.max(axis=0,keepdims=True),EPS),ref=1.)
                axsrow[0].imshow(db,origin='lower',aspect='auto',extent=[0,e-t,47.5,95.5],vmin=-30,vmax=0,cmap='magma')
                axsrow[0].set(ylabel=f'{t:.1f}-{e:.1f}s\nMIDI bins',ylim=(48,84))
                axsrow[1].plot(z['t'][i:j]-t,20*np.log10(np.maximum(z['rms'][i:j],EPS)))
                axsrow[1].set(ylabel='RMS dBFS',ylim=(-50,-5),xlim=(0,e-t));axsrow[1].grid(alpha=.2)
            axs[-1,0].set(xlabel='Relative time (s)');axs[-1,1].set(xlabel='Relative time (s)')
            fig.suptitle(motif['id']+' candidate occurrences: CQT and energy (not transcription)')
            savefig(fig,f'local_{motif["id"]}.png')
    write_csv(root/'data'/'template_search.csv',allrows)
    write_csv(root/'data'/'motif_occurrences.csv',occ)
    sections=[]
    for s in annot['sections']:
        sections.append(dict(id=s['id'],start_s=s['start'],end_s=s['end'],**summary(z,s['start'],s['end'])))
    write_csv(root/'data'/'section_features.csv',sections)
    fig,ax=plt.subplots(figsize=(15,5))
    ids=[m['id'] for m in annot['motifs']]
    for row in occ:
        yy=ids.index(row['motif']);ax.broken_barh([(row['start_s'],row['end_s']-row['start_s'])],(yy-.3,.6),facecolor='#336a94' if row['status']=='strong_candidate' else '#c28b44')
    for s in annot['sections'][1:]:ax.axvline(s['start'],color='gray',alpha=.2,lw=.7)
    ax.set(yticks=range(len(ids)),yticklabels=ids,xlabel='Time (s)',title='Candidate motif timeline; blue=strong, amber=variant/seed; no auditory verification',xlim=(0,z['t'][-1]))
    ax.grid(axis='x',alpha=.2);savefig(fig,'06_motif_timeline.png')
    # 0.1s onset-envelope periodicity: no metrical interpretation is imposed.
    fig,ax=plt.subplots(figsize=(15,4))
    centered=z['onset']-ndimage.uniform_filter1d(z['onset'],size=160)
    tg=librosa.feature.tempogram(onset_envelope=centered,sr=10,hop_length=1,win_length=160)
    lags=np.arange(tg.shape[0]);valid=(lags>=2)&(lags<=20)
    ax.imshow(tg[valid],origin='upper',aspect='auto',extent=[0,z['t'][-1],20,2],cmap='magma')
    ax.set(xlabel='Time (s)',ylabel='Period (0.1s bins)',title='16s local centered-onset autocorrelation; period 9 ~ 67/min, 18 ~ 33/min; not a beat grid')
    savefig(fig,'07_onset_periodicity.png')
    # Dominant lag in larger form cycles (14.3s and 28.7s), distinct from tempo.
    windows=[(57.8,86.5,28.7),(146.,174.7,28.7),(285.7,314.4,28.7),(351.,366.3,8.),(285.7,314.4,6.),(300.,328.7,6.)]
    write_csv(root/'data'/'phrase_comparisons.csv',[dict(a_s=a,b_s=b,duration_s=n,**compare(z,a,b,n)) for a,b,n in windows])
    periodic=[]
    for a,b in [(22,115),(145.8,203.7),(208,252.5),(253,344),(348,374)]:
        v=z['onset'][round(a/DT):round(b/DT)];v=v-v.mean()
        ac=signal.correlate(v,v,mode='full')[len(v)-1:];pp,_=signal.find_peaks(ac[3:31]);pp=pp+3
        for rank,j in enumerate(sorted(pp,key=lambda j:ac[j],reverse=True)[:4],1):
            periodic.append(dict(start_s=a,end_s=b,rank=rank,period_s=j*DT,normalized_autocorrelation=float(ac[j]/ac[0])))
    write_csv(root/'data'/'onset_periodicity.csv',periodic)
    # Auditable transposition screen: octave-folded chroma shifted through 12 keys.
    # These scores alone are weak: one held chord can match after transposition.
    transposed=[]
    for motif in annot['motifs']:
        a,b=motif['seed'];q=z['upchroma'][:,round(a/DT):round(b/DT)];n=q.shape[1]
        for shift in range(1,12):
            qq=np.roll(q,shift,axis=0)
            v=sum(signal.correlate(z['upchroma'][k],qq[k],mode='valid',method='fft') for k in range(12))/n
            pp,_=signal.find_peaks(v,distance=n)
            for j in sorted(pp,key=lambda j:v[j],reverse=True)[:3]:
                if abs(j*DT-a)<b-a:continue
                x=z['upchroma'][:,j:j+n]
                rng=np.random.default_rng(20261021);blocks=np.array_split(np.arange(n),max(2,n//5))
                null=[float(np.sum(qq*x[:,np.concatenate([blocks[k] for k in rng.permutation(len(blocks))])])/n) for _ in range(200)]
                transposed.append(dict(motif=motif['id'],start_s=j*DT,end_s=(j+n)*DT,semitone_shift=shift,
                                       chroma_score=float(v[j]),order_gain_over_shuffle95=float(v[j]-np.percentile(null,95)),status='screen_only_not_confirmed'))
    write_csv(root/'data'/'transposition_screen.csv',transposed)
