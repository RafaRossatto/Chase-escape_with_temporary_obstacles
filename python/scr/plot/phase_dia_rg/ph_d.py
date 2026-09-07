import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ===== LER OS ARQUIVOS CSV =====
try:
    # Lendo os arquivos CSV
    presos_df = pd.read_csv('presos.csv')
    coe_df = pd.read_csv('coe.csv')
    
    print("Arquivos lidos com sucesso!")
    print(f"Presos: {len(presos_df)} pontos")
    print(f"Coexistentes: {len(coe_df)} pontos")
    
except FileNotFoundError as e:
    print(f"Erro: {e}")
    print("Certifique-se que os arquivos 'presos.csv' e 'coe.csv' estão na mesma pasta.")
    exit()

# ===== ORDENANDO OS DADOS =====
presos_df = presos_df.sort_values('x')  # x = fração
coe_df = coe_df.sort_values('x')        # x = fração

# ===== CRIANDO O GRÁFICO =====
fig, ax = plt.subplots(figsize=(14, 8))

# ===== PLOTANDO AS LINHAS =====
# x = fração, y = probabilidade
ax.plot(presos_df['x'], presos_df['y'], 
        color='green', linewidth=2, marker='o', markersize=6, label='Trap-Coexistent')

ax.plot(coe_df['x'], coe_df['y'], 
        color='blue', linewidth=2, marker='s', markersize=6, label='Coexistent-Free')

# ===== CONFIGURANDO OS EIXOS =====
ax.set_xlabel('$N^{C}$', fontsize=14)
ax.set_ylabel('$P$', fontsize=14)
ax.set_title('Dynamical-regime map', fontsize=16, fontweight='bold')

# Configurando os ticks do eixo x (fração)
x_ticks = np.arange(0, 105, 5)
ax.set_xticks(x_ticks)
ax.set_xticklabels(x_ticks)

# Configurando os ticks do eixo y (probabilidade)
y_ticks = np.arange(0, 101, 10)
ax.set_yticks(y_ticks)
ax.set_yticklabels(y_ticks)

# Adicionando texto na coordenada (50, 80) com tamanho 14
ax.text(40, 80, 'Coexistent', fontsize=14, fontweight='bold', color = 'blue')

# Ou com mais opções de formatação
ax.text(15, 60, 'Trapped', fontsize=14, fontweight='bold', color='green')

# Alinhamento do texto
ax.text(80, 50, 'Untrapped', fontsize=14, fontweight='bold', color = 'black')



# ===== LEGENDA =====

ax.set_xlim(5, 102)
ax.set_ylim(0, 102)

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("phase_dia.pdf", dpi=300, bbox_inches='tight')
print("\nGráfico salvo como: grafico_linhas.pdf")
plt.show()

print("\n" + "="*80)
print("ESTATÍSTICAS DOS DADOS:")
print("="*80)
print(f"Total de pontos PRESOS: {len(presos_df)}")
print(f"Total de pontos COEXISTENTES: {len(coe_df)}")