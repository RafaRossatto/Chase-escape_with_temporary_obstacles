import pandas as pd
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configuração
sre_list = [2, 4, 8, 10, 12, 14, 16]
frac = 25
t_min = 20e4  # Tempo mínimo para começar o fit (ajuste conforme necessário)


# Caminhos
input_base_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/MSD_{frac}_per_run"
output_base_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/expoente/{frac}"

def power_law(t, alpha, c):
    """Função power law: MSD = c * t^alpha"""
    return c * (t ** alpha)

def compute_exponent_from_csv(run_csv_path, t_min):
    """Calcula o expoente alpha a partir do arquivo CSV de um run"""
    try:
        df = pd.read_csv(run_csv_path)
        
        # Filtra pelo tempo mínimo
        df_fit = df[df['time'] >= t_min].copy()
        
        if len(df_fit) < 3:
            return None, "Pontos insuficientes para fit"
        
        # Ajuste da power law
        popt, pcov = curve_fit(
            power_law, 
            df_fit['time'].values, 
            df_fit['msd'].values,
            p0=[1.0, 1.0],  # chute inicial: alpha=1, c=1
            maxfev=5000
        )
        
        alpha, c = popt
        alpha_err = np.sqrt(np.diag(pcov))[0] if len(pcov) > 0 else np.nan
        
        return {
            'alpha': alpha,
            'alpha_error': alpha_err,
            'c': c,
            'n_points': len(df_fit),
            't_min_used': t_min,
            't_max_used': df_fit['time'].max(),
            'msd_final': df['msd'].iloc[-1] if len(df) > 0 else np.nan
        }, None
        
    except Exception as e:
        return None, str(e)

def process_sre(sre):
    """Processa um SRE: calcula expoentes para todos os runs"""
    sre_input_dir = Path(input_base_path) / f"SRE_{sre}" / "individual_runs"
    sre_output_dir = Path(output_base_path) / f"SRE_{sre}"
    sre_output_dir.mkdir(parents=True, exist_ok=True)
    
    if not sre_input_dir.exists():
        print(f"  ✗ Diretório não encontrado: {sre_input_dir}")
        return None
    
    # Lista todos os arquivos CSV de runs
    run_files = sorted(sre_input_dir.glob("run_*_msd.csv"))
    
    if not run_files:
        print(f"  ✗ Nenhum arquivo de run encontrado para SRE={sre}")
        return None
    
    print(f"  Processando {len(run_files)} runs para SRE={sre}...")
    
    results = []
    successful = 0
    
    for run_file in run_files:
        # Extrai o número do run do nome do arquivo
        run_num = int(run_file.stem.split('_')[1])
        
        result, error = compute_exponent_from_csv(run_file, t_min)
        
        if result is not None:
            results.append({
                'run': run_num,
                **result
            })
            successful += 1
        else:
            print(f"    Run {run_num}: erro - {error}")
    
    if results:
        # Salva CSV com expoentes de todos os runs
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('run')
        
        output_csv = sre_output_dir / f"expoentes_SRE_{sre}_tmin{t_min}.csv"
        df_results.to_csv(output_csv, index=False)
        
        # Estatísticas consolidadas
        alpha_mean = df_results['alpha'].mean()
        alpha_std = df_results['alpha'].std()
        
        print(f"  ✓ SRE={sre}: {successful}/{len(run_files)} runs válidos")
        print(f"    α médio = {alpha_mean:.4f} ± {alpha_std:.4f}")
        
        return {
            'sre': sre,
            'alpha_mean': alpha_mean,
            'alpha_std': alpha_std,
            'n_runs': successful
        }
    else:
        print(f"  ✗ Nenhum run válido para SRE={sre}")
        return None

def process_sre_parallel(sre):
    """Wrapper para processamento paralelo por SRE"""
    return process_sre(sre)

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"Calculando expoentes α (MSD ~ t^α)")
    print(f"Tempo mínimo para fit: t_min = {t_min}")
    print(f"Fração: {frac}%")
    print(f"SREs: {sre_list}")
    print(f"{'='*60}\n")
    
    # Processa SREs em paralelo
    n_cores = min(mp.cpu_count(), len(sre_list))
    print(f"Processando {len(sre_list)} SREs em paralelo usando {n_cores} cores\n")
    
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
    
    # Salva resumo consolidado
    if all_results:
        df_summary = pd.DataFrame(all_results)
        df_summary = df_summary.sort_values('sre')
        
        summary_path = Path(output_base_path) / f"resumo_expoentes_frac{frac}_tmin{t_min}.csv"
        df_summary.to_csv(summary_path, index=False)
        
        print(f"\n{'='*60}")
        print("RESUMO FINAL")
        print(f"{'='*60}")
        print(df_summary.to_string(index=False))
        print(f"\nArquivo salvo em: {summary_path}")
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Resultados salvos em: {output_base_path}")