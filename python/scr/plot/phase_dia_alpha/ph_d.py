import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ============================================
# CONFIGURAÇÕES
# ============================================
sre = 2
output_dir = Path("/media/camafeu/data/rossatto/Chase-escape_with_temporary_obstacles_data/plot/diagrama_fase/")
output_dir.mkdir(parents=True, exist_ok=True)

# Intervalos dos eixos
frac_min, frac_max = 5, 100
prob_min, prob_max = 0.0, 1.0

# ============================================
# PONTOS PARA MARCAR NO DIAGRAMA DE FASE
# ============================================
# Edite esta lista manualmente!
# Formato: (fração, probabilidade, rótulo)
# Use rótulo = None se não quiser texto
# ============================================

pontos_manuais = [
    # Exemplos (substitua pelos seus pontos)
    (5, 0.20, "$P_c$"),
    (10, 0.20, "$P_c$"),
    (15, 0.30, "$P_c$"),
    (20, 0.30, "$P_c$"),
    (25, 0.40, "$P_c$"),
    (30, 0.40, "$P_c$"),
    (35, 0.50, "$P_c$"),
    (40, 0.50, "$P_c$"),
    (50, 0.60, "$P_c$"),
    (55, 0.60, "$P_c$"),
    (60, 0.60, "$P_c$"),
    (65, 0.60, "$P_c$"),
    (70, 0.60, "$P_c$"),
    (75, 0.60, "$P_c$"),
    (80, 0.60, "$P_c$"),
    (85, 0.60, "$P_c$"),
    (90, 0.60, "$P_c$"),
    (95, 0.70, "$P_c$"),
    (100, 0.60, "$P_c$"),

    
    # Adicione seus pontos aqui:
    # (frac, prob, "rótulo")
]

# ============================================
# PLOTAGEM
# ============================================

def plot_diagrama_fase():
    """Plota o diagrama de fase com os pontos manuais"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Define os limites dos eixos
    ax.set_xlim(prob_min - 0.05, prob_max + 0.05)
    ax.set_ylim(frac_min - 5, frac_max + 5)
    
    # 2. Configura os eixos
    ax.set_xlabel('Probabilidade', fontsize=14)
    ax.set_ylabel('Fração (%)', fontsize=14)
    ax.set_title(f'Diagrama de Fase - Pontos de Interesse\nSRE = {sre}', fontsize=16, fontweight='bold')
    
    # 3. Adiciona grade (para facilitar a localização dos pontos)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # 4. Configura ticks
    ax.set_xticks(np.arange(0.0, 1.05, 0.1))
    ax.set_yticks(range(frac_min, frac_max + 1, 10))
    ax.set_xticklabels([f'{x:.1f}' for x in np.arange(0.0, 1.05, 0.1)])
    
    # 5. Marca os pontos manuais
    for frac, prob, rotulo in pontos_manuais:
        # Plota o ponto
        ax.plot(prob, frac, 'ro', markersize=10, markerfacecolor='red', 
                markeredgecolor='darkred', markeredgewidth=1.5, zorder=5)
        
        # Adiciona rótulo se existir
        if rotulo is not None:
            ax.annotate(rotulo, 
                       xy=(prob, frac),
                       xytext=(5, 5),  # offset em pontos
                       textcoords='offset points',
                       fontsize=9,
                       fontweight='bold',
                       color='darkred',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    
    # 6. Opcional: adiciona linha diagonal ou outras referências
    # ax.plot([0, 1], [5, 100], 'k--', alpha=0.3, linewidth=0.5)
    
    # 7. Inverte o eixo Y (opcional - para ter fração crescente para cima)
    # ax.invert_yaxis()  # Descomente se quiser fração diminuindo para cima
    
    plt.tight_layout()
    
    # Salva a figura
    output_file = output_dir / f"diagrama_fase_pontos_SRE_{sre}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Diagrama de fase salvo: {output_file}")
    print(f"  Total de pontos marcados: {len(pontos_manuais)}")
    
    return output_file

# ============================================
# EXECUÇÃO
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("GERANDO DIAGRAMA DE FASE COM PONTOS MANUAIS")
    print(f"SRE = {sre}")
    print("="*60)
    
    print("\nPontos a serem marcados:")
    for frac, prob, rotulo in pontos_manuais:
        print(f"  • Fração={frac}%, Prob={prob:.2f} → {rotulo if rotulo else 'sem rótulo'}")
    
    plot_diagrama_fase()
    
    print("\n" + "="*60)
    print("✅ DIAGRAMA GERADO!")
    print("="*60)