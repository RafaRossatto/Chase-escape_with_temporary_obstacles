import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import os

# ============================================
# CONFIGURAÇÕES INICIAIS (AJUSTE AQUI)
# ============================================
# Probabilidades que você quer no painel
PROB_LIST_PANEL = [0.00, 0.20, 0.50, 1.00]

# TODAS as frações (igual ao original)
FRACOES_PANEL = list(range(5, 101, 5))

# Tamanhos de fonte
FONTSIZE_TITULO_SUBPLOT = 16
FONTSIZE_EIXOS = 16
FONTSIZE_TICKS = 16
FONTSIZE_LEGENDA = 16
FONTSIZE_LETRA_PAINEL = 16

# Caminho base (ENTRADA) - igual ao original
BASE_PATH = Path("/media/rafael/Backup_HD/data_processed/RG_sre_2_src_2_prob_v_frac_v")



# Caminho de saída (pasta do script)
OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# FUNÇÃO DE CARREGAMENTO (IDÊNTICA À ORIGINAL)
# ============================================
def load_rg_for_prob(prob, frac):
    """Carrega os dados de raio de giro para uma dada probabilidade e fração"""
    base_path = BASE_PATH / f"frac_{frac}"
    consolidated_file = base_path / f"all_runs_frac_{frac}.csv"
    
    if not consolidated_file.exists():
        return None
    
    try:
        df = pd.read_csv(consolidated_file)
        df_prob = df[df['prob'] == prob]
        
        if len(df_prob) == 0:
            return None
        
        rg_values = np.sqrt(df_prob['rg_squared'].values)
        return rg_values
    except Exception as e:
        print(f"  Erro ao ler {consolidated_file} para prob={prob}: {e}")
        return None

# ============================================
# LISTA DE MARCADORES (igual ao original)
# ============================================
marker_list = [
    'o', 's', '^', 'v', 'D',
    '*', 'p', 'h', 'X', 'd',
    'P', 'H', '8', '>', '<',
    '1', '2', '3', '4', '+'
]

# ============================================
# CRIAÇÃO DO PAINEL
# ============================================
n_prob = len(PROB_LIST_PANEL)
n_cols = 2 if n_prob > 1 else 1
n_rows = int(np.ceil(n_prob / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(8*n_cols, 7*n_rows))
if n_prob == 1:
    axes = [axes]
else:
    axes = axes.flatten()

# Cores para as curvas
colormap = plt.get_cmap('viridis', len(FRACOES_PANEL))
frac_colors = {frac: colormap(i) for i, frac in enumerate(FRACOES_PANEL)}
frac_labels = {frac: f'$N^{{C}}$ = {frac}$N_{{0}}^{{E}}$' for frac in FRACOES_PANEL}

handles_legenda = []
labels_legenda = []

# Loop pelos subplots (probabilidades)
for i, prob in enumerate(PROB_LIST_PANEL):
    ax = axes[i]
    
    # Carrega dados para todas as frações
    all_rg = {}
    for frac in FRACOES_PANEL:
        rg_values = load_rg_for_prob(prob, frac)
        if rg_values is not None and len(rg_values) > 0:
            all_rg[frac] = rg_values
            print(f"  ✓ P={prob:.2f}, frac={frac}%: {len(rg_values)} runs")
        else:
            print(f"  ✗ P={prob:.2f}, frac={frac}%: Sem dados")
    
    
    # Define o range X baseado em TODOS os dados
    all_values = np.concatenate(list(all_rg.values()))
    x_min = min(all_values)
    x_max = max(all_values)
    x_range = np.linspace(x_min, x_max, 500)
    
    # Ordena as frações para consistência
    sorted_fracs = sorted(all_rg.keys())
    
    # Loop pelas frações (com marcadores)
    for j, frac in enumerate(sorted_fracs):
        alphas = all_rg[frac]
        
        try:
            kde = stats.gaussian_kde(alphas)
            y_values = kde(x_range)
        except Exception as e:
            print(f"  Erro no KDE para fração {frac}%: {e}")
            continue
        
        marker = marker_list[j % len(marker_list)]
        
        linha, = ax.plot(x_range, y_values, 
                         color=frac_colors[frac], 
                         linewidth=2, 
                         label=frac_labels[frac],
                         linestyle='-',
                         alpha=0.8,
                         marker=marker,
                         markersize=5,
                         markevery=8,
                         markerfacecolor='white',
                         markeredgewidth=1.5)
        
        if i == 0:
            handles_legenda.append(linha)
            labels_legenda.append(frac_labels[frac])
    
    # Linha vertical em Rg = 2
    ax.axvline(x=2.0, color='red', linestyle='--', linewidth=2, alpha=0.7)
    
    # Personalização
    ax.set_xlabel(r'$R_{G}$', fontsize=FONTSIZE_EIXOS)
    ax.set_ylabel('Probability density', fontsize=FONTSIZE_EIXOS)
    ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.05, 13.00)
    
     
    # Letra do painel
    letra = chr(97 + i)
    ax.text(0.02, 1.05, letra, transform=ax.transAxes, 
            fontsize=FONTSIZE_LETRA_PAINEL, fontweight='bold', 
            va='top', ha='left')

# Remove subplots vazios
for j in range(len(PROB_LIST_PANEL), len(axes)):
    axes[j].set_visible(False)

# ============================================
# LEGENDA GLOBAL
# ============================================
fig.tight_layout()
fig.subplots_adjust(bottom=0.30)

fig.legend(handles_legenda, labels_legenda,
           loc='lower center',
           ncol=5,
           fontsize=FONTSIZE_LEGENDA,
           bbox_to_anchor=(0.5, 0.08),
           frameon=False,
           markerfirst=False)

# ============================================
# SALVAR
# ============================================
output_path = OUTPUT_DIR / "rg_representative.pdf"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✓ Painel salvo em: {output_path}")

plt.close()