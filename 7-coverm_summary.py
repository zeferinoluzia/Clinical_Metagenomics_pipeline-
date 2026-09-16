#!/usr/bin/env python3

from pathlib import Path
import pandas as pd

BASE = Path.cwd()
OUTPUTS = BASE / "outputs"

print("=" * 60)
print("Gerando resumo do CoverM")
print("=" * 60)

for sample_dir in sorted(OUTPUTS.iterdir()):

    if not sample_dir.is_dir():
        continue

    sample = sample_dir.name

    coverm_dir = sample_dir / "5-coverm"
    bowtie_dir = sample_dir / "3-bowtie2"

    coverm_file = coverm_dir / f"{sample}_reads_count.tsv"
    stats_file = bowtie_dir / f"{sample}.stats.nonhosts.tsv"
    output_csv = coverm_dir / f"{sample}_reads_count.csv"

    # verifica existência
    if not coverm_file.exists():
        print(f"[SKIP] CoverM não encontrado: {sample}")
        continue

    if not stats_file.exists():
        print(f"[SKIP] Stats não encontrado: {sample}")
        continue

    # verifica arquivo vazio
    if coverm_file.stat().st_size == 0:
        print(f"[SKIP] CoverM vazio: {sample}")
        continue

    if stats_file.stat().st_size == 0:
        print(f"[SKIP] Stats vazio: {sample}")
        continue

    print(f"Processando: {sample}")

    try:
        df_coverm = pd.read_csv(coverm_file, sep="\t")
        df_reads = pd.read_csv(stats_file, sep="\t")

    except pd.errors.EmptyDataError:
        print(f"[SKIP] Arquivo vazio: {sample}")
        continue

    # renomear colunas exatamente como no notebook
    rename_dict = {}

    for column in df_coverm.columns[1:]:
        rename_dict[column] = "_".join(column.split()[1:])

    df_coverm.rename(columns=rename_dict, inplace=True)

    # mesmo cálculo do notebook
    total_reads = int(df_reads.loc[0, "num_seqs"]) * 2

    df_coverm["Total_Reads"] = total_reads

    df_coverm["Composition"] = (
        df_coverm["Read_Count"] /
        df_coverm["Total_Reads"]
    ) * 100

    df_coverm.to_csv(output_csv, index=False)

    print(f"✓ {sample}")

print("\nResumo finalizado!")
