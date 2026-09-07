import pandas as pd
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# Configuração
sre = 2  # SRE fixo em 2

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
        
        alpha = popt[0]  # expoente
        
        return {'alpha': alpha}, None
        
    except Exception as e:
        return None, str(e)

def load_t_min_from_conf(frac, prob):
    """Carrega o t_min (primeiro_x) do arquivo conf.csv"""
    conf_path = Path(f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/config.csv")
    
    if not conf_path.exists():
        print(f"  ✗ Arquivo conf.csv não encontrado em: {conf_path}")
        return None
    
    try:
        df_conf = pd.read_csv(conf_path)
        
        # Filtra pela fração e probabilidade
        mask = (df_conf['frac'] == frac) & (df_conf['obsprob'] == prob)
        df_filtered = df_conf[mask]
        
        if len(df_filtered) == 0:
            print(f"  ✗ Configuração não encontrada: frac={frac}, obsprob={prob}")
            return None
        
        # Pega o primeiro_x (t_min) da primeira ocorrência
        t_min = df_filtered['primeiro_x'].iloc[0]
        
        return t_min
        
    except Exception as e:
        print(f"  ✗ Erro ao ler conf.csv: {e}")
        return None

def process_probability(frac, prob, output_base_path, input_base_path):
    """Processa uma probabilidade: calcula expoentes para todos os runs"""
    # Carrega t_min do arquivo conf.csv
    t_min = load_t_min_from_conf(frac, prob)
    
    if t_min is None:
        print(f"  ✗ Não foi possível obter t_min para frac={frac}, prob={prob}")
        return None
    
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
    
    print(f"  Processando {len(run_files)} runs para frac={frac}, prob={prob:.2f} (t_min={t_min:.0e})...")
    
    alphas = []
    successful = 0
    
    for run_file in run_files:
        run_num = int(run_file.stem.split('_')[1])
        
        result, error = compute_exponent_from_csv(run_file, t_min)
        
        if result is not None:
            alphas.append(result['alpha'])
            successful += 1
        else:
            if error:
                print(f"    Run {run_num}: erro - {error}")
    
    if alphas:
        # Calcula estatísticas
        alpha_mean = np.mean(alphas)
        alpha_std = np.std(alphas, ddof=1)  # Desvio padrão amostral
        alpha_var = np.var(alphas, ddof=1)   # Variância amostral
        
        # Salva resultados individuais (opcional - pode remover se não precisar)
        df_results = pd.DataFrame({'alpha': alphas})
        output_csv = prob_output_dir / f"expoentes_prob_{prob:.2f}.csv"
        df_results.to_csv(output_csv, index=False)
        
        print(f"  ✓ frac={frac}, prob={prob:.2f}: {successful}/{len(run_files)} runs válidos")
        print(f"    α médio = {alpha_mean:.6f}")
        print(f"    α std   = {alpha_std:.6f}")
        print(f"    α var   = {alpha_var:.6f}")
        
        return {
            'frac': frac,
            'prob': prob,
            't_min': t_min,
            'alpha_mean': alpha_mean,
            'alpha_std': alpha_std,
            'alpha_var': alpha_var,
            'n_runs': successful,
            'n_total_runs': len(run_files)
        }
    else:
        print(f"  ✗ Nenhum run válido para frac={frac}, prob={prob:.2f}")
        return None

def process_all_combinations(frac_list, prob_list, input_base_path_pattern, output_base_path_pattern):
    """Processa todas as combinações de frações e probabilidades"""
    
    all_results = []
    
    for frac in frac_list:
        print(f"\n{'='*60}")
        print(f"Processando fração: {frac}%")
        print(f"{'='*60}")
        
        # Constrói os caminhos específicos para esta fração
        input_base_path = input_base_path_pattern.format(frac=frac)
        output_base_path = output_base_path_pattern.format(frac=frac)
        
        # Cria diretório de saída
        Path(output_base_path).mkdir(parents=True, exist_ok=True)
        
        for prob in prob_list:
            result = process_probability(frac, prob, output_base_path, input_base_path)
            if result:
                all_results.append(result)
    
    return all_results

if __name__ == "__main__":
    # Define as frações e probabilidades a serem processadas
    # Ajuste estas listas conforme necessário
    frac_list = list(range(5, 101, 5))
    frac_list = [5,50,100]
    # Lista de probabilidades - você pode definir ou ler do conf.csv
    # Aqui estou usando um exemplo, mas você pode querer extrair do conf.csv
    prob_list = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
    
    # Padrões dos caminhos
    # input_base_path_pattern = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/MSD_sre_2_src_2_prob_v_frac_v/frac_{frac}"
    input_base_path_pattern = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/128/MSD_sre_2_src_2_prob_v_frac_v/frac_{frac}"
    output_base_path_pattern = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/128/{frac}/prob_variation"
    # output_base_path_pattern = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/{frac}/prob_variation"

    print(f"{'='*60}")
    print(f"Calculando expoentes α (MSD ~ t^α) - AJUSTE LOG-LOG")
    print(f"SRE fixo = {sre}")
    print(f"Frações: {frac_list}")
    print(f"Probabilidades: {len(prob_list)} valores")
    print(f"{'='*60}\n")
    
    # Processa todas as combinações (sem paralelismo por simplicidade)
    # Se quiser paralelismo, pode adicionar depois
    all_results = process_all_combinations(frac_list, prob_list, input_base_path_pattern, output_base_path_pattern)
    
    if all_results:
        df_summary = pd.DataFrame(all_results)
        df_summary = df_summary.sort_values(['frac', 'prob'])
        
        # Salva resumo completo
        summary_path = Path(output_base_path_pattern.format(frac=frac_list[0])).parent / f"resumo_expoentes_SRE{sre}_logfit.csv"
        df_summary.to_csv(summary_path, index=False)
        
        print(f"\n{'='*60}")
        print("RESUMO FINAL - AJUSTE LOG-LOG")
        print(f"{'='*60}")
        print(df_summary[['frac', 'prob', 't_min', 'alpha_mean', 'alpha_std', 'alpha_var', 'n_runs']].to_string(index=False))
        
        print(f"\nArquivo salvo em: {summary_path}")
    
    print(f"\n{'='*60}")
    print("PROCESSAMENTO CONCLUÍDO!")