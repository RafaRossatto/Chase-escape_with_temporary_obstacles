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
frac = 100

data_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/"
output_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/MSD_{frac}"

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
        
        return {'run': run, 'times': times, 'msd': msd_ensemble, 'success': True}
        
    except Exception as e:
        return {'run': run, 'success': False, 'error': str(e)}

def process_sre(sre):
    """Processa um SRE completo (serial)"""
    print(f"\n{'='*60}")
    print(f"Processando SRE = {sre}")
    print(f"{'='*60}")
    
    output_dir = Path(output_path) / f"SRE_{sre}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Primeiro, processa run 1 para obter tempos de referência
    print(f"  Obtendo tempos de referência...")
    ref_result = process_single_run(sre, 1)
    
    if not ref_result['success']:
        print(f"  ✗ Erro ao processar run de referência")
        return None
    
    reference_times = ref_result['times']
    all_runs_msd = []
    successful_runs = 0
    
    # Processa runs 2..num_runs em paralelo
    print(f"  Processando runs 1..{num_runs} em paralelo (usando {mp.cpu_count()} cores)...")
    
    # Prepara argumentos para todos os runs
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        # Submete todos os runs
        futures = {executor.submit(process_single_run, sre, run): run 
                  for run in range(1, num_runs + 1)}
        
        # Coleta os resultados
        for future in as_completed(futures):
            result = future.result()
            if result['success']:
                # Interpolar se necessário
                if len(result['times']) != len(reference_times):
                    f_interp = interp1d(result['times'], result['msd'], 
                                       kind='linear', fill_value='extrapolate')
                    msd_interp = f_interp(reference_times)
                    all_runs_msd.append(msd_interp)
                else:
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
        csv_path = output_dir / f"msd_ensemble_SRE_{sre}.csv"
        df_results.to_csv(csv_path, index=False)
        
        print(f"  ✓ SRE={sre} concluído: {successful_runs}/{num_runs} runs, MSD final={msd_mean[-1]:.2f}")
        return {'sre': sre, 'success': True}
    else:
        print(f"  ✗ Nenhum run válido para SRE={sre}")
        return None

# Execução principal: processa SREs em SEQUÊNCIA (não paralelo)
if __name__ == "__main__":
    print(f"Processando SREs em sequência, cada uma com paralelismo interno de {mp.cpu_count()} cores")
    print(f"Total de SREs a processar: {len(sre_list)}")
    
    for sre in sre_list:
        process_sre(sre)
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Resultados salvos em: {output_path}")


# import pandas as pd
# import numpy as np
# from trajpy.trajpy import Trajectory
# from scipy.interpolate import interp1d
# from pathlib import Path

# # Configuração
# sre_list = [2, 4, 8, 10, 12, 14, 16]  # Lista de SRE para processar
# prob = 1.00
# num_runs = 100
# frac = 25

# # Caminhos
# data_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/"
# output_path = f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/MSD_{frac}"

# # Criar diretório de saída principal
# Path(output_path).mkdir(parents=True, exist_ok=True)
# print(f"Resultados serão salvos em: {output_path}")

# # Função para unwrap das trajetórias
# def unwrap_trajectory(df_particle, L):
#     """Desfaz condições de contorno periódicas para uma trajetória"""
#     df_particle = df_particle.sort_values("time").copy()
    
#     x_unwrapped = [df_particle["x"].iloc[0]]
#     y_unwrapped = [df_particle["y"].iloc[0]]
    
#     for i in range(1, len(df_particle)):
#         dx = df_particle["x"].iloc[i] - df_particle["x"].iloc[i - 1]
#         dy = df_particle["y"].iloc[i] - df_particle["y"].iloc[i - 1]
        
#         if dx > L / 2:
#             dx -= L
#         elif dx < -L / 2:
#             dx += L
        
#         if dy > L / 2:
#             dy -= L
#         elif dy < -L / 2:
#             dy += L
        
#         x_unwrapped.append(x_unwrapped[-1] + dx)
#         y_unwrapped.append(y_unwrapped[-1] + dy)
    
#     df_particle["x_unwrapped"] = x_unwrapped
#     df_particle["y_unwrapped"] = y_unwrapped
    
#     return df_particle

# # Parâmetros
# L = 256

# # Loop sobre cada valor de SRE
# for sre in sre_list:
#     print(f"\n{'='*60}")
#     print(f"Processando SRE = {sre}")
#     print(f"{'='*60}")
    
#     # Diretório de saída para este SRE
#     output_dir = Path(output_path) / f"SRE_{sre}"
#     output_dir.mkdir(parents=True, exist_ok=True)
#     print(f"Resultados salvos em: {output_dir}")
    
#     # Lista para armazenar MSD de todos os runs
#     all_runs_times = None
#     all_runs_msd = []
#     successful_runs = 0
    
#     # Loop sobre todos os runs
#     for run in range(1, num_runs + 1):
#         file_path = f"{data_path}simulation_frac_{frac}_run_{run}_obsprob_{prob:.2f}_SRC_2_SRE_{sre}/results_chasers_run{run}.csv"
        
#         try:
#             # Carregar dados
#             df = pd.read_csv(file_path)
            
#             # Fazer unwrap para cada partícula
#             df_unwrapped_list = []
#             for pid, group in df.groupby("id"):
#                 df_unwrapped = unwrap_trajectory(group, L)
#                 df_unwrapped_list.append(df_unwrapped)
            
#             df_all = pd.concat(df_unwrapped_list, ignore_index=True)
            
#             # Organizar posições por tempo para o ensemble MSD
#             times = sorted(df_all["time"].unique())
            
#             # Obter todas as partículas únicas
#             particle_ids = df_all["id"].unique()
#             n_particles = len(particle_ids)
#             n_times = len(times)
            
#             # Criar array 3D: [partículas, tempos, coordenadas]
#             positions_3d = np.zeros((n_particles, n_times, 2))
            
#             for i, pid in enumerate(particle_ids):
#                 df_particle = df_all[df_all["id"] == pid].sort_values("time")
#                 for j, t in enumerate(times):
#                     pos = df_particle[df_particle["time"] == t][["x_unwrapped", "y_unwrapped"]].values
#                     if len(pos) > 0:
#                         positions_3d[i, j] = pos[0]
#                     else:
#                         if j > 0:
#                             positions_3d[i, j] = positions_3d[i, j-1]
            
#             # Usar o método ensemble-averaged do trajpy
#             msd_ensemble = Trajectory.msd_ensemble_averaged_(positions_3d.transpose(1, 0, 2))
            
#             # Alinhar com runs anteriores
#             if all_runs_times is None:
#                 all_runs_times = np.array(times)
#                 all_runs_msd.append(msd_ensemble)
#                 successful_runs += 1
#             elif len(times) == len(all_runs_times):
#                 all_runs_msd.append(msd_ensemble)
#                 successful_runs += 1
#             else:
#                 f_interp = interp1d(times, msd_ensemble, kind='linear', fill_value='extrapolate')
#                 msd_interp = f_interp(all_runs_times)
#                 all_runs_msd.append(msd_interp)
#                 successful_runs += 1
            
#             if run % 10 == 0:
#                 print(f"  Processados {run}/{num_runs} runs...")
                
#         except FileNotFoundError:
#             print(f"  Arquivo não encontrado: run {run}")
#             continue
#         except Exception as e:
#             print(f"  Erro no run {run}: {e}")
#             continue
    
#     if all_runs_msd:
#         # Calcular média e desvio padrão sobre todos os runs
#         all_runs_msd = np.array(all_runs_msd)
#         msd_mean = np.mean(all_runs_msd, axis=0)
#         msd_std = np.std(all_runs_msd, axis=0)
        
#         times = all_runs_times
        
#         # SALVAR DADOS EM CSV
#         df_results = pd.DataFrame({
#             'time': times,
#             'msd_mean': msd_mean,
#             'msd_std': msd_std
#         })
#         csv_path = output_dir / f"msd_ensemble_SRE_{sre}.csv"
#         df_results.to_csv(csv_path, index=False)
#         print(f"✓ Dados salvos em: {csv_path}")
        
#         # SALVAR ESTATÍSTICAS EM TXT
#         stats_path = output_dir / f"msd_stats_SRE_{sre}.txt"
#         with open(stats_path, 'w') as f:
#             f.write(f"{'='*60}\n")
#             f.write(f"RESULTADOS ENSEMBLE-AVERAGED (trajpy) PARA SRE={sre}\n")
#             f.write(f"{'='*60}\n")
#             f.write(f"Número de runs processados: {successful_runs}\n")
#             f.write(f"Tempo máximo: {times[-1]}\n")
#             f.write(f"MSD final: {msd_mean[-1]:.2f} ± {msd_std[-1]:.2f}\n")
            
#             # # Expoente α (primeiros 10 passos)
#             # n_i, n_f = 0, min(10, len(times))
#             # if n_f > n_i:
#             #     log_t = np.log(times[n_i:n_f])
#             #     log_msd = np.log(msd_mean[n_i:n_f])
#             #     alpha = np.polyfit(log_t, log_msd, 1)[0]
#             #     f.write(f"Expoente α (primeiros {n_f} passos): {alpha:.3f}\n")
#             # f.write(f"{'='*60}\n")
        
#         print(f"✓ Estatísticas salvas em: {stats_path}")
        
#         # Mostrar resumo no terminal
#         print(f"\nResumo para SRE={sre}:")
#         print(f"  Runs processados: {successful_runs}")
#         print(f"  Tempo máximo: {times[-1]}")
#         print(f"  MSD final: {msd_mean[-1]:.2f} ± {msd_std[-1]:.2f}")
        
#     else:
#         print(f"✗ Nenhum dado válido encontrado para SRE={sre}")

# print(f"\n{'='*60}")
# print("PROCESSAMENTO CONCLUÍDO!")
# print(f"{'='*60}")
# print(f"Todos os resultados foram salvos em: {output_path}")
