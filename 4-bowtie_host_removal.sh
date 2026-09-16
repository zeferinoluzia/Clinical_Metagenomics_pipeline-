#!/bin/bash

set -e

BASE=$(pwd)

for TYPE in samples controls
do

    echo ""
    echo "========== $TYPE =========="

    for CLEAN_R1 in "$BASE"/outputs/*/1-fastp/*.cleaned_R1.fq.gz
    do

        [ -f "$CLEAN_R1" ] || continue

        SAMPLE=$(basename "$CLEAN_R1" .cleaned_R1.fq.gz)

        OUT="$BASE/outputs/$SAMPLE/3-bowtie2"

        CLEAN_R2="$BASE/outputs/$SAMPLE/1-fastp/${SAMPLE}.cleaned_R2.fq.gz"

        echo ""
        echo "Processando: $SAMPLE"

        mkdir -p "$OUT"

        bowtie2 \
            --threads 4 \
			--very-sensitive-local \
            -x "$BASE/databases/bowtie2/index/hg38_index" \
            -1 "$CLEAN_R1" \
            -2 "$CLEAN_R2" \
            --un-conc-gz "$OUT/un-conc" \
            -S "$OUT/${SAMPLE}.sam"
	mv "$OUT/un-conc.1" \
	   "$OUT/${SAMPLE}.un.R1.fq.gz"

	mv "$OUT/un-conc.2" \
	   "$OUT/${SAMPLE}.un.R2.fq.gz"

        samtools sort \
            "$OUT/${SAMPLE}.sam" \
            -o "$OUT/${SAMPLE}_sorted.bam"

        samtools index \
            "$OUT/${SAMPLE}_sorted.bam"

        samtools view \
            -b \
            -f 4 \
            "$OUT/${SAMPLE}_sorted.bam" \
            > "$OUT/${SAMPLE}_sorted_unmapped.bam"

        samtools view \
            -b \
            -q 1 \
            -F 4 \
            "$OUT/${SAMPLE}_sorted.bam" \
            > "$OUT/${SAMPLE}_sorted_mapped.bam"

        samtools fastq \
            -@ 4 \
            "$OUT/${SAMPLE}_sorted_mapped.bam" \
            -1 "$OUT/${SAMPLE}_R1.host_mapped.fastq.gz" \
            -2 "$OUT/${SAMPLE}_R2.host_mapped.fastq.gz"

        samtools fastq \
            -@ 4 \
            "$OUT/${SAMPLE}_sorted_unmapped.bam" \
            -1 "$OUT/${SAMPLE}_R1.host_unmapped.fastq.gz" \
            -2 "$OUT/${SAMPLE}_R2.host_unmapped.fastq.gz"

        seqkit stats \
            -T \
            -o "$OUT/${SAMPLE}.stats.host.tsv" \
            "$OUT/${SAMPLE}_R1.host_mapped.fastq.gz"

        seqkit stats \
            -T \
            -o "$OUT/${SAMPLE}.stats.nonhosts.tsv" \
            "$OUT/${SAMPLE}_R1.host_unmapped.fastq.gz"

    done

done

echo ""
echo "Bowtie2 finalizado!"
