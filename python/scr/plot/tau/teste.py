import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================
# CONFIGURAÇÕES
# ============================================

# Caminho base onde estão os arquivos
# base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/resultados_fit_exponencial_multiplos/sre_v_src_2_prob_0_50"

base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/resultados_fit_exponencial_multiplos/sre_v_src_2_prob_1_00"
# Parâmetros fixos
obsprob = 1.00
src = 2

# Frações a comparar (AJUSTE CONFORME SEUS ARQUIVOS)
fracoes = [25, 50, 100]

# Cores e marcadores para cada fração
cores = {
    25: 'blue',
    50: 'green',
    100: 'red'
}

marcadores = {
    25: 'o',
    50: 's',
    100: '^'
}

# Pasta para salvar gráficos
output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/fit/sre_v_src_2_prob_1.00"
os.makedirs(output_dir, exist_ok=True)

print("="*80)
print("GRÁFICO: β MÉDIO vs SRE PARA DIFERENTES FRAÇÕES")
print(f"obsprob = {obsprob:.2f}, src = {src}")
print(f"Frações: {fracoes}")
print("="*80)

# ============================================
# FUNÇÃO PARA CARREGAR E PROCESSAR CADA FRAÇÃO
# ============================================

def processar_fracao(frac):
    """Carrega o arquivo da fração e calcula β médio por SRE"""
    
    arquivo = f"{base_path}/resumo_todos_runs_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.csv"
    
    if not os.path.exists(arquivo):
        print(f"  ⚠️ Arquivo não encontrado: {arquivo}")
        return None
    
    df = pd.read_csv(arquivo)
    print(f"  ✓ Carregado frac={frac}: {len(df)} runs")
    
    # Calcular média do β por SRE
    stats = df.groupby('SRE').agg({
        'beta': ['mean', 'std', 'sem', 'count'],
        'tau': ['mean', 'std'],
        'r_squared': 'mean'
    }).round(6)
    
    stats.columns = ['beta_mean', 'beta_std', 'beta_sem', 'n_runs', 
                     'tau_mean', 'tau_std', 'r2_mean']
    stats = stats.reset_index()
    
    # Adicionar coluna frac
    stats['frac'] = frac
    
    return stats

# ============================================
# CARREGAR TODAS AS FRAÇÕES
# ============================================

print("\nCarregando arquivos...")
dados_por_frac = {}

for frac in fracoes:
    stats = processar_fracao(frac)
    if stats is not None:
        dados_por_frac[frac] = stats

if not dados_por_frac:
    print("\n❌ Nenhum dado encontrado!")
    print("\nArquivos esperados:")
    for frac in fracoes:
        print(f"  {base_path}/resumo_todos_runs_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.csv")
    exit()

# ============================================
# GRÁFICO 1: β médio vs SRE (com desvio padrão)
# ============================================

fig1, ax1 = plt.subplots(figsize=(12, 8))

for frac, stats in dados_por_frac.items():
    sre_vals = stats['SRE'].values
    beta_mean = stats['beta_mean'].values
    beta_std = stats['beta_std'].values
    
    cor = cores.get(frac, 'gray')
    marker = marcadores.get(frac, 'o')
    
    # Barras de erro (desvio padrão)
    ax1.errorbar(sre_vals, beta_mean, yerr=beta_std,
                 fmt=f'{marker}-', capsize=6, markersize=8, linewidth=2,
                 color=cor, ecolor=cor, alpha=0.8,
                 label=f'frac = {frac}')
    
    # Adicionar valores nos pontos (opcional)
    for sre, beta in zip(sre_vals, beta_mean):
        ax1.annotate(f'{beta:.3f}', (sre, beta),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.7)

# Linha de referência β = 1 (exponencial)
ax1.axhline(y=1.0, color='red', linestyle='--', linewidth=2.5, alpha=0.8,
            label='β = 1 (exponencial puro)')

# Banda de referência (β = 1 ± 0.1)
ax1.axhspan(0.9, 1.1, alpha=0.1, color='red', label='Região exponencial (β ≈ 1)')

ax1.set_xlabel('SRE', fontsize=14)
ax1.set_ylabel('β médio', fontsize=14)
ax1.set_title(f'β médio vs SRE para diferentes frações\n(obsprob={obsprob:.2f}, src={src})',
              fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=12)
ax1.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/beta_medio_vs_sRE_comparacao_frac.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"\n✓ Gráfico 1 salvo: {output_dir}/beta_medio_vs_sRE_comparacao_frac.png")

# ============================================
# GRÁFICO 2: τ médio vs SRE
# ============================================

fig2, ax2 = plt.subplots(figsize=(12, 8))

for frac, stats in dados_por_frac.items():
    sre_vals = stats['SRE'].values
    tau_mean = stats['tau_mean'].values
    tau_std = stats['tau_std'].values
    
    cor = cores.get(frac, 'gray')
    marker = marcadores.get(frac, 'o')
    
    ax2.errorbar(sre_vals, tau_mean, yerr=tau_std,
                 fmt=f'{marker}-', capsize=6, markersize=8, linewidth=2,
                 color=cor, ecolor=cor, alpha=0.8,
                 label=f'frac = {frac}')

ax2.set_xlabel('SRE', fontsize=14)
ax2.set_ylabel('τ médio (tempo característico)', fontsize=14)
ax2.set_title(f'τ médio vs SRE para diferentes frações\n(obsprob={obsprob:.2f}, src={src})',
              fontsize=14, fontweight='bold')
ax2.legend(loc='best', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/tau_medio_vs_sRE_comparacao_frac.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"✓ Gráfico 2 salvo: {output_dir}/tau_medio_vs_sRE_comparacao_frac.png")

# ============================================
# GRÁFICO 3: Boxplot do β por SRE (para uma fração específica)
# ============================================

# Para fazer boxplot, precisamos dos dados brutos, não apenas médias
def carregar_dados_brutos(frac):
    arquivo = f"{base_path}/resumo_todos_runs_obsprob_{obsprob:.2f}_frac_{frac}_src_{src}.csv"
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return None

# Escolher uma fração para o boxplot (ex: a primeira da lista)
frac_boxplot = fracoes[0] if fracoes else None

if frac_boxplot:
    df_bruto = carregar_dados_brutos(frac_boxplot)
    
    if df_bruto is not None:
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        
        # Preparar dados para boxplot
        sre_unique = sorted(df_bruto['SRE'].unique())
        beta_por_sre = [df_bruto[df_bruto['SRE'] == sre]['beta'].values for sre in sre_unique]
        
        bp = ax3.boxplot(beta_por_sre, positions=sre_unique, widths=1.5,
                         patch_artist=True, showfliers=False)
        
        # Colorir as caixas
        for box, sre in zip(bp['boxes'], sre_unique):
            box.set_facecolor(cores.get(frac_boxplot, 'lightblue'))
            box.set_alpha(0.7)
        
        # Médias
        stats_frac = dados_por_frac[frac_boxplot]
        ax3.plot(stats_frac['SRE'], stats_frac['beta_mean'], 'ro-', 
                linewidth=2, markersize=8, label='Média')
        
        # Linha β = 1
        ax3.axhline(y=1.0, color='red', linestyle='--', linewidth=2, alpha=0.7)
        
        ax3.set_xlabel('SRE', fontsize=14)
        ax3.set_ylabel('β', fontsize=14)
        ax3.set_title(f'Distribuição do β por SRE (frac={frac_boxplot}, obsprob={obsprob:.2f})',
                      fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/boxplot_beta_frac_{frac_boxplot}.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Gráfico 3 (boxplot) salvo: {output_dir}/boxplot_beta_frac_{frac_boxplot}.png")

# ============================================
# GRÁFICO 4: β vs SRE com barras de erro padrão (sem)
# ============================================

fig4, ax4 = plt.subplots(figsize=(12, 8))

for frac, stats in dados_por_frac.items():
    sre_vals = stats['SRE'].values
    beta_mean = stats['beta_mean'].values
    beta_sem = stats['beta_sem'].values  # erro padrão da média
    
    cor = cores.get(frac, 'gray')
    marker = marcadores.get(frac, 'o')
    
    ax4.errorbar(sre_vals, beta_mean, yerr=beta_sem,
                 fmt=f'{marker}-', capsize=6, markersize=8, linewidth=2,
                 color=cor, ecolor=cor, alpha=0.8,
                 label=f'frac = {frac}')

ax4.axhline(y=1.0, color='red', linestyle='--', linewidth=2.5, alpha=0.8,
            label='β = 1 (exponencial puro)')

ax4.set_xlabel('SRE', fontsize=14)
ax4.set_ylabel('β médio (± erro padrão)', fontsize=14)
ax4.set_title(f'β médio vs SRE (com erro padrão da média)\n(obsprob={obsprob:.2f}, src={src})',
              fontsize=14, fontweight='bold')
ax4.legend(loc='best', fontsize=12)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/beta_medio_vs_sRE_erro_padrao.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"✓ Gráfico 4 salvo: {output_dir}/beta_medio_vs_sRE_erro_padrao.png")

# ============================================
# TABELA COMPARATIVA
# ============================================

print("\n" + "="*80)
print("TABELA COMPARATIVA - β MÉDIO POR SRE E FRAÇÃO")
print("="*80)

# Criar tabela pivot
tabela_beta = pd.DataFrame()

for frac, stats in dados_por_frac.items():
    temp = stats[['SRE', 'beta_mean', 'beta_std', 'n_runs']].copy()
    temp = temp.rename(columns={
        'beta_mean': f'β_frac_{frac}',
        'beta_std': f'σ_frac_{frac}',
        'n_runs': f'n_frac_{frac}'
    })
    
    if tabela_beta.empty:
        tabela_beta = temp
    else:
        tabela_beta = pd.merge(tabela_beta, temp, on='SRE', how='outer')

print("\n", tabela_beta.to_string(index=False))

# ============================================
# SALVAR DADOS COMBINADOS
# ============================================

# Combinar todos os dados em um único CSV
dfs_combinados = []
for frac, stats in dados_por_frac.items():
    stats['frac'] = frac
    dfs_combinados.append(stats)

if dfs_combinados:
    df_all = pd.concat(dfs_combinados, ignore_index=True)
    csv_combinado = f"{output_dir}/dados_combinados_obsprob_{obsprob:.2f}.csv"
    df_all.to_csv(csv_combinado, index=False)
    print(f"\n✓ Dados combinados salvos em: {csv_combinado}")

# ============================================
# RESUMO FINAL
# ============================================

print("\n" + "="*80)
print("RESUMO FINAL")
print("="*80)

for frac, stats in dados_por_frac.items():
    beta_medio_global = stats['beta_mean'].mean()
    print(f"\n📊 FRAC = {frac}:")
    print(f"   Número de SREs: {len(stats)}")
    print(f"   β médio global: {beta_medio_global:.4f}")
    print(f"   β varia de {stats['beta_mean'].min():.4f} a {stats['beta_mean'].max():.4f}")

print("\n" + "="*80)
print(f"✅ GRÁFICOS GERADOS COM SUCESSO!")
print(f"📁 Pasta: {output_dir}/")
print("="*80)

print("\nArquivos gerados:")
print("  • beta_medio_vs_sRE_comparacao_frac.png")
print("  • tau_medio_vs_sRE_comparacao_frac.png")
print("  • beta_medio_vs_sRE_erro_padrao.png")
if frac_boxplot:
    print(f"  • boxplot_beta_frac_{frac_boxplot}.png")
print("  • dados_combinados_obsprob_0.10.csv")