#!/usr/bin/env python3

import os
import glob
import pandas as pd
import plotly.graph_objects as go

BASE = os.getcwd()
OUTPUTS = os.path.join(BASE, "outputs")

print("=" * 60)
print("Gerando gráficos")
print("=" * 60)

processed = 0
skipped = 0

samples = sorted(
    d for d in glob.glob(os.path.join(OUTPUTS, "*"))
    if os.path.isdir(d)
)

for sample_dir in samples:

    sample = os.path.basename(sample_dir)

    reports_dir = os.path.join(sample_dir, "7-reports")
    tables_dir = os.path.join(reports_dir, "tables")
    figures_dir = os.path.join(reports_dir, "figures")

    os.makedirs(figures_dir, exist_ok=True)

    reads_file = os.path.join(
        tables_dir,
        "reads_taxonomy.csv"
    )

    species_file = os.path.join(
        tables_dir,
        "species_summary.csv"
    )

    if not os.path.exists(reads_file):
        print(f"[SKIP] {sample} - reads_taxonomy.csv não encontrado")
        skipped += 1
        continue

    if not os.path.exists(species_file):
        print(f"[SKIP] {sample} - species_summary.csv não encontrado")
        skipped += 1
        continue

    print(f"Processando: {sample}")

    try:

        df_reads = pd.read_csv(reads_file)
        df_species = pd.read_csv(species_file)

        ###############################################################
        # HEATMAP
        ###############################################################

        top_species = (
            df_species
            .sort_values("total_rpkm", ascending=False)
            .head(30)["species"]
            .dropna()
            .tolist()
        )

        df_heat = df_reads[
            df_reads["species"].isin(top_species)
        ]

        if len(df_heat) > 0:

            heatmap = df_heat.pivot_table(
                index="Contig",
                columns="species",
                values="RPKM",
                aggfunc="sum",
                fill_value=0
            )

            fig = go.Figure(

                data=go.Heatmap(

                    z=heatmap.values,

                    x=heatmap.columns,

                    y=heatmap.index,

                    colorscale="Viridis",

                    hoverongaps=False

                )

            )

            fig.update_layout(

                title=f"{sample}<br>Contig × Species (RPKM)",

                xaxis_title="Species",

                yaxis_title="Contig",

                width=1100,

                height=700

            )

            fig.update_yaxes(visible=False)

            fig.write_html(

                os.path.join(

                    figures_dir,

                    "heatmap_species.html"

                )

            )

        ###############################################################
        # BARPLOT
        ###############################################################

        df_bar = (

            df_species

            .sort_values(

                "total_rpkm",

                ascending=False

            )

            .head(20)

            .copy()

        )

        df_bar["std_rpkm"] = (

            df_bar["std_rpkm"]

            .fillna(0)

        )

        bar = go.Figure()

        bar.add_trace(

            go.Bar(

                x=df_bar["species"],

                y=df_bar["total_rpkm"],

                text=df_bar["contig_count"],

                textposition="outside",

                error_y=dict(

                    type="data",

                    array=df_bar["std_rpkm"],

                    visible=True

                )

            )

        )

        bar.update_layout(

            title=f"{sample}<br>Total RPKM por espécie",

            xaxis_title="Species",

            yaxis_title="Total RPKM",

            width=1100,

            height=700

        )

        bar.update_xaxes(

            tickangle=45

        )

        bar.write_html(

            os.path.join(

                figures_dir,

                "species_barplot.html"

            )

        )

        processed += 1

        print("✓")

    except Exception as e:

        print(f"[ERRO] {sample}: {e}")

print()

print("=" * 60)
print("Resumo")
print("=" * 60)

print(f"Processados : {processed}")
print(f"Ignorados   : {skipped}")

print()

print(
"""
Arquivos gerados

7-reports/
    figures/

        heatmap_species.html

        species_barplot.html
"""
)
