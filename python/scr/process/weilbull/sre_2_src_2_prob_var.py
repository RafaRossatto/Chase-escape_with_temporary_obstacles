import pandas as pd
import numpy as np
import os
from scipy.optimize import curve_fit

# IMPORTANTE: Configurar o backend ANTES de importar matplotlib.pyplot
import matplotlib
matplotlib.use('Agg')

# Agora sim, importar pyplot
import matplotlib.pyplot as plt

# ============================================
# CONFIGURAÇÃO
# ============================================

base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/sre_2_src_2_prob_v_frac_v/"

# Lista de probabilidades e frações a serem processadas
probabilidades = [round(p, 2) for p in np.arange(0.00, 1.01, 0.10)]
fracoes = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

# Número máximo de runs esperado
num_runs = 100

# Pasta base para todos os resultados
base_output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/resultados_fit_exponecial_multiplos/prob_v"
os.makedirs(base_output_dir, exist_ok=True)

# ============================================
# FUNÇÃO MODELO WEIBULL (β será calculado)
# ============================================

def weibull_decay(t, A, tau, beta, C):
    """Decaimento Weibull: N(t) = A * exp(-(t/tau)^beta) + C"""
    return A * np.exp(-(t / tau)**beta) + C

# ============================================
# FUNÇÃO PARA PROCESSAR UMA CONFIGURAÇÃO
# ============================================

def process_configuracao(prob, frac, num_runs=100):
    """
    Processa uma combinação de probabilidade e fração
    Calcula β (Weibull) para cada run
    """
    
    print(f"\n{'='*70}")
    print(f"PROCESSANDO: prob = {prob:.2f}, frac = {frac}")
    print(f"{'='*70}")
    
    # Criar pasta específica para esta configuração
    config_dir = f"{base_output_dir}/prob_{prob:.2f}_frac_{frac}"
    os.makedirs(config_dir, exist_ok=True)
    
    # Encontrar arquivos
    caminhos_validos = []
    runs_validos = []
    
    for run in range(1, num_runs + 1):
        caminho_pasta = f"{base_path}simulation_frac_{frac}_run_{run}_obsprob_{prob:.2f}_SRC_2_SRE_2"
        caminho_arquivo = f"{caminho_pasta}/results_N_escapers_run{run}.csv"
        if os.path.exists(caminho_arquivo):
            caminhos_validos.append(caminho_arquivo)
            runs_validos.append(run)
    
    print(f"  ✓ Encontrados {len(caminhos_validos)} arquivos")
    
    if len(caminhos_validos) == 0:
        print(f"  ✗ Nenhum arquivo encontrado! Pulando...")
        return None, None
    
    # Fit Weibull para cada run (β será calculado)
    resultados = []
    dados_para_plot = []
    
    for idx, (run_num, caminho) in enumerate(zip(runs_validos, caminhos_validos), 1):
        try:
            df = pd.read_csv(caminho)
            col_time = 'time'
            col_ne = [col for col in df.columns if col != 'time'][0]
            
            tempo = df[col_time].values
            ne = df[col_ne].values
            
            # Chutes iniciais para Weibull
            A_guess = ne[0] - ne[-1]
            C_guess = ne[-1]
            tau_guess = tempo[len(tempo)//3] if len(tempo) > 3 else tempo[-1]/2
            beta_guess = 1.5  # chute inicial para β (Weibull)
            
            # Fit Weibull (4 parâmetros)
            popt, pcov = curve_fit(weibull_decay, tempo, ne,
                                  p0=[A_guess, tau_guess, beta_guess, C_guess],
                                  bounds=([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf]),
                                  maxfev=5000)
            
            A_fit, tau_fit, beta_fit, C_fit = popt
            perr = np.sqrt(np.diag(pcov))
            
            # R²
            residuos = ne - weibull_decay(tempo, A_fit, tau_fit, beta_fit, C_fit)
            ss_res = np.sum(residuos**2)
            ss_tot = np.sum((ne - np.mean(ne))**2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Meia-vida para Weibull
            # N(t) = A*exp(-(t/tau)^beta) + C
            # Meia vida quando A*exp(-(t/tau)^beta) = A/2
            # => exp(-(t/tau)^beta) = 1/2 => (t/tau)^beta = ln(2)
            # => t = tau * (ln(2))^(1/beta)
            half_life = tau_fit * (np.log(2))**(1/beta_fit) if beta_fit > 0 else 0
            
            resultados.append({
                'run': run_num,
                'A': A_fit,
                'A_err': perr[0],
                'tau': tau_fit,
                'tau_err': perr[1],
                'beta': beta_fit,
                'beta_err': perr[2],
                'C': C_fit,
                'C_err': perr[3],
                'r_squared': r_squared,
                'half_life': half_life,
                'N0_real': ne[0],
                'Ninf_real': ne[-1]
            })
            
            # Guardar primeiros 5 runs para exemplo
            if idx <= 5:
                dados_para_plot.append({
                    'run': run_num,
                    'tempo': tempo,
                    'ne': ne,
                    'fit': weibull_decay(tempo, A_fit, tau_fit, beta_fit, C_fit),
                    'beta': beta_fit,
                    'tau': tau_fit
                })
            
            if idx % 20 == 0:
                print(f"    Processados {idx}/{len(caminhos_validos)} runs...")
                
        except Exception as e:
            print(f"    ⚠️ Erro no run {run_num}: {e}")
            continue
    
    if len(resultados) == 0:
        print(f"  ✗ Nenhum fit bem sucedido!")
        return None, None
    
    # Converter para DataFrame
    df_resultados = pd.DataFrame(resultados)
    
    # Salvar CSV completo
    csv_path = f"{config_dir}/resultados_fits_por_run.csv"
    df_resultados.to_csv(csv_path, index=False)
    
    # Salvar resumo (run, tau, beta - AGORA β É CALCULADO)
    df_resumido = df_resultados[['run', 'tau', 'tau_err', 'beta', 'beta_err', 'r_squared', 'half_life']].copy()
    csv_resumido_path = f"{config_dir}/resumo_tau_beta.csv"
    df_resumido.to_csv(csv_resumido_path, index=False)
    
    print(f"  ✓ CSV salvos em: {config_dir}")
    
    # Estatísticas
    tau_mean = df_resultados['tau'].mean()
    tau_std = df_resultados['tau'].std()
    tau_median = df_resultados['tau'].median()
    tau_cv = tau_std / tau_mean if tau_mean > 0 else 0
    
    beta_mean = df_resultados['beta'].mean()
    beta_std = df_resultados['beta'].std()
    beta_median = df_resultados['beta'].median()
    
    r2_mean = df_resultados['r_squared'].mean()
    
    stats = {
        'prob': prob,
        'frac': frac,
        'n_runs': len(resultados),
        'tau_mean': tau_mean,
        'tau_std': tau_std,
        'tau_median': tau_median,
        'tau_cv': tau_cv,
        'beta_mean': beta_mean,
        'beta_std': beta_std,
        'beta_median': beta_median,
        'r2_mean': r2_mean,
        'tau_min': df_resultados['tau'].min(),
        'tau_max': df_resultados['tau'].max(),
        'beta_min': df_resultados['beta'].min(),
        'beta_max': df_resultados['beta'].max()
    }
    
    # ============================================
    # GERAR GRÁFICOS
    # ============================================
    
    # Gráfico 1: Histograma do τ
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.hist(df_resultados['tau'], bins=20, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(tau_mean, color='red', linestyle='--', linewidth=2, label=f'Média τ = {tau_mean:.2f}')
    ax1.axvline(tau_median, color='green', linestyle='--', linewidth=2, label=f'Mediana τ = {tau_median:.2f}')
    ax1.set_xlabel('τ (tempo característico)', fontsize=12)
    ax1.set_ylabel('Frequência', fontsize=12)
    ax1.set_title(f'Distribuição de τ - prob={prob:.2f}, frac={frac}', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{config_dir}/histograma_tau.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # Gráfico 2: Histograma do β
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.hist(df_resultados['beta'], bins=20, edgecolor='black', alpha=0.7, color='coral')
    ax2.axvline(beta_mean, color='red', linestyle='--', linewidth=2, label=f'Média β = {beta_mean:.4f}')
    ax2.axvline(beta_median, color='green', linestyle='--', linewidth=2, label=f'Mediana β = {beta_median:.4f}')
    ax2.axvline(1.0, color='purple', linestyle='--', linewidth=2, alpha=0.7, label='β = 1 (exponencial)')
    ax2.set_xlabel('β (expoente de forma)', fontsize=12)
    ax2.set_ylabel('Frequência', fontsize=12)
    ax2.set_title(f'Distribuição de β - prob={prob:.2f}, frac={frac}', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{config_dir}/histograma_beta.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # Gráfico 3: τ por run
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    runs_order = df_resultados['run'].values
    tau_values = df_resultados['tau'].values
    tau_errors = df_resultados['tau_err'].values
    
    ax3.errorbar(runs_order, tau_values, yerr=tau_errors, fmt='o', 
                 capsize=3, markersize=4, alpha=0.7, color='blue')
    ax3.axhline(tau_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {tau_mean:.2f}')
    ax3.fill_between([runs_order.min(), runs_order.max()], 
                      tau_mean - tau_std, tau_mean + tau_std, 
                      alpha=0.2, color='red', label=f'±1σ = {tau_std:.2f}')
    ax3.set_xlabel('Número do Run', fontsize=12)
    ax3.set_ylabel('τ', fontsize=12)
    ax3.set_title(f'τ por run - prob={prob:.2f}, frac={frac}', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{config_dir}/tau_por_run.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # Gráfico 4: β por run
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    beta_values = df_resultados['beta'].values
    beta_errors = df_resultados['beta_err'].values
    
    ax4.errorbar(runs_order, beta_values, yerr=beta_errors, fmt='s', 
                 capsize=3, markersize=4, alpha=0.7, color='green')
    ax4.axhline(beta_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {beta_mean:.4f}')
    ax4.axhline(1.0, color='purple', linestyle='--', linewidth=2, alpha=0.7, label='β = 1')
    ax4.fill_between([runs_order.min(), runs_order.max()], 
                      beta_mean - beta_std, beta_mean + beta_std, 
                      alpha=0.2, color='red', label=f'±1σ = {beta_std:.4f}')
    ax4.set_xlabel('Número do Run', fontsize=12)
    ax4.set_ylabel('β', fontsize=12)
    ax4.set_title(f'β por run - prob={prob:.2f}, frac={frac}', fontsize=12)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{config_dir}/beta_por_run.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    # Gráfico 5: Exemplos de fits (primeiros 5 runs)
    if dados_para_plot:
        n_exemplos = len(dados_para_plot)
        fig5, axes = plt.subplots(1, n_exemplos, figsize=(15, 4))
        if n_exemplos == 1:
            axes = [axes]
        
        for idx, dado in enumerate(dados_para_plot):
            ax = axes[idx]
            ax.plot(dado['tempo'], dado['ne'], 'bo-', markersize=3, linewidth=1, alpha=0.7, label='Dados')
            ax.plot(dado['tempo'], dado['fit'], 'r-', linewidth=2, label=f'Weibull: β={dado["beta"]:.3f}')
            ax.set_title(f'Run {dado["run"]} (τ={dado["tau"]:.1f}, β={dado["beta"]:.3f})', fontsize=9)
            ax.set_xlabel('Tempo')
            ax.set_ylabel('NE')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=7)
        
        plt.suptitle(f'Fits Weibull - prob={prob:.2f}, frac={frac}', fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{config_dir}/exemplos_fits.png", dpi=150, bbox_inches='tight')
        plt.close()
    
    print(f"  ✓ Gráficos salvos em: {config_dir}")
    print(f"\n  Estatísticas para prob={prob:.2f}, frac={frac}:")
    print(f"    τ = {tau_mean:.4f} ± {tau_std:.4f} (CV = {tau_cv:.3f})")
    print(f"    β = {beta_mean:.4f} ± {beta_std:.4f}")
    print(f"    R² médio = {r2_mean:.4f}")
    
    # Interpretação do β médio
    if beta_mean < 0.9:
        print(f"    → β < 0.9: Decaimento MAIS LENTO que exponencial")
    elif beta_mean > 1.1:
        print(f"    → β > 1.1: Decaimento MAIS RÁPIDO que exponencial")
    else:
        print(f"    → β ≈ 1: Decaimento aproximadamente EXPONENCIAL")
    
    return df_resultados, stats

# ============================================
# PROCESSAR TODAS CONFIGURAÇÕES
# ============================================

print("="*80)
print("FIT WEIBULL PARA MÚLTIPLAS CONFIGURAÇÕES (β será CALCULADO)")
print("="*80)

print(f"\nConfigurações a processar:")
print(f"  Probabilidades: {probabilidades}")
print(f"  Frações: {fracoes}")
print(f"  Total: {len(probabilidades) * len(fracoes)} combinações")

# Lista para armazenar estatísticas de todas configurações
todas_estatisticas = []

for prob in probabilidades:
    for frac in fracoes:
        df_res, stats = process_configuracao(prob, frac, num_runs)
        if stats is not None:
            todas_estatisticas.append(stats)

# ============================================
# SALVAR RESUMO GERAL
# ============================================

print("\n" + "="*80)
print("SALVANDO RESUMO GERAL")
print("="*80)

if todas_estatisticas:
    df_geral = pd.DataFrame(todas_estatisticas)
    
    # Salvar CSV com resumo de todas configurações
    csv_geral_path = f"{base_output_dir}/resumo_geral_todas_configuracoes.csv"
    df_geral.to_csv(csv_geral_path, index=False)
    print(f"✓ Resumo geral salvo em: {csv_geral_path}")
    
    # ============================================
    # GRÁFICO 1: τ vs Probabilidade (para diferentes frações)
    # ============================================
    
    print("\n[Gerando gráficos comparativos...]")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    cores = {25: 'blue', 50: 'green', 100: 'red'}
    marcadores = {25: 'o', 50: 's', 100: '^'}
    
    # Gráfico 1: τ vs probabilidade
    ax1 = axes[0, 0]
    for frac in fracoes:
        df_frac = df_geral[df_geral['frac'] == frac]
        if not df_frac.empty:
            ax1.errorbar(df_frac['prob'], df_frac['tau_mean'], yerr=df_frac['tau_std'],
                        fmt=f"{marcadores[frac]}-", capsize=5, markersize=8, linewidth=2,
                        color=cores[frac], label=f'frac={frac}')
    ax1.set_xlabel('Probabilidade', fontsize=12)
    ax1.set_ylabel('τ (tempo característico)', fontsize=12)
    ax1.set_title('τ vs Probabilidade', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: β vs probabilidade
    ax2 = axes[0, 1]
    for frac in fracoes:
        df_frac = df_geral[df_geral['frac'] == frac]
        if not df_frac.empty:
            ax2.errorbar(df_frac['prob'], df_frac['beta_mean'], yerr=df_frac['beta_std'],
                        fmt=f"{marcadores[frac]}-", capsize=5, markersize=8, linewidth=2,
                        color=cores[frac], label=f'frac={frac}')
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='β = 1 (exponencial)')
    ax2.set_xlabel('Probabilidade', fontsize=12)
    ax2.set_ylabel('β (expoente de forma)', fontsize=12)
    ax2.set_title('β vs Probabilidade', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Gráfico 3: R² vs probabilidade
    ax3 = axes[1, 0]
    for frac in fracoes:
        df_frac = df_geral[df_geral['frac'] == frac]
        if not df_frac.empty:
            ax3.plot(df_frac['prob'], df_frac['r2_mean'], f"{marcadores[frac]}-", 
                    markersize=8, linewidth=2, color=cores[frac], label=f'frac={frac}')
    ax3.set_xlabel('Probabilidade', fontsize=12)
    ax3.set_ylabel('R² médio', fontsize=12)
    ax3.set_title('Qualidade do Fit vs Probabilidade', fontsize=12, fontweight='bold')
    ax3.set_ylim([0.95, 1.005])
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Gráfico 4: Número de runs vs probabilidade
    ax4 = axes[1, 1]
    for frac in fracoes:
        df_frac = df_geral[df_geral['frac'] == frac]
        if not df_frac.empty:
            ax4.bar(df_frac['prob'] - 0.02*(frac/50), df_frac['n_runs'], 
                   width=0.02, label=f'frac={frac}', alpha=0.7, color=cores[frac])
    ax4.set_xlabel('Probabilidade', fontsize=12)
    ax4.set_ylabel('Número de runs válidos', fontsize=12)
    ax4.set_title('Runs processados vs Probabilidade', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Resultados Weibull (β calculado)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{base_output_dir}/comparacao_weibull.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gráfico comparativo salvo em: {base_output_dir}/comparacao_weibull.png")
    
    # ============================================
    # GRÁFICO ESPECÍFICO: β vs Probabilidade (mais detalhado)
    # ============================================
    
    fig_beta, ax_beta = plt.subplots(figsize=(12, 8))
    
    for frac in fracoes:
        df_frac = df_geral[df_geral['frac'] == frac]
        if not df_frac.empty:
            ax_beta.errorbar(df_frac['prob'], df_frac['beta_mean'], yerr=df_frac['beta_std'],
                            fmt=f"{marcadores[frac]}-", capsize=6, markersize=10, linewidth=2.5,
                            color=cores[frac], ecolor=cores[frac], alpha=0.8,
                            label=f'frac = {frac}')
            
            # Adicionar valores nos pontos
            for _, row in df_frac.iterrows():
                ax_beta.annotate(f'{row["beta_mean"]:.3f}', (row['prob'], row['beta_mean']),
                                xytext=(5, 5), textcoords='offset points', fontsize=8, alpha=0.7)
    
    ax_beta.axhline(y=1.0, color='red', linestyle='--', linewidth=2.5, alpha=0.8,
                    label='β = 1 (exponencial puro)')
    ax_beta.axhspan(0.9, 1.1, alpha=0.1, color='red', label='Região exponencial (β ≈ 1)')
    
    ax_beta.set_xlabel('Probabilidade', fontsize=14)
    ax_beta.set_ylabel('β médio', fontsize=14)
    ax_beta.set_title('β médio vs Probabilidade (Weibull - β calculado)', 
                      fontsize=14, fontweight='bold')
    ax_beta.legend(loc='best', fontsize=12)
    ax_beta.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{base_output_dir}/beta_medio_vs_prob.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Gráfico β médio salvo em: {base_output_dir}/beta_medio_vs_prob.png")
    
    # ============================================
    # IMPRIMIR RESUMO
    # ============================================
    
    print("\n" + "="*80)
    print("RESUMO FINAL - TODAS CONFIGURAÇÕES (β CALCULADO)")
    print("="*80)
    
    for stats in todas_estatisticas:
        print(f"\nprob = {stats['prob']:.2f}, frac = {stats['frac']}:")
        print(f"  • Runs processados: {stats['n_runs']}")
        print(f"  • τ = {stats['tau_mean']:.4f} ± {stats['tau_std']:.4f}")
        print(f"  • β = {stats['beta_mean']:.4f} ± {stats['beta_std']:.4f}")
        print(f"  • R² médio = {stats['r2_mean']:.4f}")
        
        # Interpretação
        if stats['beta_mean'] < 0.9:
            print(f"    → Decaimento MAIS LENTO que exponencial")
        elif stats['beta_mean'] > 1.1:
            print(f"    → Decaimento MAIS RÁPIDO que exponencial")
        else:
            print(f"    → Decaimento aproximadamente EXPONENCIAL")
    
    print("\n" + "="*80)
    print(f"✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"📁 Resultados salvos em: {base_output_dir}/")
    print("="*80)
    
    print("\nEstrutura de pastas criada:")
    print(f"{base_output_dir}/")
    for prob in probabilidades:
        for frac in fracoes:
            print(f"  └── prob_{prob:.2f}_frac_{frac}/")
            print(f"      ├── resultados_fits_por_run.csv")
            print(f"      ├── resumo_tau_beta.csv (AGORA COM β CALCULADO)")
            print(f"      ├── histograma_tau.png")
            print(f"      ├── histograma_beta.png")
            print(f"      ├── tau_por_run.png")
            print(f"      ├── beta_por_run.png")
            print(f"      └── exemplos_fits.png")
    
else:
    print("⚠️ Nenhuma configuração foi processada com sucesso!")
    print("   Verifique se os caminhos dos dados estão corretos.")

print("\n" + "="*80)


# import pandas as pd
# import numpy as np
# import os
# from scipy.optimize import curve_fit

# # IMPORTANTE: Configurar o backend ANTES de importar matplotlib.pyplot
# import matplotlib
# matplotlib.use('Agg')

# # Agora sim, importar pyplot
# import matplotlib.pyplot as plt

# # ============================================
# # CONFIGURAÇÃO
# # ============================================

# base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/v_prob/"

# # Lista de probabilidades e frações a serem processadas
# # AJUSTE ESTES VALORES CONFORME SEUS DADOS!
# probabilidades = [0.00,0.10,0.20,0.30,0.40,0.50, 0.60, 0.70, 0.80, 0.90,1.00]  # Exemplo - ajuste conforme necessário
# fracoes = [25,50,100]  # Exemplo: frac=100 (pelo que vi nos nomes dos arquivos)

# # Número máximo de runs esperado
# num_runs = 100

# # Pasta base para todos os resultados
# base_output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/resultados_fit_exponencial_multiplos/sre_2_src_2_prob_v"
# os.makedirs(base_output_dir, exist_ok=True)

# # ============================================
# # FUNÇÃO MODELO EXPONENCIAL
# # ============================================

# def exponential_decay(t, A, tau, C):
#     """Decaimento exponencial com assíntota: N(t) = A*exp(-t/tau) + C"""
#     return A * np.exp(-t / tau) + C

# # ============================================
# # FUNÇÃO PARA PROCESSAR UMA CONFIGURAÇÃO
# # ============================================

# def process_configuracao(prob, frac, num_runs=100):
#     """
#     Processa uma combinação de probabilidade e fração
    
#     Parâmetros:
#     - prob: probabilidade dos obstáculos (ex: 0.60)
#     - frac: fração (ex: 100)
#     - num_runs: número máximo de runs esperados
    
#     Retorna:
#     - df_resultados: DataFrame com resultados de cada run
#     - stats: dicionário com estatísticas
#     """
    
#     print(f"\n{'='*70}")
#     print(f"PROCESSANDO: prob = {prob:.2f}, frac = {frac}")
#     print(f"{'='*70}")
    
#     # Criar pasta específica para esta configuração
#     config_dir = f"{base_output_dir}/prob_{prob:.2f}_frac_{frac}"
#     os.makedirs(config_dir, exist_ok=True)
    
#     # Encontrar arquivos
#     caminhos_validos = []
#     runs_validos = []
    
#     for run in range(1, num_runs + 1):
#         #caminho_pasta = f"{base_path}simulation_frac_{frac}run{run}obsprob{prob:.2f}"
#         #caminho_arquivo = f"{caminho_pasta}/results_N_escapers_run{run}.csv"
#         caminho_pasta = f"{base_path}simulation_frac_{frac}_run_{run}_obsprob_{prob:.2f}_SRC_2_SRE_2"
#         caminho_arquivo = f"{caminho_pasta}/results_N_escapers_run{run}.csv"
#         if os.path.exists(caminho_arquivo):
#             caminhos_validos.append(caminho_arquivo)
#             runs_validos.append(run)
    
#     print(f"  ✓ Encontrados {len(caminhos_validos)} arquivos")
    
#     if len(caminhos_validos) == 0:
#         print(f"  ✗ Nenhum arquivo encontrado! Pulando...")
#         return None, None
    
#     # Fit para cada run
#     resultados = []
#     dados_para_plot = []  # Guardar primeiros runs para exemplos
    
#     for idx, (run_num, caminho) in enumerate(zip(runs_validos, caminhos_validos), 1):
#         try:
#             df = pd.read_csv(caminho)
#             col_time = 'time'
#             col_ne = [col for col in df.columns if col != 'time'][0]
            
#             tempo = df[col_time].values
#             ne = df[col_ne].values
            
#             # Chutes iniciais
#             A_guess = ne[0] - ne[-1]
#             C_guess = ne[-1]
#             tau_guess = tempo[len(tempo)//3] if len(tempo) > 3 else tempo[-1]/2
            
#             # Fit
#             popt, pcov = curve_fit(exponential_decay, tempo, ne,
#                                   p0=[A_guess, tau_guess, C_guess],
#                                   bounds=([0, 0, 0], [np.inf, np.inf, np.inf]),
#                                   maxfev=5000)
            
#             A_fit, tau_fit, C_fit = popt
#             perr = np.sqrt(np.diag(pcov))
            
#             # R²
#             residuos = ne - exponential_decay(tempo, A_fit, tau_fit, C_fit)
#             ss_res = np.sum(residuos**2)
#             ss_tot = np.sum((ne - np.mean(ne))**2)
#             r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
#             # Meia-vida
#             half_life = tau_fit * np.log(2)
            
#             resultados.append({
#                 'run': run_num,
#                 'A': A_fit,
#                 'A_err': perr[0],
#                 'tau': tau_fit,
#                 'tau_err': perr[1],
#                 'C': C_fit,
#                 'C_err': perr[2],
#                 'r_squared': r_squared,
#                 'half_life': half_life,
#                 'N0_real': ne[0],
#                 'Ninf_real': ne[-1]
#             })
            
#             # Guardar primeiros 5 runs para exemplo
#             if idx <= 5:
#                 dados_para_plot.append({
#                     'run': run_num,
#                     'tempo': tempo,
#                     'ne': ne,
#                     'fit': exponential_decay(tempo, A_fit, tau_fit, C_fit)
#                 })
            
#             if idx % 20 == 0:
#                 print(f"    Processados {idx}/{len(caminhos_validos)} runs...")
                
#         except Exception as e:
#             print(f"    ⚠️ Erro no run {run_num}: {e}")
#             continue
    
#     if len(resultados) == 0:
#         print(f"  ✗ Nenhum fit bem sucedido!")
#         return None, None
    
#     # Converter para DataFrame
#     df_resultados = pd.DataFrame(resultados)
    
#     # Salvar CSV
#     csv_path = f"{config_dir}/resultados_fits_por_run.csv"
#     df_resultados.to_csv(csv_path, index=False)
    
#     # Salvar resumo (run, tau, beta)
#     df_resumido = df_resultados[['run', 'tau', 'tau_err', 'r_squared', 'half_life']].copy()
#     df_resumido['beta'] = 1.0
#     csv_resumido_path = f"{config_dir}/resumo_tau_beta.csv"
#     df_resumido.to_csv(csv_resumido_path, index=False)
    
#     print(f"  ✓ CSV salvos em: {config_dir}")
    
#     # Estatísticas
#     tau_mean = df_resultados['tau'].mean()
#     tau_std = df_resultados['tau'].std()
#     tau_median = df_resultados['tau'].median()
#     tau_cv = tau_std / tau_mean if tau_mean > 0 else 0
    
#     r2_mean = df_resultados['r_squared'].mean()
    
#     stats = {
#         'prob': prob,
#         'frac': frac,
#         'n_runs': len(resultados),
#         'tau_mean': tau_mean,
#         'tau_std': tau_std,
#         'tau_median': tau_median,
#         'tau_cv': tau_cv,
#         'r2_mean': r2_mean,
#         'tau_min': df_resultados['tau'].min(),
#         'tau_max': df_resultados['tau'].max()
#     }
    
#     # ============================================
#     # GERAR GRÁFICOS
#     # ============================================
    
#     # Gráfico 1: Histograma dos τ
#     fig1, ax1 = plt.subplots(figsize=(10, 5))
#     ax1.hist(df_resultados['tau'], bins=20, edgecolor='black', alpha=0.7, color='steelblue')
#     ax1.axvline(tau_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {tau_mean:.2f}')
#     ax1.axvline(tau_median, color='green', linestyle='--', linewidth=2, label=f'Mediana = {tau_median:.2f}')
#     ax1.set_xlabel('τ (tempo característico)', fontsize=12)
#     ax1.set_ylabel('Frequência', fontsize=12)
#     ax1.set_title(f'Distribuição de τ - prob={prob:.2f}, frac={frac}', fontsize=12)
#     ax1.legend()
#     ax1.grid(True, alpha=0.3)
#     plt.tight_layout()
#     plt.savefig(f"{config_dir}/histograma_tau.png", dpi=150, bbox_inches='tight')
#     plt.close()
    
#     # Gráfico 2: τ por run
#     fig2, ax2 = plt.subplots(figsize=(12, 5))
#     runs_order = df_resultados['run'].values
#     tau_values = df_resultados['tau'].values
#     tau_errors = df_resultados['tau_err'].values
    
#     ax2.errorbar(runs_order, tau_values, yerr=tau_errors, fmt='o', 
#                  capsize=3, markersize=4, alpha=0.7, color='blue')
#     ax2.axhline(tau_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {tau_mean:.2f}')
#     ax2.fill_between([runs_order.min(), runs_order.max()], 
#                       tau_mean - tau_std, tau_mean + tau_std, 
#                       alpha=0.2, color='red', label=f'±1σ = {tau_std:.2f}')
#     ax2.set_xlabel('Número do Run', fontsize=12)
#     ax2.set_ylabel('τ', fontsize=12)
#     ax2.set_title(f'τ por run - prob={prob:.2f}, frac={frac}', fontsize=12)
#     ax2.legend()
#     ax2.grid(True, alpha=0.3)
#     plt.tight_layout()
#     plt.savefig(f"{config_dir}/tau_por_run.png", dpi=150, bbox_inches='tight')
#     plt.close()
    
#     # Gráfico 3: Exemplos de fits (primeiros 5 runs)
#     if dados_para_plot:
#         n_exemplos = len(dados_para_plot)
#         fig3, axes = plt.subplots(1, n_exemplos, figsize=(15, 4))
#         if n_exemplos == 1:
#             axes = [axes]
        
#         for idx, dado in enumerate(dados_para_plot):
#             ax = axes[idx]
#             ax.plot(dado['tempo'], dado['ne'], 'bo-', markersize=3, linewidth=1, alpha=0.7, label='Dados')
#             ax.plot(dado['tempo'], dado['fit'], 'r-', linewidth=2, label='Fit')
#             ax.set_title(f'Run {dado["run"]}', fontsize=10)
#             ax.set_xlabel('Tempo')
#             ax.set_ylabel('NE')
#             ax.grid(True, alpha=0.3)
#             ax.legend(fontsize=8)
        
#         plt.suptitle(f'Fits Exponenciais - prob={prob:.2f}, frac={frac}', fontsize=12)
#         plt.tight_layout()
#         plt.savefig(f"{config_dir}/exemplos_fits.png", dpi=150, bbox_inches='tight')
#         plt.close()
    
#     print(f"  ✓ Gráficos salvos em: {config_dir}")
#     print(f"\n  Estatísticas para prob={prob:.2f}, frac={frac}:")
#     print(f"    τ = {tau_mean:.4f} ± {tau_std:.4f} (CV = {tau_cv:.3f})")
#     print(f"    R² médio = {r2_mean:.4f}")
    
#     return df_resultados, stats

# # ============================================
# # PROCESSAR TODAS CONFIGURAÇÕES
# # ============================================

# print("="*80)
# print("FIT EXPONENCIAL PARA MÚLTIPLAS CONFIGURAÇÕES")
# print("="*80)

# print(f"\nConfigurações a processar:")
# print(f"  Probabilidades: {probabilidades}")
# print(f"  Frações: {fracoes}")
# print(f"  Total: {len(probabilidades) * len(fracoes)} combinações")

# # Lista para armazenar estatísticas de todas configurações
# todas_estatisticas = []

# for prob in probabilidades:
#     for frac in fracoes:
#         df_res, stats = process_configuracao(prob, frac, num_runs)
#         if stats is not None:
#             todas_estatisticas.append(stats)

# # ============================================
# # SALVAR RESUMO GERAL
# # ============================================

# print("\n" + "="*80)
# print("SALVANDO RESUMO GERAL")
# print("="*80)

# if todas_estatisticas:
#     df_geral = pd.DataFrame(todas_estatisticas)
    
#     # Salvar CSV com resumo de todas configurações
#     csv_geral_path = f"{base_output_dir}/resumo_geral_todas_configuracoes.csv"
#     df_geral.to_csv(csv_geral_path, index=False)
#     print(f"✓ Resumo geral salvo em: {csv_geral_path}")
    
#     # ============================================
#     # GRÁFICO COMPARATIVO ENTRE PROBABILIDADES
#     # ============================================
    
#     print("\n[Gerando gráfico comparativo...]")
    
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
#     # Gráfico 1: τ vs probabilidade
#     probs = df_geral['prob'].values
#     tau_means = df_geral['tau_mean'].values
#     tau_stds = df_geral['tau_std'].values
    
#     ax1.errorbar(probs, tau_means, yerr=tau_stds, fmt='o-', capsize=5, 
#                  markersize=8, linewidth=2, color='blue')
#     ax1.set_xlabel('Probabilidade', fontsize=12)
#     ax1.set_ylabel('τ (tempo característico)', fontsize=12)
#     ax1.set_title('Tempo Característico vs Probabilidade', fontsize=14, fontweight='bold')
#     ax1.grid(True, alpha=0.3)
    
#     # Gráfico 2: R² vs probabilidade
#     r2_means = df_geral['r2_mean'].values
    
#     ax2.plot(probs, r2_means, 's-', markersize=8, linewidth=2, color='green')
#     ax2.set_xlabel('Probabilidade', fontsize=12)
#     ax2.set_ylabel('R² médio', fontsize=12)
#     ax2.set_title('Qualidade do Fit vs Probabilidade', fontsize=14, fontweight='bold')
#     ax2.set_ylim([0.95, 1.005])  # Ajuste conforme necessário
#     ax2.grid(True, alpha=0.3)
    
#     plt.tight_layout()
#     plt.savefig(f"{base_output_dir}/comparacao_entre_probabilidades.png", dpi=150, bbox_inches='tight')
#     plt.close()
#     print(f"✓ Gráfico comparativo salvo em: {base_output_dir}/comparacao_entre_probabilidades.png")
    
#     # ============================================
#     # IMPRIMIR RESUMO
#     # ============================================
    
#     print("\n" + "="*80)
#     print("RESUMO FINAL - TODAS CONFIGURAÇÕES")
#     print("="*80)
    
#     for stats in todas_estatisticas:
#         print(f"\nprob = {stats['prob']:.2f}, frac = {stats['frac']}:")
#         print(f"  • Runs processados: {stats['n_runs']}")
#         print(f"  • τ = {stats['tau_mean']:.4f} ± {stats['tau_std']:.4f}")
#         print(f"  • CV(τ) = {stats['tau_cv']:.3f}")
#         print(f"  • R² médio = {stats['r2_mean']:.4f}")
    
#     print("\n" + "="*80)
#     print(f"✅ PROCESSAMENTO CONCLUÍDO!")
#     print(f"📁 Resultados salvos em: {base_output_dir}/")
#     print("="*80)
    
#     print("\nEstrutura de pastas criada:")
#     print(f"{base_output_dir}/")
#     for prob in probabilidades:
#         for frac in fracoes:
#             print(f"  └── prob_{prob:.2f}_frac_{frac}/")
#             print(f"      ├── resultados_fits_por_run.csv")
#             print(f"      ├── resumo_tau_beta.csv")
#             print(f"      ├── histograma_tau.png")
#             print(f"      ├── tau_por_run.png")
#             print(f"      └── exemplos_fits.png")
    
# else:
#     print("⚠️ Nenhuma configuração foi processada com sucesso!")
#     print("   Verifique se os caminhos dos dados estão corretos.")

# print("\n" + "="*80)
# # import pandas as pd
# # import numpy as np
# # import os
# # from pathlib import Path

# # # Configuração
# # base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/v_prob/"
# # prob = 0.60
# # num_runs = 100

# # print("="*80)
# # print("ETAPA 1: VALIDAÇÃO DOS DADOS")
# # print("="*80)

# # # ============================================
# # # VERIFICAÇÃO 1: O caminho existe?
# # # ============================================
# # print("\n[1] Verificando diretório base...")
# # if os.path.exists(base_path):
# #     print(f"✓ Diretório encontrado: {base_path}")
# # else:
# #     print(f"✗ ERRO: Diretório não encontrado: {base_path}")
# #     print("  Verifique o caminho ou monte o drive corretamente.")
# #     exit()

# # # ============================================
# # # VERIFICAÇÃO 2: Listar arquivos disponíveis
# # # ============================================
# # print(f"\n[2] Procurando arquivos para prob = {prob:.2f}...")

# # # Construir padrão do nome do arquivo
# # # Exemplo: simulation_frac_100run1obsprob0.60/results_N_escapers_run1.csv
# # arquivos_encontrados = []
# # caminhos_validos = []

# # for run in range(1, num_runs + 1):
# #     caminho_pasta = f"{base_path}simulation_frac_100_run_{run}_obsprob_{prob:.2f}_SRC_2_SRE_2"
# #     caminho_arquivo = f"{caminho_pasta}/results_N_escapers_run{run}.csv"
    
# #     if os.path.exists(caminho_arquivo):
# #         arquivos_encontrados.append(run)
# #         caminhos_validos.append(caminho_arquivo)

# # print(f"✓ Encontrados {len(arquivos_encontrados)} arquivos de {num_runs} esperados")

# # if len(arquivos_encontrados) == 0:
# #     print(f"✗ Nenhum arquivo encontrado para prob = {prob:.2f}")
# #     print("  Verifique se a probabilidade está correta e os arquivos existem.")
    
# #     exit()

# # # Mostrar primeiros 5 caminhos como exemplo
# # print(f"\n  Exemplo (primeiros 5 arquivos encontrados):")
# # for i, caminho in enumerate(caminhos_validos[:5]):
# #     print(f"    {i+1}. {caminho}")

# # # ============================================
# # # VERIFICAÇÃO 3: Ler e inspecionar UM arquivo
# # # ============================================
# # print(f"\n[3] Inspecionando estrutura de um arquivo (run {arquivos_encontrados[0]})...")

# # caminho_teste = caminhos_validos[0]
# # df_teste = pd.read_csv(caminho_teste)

# # print(f"✓ Arquivo lido com sucesso!")
# # print(f"  Dimensões: {df_teste.shape[0]} linhas × {df_teste.shape[1]} colunas")
# # print(f"  Colunas: {list(df_teste.columns)}")

# # # Verificar tipos de dados
# # print(f"\n  Tipos dos dados:")
# # print(df_teste.dtypes)

# # # Verificar primeiras linhas
# # print(f"\n  Primeiras 5 linhas:")
# # print(df_teste.head())

# # print(f"\n  Últimas 5 linhas:")
# # print(df_teste.tail())

# # # ============================================
# # # VERIFICAÇÃO 4: Entender o que está em cada coluna
# # # ============================================
# # print(f"\n[4] Analisando conteúdo das colunas...")

# # for col in df_teste.columns:
# #     print(f"\n  Coluna '{col}':")
# #     print(f"    - Tipo: {df_teste[col].dtype}")
# #     print(f"    - Mínimo: {df_teste[col].min()}")
# #     print(f"    - Máximo: {df_teste[col].max()}")
# #     print(f"    - Média: {df_teste[col].mean():.2f}")
# #     print(f"    - Valores únicos (primeiros 5): {df_teste[col].unique()[:5]}")
    
# #     # Verificar se tem NaN
# #     nans = df_teste[col].isna().sum()
# #     if nans > 0:
# #         print(f"    - ⚠️  Atenção: {nans} valores NaN encontrados")

# # # ============================================
# # # VERIFICAÇÃO 5: Verificar a "primeira linha" que o código original pulava
# # # ============================================
# # print(f"\n[5] Investigando por que o código original pulava a primeira linha...")

# # # Comparar linha 0 vs linha 1
# # print("  Linha 0 (índice 0):")
# # print(df_teste.iloc[0])
# # print("\n  Linha 1 (índice 1):")
# # print(df_teste.iloc[1])

# # # Verificar se há diferença significativa
# # if 'time' in df_teste.columns:
# #     col_NE = [c for c in df_teste.columns if c != 'time'][0]
# #     print(f"\n  Coluna de análise: {col_NE}")
# #     print(f"  Linha 0: time={df_teste.iloc[0]['time']}, {col_NE}={df_teste.iloc[0][col_NE]}")
# #     print(f"  Linha 1: time={df_teste.iloc[1]['time']}, {col_NE}={df_teste.iloc[1][col_NE]}")
    
# #     # Verificar se linha 0 pode ser estado inicial ou dado corrompido
# #     if df_teste.iloc[0]['time'] == 0:
# #         print("\n  ✓ Linha 0 tem time=0 → provavelmente é o estado inicial legítimo")
# #         print("  ⚠️ Por que o código original pulava então? Talvez seja um erro!")
# #     else:
# #         print("\n  ⚠️ Linha 0 NÃO tem time=0 → pode ser cabeçalho ou dado inválido")

# # # ============================================
# # # VERIFICAÇÃO 6: Estatísticas básicas dos runs
# # # ============================================
# # print(f"\n[6] Comparando consistência entre diferentes runs...")

# # # Ler mais alguns runs para verificar consistência
# # runs_para_analisar = min(5, len(caminhos_validos))
# # tamanhos = []
# # colunas_comuns = []

# # for i in range(runs_para_analisar):
# #     df_temp = pd.read_csv(caminhos_validos[i])
# #     tamanhos.append(df_temp.shape[0])
# #     colunas_comuns.append(set(df_temp.columns))
    
# # # Verificar se todos têm o mesmo tamanho
# # if len(set(tamanhos)) == 1:
# #     print(f"✓ Todos os {runs_para_analisar} runs têm o mesmo número de linhas: {tamanhos[0]}")
# # else:
# #     print(f"⚠️ Runs têm tamanhos diferentes: {tamanhos}")
# #     print("  Isso pode causar problemas na média mais tarde!")

# # # Verificar se todos têm as mesmas colunas
# # if len(set([frozenset(cols) for cols in colunas_comuns])) == 1:
# #     print(f"✓ Todos os runs têm as mesmas colunas")
# # else:
# #     print(f"⚠️ Runs têm colunas diferentes!")
# #     for i, cols in enumerate(colunas_comuns):
# #         print(f"  Run {i+1}: {cols}")

# # # ============================================
# # # VERIFICAÇÃO 7: Verificar valores extremos
# # # ============================================
# # print(f"\n[7] Verificando plausibilidade física dos valores...")

# # valores_todos = []
# # for caminho in caminhos_validos[:runs_para_analisar]:
# #     df_temp = pd.read_csv(caminho)
# #     col_NE = [c for c in df_temp.columns if c != 'time'][0]
# #     valores_todos.extend(df_temp[col_NE].values)

# # valores_array = np.array(valores_todos)

# # print(f"  Valores de NE (Número de Escapers):")
# # print(f"    - Mínimo global: {valores_array.min()}")
# # print(f"    - Máximo global: {valores_array.max()}")
# # print(f"    - Média global: {valores_array.mean():.2f}")

# # # Verificações de plausibilidade
# # if valores_array.min() < 0:
# #     print(f"    ⚠️ ATENÇÃO: Valores negativos encontrados! (mínimo={valores_array.min()})")
# #     print("      Número de escapers não pode ser negativo → dados podem ter erro")
# # else:
# #     print(f"    ✓ Sem valores negativos (mínimo >= 0)")

# # if valores_array.max() > 1000:  # Ajuste este limite conforme seu sistema
# #     print(f"    ⚠️ Valores muito altos: máximo={valores_array.max()}")
# # else:
# #     print(f"    ✓ Valores dentro da faixa esperada")

# # # ============================================
# # # RESUMO FINAL
# # # ============================================
# # print("\n" + "="*80)
# # print("RESUMO DA ETAPA 1")
# # print("="*80)

# # problemas = []

# # if len(arquivos_encontrados) < num_runs:
# #     problemas.append(f"  - Apenas {len(arquivos_encontrados)} de {num_runs} runs encontrados")

# # if len(set(tamanhos)) != 1:
# #     problemas.append(f"  - Runs com tamanhos diferentes: {set(tamanhos)}")

# # if valores_array.min() < 0:
# #     problemas.append(f"  - Valores negativos encontrados: {valores_array.min()}")

# # if problemas:
# #     print("\n⚠️ PROBLEMAS IDENTIFICADOS:")
# #     for p in problemas:
# #         print(p)
# #     print("\n📌 Recomendações:")
# #     print("  1. Verifique se os dados estão completos")
# #     print("  2. Decida se vai usar todos os runs ou apenas os consistentes")
# #     print("  3. Investigue a necessidade de pular a primeira linha")
# # else:
# #     print("\n✓ NENHUM PROBLEMA CRÍTICO IDENTIFICADO")
# #     print("  Os dados parecem consistentes para prosseguir.")

# # print(f"\n📁 Dados disponíveis para prob = {prob:.2f}:")
# # print(f"  - Total de runs válidos: {len(arquivos_encontrados)}")
# # print(f"  - Cada run tem {tamanhos[0] if tamanhos else '?'} pontos no tempo")
# # print(f"  - Colunas presentes: {list(df_teste.columns)}")

# # print("\n" + "="*80)
# # print("PRÓXIMA ETAPA: Visualizar dados brutos")
# # print("="*80)