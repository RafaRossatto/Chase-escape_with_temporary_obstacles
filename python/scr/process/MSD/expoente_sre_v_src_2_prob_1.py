import pandas as pd
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configuração
prob = 1.00  # Probabilidade fixa em 1.00
sre_list = [2, 4, 6, 8, 10, 12, 14, 16]  # SREs de 2 a 16 de 2 em 2
frac = 100

# Dicionário para definir t_min para cada SRE
t_min_dict = {
    2: 1e6,
    4: 1e6,
    6: 1e6,
    8: 1e6,
    10: 1e6,
    12: 1e6,
    14: 1e6,
    16: 1e6,
}

# Caminhos
input_base_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/MSD_p_1/frac_{frac}"
output_base_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/{frac}/sre_variation_prob{prob:.0f}"

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
        
        # Ajuste linear no espaço log
        popt, pcov = curve_fit(
            power_law_log, 
            log_t, 
            log_msd,
            p0=[1.0, 0.0],
            maxfev=5000
        )
        
        alpha = popt[0]
        log_c = popt[1]
        c = 10**log_c
        
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

def process_sre(sre):
    """Processa um SRE: calcula expoentes para todos os runs"""
    t_min = t_min_dict.get(sre, 4e5)
    
    sre_input_dir = Path(input_base_path) / f"SRE_{sre}" / "individual_runs"
    sre_output_dir = Path(output_base_path) / f"SRE_{sre}"
    sre_output_dir.mkdir(parents=True, exist_ok=True)
    
    if not sre_input_dir.exists():
        print(f"  ✗ Diretório não encontrado: {sre_input_dir}")
        return None
    
    run_files = sorted(sre_input_dir.glob("run_*_msd.csv"))
    
    if not run_files:
        print(f"  ✗ Nenhum arquivo de run encontrado para SRE={sre}")
        return None
    
    print(f"  Processando {len(run_files)} runs para SRE={sre} (t_min={t_min:.0e})...")
    
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
        
        output_csv = sre_output_dir / f"expoentes_SRE_{sre}_tmin{t_min:.0e}.csv"
        df_results.to_csv(output_csv, index=False)
        
        alpha_mean = df_results['alpha'].mean()
        alpha_std = df_results['alpha'].std()
        alpha_std_error = df_results['alpha'].sem()
        mean_r_squared = df_results['r_squared'].mean()
        
        print(f"  ✓ SRE={sre}: {successful}/{len(run_files)} runs válidos")
        print(f"    α médio = {alpha_mean:.4f} ± {alpha_std:.4f} (std)")
        print(f"    R² médio = {mean_r_squared:.4f}")
        
        return {
            'sre': sre,
            't_min': t_min,
            'alpha_mean': alpha_mean,
            'alpha_std': alpha_std,
            'alpha_std_error': alpha_std_error,
            'mean_r_squared': mean_r_squared,
            'n_runs': successful,
            'n_total_runs': len(run_files)
        }
    else:
        print(f"  ✗ Nenhum run válido para SRE={sre}")
        return None

def process_sre_parallel(sre):
    """Wrapper para processamento paralelo por SRE"""
    return process_sre(sre)

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"Calculando expoentes α (MSD ~ t^α) - AJUSTE LOG-LOG")
    print(f"Probabilidade fixa = {prob:.2f}")
    print(f"Fração: {frac}%")
    print(f"SREs: {sre_list}")
    print(f"{'='*60}\n")
    
    print("Configuração de t_min por SRE:")
    for sre, tmin in t_min_dict.items():
        print(f"  SRE={sre}: t_min = {tmin:.0e}")
    
    print(f"\nProcessando {len(sre_list)} SREs em paralelo...\n")
    
    n_cores = min(mp.cpu_count(), len(sre_list))
    print(f"Usando {n_cores} cores\n")
    
    all_results = []
    
    with ProcessPoolExecutor(max_workers=n_cores) as executor:
        futures = {executor.submit(process_sre_parallel, sre): sre for sre in sre_list}
        
        for future in as_completed(futures):
            sre = futures[future]
            try:
                result = future.result()
                if result:
                    all_results.append(result)
            except Exception as e:
                print(f"Erro no SRE {sre}: {e}")
    
    if all_results:
        df_summary = pd.DataFrame(all_results)
        df_summary = df_summary.sort_values('sre')
        
        summary_path = Path(output_base_path) / f"resumo_expoentes_frac{frac}_prob{prob:.0f}_logfit.csv"
        df_summary.to_csv(summary_path, index=False)
        
        print(f"\n{'='*60}")
        print("RESUMO FINAL - AJUSTE LOG-LOG")
        print(f"{'='*60}")
        print(df_summary[['sre', 't_min', 'alpha_mean', 'alpha_std', 'alpha_std_error', 'mean_r_squared', 'n_runs']].to_string(index=False))
        
        print(f"\nArquivo salvo em: {summary_path}")
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Resultados salvos em: {output_base_path}")