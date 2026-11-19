import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import os
import glob

# ============================================
# CONFIGURAÇÕES INICIAIS
# ============================================
RG_THRESHOLD = 2.0
SRE = 2
FRACOES_PANEL = list(range(5, 101, 5))

FONTSIZE_TITULO = 16
FONTSIZE_EIXOS = 16
FONTSIZE_TICKS = 16
FONTSIZE_LEGENDA = 16
FONTSIZE_LETRA = 16

BASE_PATH_RG = Path("/media/rafael/Backup_HD/data_processed/RG_sre_2_src_2_prob_v_frac_v")
BASE_PATH_ALPHA = Path("/media/rafael/Backup_HD/data_processed/expoente")
BASE_PATH_NE = Path("/media/rafael/Backup_HD/data_processed/NE_x_t")

OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# FUNÇÕES DE CARREGAMENTO
# ============================================
def calcular_phi_T(frac):
    consolidated_file = BASE_PATH_RG / f"frac_{frac}" / f"all_runs_frac_{frac}.csv"
    if not consolidated_file.exists():
        return None
    df = pd.read_csv(consolidated_file)
    df['rg'] = np.sqrt(df['rg_squared'])
    resultados = []
    for prob, grupo in df.groupby('prob'):
        n_total = len(grupo)
        n_localizados = (grupo['rg'] <= RG_THRESHOLD).sum()
        phi_T = n_localizados / n_total if n_total > 0 else np.nan
        resultados.append({'prob': prob, 'phi_T': phi_T})
    return pd.DataFrame(resultados).sort_values('prob')

def calcular_rg_medio(frac):
    consolidated_file = BASE_PATH_RG / f"frac_{frac}" / f"all_runs_frac_{frac}.csv"
    if not consolidated_file.exists():
        return None
    df = pd.read_csv(consolidated_file)
    df['rg'] = np.sqrt(df['rg_squared'])
    resultados = []
    for prob, grupo in df.groupby('prob'):
        resultados.append({
            'prob': prob,
            'rg_mean': grupo['rg'].mean(),
            'rg_std': grupo['rg'].std()
        })
    return pd.DataFrame(resultados).sort_values('prob')

def calcular_alpha_medio(frac):
    resultados = []
    frac_dir = BASE_PATH_ALPHA / str(frac) / "prob_variation"
    if not frac_dir.exists():
        return None
    for prob_dir in sorted(frac_dir.glob("obsprob_*")):
        try:
            prob = float(prob_dir.name.replace("obsprob_", ""))
        except ValueError:
            continue
        files = list(prob_dir.glob("expoentes_prob_*.csv"))
        if not files:
            files = list(prob_dir.glob("*.csv"))
        if not files:
            continue
        df = pd.read_csv(files[0])
        if 'alpha' not in df.columns:
            continue
        resultados.append({
            'prob': prob,
            'alpha_mean': df['alpha'].mean(),
            'alpha_std': df['alpha'].std()
        })
    if len(resultados) == 0:
        return None
    return pd.DataFrame(resultados).sort_values('prob')

def calcular_ne_medio_normalizado(frac):
    frac_dir = BASE_PATH_NE / f"frac_{frac}"
    if not frac_dir.exists():
        return None
    
    metadata_path = frac_dir / "metadata_NE.csv"
    if metadata_path.exists():
        df_meta = pd.read_csv(metadata_path)
        if 'probabilidade' in df_meta.columns and 'media_final' in df_meta.columns:
            resultados = []
            for _, row in df_meta.iterrows():
                prob = row['probabilidade']
                arquivo_prob = frac_dir / f"NE_vs_time_prob_{prob:.2f}.csv"
                if not arquivo_prob.exists():
                    continue
                df_prob = pd.read_csv(arquivo_prob)
                if 'NE_mean' not in df_prob.columns:
                    continue
                ne_inicial = df_prob['NE_mean'].iloc[0]
                if ne_inicial == 0 or np.isnan(ne_inicial):
                    continue
                ne_final = row['media_final']
                ne_final_std = row.get('desvio_padrao_final', np.nan)
                resultados.append({
                    'prob': prob,
                    'ne_normalizado': ne_final / ne_inicial,
                    'ne_normalizado_std': ne_final_std / ne_inicial if not np.isnan(ne_final_std) else np.nan
                })
            if len(resultados) > 0:
                return pd.DataFrame(resultados).sort_values('prob')
    
    arquivos = glob.glob(str(frac_dir / "NE_vs_time_prob_*.csv"))
    if not arquivos:
        return None
    
    resultados = []
    for arquivo in arquivos:
        try:
            prob = float(Path(arquivo).name.split('prob_')[1].replace('.csv', ''))
        except (ValueError, IndexError):
            continue
        df = pd.read_csv(arquivo)
        if 'NE_mean' not in df.columns or len(df) == 0:
            continue
        ne_inicial = df['NE_mean'].iloc[0]
        if ne_inicial == 0 or np.isnan(ne_inicial):
            continue
        ne_final = df['NE_mean'].iloc[-1]
        ne_final_std = df['NE_std'].iloc[-1] if 'NE_std' in df.columns else np.nan
        resultados.append({
            'prob': prob,
            'ne_normalizado': ne_final / ne_inicial,
            'ne_normalizado_std': ne_final_std / ne_inicial if not np.isnan(ne_final_std) else np.nan
        })
    if len(resultados) == 0:
        return None
    return pd.DataFrame(resultados).sort_values('prob')

# ============================================
# CARREGAR DADOS
# ============================================
print("="*60)
print("CARREGANDO DADOS...")
print("="*60)

dados_phi = {}
dados_rg = {}
dados_alpha = {}
dados_ne_norm = {}

for frac in FRACOES_PANEL:
    print(f"\nProcessando fração {frac}%...")
    df_phi = calcular_phi_T(frac)
    df_rg = calcular_rg_medio(frac)
    df_alpha = calcular_alpha_medio(frac)
    df_ne_norm = calcular_ne_medio_normalizado(frac)
    
    if df_phi is not None: dados_phi[frac] = df_phi
    if df_rg is not None: dados_rg[frac] = df_rg
    if df_alpha is not None: dados_alpha[frac] = df_alpha
    if df_ne_norm is not None: dados_ne_norm[frac] = df_ne_norm
    
    print(f"  ✓ φ_T: {len(df_phi) if df_phi is not None else 0} | "
          f"⟨α⟩: {len(df_alpha) if df_alpha is not None else 0} | "
          f"⟨Rg⟩: {len(df_rg) if df_rg is not None else 0} | "
          f"⟨N_E⟩/N_E(0): {len(df_ne_norm) if df_ne_norm is not None else 0}")

if not any([dados_phi, dados_rg, dados_alpha, dados_ne_norm]):
    raise SystemExit("❌ Nenhum dado encontrado.")

# ============================================
# CONFIGURAÇÃO DE CORES E MARCADORES
# ============================================
colormap = plt.get_cmap('viridis', len(FRACOES_PANEL))
frac_colors = {frac: colormap(i) for i, frac in enumerate(FRACOES_PANEL)}
frac_labels = {frac: f'$N^{{C}}$ = {frac}$N_{{0}}^{{E}}$' for frac in FRACOES_PANEL}

marker_list = [
    'o', 's', '^', 'v', 'D', '*', 'p', 'h', 'X', 'd',
    'P', 'H', '8', '>', '<', '1', '2', '3', '4', '+'
]

# ============================================
# PAINEL 2x2
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
axes = axes.flatten()

handles = []
labels = []

# ---------- SUBPLOT a (0): φ_T vs. P ----------
ax = axes[0]
for j, frac in enumerate(sorted(dados_phi.keys())):
    df = dados_phi[frac]
    marker = marker_list[j % len(marker_list)]
    linha, = ax.plot(df['prob'], df['phi_T'],
                     color=frac_colors[frac], linewidth=2, linestyle='-',
                     marker=marker, markersize=7, markerfacecolor='white',
                     markeredgewidth=1.5, alpha=0.85, label=frac_labels[frac])
    handles.append(linha)
    labels.append(frac_labels[frac])

ax.set_xlabel('$P$', fontsize=FONTSIZE_EIXOS)
ax.set_ylabel(r'$\phi_{T} = N_{T}/N^{C}$', fontsize=FONTSIZE_EIXOS)
ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
ax.text(0.02, 1.08, 'a', transform=ax.transAxes, fontsize=FONTSIZE_LETRA,
        fontweight='bold', va='top', ha='right')

# ---------- SUBPLOT b (1): ⟨α⟩ vs. P COM DESVIO PADRÃO ----------
ax = axes[1]
for j, frac in enumerate(sorted(dados_alpha.keys())):
    df = dados_alpha[frac]
    marker = marker_list[j % len(marker_list)]
    ax.errorbar(df['prob'], df['alpha_mean'], yerr=df['alpha_std'],
                color=frac_colors[frac], linewidth=2, linestyle='-',
                marker=marker, markersize=6, markerfacecolor='white',
                markeredgewidth=1.5, alpha=0.85,
                capsize=3, capthick=1.5, elinewidth=1.2,
                label=frac_labels[frac])
ax.set_xlabel('$P$', fontsize=FONTSIZE_EIXOS)
ax.set_ylabel(r'$\langle \alpha \rangle$', fontsize=FONTSIZE_EIXOS)
ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(-0.05, 1.05)
ax.text(0.02, 1.08, 'b', transform=ax.transAxes, fontsize=FONTSIZE_LETRA,
        fontweight='bold', va='top', ha='right')

# ---------- SUBPLOT c (2): ⟨Rg⟩ vs. P COM DESVIO PADRÃO ----------
ax = axes[2]
for j, frac in enumerate(sorted(dados_rg.keys())):
    df = dados_rg[frac]
    marker = marker_list[j % len(marker_list)]
    ax.errorbar(df['prob'], df['rg_mean'], yerr=df['rg_std'],
                color=frac_colors[frac], linewidth=2, linestyle='-',
                marker=marker, markersize=6, markerfacecolor='white',
                markeredgewidth=1.5, alpha=0.85,
                capsize=3, capthick=1.5, elinewidth=1.2,
                label=frac_labels[frac])
ax.set_xlabel('$P$', fontsize=FONTSIZE_EIXOS)
ax.set_ylabel(r'$\langle R_{G} \rangle$', fontsize=FONTSIZE_EIXOS)
ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(-0.05, 1.05)
ax.text(0.02, 1.08, 'c', transform=ax.transAxes, fontsize=FONTSIZE_LETRA,
        fontweight='bold', va='top', ha='right')

# ---------- SUBPLOT d (3): ⟨N_E⟩/N_E(0) vs. P ----------
ax = axes[3]
for j, frac in enumerate(sorted(dados_ne_norm.keys())):
    df = dados_ne_norm[frac]
    marker = marker_list[j % len(marker_list)]
    ax.plot(df['prob'], df['ne_normalizado'],
            color=frac_colors[frac], linewidth=2, linestyle='-',
            marker=marker, markersize=6, markerfacecolor='white',
            markeredgewidth=1.5, alpha=0.85, label=frac_labels[frac])
ax.set_xlabel('$P$', fontsize=FONTSIZE_EIXOS)
ax.set_ylabel(r'$ N_{E}  / N_{E}(0)$', fontsize=FONTSIZE_EIXOS)
ax.tick_params(axis='both', labelsize=FONTSIZE_TICKS)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(-0.05, 1.05)
ax.text(0.02, 1.08, 'd', transform=ax.transAxes, fontsize=FONTSIZE_LETRA,
        fontweight='bold', va='top', ha='right')

# ============================================
# LEGENDA GLOBAL (20 frações)
# ============================================
fig.tight_layout()
fig.subplots_adjust(bottom=0.25)

fig.legend(handles, labels,
           loc='lower center', ncol=5,
           fontsize=FONTSIZE_LEGENDA,
           bbox_to_anchor=(0.5, 0.06),
           frameon=False, markerfirst=False)

# ============================================
# SALVAR
# ============================================
output_path = OUTPUT_DIR / f"painel_phi_T_alpha_Rg_NE_norm_Rg_leq_{RG_THRESHOLD:.1f}.pdf"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Painel salvo em: {output_path}")
plt.close()

# ============================================
# SALVAR CSVs
# ============================================
for nome, dados in [('phi_T', dados_phi), ('alpha', dados_alpha),
                    ('rg', dados_rg), ('ne_normalizado', dados_ne_norm)]:
    if not dados:
        continue
    all_data = []
    for frac, df in dados.items():
        df_copy = df.copy()
        df_copy['frac'] = frac
        all_data.append(df_copy)
    df_all = pd.concat(all_data, ignore_index=True)
    csv_path = OUTPUT_DIR / f"{nome}_all_frac.csv"
    df_all.to_csv(csv_path, index=False)
    print(f"✓ CSV {nome} salvo: {csv_path}")