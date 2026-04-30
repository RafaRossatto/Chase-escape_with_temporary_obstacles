#Nese código ele vai salvar uma saida para cada run de configuração, ou seja, ele vai salvar para cada congir o msd de ensable.

import pandas as pd
import numpy as np
from trajpy.trajpy import Trajectory
from scipy.interpolate import interp1d
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configuração
sre_list = [2, 4, 8, 10, 12, 14, 16]
prob = 1.00
num_runs = 100
frac = 25

data_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/"
output_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/MSD_{frac}_per_run"

Path(output_path).mkdir(parents=True, exist_ok=True)
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

def process_single_run(sre, run):
    """Processa um único run e retorna o MSD"""
    file_path = f"{data_path}simulation_frac_{frac}_run_{run}_obsprob_{prob:.2f}_SRC_2_SRE_{sre}/results_chasers_run{run}.csv"
    
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
            'sre': sre,
            'times': times, 
            'msd': msd_ensemble, 
            'success': True
        }
        
    except Exception as e:
        return {
            'run': run, 
            'sre': sre,
            'success': False, 
            'error': str(e)
        }

def process_sre(sre):
    """Processa um SRE completo - salva cada run individualmente"""
    print(f"\n{'='*60}")
    print(f"Processando SRE = {sre}")
    print(f"{'='*60}")
    
    # Diretório principal para este SRE
    output_dir = Path(output_path) / f"SRE_{sre}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Diretório para runs individuais
    runs_dir = output_dir / "individual_runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    
    # Primeiro, processa run 1 para obter tempos de referência
    print(f"  Obtendo tempos de referência...")
    ref_result = process_single_run(sre, 1)
    
    if not ref_result['success']:
        print(f"  ✗ Erro ao processar run de referência")
        return None
    
    reference_times = ref_result['times']
    all_runs_msd = []
    successful_runs = 0
    
    # Salva o run 1 individualmente
    df_run1 = pd.DataFrame({
        'time': reference_times,
        'msd': ref_result['msd']
    })
    df_run1.to_csv(runs_dir / f"run_001_msd.csv", index=False)
    all_runs_msd.append(ref_result['msd'])
    successful_runs = 1
    
    # Processa runs 2..num_runs em paralelo
    print(f"  Processando runs 2..{num_runs} em paralelo (usando {mp.cpu_count()} cores)...")
    
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        # Submete todos os runs restantes
        futures = {executor.submit(process_single_run, sre, run): run 
                  for run in range(2, num_runs + 1)}
        
        # Coleta os resultados
        for future in as_completed(futures):
            result = future.result()
            if result['success']:
                # Interpolar se necessário
                if len(result['times']) != len(reference_times):
                    f_interp = interp1d(result['times'], result['msd'], 
                                       kind='linear', fill_value='extrapolate')
                    msd_interp = f_interp(reference_times)
                    msd_final = msd_interp
                else:
                    msd_final = result['msd']
                
                # Salva MSD individual deste run
                df_run = pd.DataFrame({
                    'time': reference_times,
                    'msd': msd_final
                })
                run_filename = runs_dir / f"run_{result['run']:03d}_msd.csv"
                df_run.to_csv(run_filename, index=False)
                
                all_runs_msd.append(msd_final)
                successful_runs += 1
            
            if successful_runs % 10 == 0:
                print(f"    Processados {successful_runs}/{num_runs} runs...")
    
    if all_runs_msd:
        all_runs_msd = np.array(all_runs_msd)
        msd_mean = np.mean(all_runs_msd, axis=0)
        msd_std = np.std(all_runs_msd, axis=0)
        
        # Salva estatísticas consolidadas
        df_results = pd.DataFrame({
            'time': reference_times,
            'msd_mean': msd_mean,
            'msd_std': msd_std
        })
        csv_path = output_dir / f"msd_ensemble_SRE_{sre}.csv"
        df_results.to_csv(csv_path, index=False)
        
        print(f"  ✓ SRE={sre} concluído: {successful_runs}/{num_runs} runs, MSD final={msd_mean[-1]:.2f}")
        return {'sre': sre, 'success': True}
    else:
        print(f"  ✗ Nenhum run válido para SRE={sre}")
        return None

# Execução principal
if __name__ == "__main__":
    print(f"Processando SREs em sequência, cada uma com paralelismo interno de {mp.cpu_count()} cores")
    print(f"Total de SREs a processar: {len(sre_list)}")
    
    for sre in sre_list:
        process_sre(sre)
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Resultados salvos em: {output_path}")