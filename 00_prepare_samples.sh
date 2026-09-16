#!/bin/bash

set -e

BASE=$(pwd)

echo "===================================="
echo " Preparando estrutura do pipeline"
echo "===================================="

mkdir -p "$BASE/outputs"

for TYPE in samples controls
do

    echo
    echo "Procurando em fastq/$TYPE"

    for R1 in "$BASE"/fastq/"$TYPE"/*_R1_001.fastq.gz
    do
	FILENAME=$(basename "$R1")

	SAMPLE=$(echo "$FILENAME" | sed 's/_S[0-9]\+_L001_R1_001.fastq.gz//')

	R2=$(echo "$R1" | sed 's/_R1_001.fastq.gz/_R2_001.fastq.gz/')

        echo "Preparando $SAMPLE"

        mkdir -p "$BASE/outputs/$SAMPLE"

        mkdir -p "$BASE/outputs/$SAMPLE/1-fastp"
        mkdir -p "$BASE/outputs/$SAMPLE/2-kraken2"
        mkdir -p "$BASE/outputs/$SAMPLE/3-bowtie2"
        mkdir -p "$BASE/outputs/$SAMPLE/4-megahit"
        mkdir -p "$BASE/outputs/$SAMPLE/5-diamond"
        mkdir -p "$BASE/outputs/$SAMPLE/6-coverm"

    done

done

echo
echo "Estrutura criada com sucesso!"
