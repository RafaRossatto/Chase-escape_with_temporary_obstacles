import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURAÇÕES
# ============================================
sre = 2
prob_list = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
frac_list = list(range(5, 101, 5))
RG_THRESHOLD = 2.0

# Caminho para os dados gerados pelo programa anterior
input_data_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/phi_T")

# Caminho de saída
output_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/phi_T/sre_2_src_2_prob_v_all_frac")
output_dir.mkdir(parents=True, exist_ok=True)

def load_phi_data():
    """Carrega os dados de phi_T do CSV gerado anteriormente"""
    input_file = input_data_dir / f"dados_completos_Rg_leq_{RG_THRESHOLD:.1f}_SRE_{sre}.csv"
    
    if not input_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")
    
    df = pd.read_csv(input_file)
    df = df.rename(columns={'probabilidade': 'prob'})
    
    print(f"✓ Dados carregados: {len(df)} linhas")
    print(f"  Frações: {sorted(df['frac'].unique())}")
    print(f"  Probabilidades: {sorted(df['prob'].unique())}")
    
    return df

def compute_derivatives(df_phi):
    """
    Calcula derivadas primeira e segunda da curva φ(p)
    Usa médias e desvios para cada ponto
    """
    print("\n" + "="*60)
    print("Calculando derivadas dφ/dp e d²φ/dp²...")
    print("="*60)
    
    derivatives = []
    delta_p = 0.1
    
    for frac in frac_list:
        print(f"\n  Processando fração {frac}%...")
        
        # Pega todos os pontos para esta fração, ordenados por prob
        frac_data = []
        for prob in prob_list:
            df_prob = df_phi[(df_phi['frac'] == frac) & (df_phi['prob'] == prob)]
            if len(df_prob) > 0:
                frac_data.append({
                    'prob': prob,
                    'mean': df_prob['fraction_normalized'].mean(),
                    'std': df_prob['fraction_normalized'].std(ddof=1),
                    'n': len(df_prob)
                })
            else:
                frac_data.append({
                    'prob': prob,
                    'mean': np.nan,
                    'std': np.nan,
                    'n': 0
                })
        
        # Converte para arrays
        probs = np.array([d['prob'] for d in frac_data])
        means = np.array([d['mean'] for d in frac_data])
        stds = np.array([d['std'] for d in frac_data])
        ns = np.array([d['n'] for d in frac_data])
        
        # Remove pontos sem dados
        valid_idx = ~np.isnan(means)
        if not np.all(valid_idx):
            print(f"    ⚠ Atenção: alguns pontos sem dados para frac {frac}%")
            continue
        
        n_points = len(probs)
        
        for i in range(n_points):
            prob = probs[i]
            mean_phi = means[i]
            std_phi = stds[i]
            n_samples = ns[i]
            
            # ===== DERIVADA PRIMEIRA =====
            if i == 0:  # p = 0.00 (forward)
                mean_next = means[i+1]
                std_next = stds[i+1]
                
                dphi_dp = (mean_next - mean_phi) / delta_p
                dphi_dp_error = np.sqrt(std_phi**2 + std_next**2) / delta_p
                method1 = "forward"
                
            elif i == n_points - 1:  # p = 1.00 (backward)
                mean_prev = means[i-1]
                std_prev = stds[i-1]
                
                dphi_dp = (mean_phi - mean_prev) / delta_p
                dphi_dp_error = np.sqrt(std_phi**2 + std_prev**2) / delta_p
                method1 = "backward"
                
            else:  # pontos internos (central)
                mean_prev = means[i-1]
                std_prev = stds[i-1]
                mean_next = means[i+1]
                std_next = stds[i+1]
                
                dphi_dp = (mean_next - mean_prev) / (2 * delta_p)
                dphi_dp_error = np.sqrt(std_prev**2 + std_next**2) / (2 * delta_p)
                method1 = "central"
            
            # ===== DERIVADA SEGUNDA =====
            d2phi_dp2 = np.nan
            d2phi_dp2_error = np.nan
            method2 = "nan"
            
            # Apenas para pontos internos (0.10 a 0.90)
            if 1 <= i <= n_points - 2:
                mean_prev = means[i-1]
                std_prev = stds[i-1]
                mean_next = means[i+1]
                std_next = stds[i+1]
                
                d2phi_dp2 = (mean_next - 2*mean_phi + mean_prev) / (delta_p**2)
                d2phi_dp2_error = np.sqrt(std_next**2 + 4*std_phi**2 + std_prev**2) / (delta_p**2)
                method2 = "central"
            
            derivatives.append({
                'frac': frac,
                'prob': prob,
                'mean_phi': mean_phi,
                'std_phi': std_phi,
                'n_samples': n_samples,
                'dphi_dp': dphi_dp,
                'dphi_dp_error': dphi_dp_error,
                'd2phi_dp2': d2phi_dp2,
                'd2phi_dp2_error': d2phi_dp2_error,
                'method_d1': method1,
                'method_d2': method2
            })
            
            # Print
            if not np.isnan(d2phi_dp2):
                print(f"    Prob {prob:.2f}: dφ/dp = {dphi_dp:.6f} ± {dphi_dp_error:.6f}, "
                      f"d²φ/dp² = {d2phi_dp2:.6f} ± {d2phi_dp2_error:.6f}")
            else:
                print(f"    Prob {prob:.2f}: dφ/dp = {dphi_dp:.6f} ± {dphi_dp_error:.6f}")
    
    return pd.DataFrame(derivatives)

def save_results(df_derivatives):
    """Salva os resultados em um único arquivo CSV"""
    output_file = output_dir / f"derivadas_phi_T_Rg_leq_{RG_THRESHOLD:.1f}_SRE_{sre}.csv"
    
    # Seleciona colunas para salvar
    df_save = df_derivatives[['frac', 'prob', 'mean_phi', 'std_phi', 'n_samples',
                              'dphi_dp', 'dphi_dp_error',
                              'd2phi_dp2', 'd2phi_dp2_error']]
    
    df_save.to_csv(output_file, index=False, float_format='%.8f')
    
    print("\n" + "="*60)
    print(f"✓ Resultados salvos em: {output_file}")
    print(f"  {df_save.shape[0]} linhas, {df_save.shape[1]} colunas")
    print(f"  Colunas: {list(df_save.columns)}")
    print("="*60)
    
    return output_file

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("ANÁLISE DE DERIVADAS DA FRAÇÃO NORMALIZADA (φ_T/N^C)")
    print(f"SRE = {sre}")
    print(f"Threshold Rg = {RG_THRESHOLD}")
    print(f"Frações: {min(frac_list)}% a {max(frac_list)}%")
    print(f"Probabilidades: {prob_list[0]:.2f} a {prob_list[-1]:.2f}")
    print("="*60)
    
    try:
        # 1. Carrega dados
        print("\nCarregando dados...")
        df_phi = load_phi_data()
        
        # 2. Calcula derivadas
        df_derivatives = compute_derivatives(df_phi)
        
        # 3. Salva resultados
        output_file = save_results(df_derivatives)
        
        print("\n" + "="*60)
        print("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"Arquivo gerado: {output_file}")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERRO: {e}")
        print("\nCertifique-se de que o programa phi_T.py foi executado primeiro.")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()