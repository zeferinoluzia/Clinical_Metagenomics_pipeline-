#!/bin/bash

set -e

BASE=$(pwd)

echo "============================================================"
echo "Gerando relatórios Krona"
echo "============================================================"

############################################################
# Atualiza banco taxonômico
############################################################

ktUpdateTaxonomy.sh

echo ""

processed=0
skipped=0

############################################################
# Processa todas as amostras
############################################################

for SAMPLE_DIR in "$BASE"/outputs/*
do

    [ -d "$SAMPLE_DIR" ] || continue

    SAMPLE=$(basename "$SAMPLE_DIR")

    ########################################################

    INPUT="$SAMPLE_DIR/7-reports/krona/krona_input.tsv"

    ########################################################

    if [ ! -f "$INPUT" ]; then

        echo "[SKIP] $SAMPLE (krona_input.tsv inexistente)"

        skipped=$((skipped+1))

        continue

    fi

    if [ ! -s "$INPUT" ]; then

        echo "[SKIP] $SAMPLE (krona_input.tsv vazio)"

        skipped=$((skipped+1))

        continue

    fi

    ########################################################

    OUTDIR="$SAMPLE_DIR/9-krona"

    mkdir -p "$OUTDIR"

    cp "$INPUT" "$OUTDIR/krona_input.tsv"

    ########################################################

    echo "Processando: $SAMPLE"

    ktImportTaxonomy \
        "$OUTDIR/krona_input.tsv" \
        -o "$OUTDIR/${SAMPLE}.krona_report.html"

    echo "✓"

    processed=$((processed+1))

done

echo ""
echo "============================================================"
echo "Resumo"
echo "============================================================"

echo "Processados : $processed"
echo "Ignorados   : $skipped"

echo ""

echo "Arquivos gerados"

cat << EOF

9-krona/

    krona_input.tsv

    SAMPLE.krona_report.html

EOF
