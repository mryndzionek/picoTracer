#!/bin/sh

if [ "$#" -ne 1 ] || ! [ -d "$1" ]; then
    echo "Usage: $0 IMG_DIRECTORY" >&2
    exit 1
fi

rm $1/*.svg
rm $1/*.png

for image in `ls $1`; do
    a2s -i$1/$image -o$1/${image%.*}.svg && \
    rasterizer -d $1 $1/${image%.*}.svg
done
