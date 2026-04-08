import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import stats

# Diretório de saída
output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NO_x_P"

# Criar diretório de saída se não existir
os.makedirs(output_dir, exist_ok=True)

# Lista de valores de frac
frac_values = [25, 50, 100]

# Cores para cada frac
cores = ['blue', 'red', 'green']
marcadores = ['o', 's', '^']

# Criar figura única
plt.figure(figsize=(12, 8))

# Dicionário para armazenar os dados
dados_frac = {}

# Processar cada frac
for idx, frac in enumerate(frac_values):
    # Caminho para o diretório de dados (NO_x_t)
    base_dir = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/NO_x_t/frac_{frac}"
    
    # Ler metadados
    metadata_path = os.path.join(base_dir, "metadata_TO.csv")
    
    try:
        df_metadata = pd.read_csv(metadata_path)
        dados_frac[frac] = df_metadata
        
        print(f"frac = {frac}: {len(df_metadata)} pontos carregados")
        
        # Plotar curva para este frac
        plt.errorbar(df_metadata['probabilidade'], 
                    df_metadata['media_final'], 
                    yerr=df_metadata['desvio_padrao_final'],
                    fmt=f'{marcadores[idx]}-', 
                    capsize=5,
                    capthick=2,
                    elinewidth=2,
                    markersize=8,
                    color=cores[idx],
                    ecolor='lightgray',
                    alpha=0.8,
                    label=f'frac = {frac}',
                    markeredgecolor='darkblue' if idx == 0 else 'darkred' if idx == 1 else 'darkgreen',
                    markeredgewidth=1,
                    linewidth=2.5)
        
        # Adicionar linha de tendência (opcional - comentar se não quiser)
        slope, intercept, r_value, p_value, std_err = stats.linregress(df_metadata['probabilidade'], 
                                                                         df_metadata['media_final'])
        line_x = np.array([df_metadata['probabilidade'].min(), df_metadata['probabilidade'].max()])
        line_y = intercept + slope * line_x
        
        plt.plot(line_x, line_y, 
                '--', 
                color=cores[idx], 
                linewidth=1.5,
                alpha=0.5)
        
    except FileNotFoundError:
        print(f"  ✗ frac = {frac}: arquivo não encontrado em {metadata_path}")
    except Exception as e:
        print(f"  ✗ frac = {frac}: erro - {e}")

# Personalizar gráfico
plt.xlabel('Probabilidade', fontsize=14)
plt.ylabel('Número de Observadores (N_O) - Média Final', fontsize=14)
plt.title('N_O Final vs Probabilidade para diferentes valores de frac\n(frac = 25, 50, 100)', 
          fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(np.arange(0.0, 1.1, 0.1), rotation=45)
plt.legend(fontsize=12, loc='best')
plt.tight_layout()

# Salvar gráfico
output_path = os.path.join(output_dir, f"NO_final_vs_probability_all_frac.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Gráfico salvo: {output_path}")

plt.show()
plt.close()

# Mostrar tabela comparativa
print("\n" + "="*80)
print("COMPARAÇÃO ENTRE DIFERENTES FRAC")
print("="*80)

for frac in frac_values:
    if frac in dados_frac:
        df = dados_frac[frac]
        print(f"\n--- FRAC = {frac} ---")
        print(df[['probabilidade', 'media_final', 'desvio_padrao_final', 'num_runs']].to_string(index=False))

print("\n" + "="*80)
print(f"✓ Gráfico comparativo salvo em: {output_dir}")