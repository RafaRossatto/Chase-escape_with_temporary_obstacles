import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

frac = 25

# Caminho para o diretório de dados
base_dir = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/NE_x_t/frac_{frac}"

# Diretórios de saída para cada tipo
output_dir_NE_t = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NE_x_t"
output_dir_NE_P = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/NE_x_P"

# Criar diretórios de saída se não existirem
os.makedirs(output_dir_NE_t, exist_ok=True)
os.makedirs(output_dir_NE_P, exist_ok=True)

# Encontrar todos os arquivos CSV (exceto metadados e config)
arquivos_NE = glob.glob(os.path.join(base_dir, "NE_vs_time_prob_*.csv"))

print(f"Encontrados {len(arquivos_NE)} arquivos")

# === PLOT 1: Todas as curvas juntas (salvar em NE_x_t) ===
plt.figure(figsize=(12, 8))

# Cores para as curvas
cores = plt.cm.viridis(np.linspace(0, 1, len(arquivos_NE)))

# Ler e plotar cada arquivo
for idx, arquivo in enumerate(sorted(arquivos_NE)):
    df = pd.read_csv(arquivo)
    
    # Extrair probabilidade do nome do arquivo
    prob = float(arquivo.split('prob_')[1].replace('.csv', ''))
    
    # Plotar
    plt.plot(df['time'], df['NE_mean'], 
            #  label=f'prob = {prob:.2f} (final = {df["NE_mean"].iloc[-1]:.1f})',
             label=f'prob = {prob:.2f}',
             color=cores[idx],
             linewidth=2)
    
    # Opcional: adicionar banda de desvio padrão
    plt.fill_between(df['time'], 
                     df['NE_mean_minus_std'], 
                     df['NE_mean_plus_std'], 
                     alpha=0.2, 
                     color=cores[idx])

# Personalizar gráfico
plt.xlabel('Steps', fontsize=12)
plt.ylabel('N_E', fontsize=12)
plt.title(f'NC=NE*{frac}%', fontsize=14, fontweight='bold')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Salvar plot na pasta NE_x_t
output_path_1 = os.path.join(output_dir_NE_t, f"NE_vs_time_all_probabilities_frac_{frac}.png")
plt.savefig(output_path_1, dpi=300, bbox_inches='tight')
print(f"✓ Plot salvo em NE_x_t: {output_path_1}")

# Mostrar na tela (opcional)
plt.show()
plt.close()

# === PLOT 2: Valor final em função da probabilidade (salvar em NO_x_t) ===
# Ler metadados
df_metadata = pd.read_csv(os.path.join(base_dir, "metadata_NE.csv"))
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
             color='red',
             ecolor='gray',
             label='N_E final')

plt.xlabel('Probabilidade', fontsize=12)
plt.ylabel('N_E Final (média ± std)', fontsize=12)
plt.title(f'Valor final de N_E em função da probabilidade (frac={frac})', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.xticks(df_metadata['probabilidade'])
plt.legend()
plt.tight_layout()

# Salvar plot na pasta NO_x_t
output_path_2 = os.path.join(output_dir_NE_P, f"NE_final_vs_probability_frac_{frac}.png")
plt.savefig(output_path_2, dpi=300, bbox_inches='tight')
print(f"✓ Plot salvo em NO_x_t: {output_path_2}")

plt.show()
plt.close()

print(f"\n✓ Todos os plots salvos:")
print(f"  - NE_x_t: {output_dir_NE_t}")
print(f"  - NO_x_t: {output_dir_NE_P}")