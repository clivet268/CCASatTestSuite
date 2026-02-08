#find kernelmodules -type d -exec "cd {} && make" +
for f in kernelmodules/*; do
  if [ -d "$f" ]; then
     (cd "$f"; make clean; make) &
  fi
done
