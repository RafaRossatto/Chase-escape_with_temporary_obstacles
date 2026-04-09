import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

frac = 25

# Caminho para o diretório de dados (NO_x_t)
base_dir = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/NO_x_t/frac_{frac}"

# Diretórios de saída para cada tipo
output_dir_NO_t = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NO_x_t"
output_dir_NO_P = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NO_x_P"

# Criar diretórios de saída se não existirem
os.makedirs(output_dir_NO_t, exist_ok=True)
os.makedirs(output_dir_NO_P, exist_ok=True)

# Encontrar todos os arquivos CSV (exceto metadados e config)
# Note: os arquivos agora são TO_vs_time_prob_*.csv (Observadores)
arquivos_NO = glob.glob(os.path.join(base_dir, "TO_vs_time_prob_*.csv"))

print(f"Encontrados {len(arquivos_NO)} arquivos para frac={frac}")

# === PLOT 1: Todas as curvas juntas (salvar em NO_x_t) ===
plt.figure(figsize=(12, 8))

# Cores para as curvas
cores = plt.cm.viridis(np.linspace(0, 1, len(arquivos_NO)))

# Ler e plotar cada arquivo
for idx, arquivo in enumerate(sorted(arquivos_NO)):
    df = pd.read_csv(arquivo)
    
    # Extrair probabilidade do nome do arquivo
    prob = float(arquivo.split('prob_')[1].replace('.csv', ''))
    
    # Plotar (agora é TO_mean)
    plt.plot(df['time'], df['TO_mean'], 
             #label=f'prob = {prob:.2f} (final = {df["TO_mean"].iloc[-1]:.1f})',
             label=f'prob = {prob:.2f}',
             color=cores[idx],
             linewidth=2)
    
    # Adicionar banda de desvio padrão
    plt.fill_between(df['time'], 
                     df['TO_mean_minus_std'], 
                     df['TO_mean_plus_std'], 
                     alpha=0.2, 
                     color=cores[idx])

# Personalizar gráfico
plt.xlabel('steps', fontsize=12)
plt.ylabel('N_O', fontsize=12)
plt.title(f'N_O vs Prob. (frac={frac})', fontsize=14, fontweight='bold')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Salvar plot na pasta NO_x_t
output_path_1 = os.path.join(output_dir_NO_t, f"NO_vs_time_all_probabilities_frac_{frac}.png")
plt.savefig(output_path_1, dpi=300, bbox_inches='tight')
print(f"✓ Plot salvo em NO_x_t: {output_path_1}")

# Mostrar na tela (opcional)
plt.show()
plt.close()

# === PLOT 2: Valor final em função da probabilidade (salvar em NO_x_P) ===
# Ler metadados
metadata_path = os.path.join(base_dir, "metadata_TO.csv")  # Note: metadados chamam TO (observadores)
df_metadata = pd.read_csv(metadata_path)
print("\n=== RESUMO DOS RESULTADOS ===")
print(df_metadata.to_string(index=False))

# Criar gráfico do valor final
plt.figure(figsize=(10, 6))

plt.errorbar(df_metadata['probabilidade'], 
             df_metadata['media_final'], 
             yerr=df_metadata['desvio_padrao_final'],
             fmt='o-', 
             capsize=5,
             capthick=2,
             elinewidth=2,
             markersize=8,
             color='blue',
             ecolor='gray',
             label='N_O final')

plt.xlabel('Probabilidade', fontsize=12)
plt.ylabel('N_O Final (média ± std)', fontsize=12)
plt.title(f'Valor final de N_O em função da probabilidade (frac={frac})', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.xticks(df_metadata['probabilidade'])
plt.legend()
plt.tight_layout()

# Salvar plot na pasta NO_x_P
output_path_2 = os.path.join(output_dir_NO_P, f"NO_final_vs_probability_frac_{frac}.png")
plt.savefig(output_path_2, dpi=300, bbox_inches='tight')
print(f"✓ Plot salvo em NO_x_P: {output_path_2}")

plt.show()
plt.close()

print(f"\n✓ Todos os plots salvos:")
print(f"  - NO_x_t: {output_dir_NO_t}")
print(f"  - NO_x_P: {output_dir_NO_P}")