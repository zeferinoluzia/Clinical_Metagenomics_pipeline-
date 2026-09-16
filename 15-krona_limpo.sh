#!/bin/bash

set -e

BASE=$(pwd)

echo "============================================================"
echo "Krona limpo"
echo "============================================================"

python scripts/15-krona_limpo.py

echo ""

for SAMPLE_DIR in "$BASE"/outputs/*
do

    [ -d "$SAMPLE_DIR" ] || continue

    SAMPLE=$(basename "$SAMPLE_DIR")

    [ "${SAMPLE:0:3}" = "NTC" ] && continue

    INPUT="$SAMPLE_DIR/15-krona_limpo/krona_input.tsv"

    [ -f "$INPUT" ] || continue

    echo "Gerando Krona: $SAMPLE"

    ktImportTaxonomy \
        "$INPUT" \
        -o "$SAMPLE_DIR/15-krona_limpo/${SAMPLE}.krona_limpo.html"

done

echo ""
echo "Finalizado!"
