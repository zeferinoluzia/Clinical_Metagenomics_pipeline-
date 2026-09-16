#!/usr/bin/env python3

import os
import sys
import glob
import pandas as pd

# Adiciona a raiz do projeto ao PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from utils.taxonomy_utils import (
    get_taxids_from_blast_file,
    get_taxonomy_from_taxid,
    create_krona_file
)

from utils.constants import BLAST_COLUMNS

BASE = os.getcwd()
OUTPUTS = os.path.join(BASE, "outputs")

print("=" * 60)
print("Gerando arquivos de taxonomia")
print("=" * 60)

samples = sorted(
    [
        d
        for d in glob.glob(os.path.join(OUTPUTS, "*"))
        if os.path.isdir(d)
    ]
)
processed = 0
skipped = 0

for sample_dir in samples:

    sample = os.path.basename(sample_dir)

    diamond_dir = os.path.join(sample_dir, "6-diamond")

    diamond_file = os.path.join(
        diamond_dir,
        f"{sample}.diamond_blastx.txt"
    )

    if not os.path.exists(diamond_file):
        print(f"[SKIP] DIAMOND não encontrado: {sample}")
        skipped += 1
        continue

    if os.path.getsize(diamond_file) == 0:
        print(f"[SKIP] DIAMOND vazio: {sample}")
        skipped += 1
        continue

    reports_dir = os.path.join(sample_dir, "7-reports")
    krona_dir = os.path.join(reports_dir, "krona")
    tables_dir = os.path.join(reports_dir, "tables")
    figures_dir = os.path.join(reports_dir, "figures")
    excel_dir = os.path.join(reports_dir, "excel")

    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(krona_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(excel_dir, exist_ok=True)

    print(f"Processando: {sample}")

    try:

        df = pd.read_csv(
            diamond_file,
            sep="\t",
            header=None,
            names=BLAST_COLUMNS
        )

        taxids_detected = get_taxids_from_blast_file(df)

        create_krona_file(
            taxids_detected,
            krona_dir
        )

        taxonomy_rows = []

        for qseqid, taxid in taxids_detected:

            taxonomy = get_taxonomy_from_taxid(taxid)

            taxonomy_rows.append({

                "qseqid": qseqid,
                "taxid": taxid,
                "superkingdom": taxonomy["superkingdom"],
                "phylum": taxonomy["phylum"],
                "class": taxonomy["class"],
                "order": taxonomy["order"],
                "family": taxonomy["family"],
                "genus": taxonomy["genus"],
                "species": taxonomy["species"]

            })

        taxonomy_df = pd.DataFrame(taxonomy_rows)

        taxonomy_df.to_csv(

            os.path.join(
                diamond_dir,
                "blast_results_taxonomy.csv"
            ),

            index=False

        )

        print(f"✓ {sample}")

        processed += 1

    except Exception as e:

        print(f"[ERRO] {sample}: {e}")

print()

print("=" * 60)
print("Resumo")
print("=" * 60)

print(f"Amostras processadas : {processed}")
print(f"Ignoradas            : {skipped}")

print()

print("Arquivos gerados:")

print("""
6-diamond/
    blast_results_taxonomy.csv

7-reports/
    krona/krona_input.tsv
""")
