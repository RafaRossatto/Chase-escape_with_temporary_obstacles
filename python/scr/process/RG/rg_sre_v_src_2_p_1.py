import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
import warnings
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURAÇÕES
# ============================================
base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_raw/prob_1/"
output_base = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/gyration_radius/sre_v_src_2_p_1"

# Parâmetros
sre_list = [2, 4,6, 8, 10, 12, 14, 16]
prob = 1.00
num_runs = 100
L = 256

frac_list = [25,50,100]
# Dicionário para definir t_min para cada SRE (tempo inicial para calcular o raio de giro)
# Ajuste conforme necessário para cada configuração
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
t_min_default = 4e5  # Valor padrão se não definido

# Criar diretório base
Path(output_base).mkdir(parents=True, exist_ok=True)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def unwrap_trajectory(df_particle, L):
    """Desfaz condições de contorno periódicas"""
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

def filter_by_time(df_particle, t_min):
    """Filtra a trajetória a partir do tempo mínimo"""
    return df_particle[df_particle['time'] >= t_min].copy()

def calculate_gyration_radius(positions):
    """Calcula o raio de giro MANUALMENTE"""
    cm = np.mean(positions, axis=0)
    displacements = positions - cm
    squared_distances = displacements[:, 0]**2 + displacements[:, 1]**2
    Rg = np.sqrt(np.mean(squared_distances))
    Rg_xx = np.mean(displacements[:, 0]**2)
    Rg_yy = np.mean(displacements[:, 1]**2)
    Rg_xy = np.mean(displacements[:, 0] * displacements[:, 1])
    
    return Rg, Rg_xx, Rg_yy, Rg_xy

def process_single_run(args):
    """Processa um único run - isso roda em paralelo para cada run"""
    frac, sre, run, t_min = args
    
    file_path = f"{base_path}simulation_frac_{frac}_run_{run}_obsprob_{prob:.2f}_SRC_2_SRE_{sre}/results_chasers_run{run}.csv"
    
    try:
        df = pd.read_csv(file_path)
        
        resultados_run = []
        
        for pid, group in df.groupby("id"):
            # Desfaz condições de contorno
            df_unwrapped = unwrap_trajectory(group, L)
            
            # Filtra pelo tempo mínimo
            df_filtered = filter_by_time(df_unwrapped, t_min)
            
            if len(df_filtered) < 2:
                continue  # Poucos pontos após o filtro
            
            positions = df_filtered[["x_unwrapped", "y_unwrapped"]].values
            Rg, Rg_xx, Rg_yy, Rg_xy = calculate_gyration_radius(positions)
            
            resultados_run.append({
                'particle_id': pid,
                'Rg': Rg,
                'Rg_xx': Rg_xx,
                'Rg_yy': Rg_yy,
                'Rg_xy': Rg_xy,
                'n_points': len(positions),
                't_min_used': t_min,
                'time_first': df_filtered['time'].min(),
                'time_last': df_filtered['time'].max()
            })
        
        if resultados_run:
            df_run = pd.DataFrame(resultados_run)
            return {
                'frac': frac,
                'sre': sre,
                'run': run,
                't_min': t_min,
                'success': True,
                'Rg_mean': df_run['Rg'].mean(),
                'Rg_std': df_run['Rg'].std(),
                'Rg_median': df_run['Rg'].median(),
                'Rg_xx_mean': df_run['Rg_xx'].mean(),
                'Rg_yy_mean': df_run['Rg_yy'].mean(),
                'Rg_xy_mean': df_run['Rg_xy'].mean(),
                'n_particles': len(resultados_run),
                'all_results': df_run
            }
        else:
            return {'frac': frac, 'sre': sre, 'run': run, 'success': False}
            
    except Exception as e:
        print(f"  Erro no run {run} (frac={frac}, SRE={sre}): {e}")
        return {'frac': frac, 'sre': sre, 'run': run, 'success': False}

def process_frac_sre(frac, sre):
    """Processa UMA combinação de frac e sre - isso roda em SEQUÊNCIA"""
    
    # Obtém t_min para este SRE
    t_min = t_min_dict.get(sre, t_min_default)
    
    print(f"\n{'='*60}")
    print(f"Processando frac={frac}, SRE={sre}, t_min={t_min:.0e}")
    print(f"{'='*60}")
    
    # Diretório de saída
    output_dir = Path(output_base) / f"frac_{frac}" / f"SRE_{sre}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Preparar argumentos para todos os runs (incluindo t_min)
    args_list = [(frac, sre, run, t_min) for run in range(1, num_runs + 1)]
    
    # Processar runs em PARALELO
    all_runs_summary = []
    all_particles_data = []
    successful_runs = 0
    
    print(f"Processando {num_runs} runs em paralelo usando {mp.cpu_count()} cores...")
    print(f"Usando tempo mínimo t_min = {t_min:.0e}")
    
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        futures = {executor.submit(process_single_run, args): args for args in args_list}
        
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            
            if result['success']:
                all_runs_summary.append({
                    'run': result['run'],
                    't_min': result['t_min'],
                    'Rg_mean': result['Rg_mean'],
                    'Rg_std': result['Rg_std'],
                    'Rg_median': result['Rg_median'],
                    'Rg_xx_mean': result['Rg_xx_mean'],
                    'Rg_yy_mean': result['Rg_yy_mean'],
                    'Rg_xy_mean': result['Rg_xy_mean'],
                    'n_particles': result['n_particles']
                })
                
                df_part = result['all_results']
                df_part['run'] = result['run']
                df_part['frac'] = frac
                df_part['sre'] = sre
                all_particles_data.append(df_part)
                
                successful_runs += 1
            
            if i % 10 == 0:
                print(f"  Processados {i}/{num_runs} runs...")
    
    if all_runs_summary:
        # Salvar resultados
        df_summary = pd.DataFrame(all_runs_summary)
        df_summary.to_csv(output_dir / f'summary_runs_tmin{t_min:.0e}.csv', index=False)
        
        df_all_particles = pd.concat(all_particles_data, ignore_index=True)
        df_all_particles.to_csv(output_dir / f'all_particles_tmin{t_min:.0e}.csv', index=False)
        
        # Estatísticas finais
        final_stats = {
            'frac': frac,
            'sre': sre,
            't_min': t_min,
            'total_runs': successful_runs,
            'total_particles': len(df_all_particles),
            'Rg_mean_overall': df_all_particles['Rg'].mean(),
            'Rg_std_overall': df_all_particles['Rg'].std(),
            'Rg_median_overall': df_all_particles['Rg'].median(),
            'Rg_xx_mean': df_all_particles['Rg_xx'].mean(),
            'Rg_yy_mean': df_all_particles['Rg_yy'].mean(),
            'Rg_xy_mean': df_all_particles['Rg_xy'].mean()
        }
        
        df_stats = pd.DataFrame([final_stats])
        df_stats.to_csv(output_dir / f'final_statistics_tmin{t_min:.0e}.csv', index=False)
        
        # Salvar resumo em texto
        with open(output_dir / f'results_tmin{t_min:.0e}.txt', 'w') as f:
            f.write("="*60 + "\n")
            f.write(f"RESULTADOS - frac={frac}, SRE={sre}\n")
            f.write(f"Tempo mínimo: {t_min:.0e}\n")
            f.write("="*60 + "\n")
            f.write(f"Runs processados: {successful_runs}/{num_runs}\n")
            f.write(f"Total de partículas: {final_stats['total_particles']}\n\n")
            f.write(f"Raio de Giro (Rg):\n")
            f.write(f"  Média:  {final_stats['Rg_mean_overall']:.4f}\n")
            f.write(f"  Desvio: {final_stats['Rg_std_overall']:.4f}\n")
            f.write(f"  Mediana:{final_stats['Rg_median_overall']:.4f}\n\n")
            f.write(f"Componentes do tensor:\n")
            f.write(f"  Rg_xx:  {final_stats['Rg_xx_mean']:.4f}\n")
            f.write(f"  Rg_yy:  {final_stats['Rg_yy_mean']:.4f}\n")
            f.write(f"  Rg_xy:  {final_stats['Rg_xy_mean']:.4f}\n")
            f.write("="*60 + "\n")
        
        print(f"  ✓ frac={frac}, SRE={sre} concluído!")
        print(f"    Rg médio = {final_stats['Rg_mean_overall']:.4f} ± {final_stats['Rg_std_overall']:.4f}")
        print(f"    Usando t_min = {t_min:.0e}")
        return final_stats
    else:
        print(f"  ✗ frac={frac}, SRE={sre} falhou!")
        return None

# ============================================
# EXECUÇÃO PRINCIPAL - SEQUENCIAL POR CONFIGURAÇÃO
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("CÁLCULO DO RAIO DE GIRO (com tempo inicial)")
    print("="*60)
    print(f"SREs: {sre_list}")
    print(f"Frações: {frac_list}")
    print(f"Runs por SRE: {num_runs}")
    print(f"Cores disponíveis: {mp.cpu_count()}")
    print("="*60)
    print("\nConfiguração de t_min por SRE:")
    for sre, tmin in t_min_dict.items():
        print(f"  SRE={sre}: t_min = {tmin:.0e}")
    print("="*60)
    
    all_results = []
    
    # Loop SEQUENCIAL sobre as configurações
    for frac in frac_list:
        for sre in sre_list:
            result = process_frac_sre(frac, sre)
            if result:
                all_results.append(result)
    
    # ============================================
    # RESULTADOS GLOBAIS
    # ============================================
    if all_results:
        df_global = pd.DataFrame(all_results)
        df_global.to_csv(Path(output_base) / 'global_results.csv', index=False)
        
        print("\n" + "="*60)
        print("RESULTADOS GLOBAIS")
        print("="*60)
        print(df_global[['frac', 'sre', 't_min', 'Rg_mean_overall', 'Rg_std_overall']].to_string(index=False))
        
        # Salvar também em formato legível
        with open(Path(output_base) / 'global_results.txt', 'w') as f:
            f.write("RESULTADOS GLOBAIS - RAIO DE GIRO\n")
            f.write("="*60 + "\n")
            f.write("frac\tsre\tt_min\tRg_mean\tRg_std\tRg_median\tn_particles\n")
            for _, row in df_global.iterrows():
                f.write(f"{int(row['frac'])}\t{row['sre']}\t{row['t_min']:.0e}\t{row['Rg_mean_overall']:.4f}\t{row['Rg_std_overall']:.4f}\t{row['Rg_median_overall']:.4f}\t{row['total_particles']}\n")
    
    print("\n" + "="*60)
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"Resultados salvos em: {output_base}")
    print("="*60)