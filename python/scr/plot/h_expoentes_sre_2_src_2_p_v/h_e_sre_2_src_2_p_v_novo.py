import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import os

# ============================================
# CONFIGURAÇÕES INICIAIS
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




# Caminho base (ENTRADA)
BASE_PATH = Path("/media/rafael/Backup_HD/data_processed/expoente")

# Caminho de saída (pasta do script)
OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# FUNÇÃO DE CARREGAMENTO
# ============================================
def load_exponents_for_prob(prob, frac):
    """Carrega os dados de expoentes para uma dada probabilidade e fração"""
    prob_dir = BASE_PATH / str(frac) / "prob_variation" / f"obsprob_{prob:.2f}"
    
    if not prob_dir.exists():
        return None
    
    file_pattern = f"expoentes_prob_{prob:.2f}.csv"
    files = list(prob_dir.glob(file_pattern))
    
    if not files:
        files = list(prob_dir.glob("*.csv"))
        if not files:
            return None
    
    df = pd.read_csv(files[0])
    
    if 'alpha' not in df.columns:
        return None
    
    return df['alpha'].values

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
    all_alphas = {}
    for frac in FRACOES_PANEL:
        alphas = load_exponents_for_prob(prob, frac)
        if alphas is not None and len(alphas) > 0:
            all_alphas[frac] = alphas
            print(f"  ✓ P={prob:.2f}, frac={frac}%: {len(alphas)} runs")
        else:
            print(f"  ✗ P={prob:.2f}, frac={frac}%: Sem dados")
    
    if len(all_alphas) == 0:
        ax.set_title(f'P = {prob:.2f} (sem dados)', fontsize=FONTSIZE_TITULO_SUBPLOT)
        continue
    
    # Define o range X baseado em TODOS os dados
    all_values = np.concatenate(list(all_alphas.values()))
    data_min = min(all_values)
    data_max = max(all_values)
    data_std = np.std(all_values)
    
    x_min = max(0, data_min - 2*data_std)
    x_max = data_max + 2*data_std
    x_range = np.linspace(x_min, x_max, 500)
    
    # Loop pelas frações (com marcadores, igual ao original)
    for j, (frac, alphas) in enumerate(all_alphas.items()):
        # KDE
        kde = stats.gaussian_kde(alphas)
        y_values = kde(x_range)
        
        # Escolhe o marcador baseado no índice
        marker = marker_list[j % len(marker_list)]
        
        # Plota com marcador (igual ao original)
        linha, = ax.plot(x_range, y_values, 
                         color=frac_colors[frac], 
                         linewidth=2, 
                         label=frac_labels[frac],
                         linestyle='-',
                         marker=marker,
                         markersize=5,
                         markevery=8,
                         markerfacecolor='white',
                         markeredgewidth=1.5)
        
        if i == 0:
            handles_legenda.append(linha)
            labels_legenda.append(frac_labels[frac])
    
    # Linha para alpha = 1/3
    ax.axvline(0.33, color='black', linestyle=':', linewidth=2, alpha=0.8)
    
    # Personalização
    #ax.set_title(f'P = {prob:.2f}', fontsize=FONTSIZE_TITULO_SUBPLOT, fontweight='bold')
    ax.set_xlabel(r'$\alpha$', fontsize=FONTSIZE_EIXOS)
    ax.set_ylabel('Probability density', fontsize=FONTSIZE_EIXOS)
    ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.01, 1.30)
    
    # Letra do painel
    letra = chr(97 + i)
    ax.text(0.02, 1.10, letra, transform=ax.transAxes, 
            fontsize=FONTSIZE_LETRA_PAINEL, fontweight='bold', 
            va='top', ha='left')

# Remove subplots vazios
for j in range(len(PROB_LIST_PANEL), len(axes)):
    axes[j].set_visible(False)

# ============================================
# LEGENDA GLOBAL (com 20 frações)
# ============================================
fig.tight_layout()
fig.subplots_adjust(bottom=0.30)  # mais espaço para legenda grande

fig.legend(handles_legenda, labels_legenda,
           loc='lower center',
           ncol=5,  # 5 colunas × 4 linhas = 20 frações
           fontsize=FONTSIZE_LEGENDA,
           bbox_to_anchor=(0.5, 0.08),
           frameon=False,
           markerfirst=False)

# ============================================
# SALVAR
# ============================================
output_path = OUTPUT_DIR / "painel_MSD_alpha_por_prob.pdf"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✓ Painel salvo em: {output_path}")

plt.close()