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
        # line_x = np.array([df['probabilidade'].min(), df['probabilidade'].max()])
        # line_y = intercept + slope * line_x
        
        # plt.plot(line_x, line_y, 
        #         '--', 
        #         color=cores[idx], 
        #         linewidth=1.5,
        #         alpha=0.4)
        
    except FileNotFoundError:
        print(f"  ✗ frac = {frac}: arquivo não encontrado em {arquivo}")
    except Exception as e:
        print(f"  ✗ frac = {frac}: erro - {e}")

# Personalizar gráfico
plt.xlabel('prob', fontsize=14)
plt.ylabel('TT', fontsize=14)
plt.title('NC = NE*(25%, 50%, 100%)', 
          fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(np.arange(0.0, 1.1, 0.1), rotation=45)
plt.legend(fontsize=12, loc='best')
plt.yscale('log')
plt.xscale('linear')
plt.tight_layout()

# Salvar gráfico
output_path = os.path.join(output_dir, "NE_tempo_convergencia_all_frac.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Gráfico salvo: {output_path}")

plt.show()
plt.close()