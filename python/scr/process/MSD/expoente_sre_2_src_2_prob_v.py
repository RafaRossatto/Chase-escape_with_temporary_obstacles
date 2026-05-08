import pandas as pd
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configuração
sre = 2  # SRE fixo em 2
prob_list = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
frac = 100

# Dicionário para definir t_min para cada probabilidade
t_min_dict = {
    0.00: 4e5,
    0.10: 3e5,
    0.20: 3e5,
    0.30: 3e6,
    0.40: 3e5,
    0.50: 3e5,
    0.60: 4e5,
    0.70: 4e5,
    0.80: 4e5,
    0.90: 4e5,
    1.00: 4e5,
}


# frac = 50

# # Dicionário para definir t_min para cada probabilidade
# t_min_dict = {
#     0.00: 5e5,
#     0.10: 5e5,
#     0.20: 5e5,
#     0.30: 5e6,
#     0.40: 5e5,
#     0.50: 6e5,
#     0.60: 7e5,
#     0.70: 6e5,
#     0.80: 6e5,
#     0.90: 6e5,
#     1.00: 6e5,
# }


# frac = 25

# # Dicionário para definir t_min para cada probabilidade
# t_min_dict = {
#     0.00: 4e5,
#     0.10: 4e5,
#     0.20: 6e5,
#     0.30: 1e6,
#     0.40: 3e5,
#     0.50: 7e5,
#     0.60: 8e5,
#     0.70: 8e5,
#     0.80: 8e5,
#     0.90: 8e5,
#     1.00: 8e5,
# }

# Caminhos
input_base_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/MSD_per_run_v_prob/frac_{frac}"
output_base_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/{frac}/prob_variation"

def power_law_log(log_t, alpha, log_c):
    """Função power law no espaço log: log10(MSD) = log_c + alpha * log10(t)"""
    return log_c + alpha * log_t

def compute_exponent_from_csv(run_csv_path, t_min):
    """Calcula o expoente alpha a partir do arquivo CSV de um run (ajuste log-log)"""
    try:
        df = pd.read_csv(run_csv_path)
        
        # Filtra pelo tempo mínimo
        df_fit = df[df['time'] >= t_min].copy()
        
        if len(df_fit) < 3:
            return None, "Pontos insuficientes para fit"
        
        # Transforma para escala logarítmica
        log_t = np.log10(df_fit['time'].values)
        log_msd = np.log10(df_fit['msd'].values)
        
        # Ajuste linear no espaço log (mais estável para power laws)
        popt, pcov = curve_fit(
            power_law_log, 
            log_t, 
            log_msd,
            p0=[1.0, 0.0],  # alpha=1, log10(c)=0 -> c=1
            maxfev=5000
        )
        
        alpha = popt[0]  # expoente
        log_c = popt[1]  # log10(c)
        c = 10**log_c    # coeficiente no espaço linear
        
        # Calcula R² do ajuste no espaço log
        residuals = log_msd - power_law_log(log_t, alpha, log_c)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((log_msd - np.mean(log_msd))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else np.nan
        
        alpha_err = np.sqrt(np.diag(pcov))[0] if len(pcov) > 0 else np.nan
        
        return {
            'alpha': alpha,
            'alpha_error': alpha_err,
            'c': c,
            'log_c': log_c,
            'r_squared': r_squared,
            'n_points': len(df_fit),
            't_min_used': t_min,
            't_max_used': df_fit['time'].max(),
            'msd_final': df['msd'].iloc[-1] if len(df) > 0 else np.nan
        }, None
        
    except Exception as e:
        return None, str(e)

def process_probability(prob):
    """Processa uma probabilidade: calcula expoentes para todos os runs"""
    t_min = t_min_dict.get(prob, 20e4)
    
    # Constrói o caminho corretamente
    prob_input_dir = Path(input_base_path) / f"obsprob_{prob:.2f}" / "individual_runs"
    prob_output_dir = Path(output_base_path) / f"obsprob_{prob:.2f}"
    prob_output_dir.mkdir(parents=True, exist_ok=True)
    
    if not prob_input_dir.exists():
        print(f"  ✗ Diretório não encontrado: {prob_input_dir}")
        return None
    
    # Lista todos os arquivos CSV de runs
    run_files = sorted(prob_input_dir.glob("run_*_msd.csv"))
    
    if not run_files:
        print(f"  ✗ Nenhum arquivo de run encontrado para prob={prob:.2f}")
        return None
    
    print(f"  Processando {len(run_files)} runs para prob={prob:.2f} (t_min={t_min:.0e})...")
    
    results = []
    successful = 0
    
    for run_file in run_files:
        run_num = int(run_file.stem.split('_')[1])
        
        result, error = compute_exponent_from_csv(run_file, t_min)
        
        if result is not None:
            results.append({
                'run': run_num,
                **result
            })
            successful += 1
        else:
            if error:
                print(f"    Run {run_num}: erro - {error}")
    
    if results:
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('run')
        
        output_csv = prob_output_dir / f"expoentes_prob_{prob:.2f}_tmin{t_min:.0e}.csv"
        df_results.to_csv(output_csv, index=False)
        
        alpha_mean = df_results['alpha'].mean()
        alpha_std = df_results['alpha'].std()
        alpha_std_error = df_results['alpha'].sem()
        mean_r_squared = df_results['r_squared'].mean()
        
        print(f"  ✓ prob={prob:.2f}: {successful}/{len(run_files)} runs válidos")
        print(f"    α médio = {alpha_mean:.4f} ± {alpha_std:.4f} (std)")
        print(f"    R² médio = {mean_r_squared:.4f}")
        
        return {
            'prob': prob,
            't_min': t_min,
            'alpha_mean': alpha_mean,
            'alpha_std': alpha_std,
            'alpha_std_error': alpha_std_error,
            'mean_r_squared': mean_r_squared,
            'n_runs': successful,
            'n_total_runs': len(run_files)
        }
    else:
        print(f"  ✗ Nenhum run válido para prob={prob:.2f}")
        return None

def process_prob_parallel(prob):
    """Wrapper para processamento paralelo por probabilidade"""
    return process_probability(prob)

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"Calculando expoentes α (MSD ~ t^α) - AJUSTE LOG-LOG")
    print(f"SRE fixo = {sre}")
    print(f"Fração: {frac}%")
    print(f"Probabilidades: {len(prob_list)} valores")
    print(f"{'='*60}\n")
    
    for prob, tmin in t_min_dict.items():
        print(f"  prob={prob:.2f}: t_min = {tmin:.0e}")
    
    print(f"\nProcessando {len(prob_list)} probabilidades em paralelo...\n")
    
    n_cores = min(mp.cpu_count(), len(prob_list))
    print(f"Usando {n_cores} cores\n")
    
    all_results = []
    
    with ProcessPoolExecutor(max_workers=n_cores) as executor:
        futures = {executor.submit(process_prob_parallel, prob): prob for prob in prob_list}
        
        for future in as_completed(futures):
            prob = futures[future]
            try:
                result = future.result()
                if result:
                    all_results.append(result)
            except Exception as e:
                print(f"Erro na prob {prob:.2f}: {e}")
    
    if all_results:
        df_summary = pd.DataFrame(all_results)
        df_summary = df_summary.sort_values('prob')
        
        summary_path = Path(output_base_path) / f"resumo_expoentes_frac{frac}_SRE{sre}_logfit.csv"
        df_summary.to_csv(summary_path, index=False)
        
        print(f"\n{'='*60}")
        print("RESUMO FINAL - AJUSTE LOG-LOG")
        print(f"{'='*60}")
        print(df_summary[['prob', 't_min', 'alpha_mean', 'alpha_std', 'alpha_std_error', 'mean_r_squared', 'n_runs']].to_string(index=False))
        
        print(f"\nArquivo salvo em: {summary_path}")
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Resultados salvos em: {output_base_path}")