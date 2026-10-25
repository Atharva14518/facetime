import asyncio, json, subprocess, wave
from pathlib import Path
import numpy as np
import edge_tts

ROOT = Path(__file__).resolve().parent
SCENES = json.loads((ROOT / 'storyboard.json').read_text())
AUDIO = ROOT / 'audio'
AUDIO.mkdir(exist_ok=True)
SR = 48000

def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

async def voice(scene):
    target = AUDIO / (scene['id'] + '.mp3')
    meta = AUDIO / (scene['id'] + '.json')
    if target.exists() and meta.exists():
        return
    for attempt in range(3):
        try:
            words = []
            communicate = edge_tts.Communicate(scene['voice'], 'en-US-AndrewNeural', rate='-3%', boundary='WordBoundary')
            with target.open('wb') as f:
                async for chunk in communicate.stream():
                    if chunk['type'] == 'audio':
                        f.write(chunk['data'])
                    elif chunk['type'] == 'WordBoundary':
                        words.append({'text':chunk['text'], 'start':chunk['offset']/1e7, 'duration':chunk['duration']/1e7})
            meta.write_text(json.dumps(words))
            print('Narration ready:',scene['id'],flush=True)
            return
        except Exception:
            if attempt == 2: raise
            await asyncio.sleep(1)

async def main():
    # Two speech requests at once; each section is spoken as a paragraph for natural phrasing.
    for i in range(0,len(SCENES),2):
        await asyncio.gather(*(voice(s) for s in SCENES[i:i+2]))
    all_words=[]
    voice_track=np.zeros(SR*210,dtype=np.float32)
    for s in SCENES:
        file=AUDIO/(s['id']+'.mp3')
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(file)]))
        speed=max(1,duration/(s['duration']-.85))
        wav=AUDIO/(s['id']+'.wav')
        run(['ffmpeg','-y','-loglevel','error','-i',str(file),'-af',f'atempo={speed},afade=t=in:d=0.025,afade=t=out:st={max(0,duration/speed-.06)}:d=0.06','-ar',str(SR),'-ac','1',str(wav)])
        with wave.open(str(wav)) as f: pcm=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(np.float32)/32768
        start=round((s['start']+.35)*SR)
        voice_track[start:start+len(pcm)]+=pcm[:len(voice_track)-start]
        for w in json.loads((AUDIO/(s['id']+'.json')).read_text()):
            all_words.append({'text':w['text'],'start':s['start']+.35+w['start']/speed,'end':s['start']+.35+(w['start']+w['duration'])/speed,'scene':s['id']})
    (ROOT/'words.json').write_text(json.dumps(all_words,indent=2))
    def writewav(path,data):
        with wave.open(str(path),'wb') as f:
            f.setnchannels(1 if data.ndim==1 else data.shape[1]); f.setsampwidth(2); f.setframerate(SR)
            f.writeframes((np.clip(data,-1,1)*32767).astype('<i2').tobytes())
    writewav(AUDIO/'narration.wav',voice_track)
    # Original ambient score: four warm suspended chords, sparse plucks and a quiet pulse at 96 BPM.
    n=SR*210
    music=np.zeros((n,2),dtype=np.float32)
    chords=[[146.832,220,277.183,329.628],[130.813,195.998,246.942,293.665],[110,164.814,220,261.626],[123.471,184.997,246.942,293.665]]
    rng=np.random.default_rng(41)
    for j,start in enumerate(np.arange(0,210,10)):
        length=min(12,210-start); tt=np.arange(int(length*SR))/SR
        env=np.minimum(tt/1.8,1)*np.minimum((length-tt)/2.5,1)
        for k,freq in enumerate(chords[j%4]):
            for ch in range(2):
                detune=1+(-1 if ch==0 else 1)*.0009
                tone=np.sin(2*np.pi*freq*detune*tt+k*.6)+.15*np.sin(2*np.pi*freq*2*tt)
                pos=int(start*SR); music[pos:pos+len(tt),ch]+=tone*env*.008
    for j,start in enumerate(np.arange(15,195,1.25)):
        length=.7; tt=np.arange(int(length*SR))/SR
        freq=chords[int(start//10)%4][j%4]*2
        pluck=(np.sin(2*np.pi*freq*tt)+.14*np.sin(2*np.pi*freq*3*tt))*np.exp(-tt*7)*np.minimum(tt/.006,1)
        pos=int(start*SR)
        music[pos:pos+len(tt),j%2]+=pluck*.014
        music[pos:pos+len(tt),1-j%2]+=pluck*.008
    for start in [8,15,30,45,53,60,75,90,105,120,135,150,165,185,195]:
        tt=np.arange(int(.28*SR))/SR
        # Soft filtered breath as a transition, kept well below narration.
        noise=rng.normal(0,1,len(tt)); noise=np.convolve(noise,np.ones(17)/17,mode='same')
        whoosh=noise*np.sin(np.pi*tt/.28)**2*.025
        pos=int((start-.18)*SR)
        music[pos:pos+len(tt),:]+=whoosh[:,None]
        tickt=np.arange(int(.18*SR))/SR
        tick=np.sin(2*np.pi*740*tickt)*np.exp(-tickt*35)*.021
        pos=int((start+.5)*SR);music[pos:pos+len(tickt),:]+=tick[:,None]
    # Gentle ducking linked to speech presence, with 250 ms smoothing.
    envelope=np.repeat(np.max(np.abs(voice_track[:(n//480)*480].reshape(-1,480)),axis=1),480)
    speech=(envelope>.015).astype(np.float32)
    smooth=np.convolve(speech[::480],np.ones(25)/25,mode='same')
    duck=np.repeat(1-.6*smooth,480)[:n]
    music*=duck[:,None]
    fade=np.minimum(np.arange(n)/SR/2,1)*np.minimum((n-np.arange(n))/SR/3,1)
    music*=fade[:,None]
    writewav(AUDIO/'music-and-sfx.wav',music)
    mix=music+voice_track[:,None]*.86
    writewav(AUDIO/'mix-raw.wav',mix)
    run(['ffmpeg','-y','-loglevel','error','-i',str(AUDIO/'mix-raw.wav'),'-af','loudnorm=I=-14:TP=-1:LRA=7','-ar',str(SR),str(AUDIO/'mix.wav')])
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    lines=[]
    for i in range(0,len(all_words),6):
        group=all_words[i:i+6]
        lines.append(f'{len(lines)+1}\n{stamp(group[0]["start"])} --> {stamp(group[-1]["end"])}\n'+ ' '.join(w['text'] for w in group)+'\n')
    (ROOT/'Facetime-captions.srt').write_text('\n'.join(lines))
    print('Audio mix and word timestamps complete.',flush=True)

asyncio.run(main())
