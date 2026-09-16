#!/bin/bash

set -e

BASE=$(pwd)
OUTPUTS="$BASE/outputs"
RESULTS="$OUTPUTS/results"

echo "============================================================"
echo "Exportando resultados"
echo "============================================================"

mkdir -p "$RESULTS"/{coverm,diamond,megahit,tables,figures,comparison,excel,krona}

for SAMPLE_DIR in "$OUTPUTS"/*
do

    [ -d "$SAMPLE_DIR" ] || continue

    SAMPLE=$(basename "$SAMPLE_DIR")

    # ignora a própria pasta results
    [ "$SAMPLE" = "results" ] && continue

    echo "Exportando: $SAMPLE"

    ########################################
    # COVERM
    ########################################

    FILE="$SAMPLE_DIR/6-coverm/${SAMPLE}_reads_count.tsv"

    [ -f "$FILE" ] && \
    cp "$FILE" \
    "$RESULTS/coverm/${SAMPLE}_reads_count.tsv"

    ########################################
    # DIAMOND
    ########################################

    FILE="$SAMPLE_DIR/6-diamond/blast_results_taxonomy.csv"

    [ -f "$FILE" ] && \
    cp "$FILE" \
    "$RESULTS/diamond/${SAMPLE}_blast_results_taxonomy.csv"

    ########################################
    # MEGAHIT
    ########################################

    FILE="$SAMPLE_DIR/4-megahit/$SAMPLE/final.contigs.fa"

    [ -f "$FILE" ] && \
    cp "$FILE" \
    "$RESULTS/megahit/${SAMPLE}_final.contigs.fa"

    ########################################
    # TABLES
    ########################################

    for f in reads_taxonomy.csv species_summary.csv top_species.csv
    do

        FILE="$SAMPLE_DIR/7-reports/tables/$f"

        [ -f "$FILE" ] && \
        cp "$FILE" \
        "$RESULTS/tables/${SAMPLE}_${f}"

    done

    ########################################
    # FIGURES
    ########################################

    for f in heatmap_species.html species_barplot.html
    do

        FILE="$SAMPLE_DIR/7-reports/figures/$f"

        [ -f "$FILE" ] && \
        cp "$FILE" \
        "$RESULTS/figures/${SAMPLE}_${f}"

    done

    ########################################
    # COMPARISON
    ########################################

    for f in comparison_table.csv heatmap_vs_control.html barplot_vs_control.html
    do

        FILE="$SAMPLE_DIR/7-reports/comparison/$f"

        [ -f "$FILE" ] && \
        cp "$FILE" \
        "$RESULTS/comparison/${SAMPLE}_${f}"

    done

    ########################################
    # EXCEL
    ########################################

    FILE="$SAMPLE_DIR/7-reports/excel/report.xlsx"

    [ -f "$FILE" ] && \
    cp "$FILE" \
    "$RESULTS/excel/${SAMPLE}_report.xlsx"

    ########################################
    # KRONA
    ########################################

    FILE="$SAMPLE_DIR/9-krona/${SAMPLE}.krona_report.html"

    [ -f "$FILE" ] && \
    cp "$FILE" \
    "$RESULTS/krona/${SAMPLE}.krona_report.html"

done

echo
echo "============================================================"
echo "Exportação concluída!"
echo "============================================================"

echo
echo "Arquivos disponíveis em:"
echo
echo "$RESULTS"
