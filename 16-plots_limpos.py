#!/usr/bin/env python3

import os
import glob
import pandas as pd
import plotly.graph_objects as go

BASE = os.getcwd()
OUTPUTS = os.path.join(BASE, "outputs")

print("=" * 60)
print("Gerando gráficos limpos")
print("=" * 60)

############################################################
# Descobrir espécies presentes nos controles
############################################################

print("Lendo controles...")

control_species = set()

control_dirs = sorted(

    d for d in glob.glob(os.path.join(OUTPUTS, "NTC*"))
    if os.path.isdir(d)

)

for control_dir in control_dirs:

    species_file = os.path.join(

        control_dir,
        "7-reports",
        "tables",
        "species_summary.csv"

    )

    if not os.path.exists(species_file):
        continue

    df = pd.read_csv(species_file)

    if "species" not in df.columns:
        continue

    for s in df["species"].dropna():

        control_species.add(str(s).strip())

############################################################
# Espécies que SEMPRE serão removidas
############################################################

always_remove = {

    "Homo sapiens",
    "Unknown",
    "uncultured bacterium",
    "uncultured organism",
    "environmental sample",
    "metagenome",
    "synthetic construct"

}

control_species.update(always_remove)

print(f"Espécies removidas automaticamente: {len(control_species)}")

############################################################
# Procurar amostras
############################################################

samples = sorted(

    d for d in glob.glob(os.path.join(OUTPUTS, "*"))
    if os.path.isdir(d)

)

processed = 0
skipped = 0

############################################################
# Processar cada amostra
############################################################

for sample_dir in samples:

    sample = os.path.basename(sample_dir)

    # ignora controles
    if sample.startswith("NTC"):
        continue

    print(f"\nProcessando: {sample}")

    ########################################################

    reports_dir = os.path.join(
        sample_dir,
        "7-reports"
    )

    tables_dir = os.path.join(
        reports_dir,
        "tables"
    )

    reads_file = os.path.join(
        tables_dir,
        "reads_taxonomy.csv"
    )

    species_file = os.path.join(
        tables_dir,
        "species_summary.csv"
    )

    ########################################################

    if not os.path.exists(reads_file):

        print("  reads_taxonomy.csv inexistente")

        skipped += 1

        continue

    if not os.path.exists(species_file):

        print("  species_summary.csv inexistente")

        skipped += 1

        continue

    ########################################################

    outdir = os.path.join(

        sample_dir,
        "16-plots_limpos"

    )

    figures_dir = os.path.join(
        outdir,
        "figures"
    )

    tables_out = os.path.join(
        outdir,
        "tables"
    )

    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_out, exist_ok=True)

    ########################################################

    df_reads = pd.read_csv(reads_file)

    df_species = pd.read_csv(species_file)

    ########################################################
    # remover contaminantes
    ########################################################

    removed = df_species[

        df_species["species"].isin(control_species)

    ].copy()

    df_species = df_species[

        ~df_species["species"].isin(control_species)

    ].copy()

    ########################################################

    df_reads = df_reads[

        ~df_reads["species"].isin(control_species)

    ].copy()

    ########################################################
    # salvar tabelas filtradas
    ########################################################

    df_reads.to_csv(

        os.path.join(

            tables_out,
            "filtered_reads_taxonomy.csv"

        ),

        index=False

    )

    df_species.to_csv(

        os.path.join(

            tables_out,
            "filtered_species_summary.csv"

        ),

        index=False

    )

    removed.to_csv(

        os.path.join(

            tables_out,
            "removed_species.csv"

        ),

        index=False

    )

    print(f"  Espécies removidas: {len(removed)}")

    ###############################################################
    # HEATMAP
    ###############################################################

    top_species = (

        df_species

        .sort_values(

            "total_rpkm",

            ascending=False

        )

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

            title=f"{sample}<br>Contig × Species (RPKM) - CLEAN",

            xaxis_title="Species",

            yaxis_title="Contig",

            width=1100,

            height=700

        )

        fig.update_yaxes(

            visible=False

        )

        fig.write_html(

            os.path.join(

                figures_dir,

                "heatmap_species.html"

            )

        )

        print("  ✓ Heatmap gerado")

    else:

        print("  Nenhuma espécie restante para gerar Heatmap")


    ###############################################################
    # BARPLOT
    ###############################################################

    if len(df_species) > 0:

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

            title=f"{sample}<br>Total RPKM por espécie (CLEAN)",

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

        print("  ✓ Barplot gerado")

    else:

        print("  Nenhuma espécie restante para gerar Barplot")

    processed += 1

###############################################################
# RESUMO
###############################################################

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

outputs/
    SAMPLE/
        16-plots_limpos/

            tables/

                filtered_reads_taxonomy.csv

                filtered_species_summary.csv

                removed_species.csv

            figures/

                heatmap_species.html

                species_barplot.html
"""
)
