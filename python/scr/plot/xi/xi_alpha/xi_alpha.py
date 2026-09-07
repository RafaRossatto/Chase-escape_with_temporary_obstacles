import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================
# CONFIGURAÇÕES
# ============================================
sre = 2
output_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/xi_alpha")

input_file = output_dir / f"derivadas_alpha_SRE_{sre}.csv"
figures_dir = output_dir / "derivadas_alpha_plots"
figures_dir.mkdir(parents=True, exist_ok=True)

def load_data():
    """Carrega o CSV com as derivadas"""
    df = pd.read_csv(input_file)
    print(f"✓ Dados carregados: {len(df)} linhas")
    print(f"  Frações presentes: {sorted(df['frac'].unique())}")
    print(f"  Colunas: {list(df.columns)}")
    return df

def find_extreme_point(df_frac, column='dalpha_dp'):
    """Encontra o ponto extremo (máximo ou mínimo) da derivada"""
    values = df_frac[column].values
    
    # Remove NaNs para encontrar extremo
    valid_mask = ~np.isnan(values)
    if not np.any(valid_mask):
        return None
    
    values_valid = values[valid_mask]
    idx_valid = np.where(valid_mask)[0]
    
    # Pega o ponto com maior valor absoluto
    idx_extreme_local = np.argmax(np.abs(values_valid))
    idx_extreme = idx_valid[idx_extreme_local]
    
    extreme_point = {
        'prob': df_frac.iloc[idx_extreme]['prob'],
        'value': df_frac.iloc[idx_extreme][column],
        'error': df_frac.iloc[idx_extreme][f'{column}_error'] if f'{column}_error' in df_frac.columns else None,
        'is_max': values_valid[idx_extreme_local] > 0
    }
    
    return extreme_point

def find_inflexion_points(df_frac):
    """Encontra pontos onde a derivada segunda cruza zero (dentro do erro)"""
    inflexions = []
    
    for i in range(len(df_frac) - 1):
        d2_i = df_frac.iloc[i]['d2alpha_dp2']
        d2_next = df_frac.iloc[i + 1]['d2alpha_dp2']
        
        # Pula se algum for NaN
        if np.isnan(d2_i) or np.isnan(d2_next):
            continue
        
        # Verifica se houve mudança de sinal
        if d2_i * d2_next < 0:
            # Calcula a probabilidade do cruzamento por interpolação linear
            prob_i = df_frac.iloc[i]['prob']
            prob_next = df_frac.iloc[i + 1]['prob']
            
            # Interpola para encontrar onde d2 = 0
            if d2_next != d2_i:
                t = -d2_i / (d2_next - d2_i)  # fração entre os pontos
                prob_cross = prob_i + t * (prob_next - prob_i)
            else:
                prob_cross = (prob_i + prob_next) / 2
            
            inflexions.append({
                'prob': prob_cross,
                'interval': (prob_i, prob_next),
                'd2_left': d2_i,
                'd2_right': d2_next
            })
    
    return inflexions

def plot_derivatives_for_frac(df_frac, frac):
    """Plota derivada primeira e segunda para uma fração específica"""
    fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    ax1, ax2 = axes
    
    prob = df_frac['prob'].values
    
    # ===== GRÁFICO 1: DERIVADA PRIMEIRA =====
    d1 = df_frac['dalpha_dp'].values
    d1_err = df_frac['dalpha_dp_error'].values
    
    # Curva principal
    ax1.plot(prob, d1, 'o-', color='navy', linewidth=2, markersize=6, label='dα/dp')
    
    # Banda de erro
    # ax1.fill_between(prob, d1 - d1_err, d1 + d1_err, alpha=0.2, color='navy', label='Erro propagado')
    
    # Linha em y=0
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Ponto extremo
    extreme = find_extreme_point(df_frac, 'dalpha_dp')
    if extreme:
        ax1.plot(extreme['prob'], extreme['value'], 
                'ro', markersize=12, markerfacecolor='red', markeredgecolor='darkred',
                markeredgewidth=2, label='Ponto extremo')
        
        # Anotação
        offset_y = 0.05 * (np.max(d1[~np.isnan(d1)]) - np.min(d1[~np.isnan(d1)])) if len(d1[~np.isnan(d1)]) > 1 else 0.1
        if extreme['is_max']:
            annotation_y = extreme['value'] + offset_y
        else:
            annotation_y = extreme['value'] - offset_y
        
        ax1.annotate(f"p = {extreme['prob']:.2f}\ndα/dp = {extreme['value']:.3f}",
                    xy=(extreme['prob'], extreme['value']),
                    xytext=(extreme['prob'] + 0.1, annotation_y),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                    fontsize=9, ha='left', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax1.set_ylabel('dα/dp', fontsize=14)
    ax1.set_title(f'Derivada Primeira - Fração {frac}%, SRE = {sre}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='best', fontsize=10)
    ax1.set_ylim(-5.5, 0.5)
    
    # ===== GRÁFICO 2: DERIVADA SEGUNDA =====
    d2 = df_frac['d2alpha_dp2'].values
    d2_err = df_frac['d2alpha_dp2_error'].values
    
    # Curva principal
    ax2.plot(prob, d2, 's-', color='darkgreen', linewidth=2, markersize=6, label='d²α/dp²')
    
    # Banda de erro
    # ax2.fill_between(prob, d2 - d2_err, d2 + d2_err, alpha=0.2, color='darkgreen', label='Erro propagado')
    
    # Linha em y=0
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Pontos de inflexão (onde d2 cruza zero)
    inflexions = find_inflexion_points(df_frac)
    # for infl in inflexions:
    #     ax2.axvline(infl['prob'], color='orange', linestyle=':', linewidth=2, alpha=0.7)
    #     ax2.text(infl['prob'], ax2.get_ylim()[1] * 0.9, 
    #             f'p={infl["prob"]:.2f}', 
    #             rotation=90, fontsize=8, color='orange', ha='right', va='top')
    
    # Ponto extremo da derivada segunda (opcional)
    # extreme2 = find_extreme_point(df_frac, 'd2alpha_dp2')
    # if extreme2 and not np.isnan(extreme2['value']):
    #     ax2.plot(extreme2['prob'], extreme2['value'], 
    #             'ro', markersize=10, markerfacecolor='red', markeredgecolor='darkred',
    #             markeredgewidth=1.5, label='Extremo da d²α/dp²')
    
    ax2.set_xlabel('Probabilidade', fontsize=14)
    ax2.set_ylabel('d²α/dp²', fontsize=14)
    ax2.set_title(f'Derivada Segunda - Fração {frac}%, SRE = {sre}', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='best', fontsize=10)
    
    # Configuração comum dos eixos x
    ax2.set_xlim(-0.05, 1.05)
    ax2.set_ylim(-80.0, 60.00)
    
    plt.tight_layout()
    
    # Salva a figura
    output_file = figures_dir / f"derivadas_alpha_frac_{frac}_SRE_{sre}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"  ✓ Salvo: {output_file}")
    if inflexions:
        print(f"    Pontos de inflexão encontrados: {[f'{inf["prob"]:.2f}' for inf in inflexions]}")
    
    return inflexions

def plot_all_derivatives_together(df):
    """Plota todas as derivadas primeiras no mesmo gráfico para comparação"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax1, ax2 = axes
    
    fracs_present = sorted(df['frac'].unique())
    colormap = plt.cm.viridis
    colors = {frac: colormap(i/len(fracs_present)) for i, frac in enumerate(fracs_present)}
    
    for frac in fracs_present:
        df_frac = df[df['frac'] == frac].sort_values('prob')
        prob = df_frac['prob'].values
        
        # Derivada primeira
        d1 = df_frac['dalpha_dp'].values
        ax1.plot(prob, d1, '-', color=colors[frac], linewidth=1.5, alpha=0.7, label=f'{frac}%')
        
        # Derivada segunda (apenas onde não é NaN)
        d2 = df_frac['d2alpha_dp2'].values
        valid = ~np.isnan(d2)
        if np.any(valid):
            ax2.plot(prob[valid], d2[valid], '-', color=colors[frac], linewidth=1.5, alpha=0.7, label=f'{frac}%')
    
    # Linha y=0 em ambos
    ax1.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    ax1.set_xlabel('Probabilidade', fontsize=14)
    ax1.set_ylabel('dα/dp', fontsize=14)
    ax1.set_title(f'Derivada Primeira - Todas as frações, SRE={sre}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(-0.05, 1.05)
    
    ax2.set_xlabel('Probabilidade', fontsize=14)
    ax2.set_ylabel('d²α/dp²', fontsize=14)
    ax2.set_title(f'Derivada Segunda - Todas as frações, SRE={sre}', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim(-0.05, 1.05)
    
    # Legenda em 2 colunas
    ncol = 2 if len(fracs_present) > 10 else 1
    ax1.legend(loc='best', fontsize=8, ncol=ncol)
    ax2.legend(loc='best', fontsize=8, ncol=ncol)
    
    plt.tight_layout()
    
    output_file = figures_dir / f"derivadas_alpha_todas_frac_SRE_{sre}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"\n✓ Gráfico com todas as frações salvo: {output_file}")

def create_inflexion_summary(df):
    """Cria uma tabela resumo com os pontos de inflexão de cada fração"""
    all_inflexions = []
    
    for frac in sorted(df['frac'].unique()):
        df_frac = df[df['frac'] == frac].sort_values('prob').reset_index(drop=True)
        inflexions = find_inflexion_points(df_frac)
        
        for infl in inflexions:
            all_inflexions.append({
                'frac': frac,
                'prob_inflexao': infl['prob'],
                'intervalo': f"[{infl['interval'][0]:.2f}, {infl['interval'][1]:.2f}]",
                'd2_esquerda': infl['d2_left'],
                'd2_direita': infl['d2_right']
            })
    
    if all_inflexions:
        df_summary = pd.DataFrame(all_inflexions)
        output_file = figures_dir / f"inflexoes_alpha_SRE_{sre}.csv"
        df_summary.to_csv(output_file, index=False, float_format='%.6f')
        
        print("\n" + "="*60)
        print("PONTOS DE INFLEXÃO ENCONTRADOS")
        print("="*60)
        print(df_summary.to_string(index=False))
        print(f"\n✓ Tabela de inflexões salva: {output_file}")
    else:
        print("\n⚠ Nenhum ponto de inflexão encontrado.")
    
    return all_inflexions

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("PLOTANDO DERIVADAS PRIMEIRA E SEGUNDA DO EXPOENTE α")
    print(f"SRE = {sre}")
    print("="*60)
    
    # Carrega dados
    df = load_data()
    
    # Verifica se tem derivada segunda
    if 'd2alpha_dp2' not in df.columns:
        print("\n⚠ ERRO: Coluna 'd2alpha_dp2' não encontrada!")
        print("  Execute primeiro o programa de processamento com derivada segunda.")
        exit(1)
    
    # Plota uma figura por fração
    print("\nGerando gráficos individuais por fração...")
    all_inflexions = []
    
    for frac in sorted(df['frac'].unique()):
        df_frac = df[df['frac'] == frac].sort_values('prob').reset_index(drop=True)
        if len(df_frac) > 0:
            inflexions = plot_derivatives_for_frac(df_frac, frac)
            all_inflexions.extend(inflexions)
        else:
            print(f"  ✗ Fração {frac}%: sem dados")
    
    # Plota todas juntas
    print("\nGerando gráfico com todas as frações...")
    plot_all_derivatives_together(df)
    
    # Cria tabela resumo de inflexões
    create_inflexion_summary(df)
    
    print("\n" + "="*60)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"Figuras salvas em: {figures_dir}")
    print("="*60)