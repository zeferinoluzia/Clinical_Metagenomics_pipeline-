#!/bin/bash

set -e

BASE=$(pwd)

for REPORT in "$BASE"/outputs/*/2-kraken2/*.kraken_report
do

    [ -f "$REPORT" ] || continue

    SAMPLE=$(basename "$REPORT" .kraken_report)
    
    # Define a pasta de saída exclusiva para o Krona
    KRONA_OUT="$BASE/outputs/$SAMPLE/3-krona"
    
    # Garante que a pasta do Krona exista antes de rodar as ferramentas
    mkdir -p "$KRONA_OUT"

    echo "Gerando Krona: $SAMPLE"

    # Salva o arquivo intermediário na pasta correta
    kreport2krona.py \
        -r "$REPORT" \
        -o "$KRONA_OUT/$SAMPLE.input.krona"

    # Salva o gráfico HTML final na pasta correta
    ktImportText \
        "$KRONA_OUT/$SAMPLE.input.krona" \
        -o "$KRONA_OUT/$SAMPLE.krona.html"

done

echo ""
echo "Krona finalizado!"
