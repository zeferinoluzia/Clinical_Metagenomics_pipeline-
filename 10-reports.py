#!/usr/bin/env python3

import os
import glob
import pandas as pd

BASE = os.getcwd()
OUTPUTS = os.path.join(BASE, "outputs")

print("="*60)
print("Gerando relatórios")
print("="*60)

processed = 0
skipped = 0

samples = sorted(
    d for d in glob.glob(os.path.join(OUTPUTS, "*"))
    if os.path.isdir(d)
)

for sample_dir in samples:

    sample = os.path.basename(sample_dir)

    print(f"Processando: {sample}")

    coverm_csv = os.path.join(
        sample_dir,
        "5-coverm",
        f"{sample}_reads_count.csv"
    )

    taxonomy_csv = os.path.join(
        sample_dir,
        "6-diamond",
        "blast_results_taxonomy.csv"
    )

    if not os.path.exists(coverm_csv):
        print("  CoverM summary inexistente.")
        skipped += 1
        continue

    if not os.path.exists(taxonomy_csv):
        print("  Taxonomia inexistente.")
        skipped += 1
        continue

    reports_dir = os.path.join(sample_dir, "7-reports")

    tables_dir = os.path.join(reports_dir, "tables")
    excel_dir = os.path.join(reports_dir, "excel")

    os.makedirs(tables_dir, exist_ok=True)
    os.makedirs(excel_dir, exist_ok=True)

    try:

        df_reads = pd.read_csv(coverm_csv)

        df_tax = pd.read_csv(taxonomy_csv)

        df = df_reads.merge(
            df_tax,
            left_on="Contig",
            right_on="qseqid",
            how="left"
        )

        reads_taxonomy = os.path.join(
            tables_dir,
            "reads_taxonomy.csv"
        )

        df.to_csv(
            reads_taxonomy,
            index=False
        )

        species = (
            df
            .groupby(
                ["superkingdom","species"],
                dropna=False,
                as_index=False
            )
            .agg(
                mean_rpkm=("RPKM","mean"),
                std_rpkm=("RPKM","std"),
                total_rpkm=("RPKM","sum"),
                max_rpkm=("RPKM","max"),
                contig_count=("Contig","count"),
                total_reads=("Read_Count","sum")
            )
            .sort_values(
                "total_rpkm",
                ascending=False
            )
        )

        species.to_csv(
            os.path.join(
                tables_dir,
                "species_summary.csv"
            ),
            index=False
        )

        species.head(25).to_csv(
            os.path.join(
                tables_dir,
                "top_species.csv"
            ),
            index=False
        )

        excel = os.path.join(
            excel_dir,
            "report.xlsx"
        )

        with pd.ExcelWriter(
            excel,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="reads_taxonomy",
                index=False
            )

            species.to_excel(
                writer,
                sheet_name="species_summary",
                index=False
            )

            species.head(25).to_excel(
                writer,
                sheet_name="top_species",
                index=False
            )

        print("  ✓")

        processed += 1

    except Exception as e:

        print(e)

print()

print("="*60)
print("Resumo")
print("="*60)

print(f"Processados : {processed}")
print(f"Ignorados   : {skipped}")

print()

print("Arquivos gerados:")

print("""
7-reports/

    tables/

        reads_taxonomy.csv

        species_summary.csv

        top_species.csv

    excel/

        report.xlsx
""")
