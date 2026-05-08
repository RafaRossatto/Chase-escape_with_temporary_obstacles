import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para salvar em arquivo
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# ============================================
# CONFIGURAÇÕES
# ============================================
prob = 1.00  # Probabilidade fixa
sre_list = [2, 4, 6, 8, 10, 12, 14, 16]  # SREs para comparar
frac_list = [25, 50, 100]  # Três frações para comparar

# Base paths para cada fração
base_paths = {
    25: Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/25/sre_variation_prob1"),
    50: Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/50/sre_variation_prob1"),
    100: Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/100/sre_variation_prob1")
}

# NOVO CAMINHO DE SAÍDA
output_figures = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/H_expoentes/SRE_v_SRC_2_p_1")
output_figures.mkdir(parents=True, exist_ok=True)

# Cores para cada fração
frac_colors = {
    25: 'blue',
    50: 'green', 
    100: 'red'
}

frac_labels = {
    25: 'Fração 25%',
    50: 'Fração 50%',
    100: 'Fração 100%'
}

frac_linestyles = {
    25: '-',
    50: '-',
    100: '-'
}

def load_exponents_for_sre(sre, frac):
    """Carrega os dados de expoentes para um dado SRE e fração"""
    base_path = base_paths[frac]
    sre_dir = base_path / f"SRE_{sre}"
    
    if not sre_dir.exists():
        return None
    
    file_pattern = f"expoentes_SRE_{sre}_tmin*.csv"
    files = list(sre_dir.glob(file_pattern))
    
    if not files:
        return None
    
    df = pd.read_csv(files[0])
    
    if 'alpha' not in df.columns:
        return None
    
    return df['alpha'].values

def plot_curves_for_sre(sre):
    """Plota apenas as curvas KDE para um SRE específico"""
    print(f"\nProcessando SRE: {sre}")
    
    # Carrega dados para todas as frações
    all_alphas = {}
    for frac in frac_list:
        alphas = load_exponents_for_sre(sre, frac)
        if alphas is not None and len(alphas) > 0:
            all_alphas[frac] = alphas
            print(f"  ✓ Fração {frac}%: {len(alphas)} runs, média={np.mean(alphas):.4f}, std={np.std(alphas):.4f}")
        else:
            print(f"  ✗ Fração {frac}%: Sem dados")
    
    if len(all_alphas) == 0:
        print(f"  ✗ Nenhum dado encontrado para SRE={sre}")
        return None
    
    # Cria o gráfico apenas com curvas
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Encontra o intervalo baseado nos dados, com margem para mostrar as caudas
    all_values = np.concatenate(list(all_alphas.values()))
    data_min = min(all_values)
    data_max = max(all_values)
    data_std = np.std(all_values)
    
    # Estende o intervalo para mostrar as caudas (onde a densidade vai a zero)
    x_min = max(0, data_min - 2*data_std)  # 2 desvios para baixo, mas não abaixo de 0
    x_max = data_max + 2*data_std          # 2 desvios para cima
    
    print(f"  Intervalo de plotagem: [{x_min:.2f}, {x_max:.2f}]")
    
    x_range = np.linspace(x_min, x_max, 500)
    
    for frac, alphas in all_alphas.items():
        # KDE
        kde = stats.gaussian_kde(alphas)
        y_values = kde(x_range)
        
        # Plota a curva
        ax.plot(x_range, y_values, color=frac_colors[frac], 
               linewidth=2.5, label=f"{frac_labels[frac]}",
               linestyle=frac_linestyles[frac])
    
    # Linha para α=1 (difusão normal)
    ax.axvline(1.0, color='black', linestyle=':', linewidth=2, alpha=0.8, 
              label='α = 1 (difusão normal)')
    
    # Configurações do gráfico
    ax.set_xlabel('Expoente α', fontsize=14)
    ax.set_ylabel('Densidade de probabilidade', fontsize=14)
    ax.set_title(f'Distribuição dos Expoentes α - SRE = {sre}, Probabilidade = {prob:.2f}', fontsize=16, fontweight='bold')
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Ajusta limites
    ax.set_xlim(0.01, 1.15)
    
    # Adiciona informação da probabilidade
    ax.text(0.98, 0.98, f"Prob = {prob:.2f}", transform=ax.transAxes, 
           ha='right', va='top', fontsize=10, style='italic',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Salva a figura (NÃO usa plt.show)
    output_file = output_figures / f"curvas_expoentes_sre_{sre}_prob{prob:.2f}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ Figura salva: {output_file}")
    print(f"    Tamanho: {output_file.stat().st_size} bytes")
    
    return fig

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("Gerando curvas de distribuição dos expoentes α")
    print(f"Probabilidade fixa = {prob:.2f}")
    print(f"SREs: {sre_list}")
    print(f"Frações: {frac_list}")
    print(f"Diretório de saída: {output_figures}")
    print("="*60)
    
    for sre in sre_list:
        plot_curves_for_sre(sre)
    
    print("\n" + "="*60)
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Figuras salvas em: {output_figures}")
    print("="*60)