import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Diretório onde estão os dados processados
data_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/data_processed/tempos_convergencia"

# Diretório de saída para os plots
output_dir = "/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/tempos_convergencia"

# Criar diretório de saída se não existir
os.makedirs(output_dir, exist_ok=True)

# Lista de valores de frac
frac_values = [25, 50, 100]

# Cores e marcadores para cada frac
cores = ['blue', 'red', 'green']
marcadores = ['o', 's', '^']
linhas = ['-', '--', '-.']

# Criar figura
plt.figure(figsize=(12, 8))

# Dicionário para armazenar os dados
dados_frac = {}

# Carregar e plotar dados para cada frac
for idx, frac in enumerate(frac_values):
    # Caminho para o arquivo de tempos de convergência
    arquivo = os.path.join(data_dir, f"tempos_convergencia_NE_frac_{frac}.csv")
    
    try:
        df = pd.read_csv(arquivo)
        dados_frac[frac] = df
        
        print(f"frac = {frac}: {len(df)} pontos carregados")
        
        # Plotar curva com barras de erro
        plt.errorbar(df['probabilidade'], 
                    df['tempo_medio'], 
                    yerr=df['tempo_std'],
                    fmt=f'{marcadores[idx]}{linhas[idx]}', 
                    capsize=6,
                    capthick=2,
                    elinewidth=2,
                    markersize=8,
                    color=cores[idx],
                    ecolor='lightgray',
                    alpha=0.8,
                    label=f'frac = {frac}',
                    markeredgecolor='black',
                    markeredgewidth=1,
                    linewidth=2.5)
        
        # Opcional: adicionar linha de tendência
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(df['probabilidade'], 
                                                                         df['tempo_medio'])
        line_x = np.array([df['probabilidade'].min(), df['probabilidade'].max()])
        line_y = intercept + slope * line_x
        
        plt.plot(line_x, line_y, 
                '--', 
                color=cores[idx], 
                linewidth=1.5,
                alpha=0.4)
        
    except FileNotFoundError:
        print(f"  ✗ frac = {frac}: arquivo não encontrado em {arquivo}")
    except Exception as e:
        print(f"  ✗ frac = {frac}: erro - {e}")

# Personalizar gráfico
plt.xlabel('Probabilidade', fontsize=14)
plt.ylabel('Tempo de Convergência (média ± std)', fontsize=14)
plt.title('Tempo de Convergência do N_E (Número de Escapers) para diferentes frac\n(frac = 25, 50, 100)', 
          fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(np.arange(0.0, 1.1, 0.1), rotation=45)
plt.legend(fontsize=12, loc='best')
plt.tight_layout()

# Salvar gráfico
output_path = os.path.join(output_dir, "NE_tempo_convergencia_all_frac.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Gráfico salvo: {output_path}")

plt.show()
plt.close()

# ============================================
# GRÁFICO COMPARATIVO EM SUBPLOTS (opcional)
# ============================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, frac in enumerate(frac_values):
    if frac in dados_frac:
        df = dados_frac[frac]
        
        axes[idx].errorbar(df['probabilidade'], 
                          df['tempo_medio'], 
                          yerr=df['tempo_std'],
                          fmt='o-', 
                          capsize=5,
                          capthick=1.5,
                          elinewidth=1.5,
                          markersize=6,
                          color=cores[idx],
                          ecolor='gray',
                          alpha=0.8)
        
        axes[idx].set_xlabel('Probabilidade', fontsize=11)
        axes[idx].set_ylabel('Tempo de Convergência', fontsize=11)
        axes[idx].set_title(f'frac = {frac}', fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, linestyle='--')
        axes[idx].set_xticks(np.arange(0.0, 1.1, 0.2))
        axes[idx].tick_params(axis='x', rotation=45)

plt.suptitle('Tempo de Convergência do N_E - Comparação entre diferentes frac', 
             fontsize=14, fontweight='bold')
plt.tight_layout()

# Salvar subplots
output_path_sub = os.path.join(output_dir, "NE_tempo_convergencia_subplots.png")
plt.savefig(output_path_sub, dpi=300, bbox_inches='tight')
print(f"✓ Gráfico (subplots) salvo: {output_path_sub}")

plt.show()
plt.close()

# ============================================
# TABELA COMPARATIVA
# ============================================
print("\n" + "="*80)
print("COMPARAÇÃO DOS TEMPOS DE CONVERGÊNCIA - N_E")
print("="*80)

for frac in frac_values:
    if frac in dados_frac:
        df = dados_frac[frac]
        print(f"\n--- FRAC = {frac} ---")
        print(df[['probabilidade', 'tempo_medio', 'tempo_std', 'num_runs']].to_string(index=False))

print("\n" + "="*80)

# ============================================
# GRÁFICO DE BARRAS COMPARATIVO (para algumas probabilidades)
# ============================================
# Escolher algumas probabilidades para comparar
probs_interesse = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(probs_interesse))
width = 0.25
multiplier = 0

for frac in frac_values:
    if frac in dados_frac:
        df = dados_frac[frac]
        tempos = []
        erros = []
        
        for prob in probs_interesse:
            row = df[df['probabilidade'] == prob]
            if not row.empty:
                tempos.append(row['tempo_medio'].values[0])
                erros.append(row['tempo_std'].values[0])
            else:
                tempos.append(0)
                erros.append(0)
        
        offset = width * multiplier
        rects = ax.bar(x + offset, tempos, width, 
                      yerr=erros, capsize=3,
                      label=f'frac = {frac}',
                      color=cores[multiplier],
                      alpha=0.7,
                      edgecolor='black')
        multiplier += 1

ax.set_xlabel('Probabilidade', fontsize=12)
ax.set_ylabel('Tempo de Convergência', fontsize=12)
ax.set_title('Comparação do Tempo de Convergência do N_E para diferentes frac', 
             fontsize=14, fontweight='bold')
ax.set_xticks(x + width)
ax.set_xticklabels([f'{p:.1f}' for p in probs_interesse])
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y', linestyle='--')

plt.tight_layout()

# Salvar gráfico de barras
output_path_bars = os.path.join(output_dir, "NE_tempo_convergencia_bars_comparison.png")
plt.savefig(output_path_bars, dpi=300, bbox_inches='tight')
print(f"✓ Gráfico de barras salvo: {output_path_bars}")

plt.show()
plt.close()

print(f"\n✓ Todos os gráficos salvos em: {output_dir}")