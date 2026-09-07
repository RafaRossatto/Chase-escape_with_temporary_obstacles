import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para salvar em arquivo
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
import matplotlib.cm as cm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# ============================================
# CONFIGURAÇÕES - RAIO DE GIRO (Rg) - VARIAÇÃO DE PROBABILIDADE
# ============================================
sre = 2  # SRE fixo
prob_list = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
frac_list = list(range(5, 101, 5))

# Base paths para cada fração
base_paths = {frac: Path(f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/RG_sre_2_src_2_prob_v_frac_v/frac_{frac}") for frac in frac_list}

# Caminho de saída
output_figures = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/H_rg/sre_2_src_2_prob_v_all_frac")
output_figures.mkdir(parents=True, exist_ok=True)

# Criar um mapa de cores para as frações
colormap = cm.get_cmap('viridis', len(frac_list))
frac_colors = {frac: colormap(i) for i, frac in enumerate(frac_list)}
frac_labels = {frac: f'$N^{{C}}$ = {frac}$N_{0}^{{E}}$' for frac in frac_list}

# Markers variados
markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'd', '|', '_', 'P', 'X']
frac_markers = {frac: markers[i % len(markers)] for i, frac in enumerate(frac_list)}

def load_rg_for_prob_parallel(prob, frac):
    """Carrega os dados de raio de giro para uma dada probabilidade e fração a partir do arquivo consolidado"""
    base_path = base_paths[frac]
    
    # Arquivo consolidado para esta fração
    consolidated_file = base_path / f"all_runs_frac_{frac}.csv"
    
    if not consolidated_file.exists():
        return None
    
    try:
        df = pd.read_csv(consolidated_file)
        
        # Filtra pela probabilidade desejada
        df_prob = df[df['prob'] == prob]
        
        if len(df_prob) == 0:
            return None
        
        # Extrai os valores de rg_squared e calcula Rg
        rg_values = np.sqrt(df_prob['rg_squared'].values)
        
        return rg_values
        
    except Exception as e:
        print(f"  Erro ao ler {consolidated_file} para prob={prob}: {e}")
        return None

def process_single_prob_frac(prob, frac):
    """Processa uma única combinação de probabilidade e fração"""
    print(f"  Processando prob={prob:.2f}, frac={frac}%...")
    rg_values = load_rg_for_prob_parallel(prob, frac)
    
    if rg_values is not None and len(rg_values) > 0:
        return {
            'prob': prob,
            'frac': frac,
            'rg_values': rg_values,
            'mean': np.mean(rg_values),
            'std': np.std(rg_values),
            'n_samples': len(rg_values)
        }
    return None

def plot_curves_for_prob(prob, all_results):
    """Plota as curvas KDE para uma probabilidade específica usando resultados já carregados"""
    print(f"\nPlotando Probabilidade: {prob:.2f}")
    
    # Filtra resultados para esta probabilidade
    prob_results = {res['frac']: res for res in all_results if res['prob'] == prob}
    
    if len(prob_results) == 0:
        print(f"  ✗ Nenhum dado encontrado para Prob={prob:.2f}")
        return None
    
    # Cria o gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Encontra o intervalo baseado nos dados
    all_values = np.concatenate([res['rg_values'] for res in prob_results.values()])
    p1, p99 = np.percentile(all_values, [1, 99])
    x_min = min(all_values)
    x_max = max(all_values)
    
    print(f"  Intervalo de plotagem: [{x_min:.4f}, {x_max:.4f}]")
    
    x_range = np.linspace(x_min, x_max, 500)
    
    marker_list = ['o', 's', '^', 'v', 'D', '*', 'p', 'h', 'X', 'd',
                   'P', 'H', '8', '>', '<', '1', '2', '3', '4', '+']
    
    # ORDENAR AS FRAÇÕES antes de plotar
    sorted_fracs = sorted(prob_results.keys())  # Ordem crescente
    
    for i, frac in enumerate(sorted_fracs):
        res = prob_results[frac]
        # KDE
        try:
            kde = stats.gaussian_kde(res['rg_values'])
            y_values = kde(x_range)
            
            marker = marker_list[i % len(marker_list)]
            
            ax.plot(x_range, y_values, 
                color=frac_colors[frac], 
                linewidth=2, 
                label=f"{frac_labels[frac]}",
                linestyle='-', 
                alpha=0.8,
                marker=marker,
                markersize=5,
                markevery=8,
                markerfacecolor='white',
                markeredgewidth=1.5)
        except Exception as e:
            print(f"  Erro no KDE para fração {frac}%: {e}")

    ax.set_xlabel(r'$R_{G}$', fontsize=14)
    ax.set_ylabel('Probability density', fontsize=14)
    ax.axvline(x=2.0, 
               color='red',           
               linestyle='--',        
               linewidth=2,           
               alpha=0.7,             
               label=r'$R_{g} = 2$')       

    n_frac = len(prob_results)
    ncol = 2 if n_frac > 10 else (3 if n_frac > 15 else 1)
    ax.legend(loc='upper right', fontsize=12, ncol=ncol, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.05, 13.00)
    
    ax.text(0.98, 0.98, f"SRE = {sre}", transform=ax.transAxes, 
           ha='right', va='top', fontsize=10, style='italic',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    output_file = output_figures / f"curvas_rg_prob_{prob:.2f}_SRE_{sre}.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ Figura salva: {output_file}")
    return fig

def plot_summary_statistics(all_results):
    """Plota um resumo das médias e desvios usando resultados já carregados"""
    print("\n" + "="*60)
    print("Gerando gráfico de resumo (médias e desvios do Rg)")
    print("="*60)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Organiza dados por fração
    summary_data = {frac: {'probs': [], 'means': [], 'stds': []} for frac in frac_list}
    
    for res in all_results:
        frac = res['frac']
        prob = res['prob']
        summary_data[frac]['probs'].append(prob)
        summary_data[frac]['means'].append(res['mean'])
        summary_data[frac]['stds'].append(res['std'])
    
    # Plotar apenas frações com dados
    for frac in frac_list:
        if summary_data[frac]['probs']:
            # Ordena por probabilidade
            sorted_indices = np.argsort(summary_data[frac]['probs'])
            probs_sorted = np.array(summary_data[frac]['probs'])[sorted_indices]
            means_sorted = np.array(summary_data[frac]['means'])[sorted_indices]
            stds_sorted = np.array(summary_data[frac]['stds'])[sorted_indices]
            
            ax.errorbar(probs_sorted, means_sorted,
                       yerr=stds_sorted,
                       color=frac_colors[frac],
                       marker=frac_markers[frac],
                       capsize=3, capthick=1.5, elinewidth=1.5,
                       markersize=5, linewidth=1.5, alpha=0.7,
                       label=f"{frac_labels[frac]}")
    
    ax.set_xlabel(r'$P$', fontsize=14)
    ax.set_ylabel(r'$\langle R_{g} \rangle$', fontsize=14)
    ax.set_title(f'$SR = {sre}$', 
                fontsize=16, fontweight='bold')
    
    n_frac = len([f for f in frac_list if summary_data[f]['probs']])
    ncol = 2 if n_frac > 10 else (3 if n_frac > 15 else 1)
    ax.legend(loc='best', fontsize=12, ncol=ncol, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.05, 1.05)
    
    plt.tight_layout()
    
    output_file = output_figures / f"summary_rg_vs_prob_SRE_{sre}.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Figura de resumo salva: {output_file}")

# ============================================
# EXECUÇÃO PRINCIPAL COM PARALELISMO
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("Gerando curvas de distribuição do Raio de Giro (Rg) - VERSÃO PARALELA")
    print(f"SRE fixo = {sre}")
    print(f"Probabilidades: {len(prob_list)} valores")
    print(f"Frações: {len(frac_list)} valores de {min(frac_list)} a {max(frac_list)}")
    print(f"Diretório de saída: {output_figures}")
    print("="*60)
    
# Verifica alguns arquivos consolidados
    print("\nVerificando arquivos de entrada (amostra):")
    test_fracs = [25, 50, 100]
    for frac in test_fracs:
        if frac in base_paths:
            test_file = base_paths[frac] / f"all_runs_frac_{frac}.csv"
            if test_file.exists():
                df_test = pd.read_csv(test_file)
                n_probs = df_test['prob'].nunique()
                n_rows = len(df_test)
                print(f"  ✓ Fração {frac}%: {n_rows} linhas, {n_probs} probabilidades")
            else:
                print(f"  ✗ Fração {frac}%: {test_file} NÃO ENCONTRADO")
    
    print("\n" + "="*60)
    print("Iniciando processamento paralelo por combinação (prob, frac)...")
    print("="*60)
    
    # Gera todas as combinações
    combinations = [(prob, frac) for prob in prob_list for frac in frac_list]
    print(f"Total de combinações: {len(combinations)}")
    
    # Processa combinações em paralelo
    all_results = []
    n_cores = min(mp.cpu_count(), len(combinations))
    print(f"Usando {n_cores} núcleos\n")
    
    with ProcessPoolExecutor(max_workers=n_cores) as executor:
        # Submete todas as combinações
        future_to_comb = {executor.submit(process_single_prob_frac, prob, frac): (prob, frac) 
                         for prob, frac in combinations}
        
        # Coleta os resultados
        completed = 0
        for future in as_completed(future_to_comb):
            prob, frac = future_to_comb[future]
            try:
                result = future.result()
                if result:
                    all_results.append(result)
                completed += 1
                if completed % 20 == 0:  # Print a cada 20 combinações
                    print(f"  Progresso: {completed}/{len(combinations)} combinações processadas")
            except Exception as e:
                print(f"  Erro na combinação prob={prob:.2f}, frac={frac}%: {e}")
    
    print(f"\nProcessamento concluído! {len(all_results)} combinações bem-sucedidas")
    
    # Gera gráficos usando os resultados já carregados
    print("\n" + "="*60)
    print("Gerando gráficos...")
    print("="*60)
    
    for prob in prob_list:
        plot_curves_for_prob(prob, all_results)
    
    plot_summary_statistics(all_results)
    
    print("\n" + "="*60)
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Figuras salvas em: {output_figures}")
    print("="*60)