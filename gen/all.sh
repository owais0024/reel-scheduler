set -e
until [ -f money/timing.json ]; do sleep 3; done
mkdir -p /home/claude/videos/batch2
for n in rizq firon lust fame money; do
  cp anim.html $n/anim.html; sed -i 's#\.\./fonts#../../fonts#g' $n/anim.html
  (cd $n && python3 render.py && python3 mix.py /home/claude/videos/batch2/$n.mp4)
  echo "$n done"
done
