#!/bin/bash

# Valores de TRAIL_PROBABILITY para testar
#TRAIL_VALUES=(0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)
TRAIL_VALUES=(1.0)
SR_C_VALUES=(2)
#SR_E_VALUES=(2)
SR_E_VALUES=(2 4 6 8 10 12 14 16)
#TRAIL_VALUES=(0.0 0.1 0.2)
#TRAIL_VALUES=(0.9 1.0)

echo "========================================="
echo "Executando simulações com diferentes TRAIL_PROBABILITY"
echo "========================================="

# Compilar uma vez
make clean > /dev/null 2>&1
make

if [ $? -ne 0 ] || [ ! -f "./a.out" ]; then
    echo "❌ Erro na compilação"
    exit 1
fi

echo "✅ Compilação concluída"
echo ""

# Loop sobre os valores
for TRAIL in "${TRAIL_VALUES[@]}"; do
    for SRC in "${SR_C_VALUES[@]}"; do
        for SRE in "${SR_E_VALUES[@]}"; do
            echo "========================================="
            echo "Executando com TRAIL_PROBABILITY = $TRAIL, SR_C = $SRC, SR_E = $SRE"
            echo "========================================="
            
            # Executar passando os valores como argumentos
            ./a.out $TRAIL $SRC $SRE
            
            echo "✅ Simulação para TRAIL=$TRAIL, SR_C=$SRC, SR_E=$SRE concluída"
            echo ""
        done
    done
done

echo "========================================="
echo "Todas as simulações foram concluídas!"
echo "========================================="