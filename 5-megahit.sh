#!/bin/bash

set -e

BASE=$(pwd)

for UN_R1 in "$BASE"/outputs/*/3-bowtie2/*.un.R1.fq.gz
do
    [ -f "$UN_R1" ] || continue

    SAMPLE=$(basename "$UN_R1" .un.R1.fq.gz)

    UN_R2="$BASE/outputs/$SAMPLE/3-bowtie2/${SAMPLE}.un.R2.fq.gz"

    OUT="$BASE/outputs/$SAMPLE/4-megahit"

    mkdir -p "$OUT"

    echo ""
    echo "=============================="
    echo "MEGAHIT -> $SAMPLE"
    echo "=============================="

    megahit \
        -1 "$UN_R1" \
        -2 "$UN_R2" \
        -o "$OUT/$SAMPLE" \
        -m 0.95 \
        -t 4

done

echo ""
echo "MEGAHIT finalizado!"
