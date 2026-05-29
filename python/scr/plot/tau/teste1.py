import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================
# CONFIGURAÇÕES
# ============================================

# Caminho base onde estão os resultados processados
# ATENÇÃO: Use o caminho do processamento WEIBULL, não exponencial!
base_path = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data/data_processed/resultados_fit_weibull_multiplos/prob_v"

# Parâmetros fixos
sre_fixo = 2
src_fixo = 2

# Frações a comparar
fracoes = [25, 50, 100]

# Cores e marcadores para cada fração
cores = {
    25: 'blue',
    50: 'green',
    100: 'red',
    200: 'purple',
    300: 'orange'
}

marcadores = {
    25: 'o',
    50: 's',
    100: '^',
    200: 'D',
    300: 'v'
}

# Pasta para salvar gráficos
output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/fit/weibull_prob_v"
os.makedirs(output_dir, exist_ok=True)

print("="*80)
print("GRÁFICO: β MÉDIO vs PROBABILIDADE (WEIBULL - β CALCULADO)")
print(f"SRE fixo = {sre_fixo}, SRC fixo = {src_fixo}")
print(f"Frações: {fracoes}")
print("="*80)

# ============================================
# FUNÇÃO PARA CARREGAR DADOS DE UMA FRAÇÃO
# ============================================

def carregar_dados_fracao(frac):
    """
    Carrega todos os arquivos resumo_tau_beta.csv para uma dada fração
    """
    
    pasta_base = f"{base_path}"
    dados_combinados = []
    
    if not os.path.exists(pasta_base):
        print(f"  ⚠️ Pasta não encontrada: {pasta_base}")
        return None
    
    for item in os.listdir(pasta_base):
        if not os.path.isdir(os.path.join(pasta_base, item)):
            continue
        
        # Formato esperado: "prob_0.10_frac_25"
        if f"frac_{frac}" in item and item.startswith("prob_"):
            try:
                prob_str = item.split("_")[1]
                prob = float(prob_str)
            except:
                continue
            
            # Caminho para o arquivo resumo
            arquivo = os.path.join(pasta_base, item, "resumo_tau_beta.csv")
            
            if os.path.exists(arquivo):
                df = pd.read_csv(arquivo)
                
                # Verificar se a coluna beta existe
                if 'beta' not in df.columns:
                    print(f"  ⚠️ AVISO: prob={prob:.2f}, frac={frac} - coluna 'beta' não encontrada!")
                    print(f"     Este arquivo veio do fit exponencial (β fixo).")
                    print(f"     Use o processamento WEIBULL para ter β calculado.")
                    continue
                
                # Adicionar colunas de identificação
                df['prob'] = prob
                df['frac'] = frac
                
                dados_combinados.append(df)
                print(f"  ✓ Carregado: prob={prob:.2f}, frac={frac} -> {len(df)} runs, β médio = {df['beta'].mean():.4f}")
    
    if not dados_combinados:
        print(f"  ⚠️ Nenhum dado encontrado para frac={frac}")
        return None
    
    # Combinar todos os DataFrames
    df_completo = pd.concat(dados_combinados, ignore_index=True)
    
    # Calcular estatísticas por probabilidade
    stats = df_completo.groupby('prob').agg({
        'beta': ['mean', 'std', 'sem', 'count'],
        'tau': ['mean', 'std'],
        'r_squared': 'mean'
    }).round(6)
    
    stats.columns = ['beta_mean', 'beta_std', 'beta_sem', 'n_runs', 
                     'tau_mean', 'tau_std', 'r2_mean']
    stats = stats.reset_index()
    stats['frac'] = frac
    
    return stats

# ============================================
# CARREGAR TODAS AS FRAÇÕES
# ============================================

print("\nCarregando dados...")
dados_por_frac = {}

for frac in fracoes:
    print(f"\nProcessando frac = {frac}:")
    stats = carregar_dados_fracao(frac)
    if stats is not None:
        dados_por_frac[frac] = stats

if not dados_por_frac:
    print("\n❌ Nenhum dado encontrado!")
    print("\nVerifique se você rodou o processamento WEIBULL (não exponencial).")
    print(f"O caminho correto deve ser: {base_path}/prob_0.10_frac_25/resumo_tau_beta.csv")
    print("\nSe o arquivo não tiver a coluna 'beta', rode primeiro o programa:")
    print("  process_weibull_vs_prob.py")
    exit()

# ============================================
# GRÁFICO 1: β médio vs Probabilidade (com desvio padrão)
# ============================================

fig1, ax1 = plt.subplots(figsize=(12, 8))

for frac, stats in dados_por_frac.items():
    prob_vals = stats['prob'].values
    beta_mean = stats['beta_mean'].values
    beta_std = stats['beta_std'].values
    
    cor = cores.get(frac, 'gray')
    marker = marcadores.get(frac, 'o')
    
    ax1.errorbar(prob_vals, beta_mean, yerr=beta_std,
                 fmt=f'{marker}-', capsize=6, markersize=8, linewidth=2,
                 color=cor, ecolor=cor, alpha=0.8,
                 label=f'frac = {frac}')
    
    # # Adicionar valores nos pontos
    # for prob, beta in zip(prob_vals, beta_mean):
    #     ax1.annotate(f'{beta:.3f}', (prob, beta),
    #                 xytext=(5, 5), textcoords='offset points',
    #                 fontsize=8, alpha=0.7)

# Linha de referência β = 1
ax1.axhline(y=1.0, color='red', linestyle='--', linewidth=2.5, alpha=0.8,
            label='β = 1 (exponencial puro)')

# Banda de referência
ax1.axhspan(0.9, 1.1, alpha=0.1, color='red', label='Região exponencial (β ≈ 1)')

ax1.set_xlabel('Probabilidade', fontsize=14)
ax1.set_ylabel('β médio', fontsize=14)
ax1.set_title(f'β médio vs Probabilidade (WEIBULL - β CALCULADO)\n(SRE={sre_fixo}, SRC={src_fixo})',
              fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=12)
ax1.grid(True, alpha=0.3)

# Ajustar limites
y_min = min([stats['beta_mean'].min() - stats['beta_std'].min() for stats in dados_por_frac.values()])
y_max = max([stats['beta_mean'].max() + stats['beta_std'].max() for stats in dados_por_frac.values()])
ax1.set_ylim(max(0.5, y_min - 0.1), min(2.0, y_max + 0.1))

plt.tight_layout()
plt.savefig(f"{output_dir}/beta_medio_vs_prob_weibull.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"\n✓ Gráfico 1 salvo: {output_dir}/beta_medio_vs_prob_weibull.png")

# ============================================
# GRÁFICO 2: τ médio vs Probabilidade
# ============================================

fig2, ax2 = plt.subplots(figsize=(12, 8))

for frac, stats in dados_por_frac.items():
    prob_vals = stats['prob'].values
    tau_mean = stats['tau_mean'].values
    tau_std = stats['tau_std'].values
    
    cor = cores.get(frac, 'gray')
    marker = marcadores.get(frac, 'o')
    
    ax2.errorbar(prob_vals, tau_mean, yerr=tau_std,
                 fmt=f'{marker}-', capsize=6, markersize=8, linewidth=2,
                 color=cor, ecolor=cor, alpha=0.8,
                 label=f'frac = {frac}')

ax2.set_xlabel('Probabilidade', fontsize=14)
ax2.set_ylabel('τ médio (tempo característico)', fontsize=14)
ax2.set_title(f'τ médio vs Probabilidade (WEIBULL)\n(SRE={sre_fixo}, SRC={src_fixo})',
              fontsize=14, fontweight='bold')
ax2.legend(loc='best', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{output_dir}/tau_medio_vs_prob_weibull.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"✓ Gráfico 2 salvo: {output_dir}/tau_medio_vs_prob_weibull.png")

# ============================================
# GRÁFICO 3: Comparação β vs τ (scatter)
# ============================================

fig3, axes = plt.subplots(1, len(dados_por_frac), figsize=(6*len(dados_por_frac), 5))

if len(dados_por_frac) == 1:
    axes = [axes]

for idx, (frac, stats) in enumerate(dados_por_frac.items()):
    ax = axes[idx]
    
    prob_vals = stats['prob'].values
    beta_means = stats['beta_mean'].values
    tau_means = stats['tau_mean'].values
    
    scatter = ax.scatter(tau_means, beta_means, c=prob_vals, cmap='viridis', 
                        s=100, edgecolors='black', linewidth=1.5)
    
    # Adicionar labels com valores de probabilidade
    for prob, tau, beta in zip(prob_vals, tau_means, beta_means):
        ax.annotate(f'{prob:.1f}', (tau, beta), 
                   xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.set_xlabel('τ', fontsize=12)
    ax.set_ylabel('β', fontsize=12)
    ax.set_title(f'frac = {frac}', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Probabilidade', fontsize=10)

plt.suptitle(f'Relação β vs τ para diferentes frações (WEIBULL - β CALCULADO)\n(SRE={sre_fixo}, SRC={src_fixo})', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{output_dir}/beta_vs_tau_weibull.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"✓ Gráfico 3 salvo: {output_dir}/beta_vs_tau_weibull.png")

# ============================================
# TABELA COMPARATIVA
# ============================================

print("\n" + "="*80)
print("TABELA COMPARATIVA - β MÉDIO POR PROBABILIDADE (WEIBULL)")
print("="*80)

for frac, stats in dados_por_frac.items():
    print(f"\n📊 FRAC = {frac}:")
    print(stats[['prob', 'beta_mean', 'beta_std', 'n_runs', 'r2_mean']].to_string(index=False))

# ============================================
# SALVAR DADOS COMBINADOS
# ============================================

dfs_combinados = []
for frac, stats in dados_por_frac.items():
    stats['frac'] = frac
    dfs_combinados.append(stats)

if dfs_combinados:
    df_all = pd.concat(dfs_combinados, ignore_index=True)
    csv_combinado = f"{output_dir}/dados_combinados_weibull.csv"
    df_all.to_csv(csv_combinado, index=False)
    print(f"\n✓ Dados combinados salvos em: {csv_combinado}")

# ============================================
# RESUMO FINAL
# ============================================

print("\n" + "="*80)
print("RESUMO FINAL - β CALCULADO (WEIBULL)")
print("="*80)

for frac, stats in dados_por_frac.items():
    beta_medio_global = stats['beta_mean'].mean()
    print(f"\n📊 FRAC = {frac}:")
    print(f"   β médio global: {beta_medio_global:.4f}")
    print(f"   β varia de {stats['beta_mean'].min():.4f} a {stats['beta_mean'].max():.4f}")
    
    # Interpretação
    if beta_medio_global < 0.95:
        print(f"   → Decaimento MAIS LENTO que exponencial (β < 1)")
    elif beta_medio_global > 1.05:
        print(f"   → Decaimento MAIS RÁPIDO que exponencial (β > 1)")
    else:
        print(f"   → Decaimento aproximadamente EXPONENCIAL (β ≈ 1)")

print("\n" + "="*80)
print(f"✅ GRÁFICOS GERADOS COM SUCESSO!")
print(f"📁 Pasta: {output_dir}/")
print("="*80)