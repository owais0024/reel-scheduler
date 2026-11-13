# Reel video template (flat vector style)

Used for @edits.by.owais reels (Day 2 and Day 3). 1080x1920, 30 fps.

Pipeline:
1. Voiceover: kokoro-onnx (pip install kokoro-onnx soundfile), model files kokoro-v1.0.onnx and voices-v1.0.bin from the kokoro-onnx GitHub releases. Voice am_michael. Arabic names use IPA phoneme overrides with is_phonemes=True:
   Madinah mədˈiːnə, Abdur Rahman ibn Awf ˈæbdʊɹ ɹɑːmˈɑːn ˈɪbn ˈaʊf, Sa'd sˈɑːʕd, barakah bˈɑːɹəkə, Allah ɑlˈɑː (allah.py has an experimental final-h version).
2. timing.json: per-line start/end times from the voiceover, used by scenes.js.
3. anim.html + scenes.js: canvas animation (purple/teal/magenta, googly-eyed icons, pill labels, scene change every 2 to 4 s, small captions). No figures of the Prophet or companions.
4. render.py: Playwright steps the canvas frame by frame and pipes frames into ffmpeg.
5. mix.py: voiceover + pad + pops. Keep apad before loudnorm or the last words get cut:
   [0]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=pad_dur=5,loudnorm=I=-15:TP=-1.5:LRA=11[v]

Content rules: English only. Quran from Quran.com (Clear Quran) and hadith from Sunnah.com, exact translations with references. Verify every reference.
