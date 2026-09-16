#!/bin/bash

set -e

BASE=$(pwd)

for TYPE in samples controls
do

    echo ""
    echo "========== $TYPE =========="

	for R1 in "$BASE"/fastq/"$TYPE"/*_R1_001.fastq.gz
do

    FILENAME=$(basename "$R1")

    SAMPLE=$(echo "$FILENAME" | sed 's/_S[0-9]\+_L001_R1_001.fastq.gz//')

    R2=$(echo "$R1" | sed 's/_R1_001.fastq.gz/_R2_001.fastq.gz/')

    OUT="$BASE/outputs/$SAMPLE/1-fastp"

    echo ""
    echo "Processando: $SAMPLE"

    fastp \
        -i "$R1" \
        -I "$R2" \
        -w 4 \
        -o "$OUT/${SAMPLE}.cleaned_R1.fq.gz" \
        -O "$OUT/${SAMPLE}.cleaned_R2.fq.gz" \
        -h "$OUT/${SAMPLE}.fastp.html" \
        -j "$OUT/${SAMPLE}.fastp.json" \
        --cut_front \
        --qualified_quality_phred 30

done

    done



echo ""
echo "Fastp finalizado!"
