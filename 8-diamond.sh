#!/bin/bash

set -e

BASE=$(pwd)

echo "======================================="
echo "          DIAMOND BLASTX"
echo "======================================="

for CONTIGS in "$BASE"/outputs/*/4-megahit/*/final.contigs.fa
do
    [ -f "$CONTIGS" ] || continue

    SAMPLE=$(basename "$(dirname "$CONTIGS")")

    OUT="$BASE/outputs/$SAMPLE/6-diamond"

    mkdir -p "$OUT"

    echo ""
    echo "======================================="
    echo "Processando: $SAMPLE"
    echo "======================================="

    diamond blastx \
        --query "$CONTIGS" \
        --db "$BASE/databases/diamond_refseq_microbe/protein_db_robust.dmnd" \
        --out "$OUT/${SAMPLE}.diamond_blastx.txt" \
        --outfmt 6 \
        qseqid qlen sseqid slen pident length mismatch \
        gapopen qstart qend sstart send evalue bitscore \
        staxids sscinames sskingdoms stitle salltitles \
        nident qcovhsp \
        --evalue 0.001 \
        --threads 16 \
        --more-sensitive

done

echo ""
echo "======================================="
echo "DIAMOND finalizado!"
echo "======================================="
