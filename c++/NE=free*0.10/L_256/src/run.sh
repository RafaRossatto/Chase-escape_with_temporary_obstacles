#!/bin/bash

# Valores de TRAIL_PROBABILITY para testar
TRAIL_VALUES=(0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)
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
    echo "========================================="
    echo "Executando com TRAIL_PROBABILITY = $TRAIL"
    echo "========================================="
    
    # Executar passando o valor como argumento
    ./a.out $TRAIL
    
    echo "✅ Simulação para TRAIL=$TRAIL concluída"
    echo ""
done

echo "========================================="
echo "Todas as simulações foram concluídas!"
echo "========================================="