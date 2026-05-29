
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt  # <--- LINHA 2: Import depois de definir o backend
from pathlib import Path
from scipy import stats
import numpy as np


# ==================== PARÂMETROS CONFIGURÁVEIS ====================
frac = 5           # Fração (25, 50, 75, etc.)
sre = 2             # SRE que você quer plotar (2, 4, 8, 10, 12, 14, 16)
src = 2
prob = 0.10
t_min = 1e6         # Posição da linha vertical
n = 180              # Número de pontos para o fit (últimos n pontos)


# ==================================================================

output_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/MSD_estabilidade/SRE_v_SRC_2_p_05")
output_dir.mkdir(parents=True, exist_ok=True)  # Cria o diretório se não existir

# Caminho do arquivo
data_path = Path(f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/MSD_sre_2_src_2_prob_v_frac_v/frac_{frac}/SRE_{sre}")
file_path = data_path / f"msd_ensemble_SRE_{sre}.csv"

# Carrega os dados
df = pd.read_csv(file_path)

# Cria o gráfico
plt.figure(figsize=(10, 6))

# Plot do MSD médio com banda de desvio padrão
plt.plot(df['time'], df['msd_mean'], 'b-', linewidth=2, label='MSD médio')
plt.fill_between(df['time'], 
                  df['msd_mean'] - df['msd_std'], 
                  df['msd_mean'] + df['msd_std'], 
                  alpha=0.3, color='blue', label='Desvio padrão')

# =========== AJUSTE PELOS ÚLTIMOS N PONTOS ===========
# Pega os últimos n pontos (ou todos se tiver menos de n)
n_points = min(n, len(df))
last_n_times = df['time'].iloc[-n_points:]
last_n_msd = df['msd_mean'].iloc[-n_points:]

# Regressão linear nos últimos n pontos (escala log)
log_times = np.log10(last_n_times)
log_msd = np.log10(last_n_msd)
slope, intercept, r_value, p_value, std_err = stats.linregress(log_times, log_msd)

# Cria reta desde o início até o final com essa inclinação
t_all = df['time']
msd_trend = 10**(intercept + slope * np.log10(t_all))

# Plota a reta de tendência
plt.plot(t_all, msd_trend, color='orange', linestyle='--', linewidth=2.5, 
         label=f'Tendência últimos {n_points} pts (α = {slope:.3f}, R² = {r_value**2:.3f})')

# Opcional: marcar os pontos usados no ajuste
plt.plot(last_n_times, last_n_msd, 'ro', markersize=3, alpha=0.5, 
         label=f'Pontos usados no ajuste (últimos {n_points})')
# =========================================================

# Linha vertical
plt.axvline(x=t_min, color='red', linestyle='--', linewidth=1.5, label=f't_min = {t_min:.1e}')

# Configurações do gráfico
plt.xlabel('Tempo (t)', fontsize=12)
plt.xscale('log')
plt.yscale('log')
plt.ylabel('MSD', fontsize=12)
plt.title(f'MSD Ensemble - Fração {frac}%, SRE {sre}', fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)


# Salvar figura no novo diretório
nome_arquivo = output_dir / f"MSD_sre_{sre}_frac_{frac}.pdf"
plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
plt.close()

# Print dos resultados do ajuste
print(f"\n=== RESULTADOS DO AJUSTE (últimos {n_points} pontos) ===")
print(f"Inclinação (expoente α): {slope:.4f}")
print(f"R²: {r_value**2:.4f}")
print(f"Erro padrão: {std_err:.4f}")