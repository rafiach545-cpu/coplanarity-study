#!/bin/bash
# Memory watchdog (2026-10-18): every second, if MemAvailable < 700 MB, kill the largest F6_02_grid process (its lane restarts it; checkpoints keep
# all finished events). Protects WSL (8 GB) from the kernel OOM killer. Exits when no lane is running.
while pgrep -f "[F]6_highA_lane.sh" > /dev/null; do
  av=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
  if [ "$av" -lt 716800 ]; then
    p=$(ps -eo pid,rss,cmd --sort=-rss | awk '/[F]6_02_grid.py/{print $1; exit}')
    [ -n "$p" ] && kill "$p" && echo "$(date) MemAvailable ${av} kB -> killed pid $p"
    sleep 5
  fi
  sleep 1
done
echo "$(date) watchdog exit"
