
#!/usr/bin/env python3

import os
import glob

BASE = os.getcwd()
OUTPUTS = os.path.join(BASE, "outputs")

print("=" * 60)
print("Gerando Krona limpo")
print("=" * 60)

############################################################
# Descobrir controles
############################################################

controls = []

for sample_dir in glob.glob(os.path.join(OUTPUTS, "*")):

    sample = os.path.basename(sample_dir)

    if sample.startswith("NTC"):

        krona_file = os.path.join(
            sample_dir,
            "7-reports",
            "krona",
            "krona_input.tsv"
        )

        if os.path.exists(krona_file):
            controls.append(krona_file)

print(f"Controles encontrados: {len(controls)}")

############################################################
# Construir lista de taxids contaminantes
############################################################

control_taxids = set()

# Homo sapiens

human_taxids = {
    "9606",    # Homo sapiens
    "9605",    # Homo
    "9604",    # Hominidae
    "9443",    # Primates
    "314295",  # Haplorrhini
    "9526",    # Catarrhini
    "40674",   # Mammalia
}

control_taxids.update(human_taxids)

for control_file in controls:

    with open(control_file) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            taxid = parts[-1]

            control_taxids.add(taxid)

print(f"Taxids removidos: {len(control_taxids)}")

############################################################
# Processar amostras
############################################################

processed = 0

for sample_dir in glob.glob(os.path.join(OUTPUTS, "*")):

    sample = os.path.basename(sample_dir)

    # pula controles
    if sample.startswith("NTC"):
        continue

    input_file = os.path.join(
        sample_dir,
        "7-reports",
        "krona",
        "krona_input.tsv"
    )

    if not os.path.exists(input_file):

        print(f"[SKIP] {sample}")

        continue

    outdir = os.path.join(
        sample_dir,
        "15-krona_limpo"
    )

    os.makedirs(outdir, exist_ok=True)

    clean_file = os.path.join(
        outdir,
        "krona_input.tsv"
    )

    removed_file = os.path.join(
        outdir,
        "removed_taxa.tsv"
    )

    kept = 0
    removed = 0

    with open(clean_file, "w") as fout, \
         open(removed_file, "w") as frem:

        frem.write("taxid\n")

        with open(input_file) as fin:

            for line in fin:

                line = line.strip()

                if not line:
                    continue

                parts = line.split()

                if len(parts) < 2:
                    continue

                taxid = parts[-1]

                if taxid in control_taxids:

                    frem.write(f"{taxid}\n")

                    removed += 1

                    continue

                fout.write(line + "\n")

                kept += 1

    print(
        f"{sample}: "
        f"mantidos={kept} "
        f"removidos={removed}"
    )

    processed += 1

print("")
print("=" * 60)
print(f"Amostras processadas: {processed}")
print("=" * 60)
