import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para salvar em arquivo
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# ============================================
# CONFIGURAÇÕES - VARIAÇÃO DE PROBABILIDADE
# ============================================
sre = 2  # SRE fixo
prob_list = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]  # Probabilidades para comparar
frac_list = list(range(5, 101, 5))  # Frações de 5 a 100 em passos de 5


# base_paths = {frac: Path(f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/{frac}/prob_variation") 
#               for frac in frac_list}

# Base paths para cada fração (usando prob_variation)
base_paths = {frac: Path(f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/128/{frac}/prob_variation") 
              for frac in frac_list}

# Caminho de saída
# output_figures = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/H_expoentes/SRE_2_SRC_2_p_v/")
output_figures = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/H_expoentes/SRE_2_SRC_2_p_v/128")
output_figures.mkdir(parents=True, exist_ok=True)

# Criar um mapa de cores para as frações
# Usando uma colormap para ter cores distintas
colormap = cm.get_cmap('viridis', len(frac_list))
frac_colors = {frac: colormap(i) for i, frac in enumerate(frac_list)}

# Labels e markers para as frações
frac_labels = {frac: f'$N^{{C}}$ = {frac}$N_{0}^{{E}}$' for frac in frac_list}

# Markers variados para melhor distinção
markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'd', '|', '_', 'P', 'X']
frac_markers = {frac: markers[i % len(markers)] for i, frac in enumerate(frac_list)}

def load_exponents_for_prob(prob, frac):
    """Carrega os dados de expoentes para uma dada probabilidade e fração"""
    base_path = base_paths[frac]
    prob_dir = base_path / f"obsprob_{prob:.2f}"
    # print(prob_dir)
    # input()
    
    if not prob_dir.exists():
        return None
    
    file_pattern = f"expoentes_prob_{prob:.2f}.csv"
    files = list(prob_dir.glob(file_pattern))
    
    if not files:
        return None
    
    df = pd.read_csv(files[0])
    
    if 'alpha' not in df.columns:
        return None
    
    return df['alpha'].values

def plot_curves_for_prob(prob):
    """Plota as curvas KDE para uma probabilidade específica"""
    print(f"\nProcessando Probabilidade: {prob:.2f}")
    
    # Carrega dados para todas as frações
    all_alphas = {}
    for frac in frac_list:
        alphas = load_exponents_for_prob(prob, frac)
        if alphas is not None and len(alphas) > 0:
            all_alphas[frac] = alphas
            print(f"  ✓ Fração {frac}%: {len(alphas)} runs, média={np.mean(alphas):.4f}, std={np.std(alphas):.4f}")
        else:
            print(f"  ✗ Fração {frac}%: Sem dados")
    
    if len(all_alphas) == 0:
        print(f"  ✗ Nenhum dado encontrado para Prob={prob:.2f}")
        return None
    
    # Cria o gráfico apenas com curvas
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Encontra o intervalo baseado nos dados
    all_values = np.concatenate(list(all_alphas.values()))
    data_min = min(all_values)
    data_max = max(all_values)
    data_std = np.std(all_values)
    
    x_min = max(0, data_min - 2*data_std)
    x_max = data_max + 2*data_std
    
    print(f"  Intervalo de plotagem: [{x_min:.2f}, {x_max:.2f}]")
    
    x_range = np.linspace(x_min, x_max, 500)
    
    # for frac, alphas in all_alphas.items():
    #     # KDE
    #     kde = stats.gaussian_kde(alphas)
    #     y_values = kde(x_range)
        
    #     # Plota a curva
    #     ax.plot(x_range, y_values, color=frac_colors[frac], 
    #            linewidth=2, label=f"{frac_labels[frac]}",
    #            linestyle='-')

    marker_list = [
    'o', 's', '^', 'v', 'D',  # círculo, quadrado, triângulos, losango
    '*', 'p', 'h', 'X', 'd',  # estrela, pentágono, hexágono, X, diamante fino
    'P', 'H', '8', '>', '<',  # plus grosso, hexágono grosso, octógono
    '1', '2', '3', '4', '+'   # triângulos e +
    ]

    for i, (frac, alphas) in enumerate(all_alphas.items()):
    # KDE
        kde = stats.gaussian_kde(alphas)
        y_values = kde(x_range)
        
        # Escolhe o marcador baseado no índice (i)
        marker = marker_list[i % len(marker_list)]
        
        # Plota a curva com marcador específico
        ax.plot(x_range, y_values, 
            color=frac_colors[frac], 
            linewidth=2, 
            label=f"{frac_labels[frac]}",
            linestyle='-',
            marker=marker,
            markersize=5,
            markevery=8,  # ajuste conforme necessário
            markerfacecolor='white',  # fundo branco para melhor visualização
            markeredgewidth=1.5)
        
    # Linha para α=1 (difusão normal)
    ax.axvline(0.33, color='black', linestyle=':', linewidth=2, alpha=0.8, label=r'$\alpha$ = 1/3')
    
    # Configurações do gráfico
    ax.set_xlabel(r'$\alpha$', fontsize=14)
    ax.set_ylabel('Probability density', fontsize=14)
    #ax.set_title(f'$P = {prob:.2f}$', fontsize=16, fontweight='bold')
    
    # Ajusta a legenda - pode precisar de 2 colunas se muitas frações
    n_frac = len(all_alphas)
    ncol = 2 if n_frac > 8 else 1
    ax.legend(loc='upper left', fontsize=12, ncol=ncol, framealpha=0.9)
    
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Ajusta limites
    ax.set_xlim(-0.01, 1.30)
    
    # Adiciona informação do SRE
    ax.text(0.98, 0.98, f"SRE = {sre}", transform=ax.transAxes, 
           ha='right', va='top', fontsize=10, style='italic',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Salva a figura
    output_file = output_figures / f"curvas_expoentes_prob_{prob:.2f}_SRE_{sre}.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ Figura salva: {output_file}")
    print(f"    Tamanho: {output_file.stat().st_size} bytes")
    
    return fig

def plot_summary_statistics():
    """Plota um resumo das médias e desvios para todas as probabilidades"""
    print("\n" + "="*60)
    print("Gerando gráfico de resumo (médias e desvios)")
    print("="*60)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    summary_data = {frac: {'probs': [], 'means': [], 'stds': []} for frac in frac_list}
    
    for prob in prob_list:
        for frac in frac_list:
            alphas = load_exponents_for_prob(prob, frac)
            if alphas is not None and len(alphas) > 0:
                summary_data[frac]['probs'].append(prob)
                summary_data[frac]['means'].append(np.mean(alphas))
                summary_data[frac]['stds'].append(np.std(alphas))
    
    # Plotar apenas frações com dados
    for frac in frac_list:
        if summary_data[frac]['probs']:
            ax.errorbar(summary_data[frac]['probs'], 
                       summary_data[frac]['means'],
                       yerr=summary_data[frac]['stds'],
                       color=frac_colors[frac],
                       marker=frac_markers[frac],
                       capsize=3,
                       capthick=1.5,
                       elinewidth=1.5,
                       markersize=5,
                       linewidth=1.5,
                       alpha=0.7,
                       label=f"{frac_labels[frac]}")
    
    # Linha para α=1
    ax.axhline(1.0, color='black', linestyle=':', linewidth=2, alpha=0.8, label='α = 1')
    
    ax.set_xlabel(r'$P$', fontsize=14)
    ax.set_ylabel(r'$\langle \alpha \rangle $', fontsize=14)
    #ax.set_title(f'$SR = {sre}$', fontsize=16, fontweight='bold')
    
    # Ajusta a legenda para não ficar muito grande
    n_frac = len([f for f in frac_list if summary_data[f]['probs']])
    ncol = 2 if n_frac > 10 else (3 if n_frac > 15 else 1)
    ax.legend(loc='best', fontsize=12, ncol=ncol, framealpha=0.9)
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.05, 1.05)
    #ax.set_ylim(bottom=0.5)
    
    plt.tight_layout()
    
    output_file = output_figures / f"summary_alpha_vs_prob_SRE_{sre}.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Figura de resumo salva: {output_file}")
    print(f"  Tamanho: {output_file.stat().st_size} bytes")

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("Gerando curvas de distribuição dos expoentes α")
    print(f"SRE fixo = {sre}")
    print(f"Probabilidades: {prob_list}")
    print(f"Frações: {len(frac_list)} valores de {min(frac_list)} a {max(frac_list)}")
    print(f"Diretório de saída: {output_figures}")
    print("="*60)
    
    # Gera curvas para cada probabilidade
    for prob in prob_list:
        plot_curves_for_prob(prob)
    
    # Gera gráfico de resumo
    plot_summary_statistics()
    
    print("\n" + "="*60)
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Figuras salvas em: {output_figures}")
    print("="*60)