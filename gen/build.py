import json, sys, os, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k=Kokoro("../tts/kokoro-v1.0.onnx","../tts/voices-v1.0.bin"); SR=24000
FIX={"Allah":"ɑlˈɑː","Musa":"mˈuːsɑː","rizq":"ɹˈɪzk","taqwa":"tˈɑːkwɑː","tawakkul":"tɑːwˈækkʊl","barakah":"bˈɑːɹəkə","wudu":"wʊdˈuː"}
def ph(text):
    out=[]
    for w in text.split(" "):
        core=w.strip(".,:;!?'\"")
        if core in FIX: out.append(w.replace(core,"\x00"+core+"\x00"))
        else: out.append(w)
    parts=" ".join(out).split("\x00"); res=[]
    for p in parts:
        if p in FIX: res.append(FIX[p])
        elif p.strip(" .,:;!?"): res.append(k.tokenizer.phonemize(p.strip(),"en-us"))
    return " ".join(res)
def trim(a,th=0.01):
    i=np.where(np.abs(a)>th)[0]; return a[max(0,i[0]-120):i[-1]+120] if len(i) else a
name=sys.argv[1]; spec=json.load(open(f"{name}.json")); os.makedirs(name,exist_ok=True)
audio=[np.zeros(int(SR*0.1))]; t=0.1; segs=[]
for s in spec["segs"]:
    a,_=k.create(ph(s.get("say",s["text"])),voice="am_michael",speed=s.get("speed",1.0),lang="en-us",is_phonemes=True); a=trim(a)
    d=len(a)/SR; seg=dict(s); seg["start"]=round(t,3); seg["end"]=round(t+d,3); segs.append(seg)
    gap=0.55 if s.get("quote") else 0.3; audio+= [a,np.zeros(int(SR*gap))]; t+=d+gap
tot=round(t+0.6,3); sf.write(f"{name}/vo.wav",np.concatenate(audio+[np.zeros(int(SR*0.6))]),SR)
json.dump({"segs":segs,"total":tot},open(f"{name}/timing.json","w"),indent=1)
for f in ["anim.html"]: subprocess.run(["cp",f,f"{name}/{f}"])
subprocess.run(["sed","-i","s#\\.\\./fonts#../../fonts#g",f"{name}/anim.html"])
for f in ["render.py","mix.py"]: subprocess.run(["cp",f"../day3/{f}",f"{name}/"])
print(name,"duration",tot)
