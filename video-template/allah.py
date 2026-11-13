import numpy as np
from scipy.signal import butter, sosfilt
from kokoro_onnx import Kokoro
k=Kokoro("../tts/kokoro-v1.0.onnx","../tts/voices-v1.0.bin")
SR=24000
def trim(a,th=0.01):
    idx=np.where(np.abs(a)>th)[0]
    return a[max(0,idx[0]-120):idx[-1]+120] if len(idx) else a
def hbreath(ref,ms=150):
    n=int(SR*ms/1000); rng=np.random.default_rng(7)
    noise=sosfilt(butter(2,[400,3200],'bp',fs=SR,output='sos'),rng.standard_normal(n))
    env=np.linspace(1,0,n)**1.6; env[:int(n*0.12)]*=np.linspace(0.3,1,int(n*0.12))
    h=noise*env; rms=np.sqrt(np.mean(ref[-int(SR*0.12):]**2))
    return h/np.sqrt(np.mean(h**2)+1e-12)*rms*0.32
def allah():
    a,_=k.create("ʔɐlˈlɒː",voice="am_michael",speed=0.92,lang="en-us",is_phonemes=True)
    a=trim(a); return np.concatenate([a,hbreath(a)])
FIX=[("bˈæɹækə","bˈɑːɹəkə")]
def ph(t):
    p=k.tokenizer.phonemize(t,"en-us")
    for x,y in FIX:p=p.replace(x,y)
    return p
def speak(text,speed=0.95):
    """text with {A} for Allah. Returns audio."""
    parts=text.split("{A}"); out=[]
    for i,p in enumerate(parts):
        if p.strip():
            a,_=k.create(ph(p.strip()),voice="am_michael",speed=speed,lang="en-us",is_phonemes=True)
            out.append(trim(a)); out.append(np.zeros(int(SR*0.04)))
        if i<len(parts)-1:
            out.append(allah()); out.append(np.zeros(int(SR*0.05)))
    return np.concatenate(out)
