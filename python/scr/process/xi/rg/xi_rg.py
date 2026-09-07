import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURAÇÕES
# ============================================
sre = 2
prob_list = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
frac_list = list(range(5, 101, 5))

# Base paths para cada fração (onde estão os arquivos consolidados)
base_paths = {frac: Path(f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/RG_sre_2_src_2_prob_v_frac_v/frac_{frac}") 
              for frac in frac_list}

# Caminho de saída para o CSV
output_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/H_rg/sre_2_src_2_prob_v_all_frac/")
output_dir.mkdir(parents=True, exist_ok=True)

def load_rg_data_for_frac(frac):
    """Carrega o arquivo consolidado para uma fração"""
    file_path = base_paths[frac] / f"all_runs_frac_{frac}.csv"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    df = pd.read_csv(file_path)
    
    # Verifica se tem a coluna necessária
    if 'rg_squared' not in df.columns or 'prob' not in df.columns:
        raise ValueError(f"Colunas necessárias não encontradas em {file_path}")
    
    # Calcula Rg a partir de rg_squared
    df['rg'] = np.sqrt(df['rg_squared'])
    
    return df

def check_data_integrity():
    """Verifica se todas as combinações frac+prob existem nos dados"""
    print("="*60)
    print("Verificando integridade dos dados...")
    print("="*60)
    
    for frac in frac_list:
        df = load_rg_data_for_frac(frac)
        
        # Verifica quais probabilidades estão presentes
        probs_present = set(df['prob'].unique())
        probs_expected = set(prob_list)
        
        missing_probs = probs_expected - probs_present
        
        if missing_probs:
            raise ValueError(
                f"\nERRO: Dados incompletos para fração {frac}%\n"
                f"Probabilidades faltando: {sorted(missing_probs)}\n"
                f"Probabilidades presentes: {sorted(probs_present)}\n"
                f"Execução abortada."
            )
        
        # Verifica número de amostras por probabilidade
        for prob in prob_list:
            n_samples = len(df[df['prob'] == prob])
            if n_samples == 0:
                raise ValueError(f"Fração {frac}%, Prob {prob:.2f}: 0 amostras!")
            
            print(f"✓ Fração {frac}%, Prob {prob:.2f}: {n_samples} amostras, "
                  f"média Rg = {df[df['prob'] == prob]['rg'].mean():.4f}")
    
    print("\n✓ Todos os dados estão presentes e consistentes!\n")

def compute_statistics():
    """Calcula média e desvio padrão do Rg para cada combinação frac+prob"""
    print("="*60)
    print("Calculando estatísticas (média e std do Rg)...")
    print("="*60)
    
    results = []
    
    for frac in frac_list:
        df = load_rg_data_for_frac(frac)
        
        for prob in prob_list:
            df_prob = df[df['prob'] == prob]
            rg_values = df_prob['rg'].values
            
            mean_rg = np.mean(rg_values)
            std_rg = np.std(rg_values, ddof=1)  # ddof=1 para desvio amostral
            
            results.append({
                'frac': frac,
                'prob': prob,
                'mean_rg': mean_rg,
                'std_rg': std_rg,
                'n_samples': len(rg_values)
            })
            
            print(f"Frac {frac}%, Prob {prob:.2f}: mean_rg={mean_rg:.4f}, std_rg={std_rg:.4f}, n={len(rg_values)}")
    
    return pd.DataFrame(results)

def compute_derivatives(df_stats):
    """Calcula derivada primeira e segunda com propagação de erro"""
    print("\n" + "="*60)
    print("Calculando derivadas d⟨Rg⟩/dp e d²⟨Rg⟩/dp² com propagação de erro...")
    print("="*60)
    
    derivatives = []
    delta_p = 0.1  # espaçamento entre probabilidades
    
    for frac in frac_list:
        # Filtra dados para esta fração
        frac_df = df_stats[df_stats['frac'] == frac].sort_values('prob').reset_index(drop=True)
        
        n_points = len(frac_df)
        
        for i in range(n_points):
            prob = frac_df.loc[i, 'prob']
            mean_rg = frac_df.loc[i, 'mean_rg']
            std_rg = frac_df.loc[i, 'std_rg']
            
            # ===== DERIVADA PRIMEIRA =====
            if i == 0:  # p = 0.00 (forward)
                mean_next = frac_df.loc[i+1, 'mean_rg']
                std_next = frac_df.loc[i+1, 'std_rg']
                
                drg_dp = (mean_next - mean_rg) / delta_p
                drg_dp_error = np.sqrt(std_rg**2 + std_next**2) / delta_p
                method1 = "forward"
                
            elif i == n_points - 1:  # p = 1.00 (backward)
                mean_prev = frac_df.loc[i-1, 'mean_rg']
                std_prev = frac_df.loc[i-1, 'std_rg']
                
                drg_dp = (mean_rg - mean_prev) / delta_p
                drg_dp_error = np.sqrt(std_rg**2 + std_prev**2) / delta_p
                method1 = "backward"
                
            else:  # pontos internos (central)
                mean_prev = frac_df.loc[i-1, 'mean_rg']
                std_prev = frac_df.loc[i-1, 'std_rg']
                mean_next = frac_df.loc[i+1, 'mean_rg']
                std_next = frac_df.loc[i+1, 'std_rg']
                
                drg_dp = (mean_next - mean_prev) / (2 * delta_p)
                drg_dp_error = np.sqrt(std_prev**2 + std_next**2) / (2 * delta_p)
                method1 = "central"
            
            # ===== DERIVADA SEGUNDA =====
            # Inicializa com NaN
            d2rg_dp2 = np.nan
            d2rg_dp2_error = np.nan
            method2 = "nan"
            
            # Pontos internos para derivada segunda (precisa de vizinho dos dois lados)
            if 1 <= i <= n_points - 2:  # p = 0.10 a 0.90
                mean_prev = frac_df.loc[i-1, 'mean_rg']
                mean_curr = mean_rg
                mean_next = frac_df.loc[i+1, 'mean_rg']
                
                std_prev = frac_df.loc[i-1, 'std_rg']
                std_curr = std_rg
                std_next = frac_df.loc[i+1, 'std_rg']
                
                # Derivada segunda central
                d2rg_dp2 = (mean_next - 2*mean_curr + mean_prev) / (delta_p**2)
                d2rg_dp2_error = np.sqrt(std_next**2 + 4*std_curr**2 + std_prev**2) / (delta_p**2)
                method2 = "central"
            
            # Caso especial: p = 0.10 e p = 0.90 poderiam ter forward/backward de 2ª ordem
            # Mas por simplicidade, deixamos apenas central para os pontos 0.20 a 0.80
            
            derivatives.append({
                'frac': frac,
                'prob': prob,
                'mean_rg': mean_rg,
                'std_rg': std_rg,
                'drg_dp': drg_dp,
                'drg_dp_error': drg_dp_error,
                'd2rg_dp2': d2rg_dp2,
                'd2rg_dp2_error': d2rg_dp2_error,
                'method_d1': method1,
                'method_d2': method2
            })
            
            # Print informativo
            if not np.isnan(d2rg_dp2):
                print(f"Frac {frac}%, Prob {prob:.2f}: d⟨Rg⟩/dp = {drg_dp:.4f} ± {drg_dp_error:.4f} ({method1}), "
                      f"d²⟨Rg⟩/dp² = {d2rg_dp2:.4f} ± {d2rg_dp2_error:.4f} ({method2})")
            else:
                print(f"Frac {frac}%, Prob {prob:.2f}: d⟨Rg⟩/dp = {drg_dp:.4f} ± {drg_dp_error:.4f} ({method1})")
    
    return pd.DataFrame(derivatives)

def save_results(df_derivatives):
    """Salva os resultados em um único arquivo CSV"""
    output_file = output_dir / f"derivadas_rg_SRE_{sre}.csv"
    
    # Seleciona colunas para salvar
    df_save = df_derivatives[['frac', 'prob', 'mean_rg', 'std_rg', 
                              'drg_dp', 'drg_dp_error',
                              'd2rg_dp2', 'd2rg_dp2_error']]
    
    df_save.to_csv(output_file, index=False, float_format='%.6f')
    
    print("\n" + "="*60)
    print(f"✓ Resultados salvos em: {output_file}")
    print(f"  Formato: {df_save.shape[0]} linhas, {df_save.shape[1]} colunas")
    print(f"  Colunas: {list(df_save.columns)}")
    print("="*60)
    
    return output_file

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("ANÁLISE DE DERIVADAS DO RAIO DE GIRO (Rg)")
    print(f"SRE = {sre}")
    print(f"Frações: {frac_list}")
    print(f"Probabilidades: {prob_list}")
    print("="*60)
    
    # 1. Verifica integridade dos dados
    check_data_integrity()
    
    # 2. Calcula estatísticas (média e std do Rg)
    df_stats = compute_statistics()
    
    # 3. Calcula derivadas primeira e segunda com propagação de erro
    df_derivatives = compute_derivatives(df_stats)
    
    # 4. Salva resultados
    output_file = save_results(df_derivatives)
    
    print("\n✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print(f"Arquivo gerado: {output_file}")
    print("\nAgora execute o programa de plotagem para gerar os gráficos.")