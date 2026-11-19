import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# ============================================
# CONFIGURAÇÕES INICIAIS (AJUSTE AQUI)
# ============================================
FRACOES_PANEL = [5, 25, 50, 100]

FONTSIZE_TITULO_SUBPLOT = 16
FONTSIZE_EIXOS = 16
FONTSIZE_TICKS = 16
FONTSIZE_LEGENDA = 16
FONTSIZE_LETRA_PAINEL = 16

INPUT_DIR = "/media/rafael/Backup_HD/data_processed/no_x_t"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================
# FUNÇÃO PARA CARREGAR ARQUIVOS
# ============================================
def carregar_arquivos(frac):
    padrao = os.path.join(INPUT_DIR, f"no_x_t_frac_{frac}_obsprob_*.csv")
    arquivos = glob.glob(padrao)
    
    if not arquivos:
        print(f"⚠️ Nenhum arquivo encontrado para frac={frac} em {INPUT_DIR}")
        return []
    
    return sorted(arquivos, key=lambda x: float(x.split('obsprob_')[1].replace('.csv', '')))

# ============================================
# CRIAÇÃO DO PAINEL 2x2
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

handles_legenda = []
labels_legenda = []

for i, frac in enumerate(FRACOES_PANEL):
    ax = axes[i]
    arquivos = carregar_arquivos(frac)
    
    if not arquivos:
        ax.set_title(f"frac = {frac} (sem dados)", fontsize=FONTSIZE_TITULO_SUBPLOT)
        continue
    
    cores = plt.cm.viridis(np.linspace(0, 1, len(arquivos)))
    
    for idx, arquivo in enumerate(arquivos):
        df = pd.read_csv(arquivo)
        prob = float(arquivo.split('obsprob_')[1].replace('.csv', ''))
        
        # === CONVERSÃO ROBUSTA PARA NÚMERO ===
        time  = pd.to_numeric(df['time'],    errors='coerce').to_numpy(dtype=float)
        mean  = pd.to_numeric(df['NO_mean'], errors='coerce').to_numpy(dtype=float)
        std   = pd.to_numeric(df['NO_std'],  errors='coerce').to_numpy(dtype=float)
        
        # Remove pontos onde qualquer um dos valores é NaN
        mask = np.isfinite(time) & np.isfinite(mean) & np.isfinite(std)
        time = time[mask]
        mean = mean[mask]
        std  = std[mask]
        
        if len(time) == 0:
            print(f"⚠️ Nenhum dado válido em {arquivo}")
            continue
        
        # === NORMALIZAÇÃO: dividir por 256*256 ===
        FATOR_NORMALIZACAO = 256 * 256   # = 65536
        mean = mean / FATOR_NORMALIZACAO
        std  = std  / FATOR_NORMALIZACAO
        
        # Linha média (já normalizada)
        linha, = ax.plot(time, mean, 
                         color=cores[idx],
                         linewidth=2,
                         label=f'P = {prob:.2f}')
        
        # Banda de desvio padrão (já normalizada)
        ax.fill_between(time, mean - std, mean + std, 
                        alpha=0.2, 
                        color=cores[idx])
        
        if i == 0:
            
            handles_legenda.append(linha)
            labels_legenda.append(f'P = {prob:.2f}')
    
    #ax.set_title(f'frac = {frac}', fontsize=FONTSIZE_TITULO_SUBPLOT, fontweight='bold')
    ax.set_xlabel('steps', fontsize=FONTSIZE_EIXOS)
    ax.set_ylabel(r'$\rho_0(t)$', fontsize=FONTSIZE_EIXOS)
    ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
    ax.grid(True, alpha=0.3)
    
    letra = chr(97 + i)
    ax.text(0.02, 1.08, letra, transform=ax.transAxes, 
            fontsize=FONTSIZE_LETRA_PAINEL, fontweight='bold', 
            va='top', ha='left')

# ============================================
# LEGENDA GLOBAL
# ============================================
fig.tight_layout()
fig.subplots_adjust(bottom=0.18)

fig.legend(handles_legenda, labels_legenda, 
           loc='lower center', 
           ncol=5,
           fontsize=FONTSIZE_LEGENDA,
           title_fontsize=FONTSIZE_LEGENDA + 1,
           bbox_to_anchor=(0.5, 0.02),
           frameon=False,
           markerfirst=False)

# ============================================
# SALVAR
# ============================================
output_path = os.path.join(OUTPUT_DIR, "painel_NO_vs_time_frac_5_25_50_100.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✓ Painel salvo em: {output_path}")

plt.show()
plt.close()