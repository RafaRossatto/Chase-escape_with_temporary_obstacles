#!/bin/bash

RUN=$1
TIMESTEP=$2

# Definir os nomes dos arquivos (use uma vez só)
PREY_FILE="NC_1433_NE_2867_O_4915_TCC_1.000000_SR_2_TCT_1.000000_SR_2.dat_run_${RUN}_prey_trajectories.csv"
TEMP_FILE="NC_1433_NE_2867_O_4915_TCC_1.000000_SR_2_TCT_1.000000_SR_2.dat_run_${RUN}_temp_obs_trajectories.csv"

echo "Verificando sobreposições no timestep $TIMESTEP (Run $RUN)"
echo "Arquivo Prey: $PREY_FILE"
echo "Arquivo Temp: $TEMP_FILE"
echo "-----------------------------------"

# Verificar se os arquivos existem
if [ ! -f "$PREY_FILE" ]; then
    echo "ERRO: Arquivo de prey não encontrado: $PREY_FILE"
    exit 1
fi

if [ ! -f "$TEMP_FILE" ]; then
    echo "ERRO: Arquivo de temp_obs não encontrado: $TEMP_FILE"
    exit 1
fi

# Extrair posições das presas no timestep
grep "^$TIMESTEP," "$PREY_FILE" | cut -d',' -f3,4 > "prey_pos_${TIMESTEP}.tmp"

# Extrair posições dos temp_obs no timestep
grep "^$TIMESTEP," "$TEMP_FILE" | cut -d',' -f3,4 > "temp_pos_${TIMESTEP}.tmp"

echo "Posições das presas no timestep $TIMESTEP:"
cat "prey_pos_${TIMESTEP}.tmp"
echo ""
echo "Posições dos temp_obs no timestep $TIMESTEP:"
cat "temp_pos_${TIMESTEP}.tmp"
echo ""

# Verificar sobreposições
echo "Posições sobrepostas (prey e temp_obs no mesmo local):"
OVERLAPS_FOUND=0

while IFS=',' read -r x y; do
    if [ -n "$x" ] && [ -n "$y" ]; then  # Ignorar linhas vazias
        if grep -q "^$x,$y$" "temp_pos_${TIMESTEP}.tmp"; then
            echo "SOBREPOSIÇÃO em ($x, $y)"
            OVERLAPS_FOUND=1
        fi
    fi
done < "prey_pos_${TIMESTEP}.tmp"

if [ $OVERLAPS_FOUND -eq 0 ]; then
    echo "Nenhuma sobreposição encontrada no timestep $TIMESTEP"
fi

# Mostrar estatísticas
PREY_COUNT=$(wc -l < "prey_pos_${TIMESTEP}.tmp" | tr -d ' ')
TEMP_COUNT=$(wc -l < "temp_pos_${TIMESTEP}.tmp" | tr -d ' ')
echo ""
echo "Estatísticas do timestep $TIMESTEP:"
echo "- Número de presas: $PREY_COUNT"
echo "- Número de temp_obs: $TEMP_COUNT"

# Limpar
rm -f "prey_pos_${TIMESTEP}.tmp" "temp_pos_${TIMESTEP}.tmp"