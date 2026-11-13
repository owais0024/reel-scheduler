import json, subprocess, sys
tim=json.load(open("timing.json")); D=tim["total"]; out=sys.argv[1]
starts=[int(s["start"]*1000) for s in tim["segs"]][1:]
sh=lambda c: subprocess.run(c,shell=True,check=True)
sh(f'ffmpeg -loglevel error -y -f lavfi -i "sine=f=600:d=0.12" -af "asetrate=48000*1.0,aresample=48000,afade=t=out:st=0:d=0.12,volume=0.5" -ac 2 pop.wav')
sh(f'ffmpeg -loglevel error -y -f lavfi -i "sine=f=146.83:d={D}" -f lavfi -i "sine=f=220:d={D}" -f lavfi -i "sine=f=293.66:d={D}" -filter_complex "[0][1][2]amix=inputs=3,tremolo=f=0.2:d=0.3,lowpass=f=1000,volume=0.5,afade=t=in:d=2,afade=t=out:st={D-2.5}:d=2.5" -ar 48000 -ac 2 pad.wav')
n=len(starts); split="".join(f"[p{i}]" for i in range(n))
dl=";".join(f"[p{i}]adelay={ms}|{ms}[d{i}]" for i,ms in enumerate(starts))
mixin="".join(f"[d{i}]" for i in range(n))
fc=f"[0]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=pad_dur=5,loudnorm=I=-15:TP=-1.5:LRA=11[v];[1]volume=0.09[p];[2]asplit={n}{split};{dl};{mixin}amix=inputs={n}:normalize=0,volume=0.35[pops];[v][p][pops]amix=inputs=3:normalize=0[m]"
sh(f'ffmpeg -loglevel error -y -i vo.wav -i pad.wav -i pop.wav -filter_complex "{fc}" -map "[m]" -t {D} mix.wav')
sh(f'ffmpeg -loglevel error -y -i frames.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart {out}')
print("done")
