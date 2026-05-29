import pandas as pd
import numpy as np
from trajpy.trajpy import Trajectory
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configuração
prob_list = [round(p, 2) for p in np.arange(0.00, 1.01, 0.10)]
sre_fixo = 2
num_runs = 100
frac_list = [25, 50, 100]

base_data_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/v_prob/"
base_output_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/MSD_per_run_v_prob"

Path(base_output_path).mkdir(parents=True, exist_ok=True)
L = 256

def unwrap_trajectory(df_particle, L):
    """Desfaz condições de contorno periódicas para uma trajetória"""
    df_particle = df_particle.sort_values("time").copy()
    
    x_unwrapped = [df_particle["x"].iloc[0]]
    y_unwrapped = [df_particle["y"].iloc[0]]
    
    for i in range(1, len(df_particle)):
        dx = df_particle["x"].iloc[i] - df_particle["x"].iloc[i - 1]
        dy = df_particle["y"].iloc[i] - df_particle["y"].iloc[i - 1]
        
        if dx > L / 2:
            dx -= L
        elif dx < -L / 2:
            dx += L
        
        if dy > L / 2:
            dy -= L
        elif dy < -L / 2:
            dy += L
        
        x_unwrapped.append(x_unwrapped[-1] + dx)
        y_unwrapped.append(y_unwrapped[-1] + dy)
    
    df_particle["x_unwrapped"] = x_unwrapped
    df_particle["y_unwrapped"] = y_unwrapped
    
    return df_particle

def process_single_run(frac, prob, sre, run):
    """Processa um único run e retorna o MSD"""
    prob_str = f"{prob:.2f}"
    file_path = f"{base_data_path}simulation_frac_{frac}_run_{run}_obsprob_{prob_str}_SRC_2_SRE_{sre}/results_chasers_run{run}.csv"
    
    try:
        df = pd.read_csv(file_path)
        
        df_unwrapped_list = []
        for pid, group in df.groupby("id"):
            df_unwrapped = unwrap_trajectory(group, L)
            df_unwrapped_list.append(df_unwrapped)
        
        df_all = pd.concat(df_unwrapped_list, ignore_index=True)
        times = sorted(df_all["time"].unique())
        particle_ids = df_all["id"].unique()
        n_particles = len(particle_ids)
        n_times = len(times)
        
        positions_3d = np.zeros((n_particles, n_times, 2))
        
        for i, pid in enumerate(particle_ids):
            df_particle = df_all[df_all["id"] == pid].sort_values("time")
            for j, t in enumerate(times):
                pos = df_particle[df_particle["time"] == t][["x_unwrapped", "y_unwrapped"]].values
                if len(pos) > 0:
                    positions_3d[i, j] = pos[0]
                elif j > 0:
                    positions_3d[i, j] = positions_3d[i, j-1]
        
        msd_ensemble = Trajectory.msd_ensemble_averaged_(positions_3d.transpose(1, 0, 2))
        
        return {
            'run': run, 
            'frac': frac,
            'prob': prob,
            'times': times, 
            'msd': msd_ensemble, 
            'success': True
        }
        
    except Exception as e:
        return {
            'run': run, 
            'frac': frac,
            'prob': prob,
            'success': False, 
            'error': str(e)
        }

def process_probability(frac, prob):
    """Processa uma probabilidade completa - salva cada run individualmente"""
    print(f"\n{'='*60}")
    print(f"Processando: frac = {frac}%, prob = {prob:.2f}")
    print(f"{'='*60}")
    
    output_dir = Path(base_output_path) / f"frac_{frac}" / f"obsprob_{prob:.2f}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    runs_dir = output_dir / "individual_runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    
    # Processa run 1 para referência
    print(f"  Obtendo tempos de referência...")
    ref_result = process_single_run(frac, prob, sre_fixo, 1)
    
    if not ref_result['success']:
        print(f"  ✗ Erro ao processar run de referência: {ref_result.get('error', 'Unknown error')}")
        return None
    
    reference_times = ref_result['times']
    all_runs_msd = [ref_result['msd']]
    successful_runs = 1
    
    # Salva run 1
    df_run1 = pd.DataFrame({
        'time': reference_times,
        'msd': ref_result['msd']
    })
    df_run1.to_csv(runs_dir / f"run_001_msd.csv", index=False)
    
    # Processa runs 2..num_runs em paralelo
    print(f"  Processando runs 2..{num_runs} em paralelo (usando {mp.cpu_count()} cores)...")
    
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        futures = {executor.submit(process_single_run, frac, prob, sre_fixo, run): run 
                  for run in range(2, num_runs + 1)}
        
        for future in as_completed(futures):
            result = future.result()
            if result['success']:
                # Como os tempos são iguais, usamos diretamente sem interpolação
                df_run = pd.DataFrame({
                    'time': reference_times,  # ou result['times'] - são iguais
                    'msd': result['msd']
                })
                run_filename = runs_dir / f"run_{result['run']:03d}_msd.csv"
                df_run.to_csv(run_filename, index=False)
                
                all_runs_msd.append(result['msd'])
                successful_runs += 1
            
            if successful_runs % 10 == 0:
                print(f"    Processados {successful_runs}/{num_runs} runs...")
    
    if all_runs_msd:
        all_runs_msd = np.array(all_runs_msd)
        msd_mean = np.mean(all_runs_msd, axis=0)
        msd_std = np.std(all_runs_msd, axis=0)
        
        df_results = pd.DataFrame({
            'time': reference_times,
            'msd_mean': msd_mean,
            'msd_std': msd_std
        })
        csv_path = output_dir / f"msd_ensemble_frac_{frac}_obsprob_{prob:.2f}.csv"
        df_results.to_csv(csv_path, index=False)
        
        print(f"  ✓ Completo: frac={frac}%, prob={prob:.2f} - {successful_runs}/{num_runs} runs")
        return {'frac': frac, 'prob': prob, 'success': True}
    else:
        print(f"  ✗ Nenhum run válido")
        return None

# Execução principal
if __name__ == "__main__":
    total_combinations = len(frac_list) * len(prob_list)
    print(f"Processando combinações de frac e probabilidade")
    print(f"Frações: {frac_list}%")
    print(f"Probabilidades: {len(prob_list)} valores de 0.00 a 1.00")
    print(f"Total de combinações: {total_combinations}")
    
    completed = 0
    failed = 0
    
    for frac in frac_list:
        print(f"\n{'#'*60}")
        print(f"# Processando fração: {frac}%")
        print(f"{'#'*60}")
        
        for prob in prob_list:
            result = process_probability(frac, prob)
            if result and result['success']:
                completed += 1
            else:
                failed += 1
            
            print(f"Progresso: {completed + failed}/{total_combinations}")
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Completos: {completed}")
    print(f"Falhas: {failed}")