import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

# ============================================
# CONFIGURAÇÕES
# ============================================
sre = 2
prob_list = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
frac_list = list(range(5, 101, 5))

# Base paths
base_paths = {frac: Path(f"/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/expoente/{frac}/prob_variation")
              for frac in frac_list}

# Caminho de saída
output_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/xi_alpha")
output_dir.mkdir(parents=True, exist_ok=True)

def load_exponents_for_prob(prob, frac):
    """Carrega os dados de expoentes para uma dada probabilidade e fração"""
    base_path = base_paths[frac]
    prob_dir = base_path / f"obsprob_{prob:.2f}"
    
    if not prob_dir.exists():
        return None
    
    file_pattern = f"expoentes_prob_{prob:.2f}.csv"
    files = list(prob_dir.glob(file_pattern))
    
    if not files:
        return None
    
    df = pd.read_csv(files[0])
    
    if 'alpha' not in df.columns:
        return None
    
    return df['alpha'].values

def check_data_integrity():
    """Verifica se todos os dados existem para todas combinações frac+prob"""
    print("="*60)
    print("Verificando integridade dos dados...")
    print("="*60)
    
    for frac in frac_list:
        for prob in prob_list:
            alphas = load_exponents_for_prob(prob, frac)
            
            if alphas is None or len(alphas) == 0:
                raise FileNotFoundError(
                    f"\nERRO: Dados incompletos!\n"
                    f"Fração: {frac}%\n"
                    f"Probabilidade: {prob:.2f}\n"
                    f"Arquivo esperado: {base_paths[frac]}/obsprob_{prob:.2f}/expoentes_prob_{prob:.2f}.csv\n"
                    f"\nExecução abortada."
                )
            
            print(f"✓ Fração {frac}%, Prob {prob:.2f}: {len(alphas)} runs")
    
    print("\n✓ Todos os dados estão presentes!\n")

def compute_statistics():
    """Calcula média e desvio padrão para cada combinação frac+prob"""
    print("="*60)
    print("Calculando estatísticas (média e std)...")
    print("="*60)
    
    results = []
    
    for frac in frac_list:
        for prob in prob_list:
            alphas = load_exponents_for_prob(prob, frac)
            mean_alpha = np.mean(alphas)
            std_alpha = np.std(alphas, ddof=1)  # ddof=1 para desvio amostral
            
            results.append({
                'frac': frac,
                'prob': prob,
                'mean_alpha': mean_alpha,
                'std_alpha': std_alpha
            })
            
            print(f"Frac {frac}%, Prob {prob:.2f}: mean={mean_alpha:.4f}, std={std_alpha:.4f}")
    
    return pd.DataFrame(results)

def compute_derivative(df):
    """Calcula derivada primeira e segunda com propagação de erro usando diferença central e one-sided"""
    print("\n" + "="*60)
    print("Calculando derivadas dα/dp e d²α/dp² com propagação de erro...")
    print("="*60)
    
    derivatives = []
    delta_p = 0.1  # espaçamento entre probabilidades
    
    for frac in frac_list:
        # Filtra dados para esta fração
        frac_df = df[df['frac'] == frac].sort_values('prob').reset_index(drop=True)
        
        n_points = len(frac_df)
        
        for i in range(n_points):
            prob = frac_df.loc[i, 'prob']
            mean_alpha = frac_df.loc[i, 'mean_alpha']
            std_alpha = frac_df.loc[i, 'std_alpha']
            
            # ===== DERIVADA PRIMEIRA =====
            if i == 0:  # p = 0.00 (forward)
                mean_next = frac_df.loc[i+1, 'mean_alpha']
                std_next = frac_df.loc[i+1, 'std_alpha']
                
                dalpha_dp = (mean_next - mean_alpha) / delta_p
                dalpha_dp_error = np.sqrt(std_alpha**2 + std_next**2) / delta_p
                method1 = "forward"
                
            elif i == n_points - 1:  # p = 1.00 (backward)
                mean_prev = frac_df.loc[i-1, 'mean_alpha']
                std_prev = frac_df.loc[i-1, 'std_alpha']
                
                dalpha_dp = (mean_alpha - mean_prev) / delta_p
                dalpha_dp_error = np.sqrt(std_alpha**2 + std_prev**2) / delta_p
                method1 = "backward"
                
            else:  # pontos internos (central)
                mean_prev = frac_df.loc[i-1, 'mean_alpha']
                std_prev = frac_df.loc[i-1, 'std_alpha']
                mean_next = frac_df.loc[i+1, 'mean_alpha']
                std_next = frac_df.loc[i+1, 'std_alpha']
                
                dalpha_dp = (mean_next - mean_prev) / (2 * delta_p)
                dalpha_dp_error = np.sqrt(std_prev**2 + std_next**2) / (2 * delta_p)
                method1 = "central"
            
            # ===== DERIVADA SEGUNDA =====
            # Inicializa com NaN
            d2alpha_dp2 = np.nan
            d2alpha_dp2_error = np.nan
            method2 = "nan"
            
            # Pontos internos para derivada segunda (precisa de vizinho dos dois lados)
            if 1 <= i <= n_points - 2:  # p = 0.10 a 0.90
                mean_prev = frac_df.loc[i-1, 'mean_alpha']
                mean_curr = mean_alpha
                mean_next = frac_df.loc[i+1, 'mean_alpha']
                
                std_prev = frac_df.loc[i-1, 'std_alpha']
                std_curr = std_alpha
                std_next = frac_df.loc[i+1, 'std_alpha']
                
                # Derivada segunda central
                d2alpha_dp2 = (mean_next - 2*mean_curr + mean_prev) / (delta_p**2)
                d2alpha_dp2_error = np.sqrt(std_next**2 + 4*std_curr**2 + std_prev**2) / (delta_p**2)
                method2 = "central"
            
            # Caso especial: p = 0.00 e p = 1.00 não têm derivada segunda
            # Caso especial: p = 0.10 e p = 0.90 poderiam ter forward/backward de 2ª ordem
            # Mas por simplicidade, deixamos apenas central para os pontos 0.20 a 0.80
            
            derivatives.append({
                'frac': frac,
                'prob': prob,
                'mean_alpha': mean_alpha,
                'std_alpha': std_alpha,
                'dalpha_dp': dalpha_dp,
                'dalpha_dp_error': dalpha_dp_error,
                'd2alpha_dp2': d2alpha_dp2,
                'd2alpha_dp2_error': d2alpha_dp2_error,
                'method_d1': method1,
                'method_d2': method2
            })
            
            # Print informativo
            if not np.isnan(d2alpha_dp2):
                print(f"Frac {frac}%, Prob {prob:.2f}: dα/dp = {dalpha_dp:.4f} ± {dalpha_dp_error:.4f} ({method1}), "
                      f"d²α/dp² = {d2alpha_dp2:.4f} ± {d2alpha_dp2_error:.4f} ({method2})")
            else:
                print(f"Frac {frac}%, Prob {prob:.2f}: dα/dp = {dalpha_dp:.4f} ± {dalpha_dp_error:.4f} ({method1})")
    
    return pd.DataFrame(derivatives)

def save_results(df_derivatives):
    """Salva os resultados em um único arquivo CSV"""
    output_file = output_dir / f"derivadas_alpha_SRE_{sre}.csv"
    
    # Seleciona colunas para salvar (incluindo derivada segunda)
    df_save = df_derivatives[['frac', 'prob', 'mean_alpha', 'std_alpha', 
                              'dalpha_dp', 'dalpha_dp_error',
                              'd2alpha_dp2', 'd2alpha_dp2_error']]
    
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
    print("ANÁLISE DE DERIVADA DO EXPOENTE α EM FUNÇÃO DA PROBABILIDADE")
    print(f"SRE = {sre}")
    print(f"Frações: {frac_list}")
    print(f"Probabilidades: {prob_list}")
    print("="*60)
    
    # 1. Verifica integridade dos dados
    check_data_integrity()
    
    # 2. Calcula estatísticas (média e std)
    df_stats = compute_statistics()
    
    # 3. Calcula derivada com propagação de erro
    df_derivatives = compute_derivative(df_stats)
    
    # 4. Salva resultados
    output_file = save_results(df_derivatives)
    
    print("\n✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
    print(f"Arquivo gerado: {output_file}")