import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================
# CONFIGURAÇÕES
# ============================================
sre = 2
RG_THRESHOLD = 2.0

# Caminho para o arquivo de derivadas gerado anteriormente
input_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/phi_T/sre_2_src_2_prob_v_all_frac")
input_file = input_dir / f"derivadas_phi_T_Rg_leq_{RG_THRESHOLD:.1f}_SRE_{sre}.csv"

# Caminho de saída para as figuras
figures_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/phi_T/derivadas_plots")
figures_dir.mkdir(parents=True, exist_ok=True)

def load_data():
    """Carrega o CSV com as derivadas"""
    if not input_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")
    
    df = pd.read_csv(input_file)
    print(f"✓ Dados carregados: {len(df)} linhas")
    print(f"  Frações presentes: {sorted(df['frac'].unique())}")
    print(f"  Colunas: {list(df.columns)}")
    return df

def plot_derivatives_for_frac(df_frac, frac):
    """Plota derivada primeira e segunda para uma fração específica"""
    fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    ax1, ax2 = axes
    
    prob = df_frac['prob'].values
    d1 = df_frac['dphi_dp'].values
    d2 = df_frac['d2phi_dp2'].values
    
    # ===== GRÁFICO 1: DERIVADA PRIMEIRA =====
    ax1.plot(prob, d1, 'o-', color='navy', linewidth=2, markersize=6, label='dφ/dp')
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_ylabel('dφ/dp', fontsize=14)
    ax1.set_title(f'Derivada Primeira - Fração {frac}%, SRE = {sre}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='best', fontsize=10)
    ax1.set_ylim(-0.05, 4.20)
    
    # ===== GRÁFICO 2: DERIVADA SEGUNDA =====
    ax2.plot(prob, d2, 's-', color='darkgreen', linewidth=2, markersize=6, label='d²φ/dp²')
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Probabilidade', fontsize=14)
    ax2.set_ylabel('d²φ/dp²', fontsize=14)
    ax2.set_title(f'Derivada Segunda - Fração {frac}%, SRE = {sre}', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='best', fontsize=10)
    
    # Configuração dos eixos x
    ax2.set_xlim(-0.05, 1.05)
    ax2.set_ylim(-60.05, 60.05)
    
    plt.tight_layout()
    
    # Salva a figura
    output_file = figures_dir / f"derivadas_phi_T_frac_{frac}_SRE_{sre}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ Salvo: {output_file}")

def plot_all_derivatives_together(df):
    """Plota todas as derivadas primeiras e segundas no mesmo gráfico para comparação"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax1, ax2 = axes
    
    fracs_present = sorted(df['frac'].unique())
    colormap = plt.cm.viridis
    colors = {frac: colormap(i/len(fracs_present)) for i, frac in enumerate(fracs_present)}
    
    for frac in fracs_present:
        df_frac = df[df['frac'] == frac].sort_values('prob')
        prob = df_frac['prob'].values
        
        # Derivada primeira
        d1 = df_frac['dphi_dp'].values
        ax1.plot(prob, d1, '-', color=colors[frac], linewidth=1.5, alpha=0.7, label=f'{frac}%')
        
        # Derivada segunda (apenas onde não é NaN)
        d2 = df_frac['d2phi_dp2'].values
        valid = ~np.isnan(d2)
        if np.any(valid):
            ax2.plot(prob[valid], d2[valid], '-', color=colors[frac], linewidth=1.5, alpha=0.7, label=f'{frac}%')
    
    # Linha y=0 em ambos
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    ax1.set_xlabel('Probabilidade', fontsize=14)
    ax1.set_ylabel('dφ/dp', fontsize=14)
    ax1.set_title(f'Derivada Primeira - Todas as frações, SRE={sre}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(-0.05, 1.05)
    
    ax2.set_xlabel('Probabilidade', fontsize=14)
    ax2.set_ylabel('d²φ/dp²', fontsize=14)
    ax2.set_title(f'Derivada Segunda - Todas as frações, SRE={sre}', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim(-0.05, 1.05)
    
    # Legenda em 2 colunas
    ncol = 2 if len(fracs_present) > 10 else 1
    ax1.legend(loc='best', fontsize=8, ncol=ncol)
    ax2.legend(loc='best', fontsize=8, ncol=ncol)
    
    plt.tight_layout()
    
    output_file = figures_dir / f"derivadas_phi_T_todas_frac_SRE_{sre}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"\n✓ Gráfico com todas as frações salvo: {output_file}")

def plot_selected_fracs(df, selected_fracs=[5, 25, 50, 75, 100]):
    """Plota um subconjunto de frações para melhor visualização"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax1, ax2 = axes
    
    # Filtra apenas as frações selecionadas
    df_selected = df[df['frac'].isin(selected_fracs)]
    fracs_present = sorted(df_selected['frac'].unique())
    
    colormap = plt.cm.plasma
    colors = {frac: colormap(i/len(fracs_present)) for i, frac in enumerate(fracs_present)}
    
    for frac in fracs_present:
        df_frac = df_selected[df_selected['frac'] == frac].sort_values('prob')
        prob = df_frac['prob'].values
        
        # Derivada primeira
        d1 = df_frac['dphi_dp'].values
        ax1.plot(prob, d1, '-o', color=colors[frac], linewidth=2, markersize=5, 
                alpha=0.8, label=f'{frac}%')
        
        # Derivada segunda
        d2 = df_frac['d2phi_dp2'].values
        valid = ~np.isnan(d2)
        if np.any(valid):
            ax2.plot(prob[valid], d2[valid], '-s', color=colors[frac], linewidth=2, 
                    markersize=4, alpha=0.8, label=f'{frac}%')
    
    # Linha y=0 em ambos
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    ax1.set_xlabel('Probabilidade', fontsize=14)
    ax1.set_ylabel('dφ/dp', fontsize=14)
    ax1.set_title(f'Derivada Primeira - Frações selecionadas, SRE={sre}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(-0.05, 1.05)
    
    ax2.set_xlabel('Probabilidade', fontsize=14)
    ax2.set_ylabel('d²φ/dp²', fontsize=14)
    ax2.set_title(f'Derivada Segunda - Frações selecionadas, SRE={sre}', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim(-0.05, 1.05)
    
    ax1.legend(loc='best', fontsize=10)
    ax2.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    
    output_file = figures_dir / f"derivadas_phi_T_selected_frac_SRE_{sre}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"\n✓ Gráfico com frações selecionadas salvo: {output_file}")

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("PLOTANDO DERIVADAS DA FRAÇÃO NORMALIZADA (φ_T/N^C)")
    print(f"SRE = {sre}")
    print(f"Threshold Rg = {RG_THRESHOLD}")
    print("="*60)
    
    try:
        # Carrega dados
        print("\nCarregando dados...")
        df = load_data()
        
        # Verifica se tem as colunas necessárias
        required_cols = ['dphi_dp', 'd2phi_dp2']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Colunas faltando: {missing}")
        
        # Plota uma figura por fração
        print("\nGerando gráficos individuais por fração...")
        for frac in sorted(df['frac'].unique()):
            df_frac = df[df['frac'] == frac].sort_values('prob').reset_index(drop=True)
            if len(df_frac) > 0:
                plot_derivatives_for_frac(df_frac, frac)
            else:
                print(f"  ✗ Fração {frac}%: sem dados")
        
        # Plota todas juntas
        print("\nGerando gráfico com todas as frações...")
        plot_all_derivatives_together(df)
        
        # Plota frações selecionadas
        print("\nGerando gráfico com frações selecionadas...")
        plot_selected_fracs(df, selected_fracs=[5, 25, 50, 75, 100])
        
        print("\n" + "="*60)
        print("✅ PROCESSAMENTO CONCLUÍDO!")
        print(f"Figuras salvas em: {figures_dir}")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERRO: {e}")
        print("\nCertifique-se de que o programa de derivadas foi executado primeiro.")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()