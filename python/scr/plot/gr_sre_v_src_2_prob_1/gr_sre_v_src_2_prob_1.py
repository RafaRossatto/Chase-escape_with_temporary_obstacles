import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para salvar em arquivo
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# ============================================
# CONFIGURAÇÕES - RAIO DE GIRO (Rg)
# ============================================
prob = 0.50  # Probabilidade fixa
sre_list = [2, 4, 6, 8, 10, 12, 14, 16]  # SREs para comparar
frac_list = [25, 50, 100]  # Três frações para comparar

# Base paths para cada fração - DADOS DE RAIO DE GIRO
base_paths = {
    25: Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/gyration_radius/sre_v_src_2_p_05/frac_25"),
    50: Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/gyration_radius/sre_v_src_2_p_05/frac_50"),
    100: Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/gyration_radius/sre_v_src_2_p_05/frac_100")
}

# Caminho de saída para os plots
output_figures = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/H_rg/sre_v_src_2_prob_05")
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

def load_rg_for_sre(sre, frac):
    """Carrega os dados de raio de giro (coluna Rg) do arquivo all_particles para um dado SRE e fração"""
    base_path = base_paths[frac]
    sre_dir = base_path / f"SRE_{sre}"
    
    if not sre_dir.exists():
        return None
    
    # Procura pelo arquivo all_particles
    all_particles_files = list(sre_dir.glob("*all_particles*.csv"))
    
    # Se não encontrar com all_particles, tenta qualquer arquivo CSV
    if not all_particles_files:
        all_particles_files = list(sre_dir.glob("*.csv"))
    
    if not all_particles_files:
        return None
    
    # Usa o primeiro arquivo encontrado
    file_path = all_particles_files[0]
    print(f"    Lendo arquivo: {file_path.name}")
    
    df = pd.read_csv(file_path)
    
    # Verifica se a coluna 'Rg' existe
    if 'Rg' not in df.columns:
        print(f"    ERRO: Coluna 'Rg' não encontrada. Colunas disponíveis: {list(df.columns)}")
        return None
    
    return df['Rg'].values

def plot_curves_for_sre(sre):
    """Plota as curvas KDE para o raio de giro de um SRE específico"""
    print(f"\nProcessando SRE: {sre}")
    
    # Carrega dados para todas as frações
    all_rg = {}
    for frac in frac_list:
        print(f"  Buscando fração {frac}%:")
        rg_values = load_rg_for_sre(sre, frac)
        if rg_values is not None and len(rg_values) > 0:
            all_rg[frac] = rg_values
            print(f"    ✓ {len(rg_values)} amostras, média={np.mean(rg_values):.4f}, std={np.std(rg_values):.4f}")
        else:
            print(f"    ✗ Sem dados")
    
    if len(all_rg) == 0:
        print(f"  ✗ Nenhum dado encontrado para SRE={sre}")
        return None
    
    # Cria o gráfico com as curvas KDE
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Encontra o intervalo baseado nos dados
    all_values = np.concatenate(list(all_rg.values()))
    data_min = min(all_values)
    data_max = max(all_values)
    data_std = np.std(all_values)
    
    # Estende o intervalo para mostrar as caudas
    x_min = max(0, data_min - 2*data_std)
    x_max = data_max + 2*data_std
    
    print(f"  Intervalo de plotagem: [{x_min:.4f}, {x_max:.4f}]")
    
    x_range = np.linspace(x_min, x_max, 500)
    
    for frac, rg_values in all_rg.items():
        # KDE
        try:
            kde = stats.gaussian_kde(rg_values)
            y_values = kde(x_range)
            
            # Plota a curva
            ax.plot(x_range, y_values, color=frac_colors[frac], 
                   linewidth=2.5, label=f"{frac_labels[frac]}",
                   linestyle=frac_linestyles[frac])
        except Exception as e:
            print(f"  Erro no KDE para fração {frac}%: {e}")
    
    # Configurações do gráfico
    ax.set_xlabel('Raio de Giro (Rg)', fontsize=14)
    ax.set_ylabel('Densidade de probabilidade', fontsize=14)
    ax.set_title(f'Distribuição do Raio de Giro - SRE = {sre}, Probabilidade = {prob:.2f}', fontsize=16, fontweight='bold')
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Adiciona informação da probabilidade
    ax.text(0.98, 0.98, f"Prob = {prob:.2f}", transform=ax.transAxes, 
           ha='right', va='top', fontsize=10, style='italic',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Salva a figura
    output_file = output_figures / f"curvas_rg_sre_{sre}_prob{prob:.2f}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ Figura salva: {output_file}")
    print(f"    Tamanho: {output_file.stat().st_size} bytes")
    
    return fig

def plot_summary_statistics():
    """Plota um resumo das médias e desvios do raio de giro para todos os SREs"""
    print("\n" + "="*60)
    print("Gerando gráfico de resumo (médias e desvios do Rg)")
    print("="*60)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    summary_data = {frac: {'sres': [], 'means': [], 'stds': []} for frac in frac_list}
    
    for sre in sre_list:
        for frac in frac_list:
            rg_values = load_rg_for_sre(sre, frac)
            if rg_values is not None and len(rg_values) > 0:
                summary_data[frac]['sres'].append(sre)
                summary_data[frac]['means'].append(np.mean(rg_values))
                summary_data[frac]['stds'].append(np.std(rg_values))
    
    for frac in frac_list:
        if summary_data[frac]['sres']:
            ax.errorbar(summary_data[frac]['sres'], 
                       summary_data[frac]['means'],
                       yerr=summary_data[frac]['stds'],
                       color=frac_colors[frac],
                       marker='o',
                       capsize=5,
                       capthick=2,
                       elinewidth=2,
                       markersize=8,
                       linewidth=2,
                       label=f"{frac_labels[frac]}")
    
    ax.set_xlabel('SRE', fontsize=14)
    ax.set_ylabel('Raio de Giro (média ± desvio)', fontsize=14)
    ax.set_title(f'Evolução do Raio de Giro com SRE - Probabilidade = {prob:.2f}', fontsize=16, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    output_file = output_figures / f"summary_rg_vs_sre_prob{prob:.2f}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Figura de resumo salva: {output_file}")
    print(f"  Tamanho: {output_file.stat().st_size} bytes")

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("Gerando curvas de distribuição do Raio de Giro (Rg)")
    print(f"Probabilidade fixa = {prob:.2f}")
    print(f"SREs: {sre_list}")
    print(f"Frações: {frac_list}")
    print(f"Diretório de saída: {output_figures}")
    print("="*60)
    
    # Verifica se os diretórios de entrada existem
    print("\nVerificando diretórios de entrada:")
    for frac in frac_list:
        if base_paths[frac].exists():
            print(f"  ✓ Diretório para fração {frac}%: {base_paths[frac]}")
            # Lista os subdiretórios SRE encontrados
            sre_dirs = [d.name for d in base_paths[frac].iterdir() if d.is_dir()]
            print(f"    Subdiretórios encontrados: {sre_dirs}")
        else:
            print(f"  ✗ Diretório para fração {frac}% NÃO ENCONTRADO: {base_paths[frac]}")
    
    print("\n" + "="*60)
    
    # Gera curvas para cada SRE
    for sre in sre_list:
        plot_curves_for_sre(sre)
    
    # Gera gráfico de resumo
    plot_summary_statistics()
    
    print("\n" + "="*60)
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Figuras salvas em: {output_figures}")
    print("="*60)