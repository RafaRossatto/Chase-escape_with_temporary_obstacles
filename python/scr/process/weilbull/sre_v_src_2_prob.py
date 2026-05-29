# base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/sre_v_prob_0_50/"
# base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/prob_1/"

# # Parâmetros fixos
# obsprob = 1.00  # Probabilidade fixa
# frac = 100      # Fração fixa
# src = 2         # SRC fixo

# # Valores de SRE a processar
# valores_SRE = [2, 4, 6, 8, 10, 12, 14, 16]

# # Número de runs esperado por configuração
# num_runs = 100

# # Pasta BASE para resultados (raiz)
# output_root = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/resultados_fit_exponencial_multiplos/sre_v_src_2_prob_1_00"


import pandas as pd
import numpy as np
import os
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================
# CONFIGURAÇÕES
# ============================================

# base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/sre_v_prob_0_50/"
base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/prob_1/"

# Parâmetros fixos
obsprob = 1.00  # Probabilidade fixa
frac = 100       # Fração fixa
src = 2         # SRC fixo

# Valores de SRE a processar
valores_SRE = [2, 4, 6, 8, 10, 12, 14, 16]

# Número de runs esperado por configuração
num_runs = 100

# Pasta BASE para resultados (raiz)
output_root = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/resultados_fit_exponencial_multiplos/sre_v_src_2_prob_1_00"
os.makedirs(output_root, exist_ok=True)

print("="*80)
print("FIT WEIBULL POR RUN - VARIANDO SRE (β será calculado)")
print(f"obsprob = {obsprob:.2f}, frac = {frac}, src = {src}")
print(f"Valores de SRE: {valores_SRE}")
print("="*80)

# ============================================
# FUNÇÃO MODELO (WEIBULL - β será ajustado)
# ============================================

def weibull_decay(t, A, tau, beta, C):
    """Decaimento Weibull: N(t) = A * exp(-(t/tau)^beta) + C"""
    return A * np.exp(-(t / tau)**beta) + C

# ============================================
# PROCESSAR CADA VALOR DE SRE
# ============================================

resultados_gerais = []  # Para consolidar médias
resultados_por_run = []  # Para consolidar todos os runs individuais

for sre in valores_SRE:
    print(f"\n{'='*70}")
    print(f"PROCESSANDO SRE = {sre}")
    print(f"{'='*70}")
    
    # ============================================
    # CRIAR PASTA COM TODAS AS CARACTERÍSTICAS + SRE
    # ============================================
    output_base = f"{output_root}/obsprob_{obsprob:.2f}_frac_{frac}_src_{src}_SRE_{sre}"
    os.makedirs(output_base, exist_ok=True)
    print(f"  Pasta de saída: {output_base}")
    
    # Lista para armazenar dados deste SRE
    todos_dados = []
    tempo_referencia = None
    runs_encontrados = []
    
    # Lista para armazenar fits individuais
    resultados_runs_individuais = []
    
    # Tentar ler runs 1 a num_runs
    for run in range(1, num_runs + 1):
        # Construir caminho no padrão correto
        caminho = f"{base_path}simulation_frac_{frac}_run_{run}_obsprob_{obsprob:.2f}_SRC_{src}_SRE_{sre}/results_N_escapers_run{run}.csv"
        
        try:
            df = pd.read_csv(caminho)
            
            # Verificar estrutura do arquivo
            if 'time' not in df.columns:
                if run == 1:
                    print(f"  ⚠️ Run {run}: coluna 'time' não encontrada. Colunas: {df.columns}")
                continue
            
            # Identificar coluna de NE
            col_ne = [col for col in df.columns if col != 'time']
            if not col_ne:
                continue
            col_ne = col_ne[0]
            
            # Pular primeira linha (como no original)
            if len(df) > 1:
                df_cortado = df.iloc[1:].reset_index(drop=True)
                tempo = df_cortado['time'].values
                ne = df_cortado[col_ne].values
            else:
                tempo = df['time'].values
                ne = df[col_ne].values
            
            # Guardar tempo de referência
            if tempo_referencia is None:
                tempo_referencia = tempo
            
            # Verificar consistência
            if len(tempo) != len(tempo_referencia):
                print(f"  ⚠️ Run {run}: tamanho do tempo diferente")
                continue
            
            # Armazenar dados para média
            todos_dados.append(ne)
            runs_encontrados.append(run)
            
            # ============================================
            # FIT WEIBULL PARA ESTE RUN INDIVIDUAL
            # ============================================
            try:
                # Chutes iniciais para este run
                A_guess_run = ne[0] - ne[-1]
                C_guess_run = ne[-1]
                tau_guess_run = tempo[len(tempo)//3] if len(tempo) > 3 else tempo[-1]/2
                beta_guess_run = 1.5  # chute inicial para β (Weibull)
                
                # Fit para este run (todos os 4 parâmetros)
                popt_run, pcov_run = curve_fit(weibull_decay, tempo, ne,
                                              p0=[A_guess_run, tau_guess_run, beta_guess_run, C_guess_run],
                                              bounds=([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf]),
                                              maxfev=5000)
                
                A_fit_run, tau_fit_run, beta_fit_run, C_fit_run = popt_run
                perr_run = np.sqrt(np.diag(pcov_run))
                
                # R² para este run
                residuos_run = ne - weibull_decay(tempo, A_fit_run, tau_fit_run, beta_fit_run, C_fit_run)
                ss_res_run = np.sum(residuos_run**2)
                ss_tot_run = np.sum((ne - np.mean(ne))**2)
                r_squared_run = 1 - (ss_res_run / ss_tot_run) if ss_tot_run > 0 else 0
                
                # Meia-vida (aproximada para Weibull)
                # N(t) = A*exp(-(t/tau)^beta) + C
                # Meia vida quando A*exp(-(t/tau)^beta) = A/2
                # => exp(-(t/tau)^beta) = 1/2 => (t/tau)^beta = ln(2)
                # => t = tau * (ln(2))^(1/beta)
                half_life_run = tau_fit_run * (np.log(2))**(1/beta_fit_run)
                
                # Armazenar resultados individuais
                resultados_runs_individuais.append({
                    'SRE': sre,
                    'run': run,
                    'A': A_fit_run,
                    'A_err': perr_run[0],
                    'tau': tau_fit_run,
                    'tau_err': perr_run[1],
                    'beta': beta_fit_run,
                    'beta_err': perr_run[2],
                    'C': C_fit_run,
                    'C_err': perr_run[3],
                    'r_squared': r_squared_run,
                    'half_life': half_life_run,
                    'N0': ne[0],
                    'Ninf': ne[-1]
                })
                
            except Exception as e:
                print(f"  ⚠️ Erro no fit do run {run}: {e}")
                continue
            
        except FileNotFoundError:
            continue
        except Exception as e:
            if run == 1:
                print(f"  ⚠️ Erro no run {run}: {e}")
            continue
    
    if not todos_dados:
        print(f"✗ NENHUM DADO ENCONTRADO para SRE={sre}")
        print(f"  Verifique o padrão do nome do arquivo!")
        print(f"  Tentou: {caminho}")
        continue
    
    # Converter para array
    todos_dados = np.array(todos_dados)
    n_runs = len(todos_dados)
    n_tempos = len(tempo_referencia)
    
    print(f"✓ Encontrados {n_runs} runs válidos")
    print(f"✓ Fits realizados para {len(resultados_runs_individuais)} runs")
    print(f"✓ {n_tempos} pontos no tempo cada")
    
    # ============================================
    # SALVAR RESULTADOS INDIVIDUAIS POR RUN
    # ============================================
    
    if resultados_runs_individuais:
        # DataFrame com resultados de cada run
        df_runs_individuais = pd.DataFrame(resultados_runs_individuais)
        
        # Salvar CSV com todos os runs individuais
        csv_individual_path = f"{output_base}/resultados_por_run_SRE_{sre}.csv"
        df_runs_individuais.to_csv(csv_individual_path, index=False)
        print(f"  ✓ CSV com {len(resultados_runs_individuais)} runs salvo em: {csv_individual_path}")
        
        # Salvar versão resumida (run, tau, beta)
        df_resumo_runs = df_runs_individuais[['run', 'tau', 'tau_err', 'beta', 'beta_err', 'r_squared', 'half_life']].copy()
        csv_resumo_path = f"{output_base}/resumo_tau_beta_por_run_SRE_{sre}.csv"
        df_resumo_runs.to_csv(csv_resumo_path, index=False)
        print(f"  ✓ Resumo por run salvo em: {csv_resumo_path}")
    
    # ============================================
    # ESTATÍSTICAS DOS FITS INDIVIDUAIS
    # ============================================
    
    if resultados_runs_individuais:
        tau_values = [r['tau'] for r in resultados_runs_individuais]
        beta_values = [r['beta'] for r in resultados_runs_individuais]
        
        tau_mean = np.mean(tau_values)
        tau_std = np.std(tau_values)
        tau_median = np.median(tau_values)
        
        beta_mean = np.mean(beta_values)
        beta_std = np.std(beta_values)
        beta_median = np.median(beta_values)
        
        print(f"\n  Estatísticas do τ entre os runs:")
        print(f"    Média = {tau_mean:.4f} ± {tau_std:.4f}")
        print(f"    Mediana = {tau_median:.4f}")
        
        print(f"\n  Estatísticas do β entre os runs:")
        print(f"    Média = {beta_mean:.4f} ± {beta_std:.4f}")
        print(f"    Mediana = {beta_median:.4f}")
    
    # ============================================
    # CALCULAR MÉDIA DOS DADOS
    # ============================================
    
    media = np.mean(todos_dados, axis=0)
    desvio_padrao = np.std(todos_dados, axis=0)
    
    # ============================================
    # FIT WEIBULL NA MÉDIA
    # ============================================
    
    A_guess = media[0] - media[-1]
    C_guess = media[-1]
    tau_guess = tempo_referencia[len(tempo_referencia)//3] if n_tempos > 3 else tempo_referencia[-1]/2
    beta_guess = 1.5  # chute inicial
    
    try:
        popt, pcov = curve_fit(weibull_decay, tempo_referencia, media,
                              p0=[A_guess, tau_guess, beta_guess, C_guess],
                              bounds=([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf]),
                              maxfev=5000)
        
        A_fit, tau_fit, beta_fit, C_fit = popt
        perr = np.sqrt(np.diag(pcov))
        
        # R²
        residuos = media - weibull_decay(tempo_referencia, A_fit, tau_fit, beta_fit, C_fit)
        ss_res = np.sum(residuos**2)
        ss_tot = np.sum((media - np.mean(media))**2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Meia-vida
        half_life = tau_fit * (np.log(2))**(1/beta_fit)
        
        # Armazenar resultados consolidados (média)
        resultados_gerais.append({
            'SRE': sre,
            'obsprob': obsprob,
            'frac': frac,
            'src': src,
            'n_runs': n_runs,
            'tau_mean': tau_fit,
            'tau_std': perr[1],
            'beta_mean': beta_fit,
            'beta_std': perr[2],
            'r_squared': r_squared,
            'half_life': half_life,
            'N0_medio': media[0],
            'Ninf_medio': media[-1]
        })
        
        print(f"\n✓ FIT DA MÉDIA REALIZADO:")
        print(f"  τ = {tau_fit:.4f} ± {perr[1]:.4f}")
        print(f"  β = {beta_fit:.4f} ± {perr[2]:.4f}")
        print(f"  R² = {r_squared:.4f}")
        
        # ============================================
        # SALVAR CSV DO FIT DA MÉDIA
        # ============================================
        
        df_media = pd.DataFrame([{
            'SRE': sre,
            'tau': tau_fit,
            'tau_err': perr[1],
            'beta': beta_fit,
            'beta_err': perr[2],
            'r_squared': r_squared,
            'half_life': half_life,
            'A': A_fit,
            'C': C_fit,
            'N0': media[0],
            'Ninf': media[-1]
        }])
        df_media.to_csv(f"{output_base}/resultado_media_SRE_{sre}.csv", index=False)
        print(f"  ✓ CSV da média salvo: {output_base}/resultado_media_SRE_{sre}.csv")
        
        # ============================================
        # GRÁFICO 1: Fit da média
        # ============================================
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Dados
        ax.plot(tempo_referencia, media, 'bo-', label='Média dos dados', 
                markersize=4, linewidth=1.5)
        ax.fill_between(tempo_referencia, media - desvio_padrao, media + desvio_padrao,
                        alpha=0.2, color='blue', label='±1 Desvio Padrão')
        
        # Curva do fit
        tempo_fit = np.linspace(tempo_referencia.min(), tempo_referencia.max(), 500)
        media_fit = weibull_decay(tempo_fit, A_fit, tau_fit, beta_fit, C_fit)
        ax.plot(tempo_fit, media_fit, 'r-', linewidth=2, 
                label=f'Weibull: τ={tau_fit:.2f}, β={beta_fit:.3f}')
        
        # Assíntota
        ax.axhline(y=C_fit, color='orange', linestyle='--', alpha=0.7,
                   label=f'Assíntota C = {C_fit:.2f}')
        
        ax.set_xlabel('Tempo', fontsize=12)
        ax.set_ylabel('NE', fontsize=12)
        ax.set_title(f'Fit Weibull da Média - SRE={sre} (obsprob={obsprob:.2f}, frac={frac})', 
                     fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Texto com parâmetros
        textstr = f'Parâmetros:\n' \
                  f'  τ = {tau_fit:.4f} ± {perr[1]:.4f}\n' \
                  f'  β = {beta_fit:.4f} ± {perr[2]:.4f}\n' \
                  f'  A = {A_fit:.2f} ± {perr[0]:.2f}\n' \
                  f'  C = {C_fit:.2f} ± {perr[3]:.2f}\n\n' \
                  f'Estatísticas:\n' \
                  f'  R² = {r_squared:.4f}\n' \
                  f'  t₁/₂ = {half_life:.2f}\n' \
                  f'  N(0) = {media[0]:.1f}\n' \
                  f'  N(∞) = {media[-1]:.1f}'
        
        # Interpretação do β
        if beta_fit < 1:
            textstr += f'\n\nβ < 1: Decaimento LENTO no início'
        elif beta_fit > 1:
            textstr += f'\n\nβ > 1: Decaimento ACELERADO'
        else:
            textstr += f'\n\nβ = 1: Decaimento EXPONENCIAL'
        
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(f"{output_base}/fit_media_SRE_{sre}.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Gráfico da média salvo: {output_base}/fit_media_SRE_{sre}.png")
        
        # ============================================
        # GRÁFICO 2: Histograma dos τ e β individuais
        # ============================================
        
        if resultados_runs_individuais and len(tau_values) > 1:
            fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Histograma do τ
            ax2a.hist(tau_values, bins=20, edgecolor='black', alpha=0.7, color='steelblue')
            ax2a.axvline(tau_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {tau_mean:.2f}')
            ax2a.axvline(tau_median, color='green', linestyle='--', linewidth=2, label=f'Mediana = {tau_median:.2f}')
            ax2a.set_xlabel('τ (tempo característico)', fontsize=12)
            ax2a.set_ylabel('Frequência', fontsize=12)
            ax2a.set_title(f'Distribuição de τ - SRE={sre}', fontsize=12, fontweight='bold')
            ax2a.legend()
            ax2a.grid(True, alpha=0.3)
            
            # Histograma do β
            ax2b.hist(beta_values, bins=20, edgecolor='black', alpha=0.7, color='coral')
            ax2b.axvline(beta_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {beta_mean:.4f}')
            ax2b.axvline(beta_median, color='green', linestyle='--', linewidth=2, label=f'Mediana = {beta_median:.4f}')
            ax2b.axvline(1.0, color='purple', linestyle='--', linewidth=2, alpha=0.7, label='β = 1 (exponencial)')
            ax2b.set_xlabel('β (expoente de forma)', fontsize=12)
            ax2b.set_ylabel('Frequência', fontsize=12)
            ax2b.set_title(f'Distribuição de β - SRE={sre}', fontsize=12, fontweight='bold')
            ax2b.legend()
            ax2b.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{output_base}/histogramas_SRE_{sre}.png", dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"  ✓ Histogramas salvo: {output_base}/histogramas_SRE_{sre}.png")
        
        # ============================================
        # GRÁFICO 3: τ e β por run
        # ============================================
        
        if resultados_runs_individuais:
            fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6))
            
            runs_num = [r['run'] for r in resultados_runs_individuais]
            tau_vals = [r['tau'] for r in resultados_runs_individuais]
            tau_errs = [r['tau_err'] for r in resultados_runs_individuais]
            beta_vals = [r['beta'] for r in resultados_runs_individuais]
            beta_errs = [r['beta_err'] for r in resultados_runs_individuais]
            
            # τ por run
            ax3a.errorbar(runs_num, tau_vals, yerr=tau_errs, fmt='o', 
                         capsize=3, markersize=4, alpha=0.7, color='blue')
            ax3a.axhline(tau_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {tau_mean:.2f}')
            ax3a.fill_between([min(runs_num), max(runs_num)], 
                              tau_mean - tau_std, tau_mean + tau_std, 
                              alpha=0.2, color='red', label=f'±1σ = {tau_std:.2f}')
            ax3a.set_xlabel('Número do Run', fontsize=12)
            ax3a.set_ylabel('τ', fontsize=12)
            ax3a.set_title(f'τ por run - SRE={sre}', fontsize=12, fontweight='bold')
            ax3a.legend()
            ax3a.grid(True, alpha=0.3)
            
            # β por run
            ax3b.errorbar(runs_num, beta_vals, yerr=beta_errs, fmt='s', 
                         capsize=3, markersize=4, alpha=0.7, color='green')
            ax3b.axhline(beta_mean, color='red', linestyle='--', linewidth=2, label=f'Média = {beta_mean:.4f}')
            ax3b.axhline(1.0, color='purple', linestyle='--', linewidth=2, alpha=0.7, label='β = 1')
            ax3b.fill_between([min(runs_num), max(runs_num)], 
                              beta_mean - beta_std, beta_mean + beta_std, 
                              alpha=0.2, color='red', label=f'±1σ = {beta_std:.4f}')
            ax3b.set_xlabel('Número do Run', fontsize=12)
            ax3b.set_ylabel('β', fontsize=12)
            ax3b.set_title(f'β por run - SRE={sre}', fontsize=12, fontweight='bold')
            ax3b.legend()
            ax3b.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{output_base}/parametros_por_run_SRE_{sre}.png", dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"  ✓ Gráfico parâmetros por run salvo: {output_base}/parametros_por_run_SRE_{sre}.png")
        
        # Adicionar resultados individuais ao consolidado geral
        if resultados_runs_individuais:
            for r in resultados_runs_individuais:
                resultados_por_run.append(r)
        
    except Exception as e:
        print(f"✗ Erro no fit da média para SRE={sre}: {e}")
        continue

# ============================================
# RESULTADOS GERAIS (TODOS SRE)
# ============================================

# Salvar resultados consolidados (médias por SRE)
if resultados_gerais:
    df_resultados = pd.DataFrame(resultados_gerais)
    csv_consolidado = f"{output_root}/resultados_consolidados_medias_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.csv"
    df_resultados.to_csv(csv_consolidado, index=False)
    print(f"\n✓ Resultados consolidados (médias) salvos em: {csv_consolidado}")

# Salvar resultados de todos os runs individuais
if resultados_por_run:
    df_todos_runs = pd.DataFrame(resultados_por_run)
    csv_todos_runs = f"{output_root}/resultados_todos_runs_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.csv"
    df_todos_runs.to_csv(csv_todos_runs, index=False)
    print(f"✓ Resultados de TODOS os runs ({len(resultados_por_run)} runs) salvos em: {csv_todos_runs}")
    
    # Salvar versão resumida (SRE, run, tau, beta)
    df_resumo_todos = df_todos_runs[['SRE', 'run', 'tau', 'tau_err', 'beta', 'beta_err', 'r_squared', 'half_life']].copy()
    csv_resumo_todos = f"{output_root}/resumo_todos_runs_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.csv"
    df_resumo_todos.to_csv(csv_resumo_todos, index=False)
    print(f"✓ Resumo de todos os runs salvo em: {csv_resumo_todos}")

# ============================================
# GRÁFICOS: τ vs SRE e β vs SRE
# ============================================

if resultados_gerais:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))
    
    sre_vals = [r['SRE'] for r in resultados_gerais]
    tau_means = [r['tau_mean'] for r in resultados_gerais]
    tau_stds = [r['tau_std'] for r in resultados_gerais]
    beta_means = [r['beta_mean'] for r in resultados_gerais]
    beta_stds = [r['beta_std'] for r in resultados_gerais]
    r2_vals = [r['r_squared'] for r in resultados_gerais]
    
    # Gráfico 1: τ vs SRE
    ax1.errorbar(sre_vals, tau_means, yerr=tau_stds, fmt='o-', 
                 capsize=5, markersize=8, linewidth=2, color='blue')
    ax1.set_xlabel('SRE', fontsize=12)
    ax1.set_ylabel('τ (tempo característico)', fontsize=12)
    ax1.set_title('τ vs SRE', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: β vs SRE
    ax2.errorbar(sre_vals, beta_means, yerr=beta_stds, fmt='s-', 
                 capsize=5, markersize=8, linewidth=2, color='green')
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='β = 1 (exponencial)')
    ax2.set_xlabel('SRE', fontsize=12)
    ax2.set_ylabel('β (expoente de forma)', fontsize=12)
    ax2.set_title('β vs SRE', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Gráfico 3: R² vs SRE
    ax3.plot(sre_vals, r2_vals, 'd-', markersize=8, linewidth=2, color='purple')
    ax3.set_xlabel('SRE', fontsize=12)
    ax3.set_ylabel('R²', fontsize=12)
    ax3.set_title('Qualidade do Fit vs SRE', fontsize=12, fontweight='bold')
    ax3.set_ylim([0.95, 1.005])
    ax3.grid(True, alpha=0.3)
    
    # Gráfico 4: Número de runs por SRE
    n_runs_vals = [r['n_runs'] for r in resultados_gerais]
    ax4.bar(sre_vals, n_runs_vals, color='orange', alpha=0.7, edgecolor='black')
    ax4.set_xlabel('SRE', fontsize=12)
    ax4.set_ylabel('Número de runs válidos', fontsize=12)
    ax4.set_title('Runs processados por SRE', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle(f'Resultados Weibull - obsprob={obsprob:.2f}, frac={frac}, src={src}', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{output_root}/resumos_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.png", dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráficos resumo salvos em: {output_root}/resumos_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.png")

# ============================================
# RESUMO FINAL
# ============================================

print("\n" + "="*80)
print("RESULTADOS FINAIS")
print("="*80)

if resultados_por_run:
    print(f"\n✅ TOTAL DE RUNS PROCESSADOS: {len(resultados_por_run)}")
    print(f"   Distribuição por SRE:")
    for sre in valores_SRE:
        count = sum(1 for r in resultados_por_run if r['SRE'] == sre)
        if count > 0:
            print(f"     SRE={sre}: {count} runs")
    
    # Estatísticas gerais de β
    all_betas = [r['beta'] for r in resultados_por_run]
    print(f"\n📊 Estatísticas gerais do β:")
    print(f"   Média = {np.mean(all_betas):.4f} ± {np.std(all_betas):.4f}")
    print(f"   Mediana = {np.median(all_betas):.4f}")
    print(f"   Min = {np.min(all_betas):.4f}")
    print(f"   Max = {np.max(all_betas):.4f}")

print("\n" + "="*80)
print(f"✅ PROCESSAMENTO CONCLUÍDO!")
print(f"📁 Resultados em: {output_root}/")
print("="*80)