#!/bin/bash

set -e

BASE=$(pwd)

for TYPE in samples controls
do

    echo ""
    echo "========== $TYPE =========="

    for R1 in "$BASE"/fastq/"$TYPE"/*_R1_001.fastq.gz
    do

        [ -f "$R1" ] || continue

        FILENAME=$(basename "$R1")
        SAMPLE=${FILENAME%%_S*_L001_R1_001.fastq.gz}

        echo ""
        echo "Processando: $SAMPLE"

        CLEAN_R1="$BASE/outputs/$SAMPLE/1-fastp/${SAMPLE}.cleaned_R1.fq.gz"
        CLEAN_R2="$BASE/outputs/$SAMPLE/1-fastp/${SAMPLE}.cleaned_R2.fq.gz"

        OUT="$BASE/outputs/$SAMPLE/2-kraken2"

        # Garante que a pasta de saída para a amostra existe
        mkdir -p "$OUT"

        kraken2 \
            --db "$BASE/databases/kraken2_pluspf_full" \
            --threads 16 \
            --paired \
            "$CLEAN_R1" \
            "$CLEAN_R2" \
            --report "$OUT/${SAMPLE}.kraken_report" \
            --output "$OUT/${SAMPLE}.kraken"

        kreport2krona.py \
            -r "$OUT/${SAMPLE}.kraken_report" \
            -o "$OUT/${SAMPLE}.input.krona"

    done
done

echo ""
echo "Kraken2 finalizado!"
