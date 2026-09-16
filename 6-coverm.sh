#!/bin/bash

set -e

BASE=$(pwd)

for CLEAN_R1 in "$BASE"/outputs/*/1-fastp/*.cleaned_R1.fq.gz
do
    [ -f "$CLEAN_R1" ] || continue

    SAMPLE=$(basename "$CLEAN_R1" .cleaned_R1.fq.gz)

    CLEAN_R2="$BASE/outputs/$SAMPLE/1-fastp/${SAMPLE}.cleaned_R2.fq.gz"

    CONTIGS="$BASE/outputs/$SAMPLE/4-megahit/$SAMPLE/final.contigs.fa"

    OUT="$BASE/outputs/$SAMPLE/5-coverm"

    mkdir -p "$OUT"

    coverm contig \
        --coupled "$CLEAN_R1" "$CLEAN_R2" \
        --reference "$CONTIGS" \
        -m covered_fraction count reads_per_base mean rpkm tpm \
        -o "$OUT/${SAMPLE}_reads_count.tsv" \
        --bam-file-cache-directory "$OUT/bam_files"

done

echo ""
echo "CoverM finalizado!"
