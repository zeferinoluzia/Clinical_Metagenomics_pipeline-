#!/usr/bin/env python3

import os
import glob
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE = os.getcwd()
OUTPUTS = os.path.join(BASE, "outputs")

print("=" * 60)
print("Comparando amostras com controles")
print("=" * 60)


def find_control(sample):

    if sample.startswith("NTC"):
        return None

    acid = "RNA" if "RNA" in sample else "DNA"

    controls = [
        os.path.basename(x)
        for x in glob.glob(os.path.join(OUTPUTS, "NTC*"))
    ]

    for c in controls:

        if acid in c:
            return c

    return None


processed = 0
skipped = 0

samples = sorted(

    d for d in glob.glob(os.path.join(OUTPUTS, "*"))

    if os.path.isdir(d)

)

for sample_dir in samples:

    sample = os.path.basename(sample_dir)

    if sample.startswith("NTC"):
        continue

    control = find_control(sample)

    if control is None:

        print(f"[SKIP] Controle não encontrado para {sample}")

        skipped += 1

        continue

    print(f"\nProcessando: {sample}")

    print(f"Controle: {control}")

    reports_dir = os.path.join(

        sample_dir,

        "7-reports"

    )

    comparison_dir = os.path.join(

        reports_dir,

        "comparison"

    )

    os.makedirs(

        comparison_dir,

        exist_ok=True

    )

    sample_reads = os.path.join(

        sample_dir,

        "7-reports",

        "tables",

        "reads_taxonomy.csv"

    )

    sample_species = os.path.join(

        sample_dir,

        "7-reports",

        "tables",

        "species_summary.csv"

    )

    control_reads = os.path.join(

        OUTPUTS,

        control,

        "7-reports",

        "tables",

        "reads_taxonomy.csv"

    )

    control_species = os.path.join(

        OUTPUTS,

        control,

        "7-reports",

        "tables",

        "species_summary.csv"

    )

    if not os.path.exists(sample_reads):

        print("Reads da amostra inexistente.")

        skipped += 1

        continue

    if not os.path.exists(control_reads):

        print("Reads do controle inexistente.")

        skipped += 1

        continue

    try:

        df_sample = pd.read_csv(sample_reads)

        df_control = pd.read_csv(control_reads)

        df_species = pd.read_csv(sample_species)

        df_species_control = pd.read_csv(control_species)

        #######################################################
        # tabela comparativa
        #######################################################

        comparison = (

            df_species[

                [

                    "species",

                    "total_rpkm",

                    "contig_count"

                ]

            ]

            .rename(

                columns={

                    "total_rpkm": "sample_rpkm",

                    "contig_count": "sample_contigs"

                }

            )

            .merge(

                df_species_control[

                    [

                        "species",

                        "total_rpkm",

                        "contig_count"

                    ]

                ]

                .rename(

                    columns={

                        "total_rpkm": "control_rpkm",

                        "contig_count": "control_contigs"

                    }

                ),

                how="outer",

                on="species"

            )

        )

        comparison = comparison.fillna(0)

        comparison["difference"] = (

            comparison["sample_rpkm"]

            -

            comparison["control_rpkm"]

        )

        comparison = comparison.sort_values(

            "difference",

            ascending=False

        )

        comparison.to_csv(

            os.path.join(

                comparison_dir,

                "comparison_table.csv"

            ),

            index=False

        )

        #######################################################
        # heatmap notebook
        #######################################################
        top_species = pd.concat(
            [
                df_species.nlargest(20, "total_rpkm")["species"],
                df_species_control.nlargest(20, "total_rpkm")["species"]
            ]
        ).drop_duplicates()

        heat_sample = (
            df_sample[
                df_sample["species"].isin(top_species)
            ]
            .pivot_table(
                index="Contig",
                columns="species",
                values="RPKM",
                aggfunc="sum",
                fill_value=0
            )
        )

        heat_control = (
            df_control[
                df_control["species"].isin(top_species)
            ]
            .pivot_table(
                index="Contig",
                columns="species",
                values="RPKM",
                aggfunc="sum",
                fill_value=0
            )
        )

        zmax = max(

            heat_sample.values.max() if heat_sample.size else 0,

            heat_control.values.max() if heat_control.size else 0

        )

        fig = make_subplots(

            rows=1,

            cols=2,

            subplot_titles=(

                sample,

                control

            ),

            horizontal_spacing=0.08

        )

        fig.add_trace(

            go.Heatmap(

                z=heat_sample.values,

                x=heat_sample.columns,

                y=heat_sample.index,

                colorscale="Viridis",

                zmin=0,

                zmax=zmax,

                hoverongaps=False

            ),

            row=1,

            col=1

        )

        fig.add_trace(

            go.Heatmap(

                z=heat_control.values,

                x=heat_control.columns,

                y=heat_control.index,

                colorscale="Viridis",

                zmin=0,

                zmax=zmax,

                hoverongaps=False,

                showscale=False

            ),

            row=1,

            col=2

        )

        fig.update_layout(

            title=f"{sample} vs {control}",

            width=1400,

            height=700

        )

        fig.update_xaxes(

            tickangle=45

        )

        fig.update_yaxes(

            visible=False

        )

        fig.write_html(

            os.path.join(

                comparison_dir,

                "heatmap_vs_control.html"

            )

        )

        #######################################################
        # barplot comparativo
        #######################################################

        comparison_plot = comparison.nlargest(
            20,
            "sample_rpkm"
        )

        bar = go.Figure()

        bar.add_trace(

            go.Bar(

                name=sample,

                x=comparison_plot["species"],

                y=comparison_plot["sample_rpkm"]

            )

        )

        bar.add_trace(

            go.Bar(

                name=control,

                x=comparison_plot["species"],

                y=comparison_plot["control_rpkm"]

            )

        )

        bar.update_layout(

            barmode="group",

            title=f"{sample} vs {control}",

            xaxis_title="Species",

            yaxis_title="Total RPKM",

            width=1300,

            height=700

        )

        bar.update_xaxes(

            tickangle=45

        )

        bar.write_html(

            os.path.join(

                comparison_dir,

                "barplot_vs_control.html"

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

print(f"Comparações geradas : {processed}")

print(f"Ignoradas           : {skipped}")

print()

print("""

Arquivos gerados

7-reports/
    comparison/

        comparison_table.csv

        heatmap_vs_control.html

        barplot_vs_control.html

""")
